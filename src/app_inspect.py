import os
import shutil
import sys
import requests
from requests.auth import HTTPBasicAuth
from threading import Thread
from time import sleep
import traceback

import helper_github_action as utils

TIMEOUT_MAX = 240


class SplunkAppInspect:

    LOGIN_URL = "https://api.splunk.com/2.0/rest/login/splunk"
    BASE_URL = "https://appinspect.splunk.com/v1/app"
    SUBMIT_URL = "{}/validate".format(BASE_URL)
    STATUS_CHECK_URL = "{}/validate/status".format(BASE_URL)
    HTML_RESPONSE_URL = "{}/report".format(BASE_URL)


    def __init__(self, app_build_path, app_package_id, app_version_encoded, app_build_number_encoded) -> None:
        self.is_app_inspect_check = utils.str_to_boolean(
            utils.get_input('is_app_inspect_check'))
        utils.info("is_app_inspect_check: {}".format(
            self.is_app_inspect_check))
        if not self.is_app_inspect_check:
            utils.info("Ignoring App-inspect checks.")
            return

        self.splunkbase_username = utils.get_input('splunkbase_username')
        self.splunkbase_password = utils.get_input('splunkbase_password')

        if not self.splunkbase_username:
            msg = "splunkbase_username input is not provided."
            utils.error(msg)
            raise Exception(msg)

        if not self.splunkbase_password:
            msg = "splunkbase_password input is not provided."
            utils.error(msg)
            raise Exception(msg)

        self.app_build_path = app_build_path

        self.report_name_prefix = f"{app_package_id}_{app_version_encoded}_{app_build_number_encoded}"

        self.app_build_filename = os.path.basename(app_build_path)
        self.app_inspect_report_dir = "{}_reports".format(self.report_name_prefix)

        try:
            shutil.rmtree(self.app_inspect_report_dir)
        except:
            pass   # nothing to delete if folder not exist
        os.mkdir(self.app_inspect_report_dir)

        self.headers = None
        self.headers_report = None
        self.app_inspect_result = ["Running", "Running", "Running"]
        # For Above  ->  app_inspect_result, cloud_inspect_result, ssai_inspect_result

        self._api_login()

        os.chdir(utils.CommonDirPaths.MAIN_DIR)


    def _api_login(self):
        utils.info("Creating access token.")
        response = requests.request("GET", self.LOGIN_URL, auth=HTTPBasicAuth(
            self.splunkbase_username, self.splunkbase_password), data={}, timeout=TIMEOUT_MAX)

        if response.status_code != 200:
            utils.error("Error while logging. status_code={}, response={}".format(
                response.status_code, response.text))
            raise Exception("Unable to login to Splunkbase.")

        res = response.json()
        token = res['data']['token']
        user = res['data']['user']['name']
        utils.info("Got access token for {}".format(user))

        self.headers = {
            'Authorization': 'bearer {}'.format(token),
        }
        self.headers_report = {
            'Authorization': 'bearer {}'.format(token),
            'Content-Type': 'text/html',
        }


    def _perform_checks(self, check_type="APP_INSPECT"):
        if check_type == "APP_INSPECT":
            payload = {}
            report_file_name = '{}_app_inspect_check.html'.format(
                self.report_name_prefix)

        elif check_type == "CLOUD_INSPECT":
            payload = {'included_tags': 'cloud'}
            report_file_name = '{}_cloud_inspect_check.html'.format(
                self.report_name_prefix)

        elif check_type == "SSAI_INSPECT":
            payload = {'included_tags': 'self-service'}
            report_file_name = '{}_ssai_inspect_check.html'.format(
                self.report_name_prefix)

        app_build_f = open(self.app_build_path, 'rb')
        app_build_f.seek(0)

        files = [
            ('app_package', (self.app_build_filename,
             app_build_f, 'application/octet-stream'))
        ]

        utils.info("App build submitting (check_type={})".format(check_type))
        response = requests.request(
            "POST", self.SUBMIT_URL, headers=self.headers, files=files, data=payload, timeout=TIMEOUT_MAX)
        utils.info("App package submit (check_type={}) response: status_code={}, text={}".format(
            check_type, response.status_code, response.text))

        if response.status_code != 200:
            utils.error("Error while requesting for app-inspect check. check_type={}, status_code={}".format(
                check_type, response.status_code))
            return "Exception"

        res = response.json()
        request_id = res['request_id']
        utils.info("App package submit (check_type={}) request_id={}".format(
            check_type, request_id))

        status = None
        # Status check
        for i in range(10):
            sleep(60)    # check every minute for updated status
            utils.info("...")
            try:
                response = requests.request("GET", "{}/{}".format(
                    self.STATUS_CHECK_URL, request_id), headers=self.headers, data={}, timeout=TIMEOUT_MAX)
            except:
                # continue if there is any error (specifically 10 times for timeout error)
                continue

            utils.info("App package status check (check_type={}) response: status_code={}, text={}".format(
                check_type, response.status_code, response.text))

            if response.status_code != 200:
                utils.error("Error while requesting for app-inspect check status update. check_type={}, status_code={}".format(
                    check_type, response.status_code))
                return "Exception"

            res = response.json()
            res_status = res['status']

            if res_status == 'PROCESSING':
                utils.info(
                    "Report is processing for check_type={}".format(check_type))
                continue

            # Processing completed
            utils.info("App package status success (check_type={}) response: status_code={}, text={}".format(
                check_type, response.status_code, response.text))

            if int(res['info']['failure']) != 0:
                status = "Failure"
            elif int(res['info']['error']) != 0:
                status = "Error"
            else:
                status = "Passed"
            break

        else:
            return "Timed-out"

        # HTML Report retrive
        utils.info("Html report generating for check_type={}".format(check_type))
        response = requests.request("GET", "{}/{}".format(self.HTML_RESPONSE_URL,
                                                          request_id), headers=self.headers_report, data={}, timeout=TIMEOUT_MAX)
        if response.status_code != 200:
            utils.error("Error while requesting for app-inspect check report. check_type={}, status_code={}".format(
                check_type, response.status_code))
            return "Exception"

        # write results into a file
        report_file = os.path.join(
            self.app_inspect_report_dir, report_file_name)
        with open(report_file, 'w+') as f:
            utils.info(f"Writing the App-inspect report in file={report_file}")
            f.write(response.text)

        return status


    def _perform_app_inspect_check(self):
        utils.info("Performing app-inspect checks...")
        status = "Error"
        try:
            status = self._perform_checks()
        except Exception as e:
            utils.error("Error while checking app-inspect:{}".format(e))
            utils.error(traceback.format_exc())
            raise e
        self.app_inspect_result[0] = status


    def _perform_cloud_inspect_check(self):
        utils.info("Performing cloud-inspect checks...")
        status = "Error"
        try:
            status = self._perform_checks(check_type="CLOUD_INSPECT")
        except Exception as e:
            utils.error("Error while checking cloud-inspect:{}".format(e))
            utils.error(traceback.format_exc())
            raise e
        self.app_inspect_result[1] = status


    def _perform_ssai_inspect_check(self):
        utils.info("Performing ssai-inspect checks...")
        status = "Error"
        try:
            status = self._perform_checks(check_type="SSAI_INSPECT")
        except Exception as e:
            utils.error("Error while checking ssai-inspect:{}".format(e))
            utils.error(traceback.format_exc())
            raise e
        self.app_inspect_result[2] = status


    def run_all_checks(self):
        utils.info("Running the Splunk App inspect check.")
        if not self.is_app_inspect_check:
            return

        thread_app_inspect = Thread(target=self._perform_app_inspect_check)
        thread_app_inspect.start()

        thread_cloud_inspect = Thread(target=self._perform_cloud_inspect_check)
        thread_cloud_inspect.start()

        thread_ssai_inspect = Thread(target=self._perform_ssai_inspect_check)
        thread_ssai_inspect.start()

        # wait for all threads to complete
        thread_app_inspect.join()
        thread_cloud_inspect.join()
        thread_ssai_inspect.join()
        utils.info(
            "All threads for Splunk App Inspect Checkes has been completed.")

        if all(i == "Passed" for i in self.app_inspect_result):
            utils.info(
                "All status [app-inspect, cloud-checks, self-service-checks]:{}".format(self.app_inspect_result))
        else:
            msg = "All status [app-inspect, cloud-checks, self-service-checks]:{}".format(
                self.app_inspect_result)
            utils.error(msg)
            raise Exception(msg)
