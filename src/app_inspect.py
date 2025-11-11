# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
import json
import os
import shutil
import subprocess
import traceback
from threading import Thread
from time import sleep
from typing import Any, cast

import github_action_toolkit as gat
import requests
from requests.auth import HTTPBasicAuth

import helpers.check_run_publisher as check_run_publisher
import helpers.sarif_converter as sarif_converter
from helpers.saved_values import AppInfo, SavedPaths

TIMEOUT_MAX = 240


class SplunkAppInspect:
    LOGIN_URL: str = "https://api.splunk.com/2.0/rest/login/splunk"
    BASE_URL: str = "https://appinspect.splunk.com/v1/app"
    SUBMIT_URL: str = f"{BASE_URL}/validate"
    STATUS_CHECK_URL: str = f"{BASE_URL}/validate/status"
    JSON_RESPONSE_URL: str = f"{BASE_URL}/report"
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
        json_report_file_name: str
        html_report_file_name: str

        if check_type == "APP_INSPECT":
            payload = {}
            json_report_file_name = f"{self.report_name_prefix}_app_inspect_check.json"
            html_report_file_name = f"{self.report_name_prefix}_app_inspect_check.html"

        elif check_type == "CLOUD_INSPECT":
            payload = {"included_tags": "cloud"}
            json_report_file_name = f"{self.report_name_prefix}_cloud_inspect_check.json"
            html_report_file_name = f"{self.report_name_prefix}_cloud_inspect_check.html"

        elif check_type == "SSAI_INSPECT":
            payload = {"included_tags": "self-service"}
            json_report_file_name = f"{self.report_name_prefix}_ssai_inspect_check.json"
            html_report_file_name = f"{self.report_name_prefix}_ssai_inspect_check.html"

        else:
            json_report_file_name = f"{self.report_name_prefix}_default_check.json"
            html_report_file_name = f"{self.report_name_prefix}_default_check.html"

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

        # First, fetch JSON Report
        gat.info(f"Fetching JSON report for check_type={check_type}")

        # Prepare headers for JSON request
        json_headers = dict(self.headers_report) if self.headers_report else {}
        json_headers["Content-Type"] = "application/json"

        json_response = requests.request(
            "GET",
            f"{self.JSON_RESPONSE_URL}/{request_id}",
            headers=json_headers,
            data={},
            timeout=TIMEOUT_MAX,
        )
        if json_response.status_code != 200:
            gat.error(
                f"Error while requesting JSON report for app-inspect check. check_type={check_type}, status_code={json_response.status_code}"
            )
            return "Exception"

        # Save JSON report to file
        json_report_file = os.path.join(self.app_inspect_report_dir, json_report_file_name)
        with open(json_report_file, "w+") as f:
            gat.info(f"Writing the App-inspect JSON report in file={json_report_file}")
            f.write(json_response.text)

        # Convert JSON to HTML using the converter module
        gat.info(f"Converting JSON report to HTML for check_type={check_type}")
        html_report_file = os.path.join(self.app_inspect_report_dir, html_report_file_name)

        try:
            from helpers.splunk_app_inspect_report_json_to_html_converter import (
                convert_json_file_to_html_file,
            )

            convert_json_file_to_html_file(json_report_file, html_report_file)
            gat.info(f"HTML report generated successfully: {html_report_file}")
        except Exception as e:
            gat.warning(f"Could not convert JSON report to HTML: {e}")
            gat.debug(traceback.format_exc())

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

            # Set output variables for inspect statuses
            gat.set_output("app_inspect_status", self.app_inspect_result[0])
            gat.set_output("cloud_inspect_status", self.app_inspect_result[1])
            gat.set_output("ssai_inspect_status", self.app_inspect_result[2])

            if all(i == "Passed" for i in self.app_inspect_result):
                gat.info("All Splunk app inspect checks completed successfully - all checks passed")
            else:
                msg = f"Splunk app inspect checks failed - results: [app-inspect: {self.app_inspect_result[0]}, cloud-checks: {self.app_inspect_result[1]}, ssai-checks: {self.app_inspect_result[2]}]"
                gat.error(msg)
                raise Exception(msg)


