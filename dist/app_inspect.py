import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from threading import Thread
from time import sleep
from . import utils


# This is just for testing
def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        utils.debug('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            utils.debug('{}{}'.format(subindent, f))

list_files(os.getcwd())


# Read Credentials
username = utils.get_input('splunkbase_username')
password = utils.get_input('splunkbase_password')

# Read App Build File
app_build_path = utils.get_input('app_build')
app_build_name = os.path.split(app_build_path)[1]

report_prefix = utils.get_input('report_prefix')


TIMEOUT_MAX = 120

LOGIN_URL = "https://api.splunk.com/2.0/rest/login/splunk"
BASE_URL = "https://appinspect.splunk.com/v1/app"

submit_url = "{}/validate".format(BASE_URL)
status_check_url = "{}/validate/status".format(BASE_URL)
html_response_url = "{}/report".format(BASE_URL)


# Login
response = requests.request("GET", LOGIN_URL, auth=HTTPBasicAuth(
    username, password), data={}, timeout=TIMEOUT_MAX)

if response.status_code != 200:
    utils.error("Error while logining. type={}, status_code={}".format(type, response.status_code))
    sys.exit(1)

res = response.json()
token = res['data']['token']
user = res['data']['user']['name']


HEADERS = {
    'Authorization': 'bearer {}'.format(token),
}

HEADERS_REPORT = {
    'Authorization': 'bearer {}'.format(token),
    'Content-Type': 'text/html',
}



app_inspect_result = ["Running", "Running", "Running"]
                     # app_inspect_result, cloud_inspect_result, ssai_inspect_result


def perform_checks(type="APP_INSPECT"):
    if type=="APP_INSPECT":
        payload = {}
        report_file_name = '{}_app_inspect_check.html'.format(report_prefix)

    elif type == "CLOUD_INSPECT":
        payload = {'included_tags': 'cloud'}
        report_file_name = '{}_cloud_inspect_check.html'.format(report_prefix)

    elif type == "SSAI_INSPECT":
        payload = {'included_tags': 'self-service'}
        report_file_name = '{}_ssai_inspect_check.html'.format(report_prefix)

    app_build_f = open(app_build_path, 'rb')
    app_build_f.seek(0)

    files = [
        ('app_package', (app_build_name, app_build_f, 'application/octet-stream'))
    ]

    utils.debug("App build submitting (type={})".format(type))
    response = requests.request(
        "POST", submit_url, headers=HEADERS, files=files, data=payload, timeout=TIMEOUT_MAX)
    utils.debug("App package submit (type={}) response: status_code={}, text={}".format(type, response.status_code, response.text))
    
    if response.status_code != 200:
        utils.error("Error while requesting for app-inspect check. type={}, status_code={}".format(type, response.status_code))
        return "Exception"

    res = response.json()
    request_id = res['request_id']
    utils.debug("App package submit (type={}) request_id={}".format(type, request_id))

    status = None
    # Status check
    for i in range(10):
        sleep(60)    # check every minute for updated status
        response = requests.request("GET", "{}/{}".format(
            status_check_url, request_id), headers=HEADERS, data={}, timeout=TIMEOUT_MAX)

        utils.debug("App package status check (type={}) response: status_code={}, text={}".format(type, response.status_code, response.text))

        if response.status_code != 200:
            utils.error("Error while requesting for app-inspect check status update. type={}, status_code={}".format(type, response.status_code))
            return "Exception"

        res = response.json()
        res_status = res['status']

        if res_status == 'PROCESSING':
            print("Report is processing for type={}".format(type))
            continue

        # Processing completed
        utils.debug("App package status success (type={}) response: status_code={}, text={}".format(type, response.status_code, response.text))

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
    utils.debug("Html report generating for type={}".format(type))
    response = requests.request("GET", "{}/{}".format(html_response_url,
                                                      request_id), headers=HEADERS_REPORT, data={}, timeout=TIMEOUT_MAX)
    if response.status_code != 200:
        utils.debug("Error while requesting for app-inspect check report. type={}, status_code={}".format(type, response.status_code))
        return "Exception"

    # write results into a file
    with open(report_file_name, 'w+') as f:
        f.write(response.text)

    return status


def perform_app_inspect_check(app_inspect_result):
    status = perform_checks()
    app_inspect_result[0] = status


def perform_cloud_inspect_check(app_inspect_result):
    status = perform_checks(type="CLOUD_INSPECT")
    app_inspect_result[1] = status


def perform_ssai_inspect_check(app_inspect_result):
    status = perform_checks(type="SSAI_INSPECT")
    app_inspect_result[2] = status


thread_app_inspect = Thread(target=perform_app_inspect_check, args=(app_inspect_result,))
thread_app_inspect.start()

thread_cloud_inspect = Thread(target=perform_cloud_inspect_check, args=(app_inspect_result,))
thread_cloud_inspect.start()

thread_ssai_inspect = Thread(target=perform_ssai_inspect_check, args=(app_inspect_result,))
thread_ssai_inspect.start()

# wait for all threads to complete
thread_app_inspect.join()
thread_cloud_inspect.join()
thread_ssai_inspect.join()
utils.debug("All status [app-inspect, cloud-checks, self-service-checks]:{}".format(app_inspect_result))
