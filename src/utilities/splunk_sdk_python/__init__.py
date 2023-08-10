
import os, re

import helper_github_action as utils
import helper_github_pr


class SplunkPythonSDKUtility:
    def __init__(self) -> None:
        self.folder_to_install_splunklib = os.path.join(utils.CommonDirPaths.APP_DIR, 'bin')

        os.chdir(self.folder_to_install_splunklib)
        if not os.path.exists(self.folder_to_install_splunklib):
            os.mkdir(self.folder_to_install_splunklib)


    def _get_splunklib_version(file_path):
        try:
            with open(file_path, 'r') as f:
                match = re.search(r"\n__version_info__\s*=\s*([^\n]+)", f.read())
                version = match.group(1)
                utils.info(f"Existing splunklib version = {version}")
                return version
        except:
            utils.info("Error with getting the splunklib version.")


    def install_splunk_python_sdk(self):
        # Check if splunklib exist already
        already_exist = False
        previous_version = None

        splunklib_dir = os.path.join(self.folder_to_install_splunklib, 'splunklib')
        init_file = os.path.join(splunklib_dir, '__init__.py')

        if os.path.exists(splunklib_dir) and os.path.isdir(splunklib_dir) and os.path.isfile(init_file):
            already_exist = True
            previous_version = self._get_splunklib_version(init_file)

        if already_exist:
            os.system('pip install splunk-sdk --upgrade')
        else:
            os.system('pip install splunk-sdk')

        new_version = self._get_splunklib_version(init_file)

        if not already_exist or previous_version != new_version:
            return helper_github_pr.get_file_hash(init_file)
