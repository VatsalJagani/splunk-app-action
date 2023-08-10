
import os

import helper_github_action as utils
import helper_github_pr
from helper_file_handler import FullRawFileHandler


class CommonJSUtilitiesFile:
    def __init__(self) -> None:
        self.folder_path = os.path.join(utils.CommonDirPaths.APP_DIR, 'appserver', 'static')
        self.file_path = os.path.join(self.folder_path, 'splunk_common_js_v_utilities.js')

        os.chdir(utils.CommonDirPaths.APP_DIR)
        os.makedirs(self.folder_path)


    def add_js_utility_file(self):
        is_updated = FullRawFileHandler(
            os.path.join(os.path.dirname(__file__), 'splunk_common_js_v_utilities.js'),
            os.path.join(self.file_path)
        ).validate_file_content()

        if is_updated:
            return helper_github_pr.get_file_hash(self.file_path)
        return False
