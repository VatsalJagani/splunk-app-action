import os
import shutil
import traceback
from threading import Thread
from time import sleep

import github_action_toolkit as gat
import requests
from requests.auth import HTTPBasicAuth

from helpers.saved_values import AppInfo, SavedPaths

TIMEOUT_MAX = 240


class SplunkAppInspect:
    LOGIN_URL: str = "https://api.splunk.com/2.0/rest/login/splunk"
    BASE_URL: str = "https://appinspect.splunk.com/v1/app"
    SUBMIT_URL: str = f"{BASE_URL}/validate"
    STATUS_CHECK_URL: str = f"{BASE_URL}/validate/status"
    HTML_RESPONSE_URL: str = f"{BASE_URL}/report"

    def __init__(
        self,
        saved_paths: SavedPaths,
        app_info: AppInfo,
        app_build_path: str,
        splunkbase_username: str,
        splunkbase_password: str,
    ) -> None:
        self.splunkbase_username: str = splunkbase_username
        self.splunkbase_password: str = splunkbase_password

        if not self.splunkbase_username:
            msg = "splunkbase_username input is not provided."
            gat.error(msg)
            raise Exception(msg)

        if not self.splunkbase_password:
            msg = "splunkbase_password input is not provided."
            gat.error(msg)
            raise Exception(msg)

        self.app_build_path: str = app_build_path

        self.report_name_prefix: str = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}"

        self.app_build_filename: str = os.path.basename(app_build_path)
        self.app_inspect_report_dir: str = f"{self.report_name_prefix}_reports"

        try:
            shutil.rmtree(self.app_inspect_report_dir)
        except Exception as e:
            # nothing to delete if folder not exist
            gat.debug(f"No folder present nothing to be done. {e}")
        os.mkdir(self.app_inspect_report_dir)

        self.headers: dict[str, str] | None = None
        self.headers_report: dict[str, str] | None = None
        self.app_inspect_result: list[str] = ["Running", "Running", "Running"]
        # For Above  ->  app_inspect_result, cloud_inspect_result, ssai_inspect_result

        self._api_login()

        os.chdir(saved_paths.root_dir_path)

    def _api_login(self):
        gat.info("Starting Splunkbase API authentication...")
        gat.debug(f"Authenticating user: {self.splunkbase_username}")

        response = requests.request(
            "GET",
            self.LOGIN_URL,
            auth=HTTPBasicAuth(self.splunkbase_username, self.splunkbase_password),
            data={},
            timeout=TIMEOUT_MAX,
        )

        if response.status_code != 200:
            gat.error(f"Authentication failed with status {response.status_code}: {response.text}")
            raise Exception("Unable to authenticate with Splunkbase API")

        res = response.json()
        token = res["data"]["token"]
        user = res["data"]["user"]["name"]
        gat.debug(f"Authentication successful for user: {user}")

        self.headers = {
            "Authorization": f"bearer {token}",
        }

        gat.info("Splunkbase API authentication completed successfully")
        self.headers_report = {
            "Authorization": f"bearer {token}",
            "Content-Type": "text/html",
        }

    def _perform_checks(self, check_type: str = "APP_INSPECT") -> str:
        payload: dict[str, str] = {}
        report_file_name: str

        if check_type == "APP_INSPECT":
            payload = {}
            report_file_name = f"{self.report_name_prefix}_app_inspect_check.html"

        elif check_type == "CLOUD_INSPECT":
            payload = {"included_tags": "cloud"}
            report_file_name = f"{self.report_name_prefix}_cloud_inspect_check.html"

        elif check_type == "SSAI_INSPECT":
            payload = {"included_tags": "self-service"}
            report_file_name = f"{self.report_name_prefix}_ssai_inspect_check.html"

        else:
            report_file_name = f"{self.report_name_prefix}_default_check.html"

        app_build_f = open(self.app_build_path, "rb")
        app_build_f.seek(0)

        files = [
            ("app_package", (self.app_build_filename, app_build_f, "application/octet-stream"))
        ]

        gat.info(f"App build submitting (check_type={check_type})")
        response = requests.request(
            "POST",
            self.SUBMIT_URL,
            headers=self.headers,
            files=files,
            data=payload,
            timeout=TIMEOUT_MAX,
        )
        gat.info(
            f"App package submit (check_type={check_type}) response: status_code={response.status_code}, text={response.text}"
        )

        if response.status_code != 200:
            gat.error(
                f"Error while requesting for app-inspect check. check_type={check_type}, status_code={response.status_code}"
            )
            return "Exception"

        res = response.json()
        request_id = res["request_id"]
        gat.info(f"App package submit (check_type={check_type}) request_id={request_id}")

        status = None
        # Status check
        for _ in range(10):
            sleep(60)  # check every minute for updated status
            gat.info("...")
            try:
                response = requests.request(
                    "GET",
                    f"{self.STATUS_CHECK_URL}/{request_id}",
                    headers=self.headers,
                    data={},
                    timeout=TIMEOUT_MAX,
                )
            except Exception as e:
                # continue if there is any error (specifically 10 times for timeout error)
                gat.debug(f"No action needed. {e}")
                continue

            gat.info(
                f"App package status check (check_type={check_type}) response: status_code={response.status_code}, text={response.text}"
            )

            if response.status_code != 200:
                gat.error(
                    f"Error while requesting for app-inspect check status update. check_type={check_type}, status_code={response.status_code}"
                )
                return "Exception"

            res = response.json()
            res_status = res["status"]

            if res_status == "PROCESSING":
                gat.info(f"Report is processing for check_type={check_type}")
                continue

            # Processing completed
            gat.info(
                f"App package status success (check_type={check_type}) response: status_code={response.status_code}, text={response.text}"
            )

            if int(res["info"]["failure"]) != 0:
                status = "Failure"
            elif int(res["info"]["error"]) != 0:
                status = "Error"
            else:
                status = "Passed"
            break

        else:
            return "Timed-out"

        # HTML Report retrieve
        gat.info(f"Html report generating for check_type={check_type}")
        response = requests.request(
            "GET",
            f"{self.HTML_RESPONSE_URL}/{request_id}",
            headers=self.headers_report,
            data={},
            timeout=TIMEOUT_MAX,
        )
        if response.status_code != 200:
            gat.error(
                f"Error while requesting for app-inspect check report. check_type={check_type}, status_code={response.status_code}"
            )
            return "Exception"

        # write results into a file
        report_file = os.path.join(self.app_inspect_report_dir, report_file_name)
        with open(report_file, "w+") as f:
            gat.info(f"Writing the App-inspect report in file={report_file}")
            f.write(response.text)

        return status

    def _perform_app_inspect_check(self) -> None:
        gat.info("Starting app-inspect checks...")
        status = "Error"
        try:
            status = self._perform_checks()
            gat.debug(f"App-inspect check completed with status: {status}")
            gat.info("App-inspect checks completed successfully")
        except Exception as e:
            gat.error(f"App-inspect check failed: {e}")
            gat.error(traceback.format_exc())
            raise e
        self.app_inspect_result[0] = status

    def _perform_cloud_inspect_check(self) -> None:
        gat.info("Starting cloud-inspect checks...")
        status = "Error"
        try:
            status = self._perform_checks(check_type="CLOUD_INSPECT")
            gat.debug(f"Cloud-inspect check completed with status: {status}")
            gat.info("Cloud-inspect checks completed successfully")
        except Exception as e:
            gat.error(f"Cloud-inspect check failed: {e}")
            gat.error(traceback.format_exc())
            raise e
        self.app_inspect_result[1] = status

    def _perform_ssai_inspect_check(self) -> None:
        gat.info("Starting SSAI-inspect checks...")
        status = "Error"
        try:
            status = self._perform_checks(check_type="SSAI_INSPECT")
            gat.debug(f"SSAI-inspect check completed with status: {status}")
            gat.info("SSAI-inspect checks completed successfully")
        except Exception as e:
            gat.error(f"SSAI-inspect check failed: {e}")
            gat.error(traceback.format_exc())
            raise e
        self.app_inspect_result[2] = status

    def run_all_checks(self) -> None:
        with gat.group("✅ Running Splunk app inspect checks"):
            gat.debug(
                "Launching Splunk app-inspect, cloud-inspect, and SSAI-inspect checks in parallel."
            )

            thread_app_inspect = Thread(target=self._perform_app_inspect_check)
            thread_app_inspect.start()

            thread_cloud_inspect = Thread(target=self._perform_cloud_inspect_check)
            thread_cloud_inspect.start()

            thread_ssai_inspect = Thread(target=self._perform_ssai_inspect_check)
            thread_ssai_inspect.start()

            # wait for all threads to complete
            gat.debug("Waiting for all inspect check threads to complete...")
            thread_app_inspect.join()
            thread_cloud_inspect.join()
            thread_ssai_inspect.join()

            # Evaluate results
            gat.debug(
                f"Inspect results - app:{self.app_inspect_result[0]}, cloud:{self.app_inspect_result[1]}, ssai:{self.app_inspect_result[2]}"
            )

            if all(i == "Passed" for i in self.app_inspect_result):
                gat.info("All Splunk app inspect checks completed successfully - all checks passed")
            else:
                msg = f"Splunk app inspect checks failed - results: [app-inspect: {self.app_inspect_result[0]}, cloud-checks: {self.app_inspect_result[1]}, ssai-checks: {self.app_inspect_result[2]}]"
                gat.error(msg)
                raise Exception(msg)
