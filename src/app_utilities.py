
import os
import shutil
import helper_github_action as utils
from utilities.whats_inside_app import WhatsInsideTheAppUtility
from utilities.logger import LoggerUtility
from utilities.splunk_sdk_python import SplunkPythonSDKUtility
from utilities.common_splunk_js_utilities import CommonJSUtilitiesFile
from utilities.ucc_additional_packaging import UCCAdditionalPackagingUtility


class SplunkAppUtilities:
    def __init__(self, app_read_dir, app_write_dir, is_test=False) -> None:
        self.app_read_dir = app_read_dir
        self.app_write_dir = app_write_dir
        self.is_test = is_test
        # Get Inputs
        app_utilities = utils.get_input('app_utilities')
        if not app_utilities or app_utilities == "NONE" or app_utilities == "":
            self.app_utilities = []
        else:
            app_utilities = app_utilities.split(',')
            app_utilities = [u.strip() for u in app_utilities]

        os.chdir(utils.CommonDirPaths.MAIN_DIR)

        self.add_utilities(app_utilities)


    def add_utilities(self, app_utilities):
        utils.info(f"Adding utilities: {app_utilities}")
        for utility in app_utilities:
            if utility == "whats_in_the_app":
                WhatsInsideTheAppUtility(self.app_read_dir, self.app_write_dir)

            elif utility == "logger":
                LoggerUtility(self.app_read_dir, self.app_write_dir)

            elif utility == "splunk_python_sdk":
                SplunkPythonSDKUtility(self.app_read_dir, self.app_write_dir)

            elif utility == "common_js_utilities":
                CommonJSUtilitiesFile(self.app_read_dir, self.app_write_dir)

            elif utility == "ucc_additional_packaging":
                UCCAdditionalPackagingUtility(self.app_read_dir, self.app_write_dir)

            else:
                utils.error("utility={} is not supported.".format(utility))
