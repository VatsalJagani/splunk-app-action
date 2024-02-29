
import os

import helper_github_action as utils
from helper_file_handler import FullRawFileHandler
from utilities.base_utility import BaseUtility


class CommonPythonUtilitiesFile(BaseUtility):

    def implement_utility(self):
        utils.info("Adding CommonPythonUtilitiesFile.")

        utils.info("app_package_id: {}".format(app_package_id))

        words_for_replacement = {
            '<<<app_package_id>>>': app_package_id
        }

        folder_path = os.path.join(self.app_write_dir, 'bin')
        file_path = os.path.join(
            folder_path, 'splunk_common_python_v_utilities.py')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        is_updated = FullRawFileHandler(
            os.path.join(os.path.dirname(__file__),
                         'splunk_common_python_v_utilities.py'),
            os.path.join(file_path),
            words_for_replacement
        ).validate_file_content()

        if is_updated:
            utils.info("Updated splunk_common_python_v_utilities.py file.")
            return os.path.join(self.app_write_dir,
                             'bin', 'splunk_common_python_v_utilities.py')
        utils.info("No change in splunk_common_python_v_utilities.py file.")
