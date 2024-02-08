
import os

import helper_github_action as utils
from helper_file_handler import FullRawFileHandler
from utilities.base_utility import BaseUtility


class UCCAdditionalPackagingUtility(BaseUtility):

    def implement_utility(self):
        utils.info("Adding UCCAdditionalPackagingUtility")

        folder_path = self.app_write_dir
        file_path = os.path.join(folder_path, 'additional_packaging.js')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        is_updated = FullRawFileHandler(
            os.path.join(os.path.dirname(__file__),
                         'additional_packaging.py'),
            os.path.join(file_path)
        ).validate_file_content()

        if is_updated:
            utils.info("Change in the file additional_packaging.py")
            return file_path
        utils.info("No change in the file additional_packaging.py")
