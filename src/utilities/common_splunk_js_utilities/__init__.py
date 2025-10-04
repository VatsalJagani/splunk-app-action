
import os
import github_action_toolkit as gat

from helpers.file_manager import FullRawFileHandler
from utilities.base_utility import BaseUtility


class CommonJSUtilitiesFile(BaseUtility):

    def implement_utility(self):
        gat.info("Adding CommonJSUtilitiesFile")

        folder_path = os.path.join(
            self.app_write_dir, 'appserver', 'static')
        file_path = os.path.join(
            folder_path, 'splunk_common_js_v_utilities.js')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        is_updated = FullRawFileHandler(
            os.path.join(os.path.dirname(__file__),
                         'splunk_common_js_v_utilities.js'),
            os.path.join(file_path)
        ).validate_file_content()

        if is_updated:
            gat.info("Change in the file splunk_common_js_v_utilities.js")
            return file_path
        gat.info("No change in the file splunk_common_js_v_utilities.js")
