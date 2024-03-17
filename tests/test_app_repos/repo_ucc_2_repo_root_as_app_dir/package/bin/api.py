import time
from datetime import datetime
import re
import requests
import traceback


SOURCETYPE_1 = "mydata:my_input"
SOURCETYPE_2 = "mydata:my_input2"



class API:
    def __init__(self, logger, addon_input, account_details, proxy_settings=None):
        self.logger = logger
        self.addon_input = addon_input
        self.input_name = addon_input.input_name
        self.input_item = addon_input.input_item
        self.account_details = account_details
        self.proxy_settings = proxy_settings
        self.verify = False

        self.logger.debug(f"Account Details: {account_details}")
        self.base_url = account_details.url
        # self._login()
        self.logger.debug("API class initialized.")


    def make_api_call(self, url, method="GET", params=None, data=None):
        headers = {'X-ApiKeys': 'accessKey={0} ; secretKey={1}'.format(self.account_details.client_id, self.account_details.client_secret), 'content-type': 'application/json'}
        full_url = f'{self.base_url.rstrip("/")}/{url.lstrip("/")}'

        self.logger.info(f"HTTP request. URL={full_url}, params={params}")
        self.logger.debug(f"HTTP request. data={data}")

        try:
            response = requests.request(method, full_url, params=params, json=data, headers=headers, proxies=self.proxy_settings, verify=self.verify, timeout=280)
            status_code = response.status_code

            self.logger.info("HTTP response. URL={}: status_code={}".format(full_url, status_code))
            self.logger.debug("HTTP response. response_text={}".format(response.text))

            if response.ok:
                if 'download' in response.text:
                    return response.text
                else:
                    return response.json()
            else:
                self.logger.error('Error while making the API call to URL={}, status_code={}'.format(full_url, status_code))
                return None

        except Exception as exception:
            self.logger.exception(
                'Error while making the API call to URL={}, error={}'.format(full_url, exception))
            return False


    def collect_data(self, ckpt):
        return ckpt

    def collect_data1(self, ckpt):
        return ckpt