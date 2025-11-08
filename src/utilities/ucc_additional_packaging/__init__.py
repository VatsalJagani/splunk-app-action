import os
from typing import override

import github_action_toolkit as gat

from helpers.file_manager import FullRawFileHandler
from utilities.base_utility import BaseUtility


class UCCAdditionalPackagingUtility(BaseUtility):
    """
    Utility to add additional packaging script for UCC-based add-ons.

    Adds the `additional_packaging.py` script to UCC add-on projects, which can be
    used for custom build steps or packaging requirements beyond the standard UCC
    generator output.
    """

    @override
    def implement_utility(self) -> str | None:
        """
        Add the additional_packaging.py script to the app directory.

        Returns:
            Path to the added script if changes were made, None otherwise.
        """
        gat.info("📦 Adding UCCAdditionalPackagingUtility")

        folder_path = os.path.dirname(
            self.app_write_dir
        )  # additional_packaging.py file has to be in the app_dir folder of the repo instead of in the package folder
        file_path = os.path.join(folder_path, "additional_packaging.py")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        is_updated = FullRawFileHandler(
            os.path.join(os.path.dirname(__file__), "additional_packaging.py"),
            os.path.join(file_path),
        ).validate_file_content()

        if is_updated:
            gat.info("Change in the file additional_packaging.py")
            return file_path
        gat.info("No change in the file additional_packaging.py")