class SplunkLocalAppInspect:
    """Local app inspect using the splunk-appinspect Python library"""

    def __init__(
        self,
        saved_paths: SavedPaths,
        app_info: AppInfo,
        app_build_path: str,
    ) -> None:
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

        self.app_inspect_result: list[str] = ["Running", "Running", "Running"]
        # For Above  ->  app_inspect_result, cloud_inspect_result, ssai_inspect_result

        os.chdir(saved_paths.root_dir_path)

    def _run_local_inspect(self, check_type: str = "APP_INSPECT") -> str:
        """Run local app inspect using splunk-appinspect CLI"""
        gat.info(f"Running local app inspect check (check_type={check_type})")

        report_file_name: str
        included_tags: list[str] = []

        if check_type == "APP_INSPECT":
            report_file_name = f"{self.report_name_prefix}_app_inspect_check.json"
            # No specific tags for app inspect - run all checks
        elif check_type == "CLOUD_INSPECT":
            report_file_name = f"{self.report_name_prefix}_cloud_inspect_check.json"
            included_tags = ["cloud"]
        elif check_type == "SSAI_INSPECT":
            report_file_name = f"{self.report_name_prefix}_ssai_inspect_check.json"
            included_tags = ["self-service"]
        else:
            report_file_name = f"{self.report_name_prefix}_default_check.json"

        report_file_path = os.path.join(self.app_inspect_report_dir, report_file_name)

        # Build the splunk-appinspect command
        cmd = [
            "splunk-appinspect",
            "inspect",
            self.app_build_path,
            "--mode",
            "precert",
            "--output-file",
            report_file_path,
            "--data-format",
            "json",
            "--max-messages",
            "all",
        ]

        # Add included tags if specified
        for tag in included_tags:
            cmd.extend(["--included-tags", tag])

        gat.debug(f"Running command: {' '.join(cmd)}")

        try:
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
                check=False,  # Don't raise exception on non-zero exit code
            )

            gat.debug(f"Command stdout: {result.stdout}")
            if result.stderr:
                gat.debug(f"Command stderr: {result.stderr}")

            # Check if the command completed successfully or at least generated a report
            # Note: splunk-appinspect may return non-zero exit code even when it generates a valid report
            # if there are failures in the checks, so we check for the report file rather than exit code
            if not os.path.exists(report_file_path):
                gat.error(
                    f"Report file was not generated: {report_file_path}. Command exit code: {result.returncode}"
                )
                return "Exception"

            # Parse the JSON report to determine status

            with open(report_file_path) as f:
                report_data_raw = json.load(f)
                if not isinstance(report_data_raw, dict):
                    gat.error("Unexpected report format: root is not a dict")
                    return "Exception"
                # Narrow dynamic JSON to a typed mapping for downstream usage
                report_data: dict[str, Any] = cast(dict[str, Any], report_data_raw)

            # Generate HTML report from JSON using the converter module
            html_report_name = report_file_name.replace(".json", ".html")
            html_report_path = os.path.join(self.app_inspect_report_dir, html_report_name)

            try:
                from helpers.splunk_app_inspect_report_json_to_html_converter import (
                    convert_json_file_to_html_file,
                )

                convert_json_file_to_html_file(report_file_path, html_report_path)
                gat.info(f"HTML report generated successfully: {html_report_path}")
            except Exception as e:
                gat.warning(f"Could not convert JSON report to HTML: {e}")
                gat.debug(traceback.format_exc())

            # Determine status based on report summary
            summary_val = report_data.get("summary")
            summary: dict[str, Any] = (
                cast(dict[str, Any], summary_val)
                if isinstance(summary_val, dict)
                else dict[str, Any]()
            )
            failure_count = int(summary.get("failure", 0))
            error_count = int(summary.get("error", 0))

            gat.debug(f"Check results - failures: {failure_count}, errors: {error_count}")

            if failure_count > 0:
                return "Failure"
            elif error_count > 0:
                return "Error"
            else:
                return "Passed"

        except subprocess.TimeoutExpired:
            gat.error(f"App inspect check timed out for check_type={check_type}")
            return "Timed-out"
        except Exception as e:
            gat.error(f"Error running local app inspect: {e}")
            gat.error(traceback.format_exc())
            return "Exception"

    def _perform_app_inspect_check(self) -> None:
        gat.info("Starting local app-inspect checks...")
        status = "Error"
        try:
            status = self._run_local_inspect()
            gat.debug(f"Local app-inspect check completed with status: {status}")
            gat.info("Local app-inspect checks completed successfully")
        except Exception as e:
            gat.error(f"Local app-inspect check failed: {e}")
            gat.error(traceback.format_exc())
            raise e
        self.app_inspect_result[0] = status

    def _perform_cloud_inspect_check(self) -> None:
        gat.info("Starting local cloud-inspect checks...")
        status = "Error"
        try:
            status = self._run_local_inspect(check_type="CLOUD_INSPECT")
            gat.debug(f"Local cloud-inspect check completed with status: {status}")
            gat.info("Local cloud-inspect checks completed successfully")
        except Exception as e:
            gat.error(f"Local cloud-inspect check failed: {e}")
            gat.error(traceback.format_exc())
            raise e
        self.app_inspect_result[1] = status

    def _perform_ssai_inspect_check(self) -> None:
        gat.info("Starting local SSAI-inspect checks...")
        status = "Error"
        try:
            status = self._run_local_inspect(check_type="SSAI_INSPECT")
            gat.debug(f"Local SSAI-inspect check completed with status: {status}")
            gat.info("Local SSAI-inspect checks completed successfully")
        except Exception as e:
            gat.error(f"Local SSAI-inspect check failed: {e}")
            gat.error(traceback.format_exc())
            raise e
        self.app_inspect_result[2] = status

    def run_all_checks(self) -> None:
        with gat.group("✅ Running local Splunk app inspect checks"):
            gat.debug(
                "Launching local Splunk app-inspect, cloud-inspect, and SSAI-inspect checks in parallel."
            )

            thread_app_inspect = Thread(target=self._perform_app_inspect_check)
            thread_app_inspect.start()

            thread_cloud_inspect = Thread(target=self._perform_cloud_inspect_check)
            thread_cloud_inspect.start()

            thread_ssai_inspect = Thread(target=self._perform_ssai_inspect_check)
            thread_ssai_inspect.start()

            # wait for all threads to complete
            gat.debug("Waiting for all local inspect check threads to complete...")
            thread_app_inspect.join()
            thread_cloud_inspect.join()
            thread_ssai_inspect.join()

            # Evaluate results
            gat.debug(
                f"Local inspect results - app:{self.app_inspect_result[0]}, cloud:{self.app_inspect_result[1]}, ssai:{self.app_inspect_result[2]}"
            )

            # Set output variables for inspect statuses
            gat.set_output("app_inspect_status", self.app_inspect_result[0])
            gat.set_output("cloud_inspect_status", self.app_inspect_result[1])
            gat.set_output("ssai_inspect_status", self.app_inspect_result[2])

            # Generate SARIF reports if enabled
            publish_sarif = gat.get_user_input_as("publish_sarif", bool, True)
            if publish_sarif:
                self._generate_sarif_reports()

            # Publish check runs
            self._publish_check_runs()

            if all(i == "Passed" for i in self.app_inspect_result):
                gat.info(
                    "All local Splunk app inspect checks completed successfully - all checks passed"
                )
            else:
                msg = f"Local Splunk app inspect checks failed - results: [app-inspect: {self.app_inspect_result[0]}, cloud-checks: {self.app_inspect_result[1]}, ssai-checks: {self.app_inspect_result[2]}]"
                gat.error(msg)
                raise Exception(msg)

    def _generate_sarif_reports(self) -> None:
        """Generate SARIF reports from JSON AppInspect results."""
        try:
            gat.info("Generating SARIF reports from AppInspect results...")

            sarif_files = []

            # Convert app-inspect report
            app_json = os.path.join(
                self.app_inspect_report_dir, f"{self.report_name_prefix}_app_inspect_check.json"
            )
            if os.path.exists(app_json):
                app_sarif = os.path.join(
                    self.app_inspect_report_dir,
                    f"{self.report_name_prefix}_app_inspect_check.sarif",
                )
                sarif_converter.convert_appinspect_to_sarif(app_json, app_sarif, "app-inspect")
                sarif_files.append(app_sarif)

            # Convert cloud-inspect report
            cloud_json = os.path.join(
                self.app_inspect_report_dir,
                f"{self.report_name_prefix}_cloud_inspect_check.json",
            )
            if os.path.exists(cloud_json):
                cloud_sarif = os.path.join(
                    self.app_inspect_report_dir,
                    f"{self.report_name_prefix}_cloud_inspect_check.sarif",
                )
                sarif_converter.convert_appinspect_to_sarif(
                    cloud_json, cloud_sarif, "cloud-inspect"
                )
                sarif_files.append(cloud_sarif)

            # Convert SSAI-inspect report
            ssai_json = os.path.join(
                self.app_inspect_report_dir, f"{self.report_name_prefix}_ssai_inspect_check.json"
            )
            if os.path.exists(ssai_json):
                ssai_sarif = os.path.join(
                    self.app_inspect_report_dir,
                    f"{self.report_name_prefix}_ssai_inspect_check.sarif",
                )
                sarif_converter.convert_appinspect_to_sarif(ssai_json, ssai_sarif, "ssai-inspect")
                sarif_files.append(ssai_sarif)

            # Merge all SARIF reports into one
            if sarif_files:
                merged_sarif = os.path.join(self.app_inspect_report_dir, "appinspect.sarif")
                sarif_converter.merge_sarif_reports(sarif_files, merged_sarif)
                gat.info(f"SARIF reports generated and merged: {merged_sarif}")

        except Exception as e:
            gat.warning(f"Failed to generate SARIF reports: {e}")
            # Don't fail the whole run if SARIF generation fails

    def _publish_check_runs(self) -> None:
        """Publish GitHub Check Runs for AppInspect results."""
        try:
            gat.info("Publishing GitHub Check Runs for AppInspect results...")
            check_run_publisher.publish_appinspect_check_runs(
                app_inspect_status=self.app_inspect_result[0],
                cloud_inspect_status=self.app_inspect_result[1],
                ssai_inspect_status=self.app_inspect_result[2],
                report_dir=self.app_inspect_report_dir,
            )
        except Exception as e:
            gat.warning(f"Failed to publish check runs: {e}")
            # Don't fail the whole run if check run publishing fails
