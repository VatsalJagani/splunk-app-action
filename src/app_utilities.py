
import os
import shutil
import helper_github_action as utils
from utilities.whats_inside_app import WhatsInsideTheAppUtility
from utilities.logger import LoggerUtility
from utilities.splunk_sdk_python import SplunkPythonSDKUtility
from utilities.common_splunk_js_utilities import CommonJSUtilitiesFile


class SplunkAppUtilities:
    def __init__(self, use_ucc_gen=False, new_app_dir=None, is_test=False) -> None:
        self.use_ucc_gen = use_ucc_gen
        self.new_app_dir = new_app_dir
        self.is_test = is_test
        # Get Inputs
        app_utilities = utils.get_input('app_utilities')
        if not app_utilities or app_utilities == "NONE" or app_utilities == "":
            self.app_utilities = []
        else:
            app_utilities = app_utilities.split(',')
            app_utilities = [u.strip() for u in app_utilities]

        os.chdir(utils.CommonDirPaths.MAIN_DIR)
        # copy folder to generate build, rather than affecting the original repo checkout
        utils.execute_system_command(f"rm -rf {utils.CommonDirPaths.UTILITIES_DIR_NAME}")
        shutil.copytree(utils.CommonDirPaths.REPO_DIR_NAME, utils.CommonDirPaths.UTILITIES_DIR_NAME)

        self.add_utilities(app_utilities)


    def add_utilities(self, app_utilities):
        utils.info(f"Adding utilities: {app_utilities}")
        for utility in app_utilities:
            if utility == "whats_in_the_app":
                WhatsInsideTheAppUtility(use_ucc_gen=self.use_ucc_gen, new_app_dir=self.new_app_dir)

            elif utility == "logger":
                LoggerUtility(use_ucc_gen=self.use_ucc_gen, new_app_dir=self.new_app_dir)

            elif utility == "splunk_python_sdk":
                SplunkPythonSDKUtility(use_ucc_gen=self.use_ucc_gen, new_app_dir=self.new_app_dir)

            elif utility == "common_js_utilities":
                CommonJSUtilitiesFile(use_ucc_gen=self.use_ucc_gen, new_app_dir=self.new_app_dir)

            else:
                utils.error("utility={} is not supported.".format(utility))
