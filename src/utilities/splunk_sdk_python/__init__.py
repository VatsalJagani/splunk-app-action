
import os
import re

import helper_github_action as utils
from utilities.base_utility import BaseUtility


class SplunkPythonSDKUtility(BaseUtility):

    def _get_splunklib_version(self, file_path):
        try:
            with open(file_path, 'r') as f:
                match = re.search(
                    r"\n__version_info__\s*=\s*([^\n]+)", f.read())
                version = match.group(1)
                return version
        except:
            utils.info("Error with getting the splunklib version.")


    def implement_utility(self):
        utils.info("Adding SplunkPythonSDKUtility")

        folder_to_install_splunklib = os.path.join(
            utils.CommonDirPaths.APP_DIR, 'bin')

        os.chdir(folder_to_install_splunklib)
        if not os.path.exists(folder_to_install_splunklib):
            os.mkdir(folder_to_install_splunklib)

        # Check if splunklib exist already
        already_exist = False
        previous_version = None

        splunklib_dir = os.path.join(folder_to_install_splunklib, 'splunklib')
        init_file = os.path.join(splunklib_dir, '__init__.py')

        if os.path.exists(splunklib_dir) and os.path.isdir(splunklib_dir) and os.path.isfile(init_file):
            already_exist = True
            previous_version = self._get_splunklib_version(init_file)
            utils.info(f"Previous splunklib version = {previous_version}")

        if already_exist:
            utils.info(
                "splunklib already present under bin directory of the App, upgrading...")
            os.system(
                f'pip install splunk-sdk --upgrade --target {folder_to_install_splunklib}')
        else:
            utils.info(
                "splunklib not present under bin directory of the App, installing...")
            os.system(
                f'pip install splunk-sdk --target {folder_to_install_splunklib}')

        new_version = self._get_splunklib_version(init_file)
        utils.info(f"New splunklib version = {new_version}")

        if not already_exist or previous_version != new_version:
            return init_file
