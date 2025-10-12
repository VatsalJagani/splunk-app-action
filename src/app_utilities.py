import os

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths
from utilities.common_splunk_js_utilities import CommonJSUtilitiesFile
from utilities.logger import LoggerUtility
from utilities.splunk_sdk_python import SplunkPythonSDKUtility
from utilities.ucc_additional_packaging import UCCAdditionalPackagingUtility
from utilities.whats_inside_app import WhatsInsideTheAppUtility


class SplunkAppUtilities:
    def __init__(self, saved_paths: SavedPaths, app_info: AppInfo, app_read_dir, app_write_dir, is_test=False) -> None:
        self.app_read_dir = app_read_dir
        self.app_write_dir = app_write_dir
        self.is_test = is_test
        # Get Inputs
        app_utilities = gat.get_user_input("app_utilities")
        if not app_utilities or app_utilities == "NONE" or app_utilities == "":
            self.app_utilities = []
        else:
            app_utilities = app_utilities.split(",")
            app_utilities = [u.strip() for u in app_utilities]

        os.chdir(saved_paths.root_dir_path)

        self.add_utilities(app_utilities)

    def add_utilities(self, app_utilities):
        gat.info(f"Adding utilities: {app_utilities}")
        for utility in app_utilities:
            if utility == "whats_in_the_app":
                WhatsInsideTheAppUtility(self.app_read_dir, self.app_write_dir)

            elif utility == "logger":
                LoggerUtility(self.app_read_dir, self.app_write_dir).add()

            elif utility == "splunk_python_sdk":
                SplunkPythonSDKUtility(self.app_read_dir, self.app_write_dir).add()

            elif utility == "common_js_utilities":
                CommonJSUtilitiesFile(self.app_read_dir, self.app_write_dir).add()

            elif utility == "ucc_additional_packaging":
                UCCAdditionalPackagingUtility(self.app_read_dir, self.app_write_dir).add()

            else:
                gat.error(f"utility={utility} is not supported.")
