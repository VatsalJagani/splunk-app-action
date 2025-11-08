import os
from collections.abc import Sequence

import github_action_toolkit as gat

from helpers.file_manager import get_file_hash, get_folder_hash, get_multi_files_hash


class BaseUtility:
    """
    Base class for Splunk app utilities that can be applied to apps.

    Provides common functionality for applying utilities to Splunk apps,
    including automatic PR creation when changes are detected. Child classes
    must implement the `implement_utility` method to define specific utility behavior.
    """

    def __init__(self, app_read_dir: str, app_write_dir: str) -> None:
        """
        Initialize the base utility with read and write directories.

        Args:
            app_read_dir: Directory to read the original app files from.
            app_write_dir: Directory to write modified app files to.
        """
        self.app_read_dir: str = app_read_dir
        self.app_write_dir: str = app_write_dir

    def add(self) -> None:
        """
        Apply the utility to the app and create a PR if changes are detected.

        Executes the utility implementation, calculates file hashes to detect changes,
        and automatically creates a pull request if files were modified. Handles
        different return types from the utility implementation (bool, str, Sequence).
        """
        with gat.group(f"🛠️ Applying Utility: {type(self).__name__}"):
            try:
                with gat.Repo(path=self.app_write_dir, cleanup=True) as github:
                    files_or_folders_updated = self.implement_utility()
                    hash = None

                if not files_or_folders_updated:
                    gat.info(f"Utility={type(self).__name__} has no change.")
                    return

                if isinstance(files_or_folders_updated, bool):
                    # Boolean return indicates success/failure but no specific files
                    gat.info(
                        f"Utility={type(self).__name__} completed with status: {files_or_folders_updated}"
                    )
                    return
                elif not isinstance(files_or_folders_updated, str):
                    # Handle Sequence case
                    hash = get_multi_files_hash(list(files_or_folders_updated))
                else:
                    # Handle str case
                    if os.path.isfile(files_or_folders_updated):
                        hash = get_file_hash(files_or_folders_updated)
                    elif os.path.isdir(files_or_folders_updated):
                        hash = get_folder_hash(files_or_folders_updated)
                    else:
                        gat.error("File to generate hash is invalid.")

                if hash:
                    gat.debug("Committing and creating PR for the code change.")
                    _msg = f"splunk_app_action_{hash}"
                    github.create_new_branch(_msg)
                    github.add_all_and_commit(_msg)
                    github.push()
                    github.create_pr()
                else:
                    gat.error("Unable to get hash to generate PR for app utility.")
            except Exception as e:
                gat.error(f"Error in utility {type(self).__name__}: {e}")

    def implement_utility(self) -> str | Sequence[str] | bool | None:
        """
        Implement the specific utility functionality.

        Must be overridden by child classes to provide the actual utility implementation.

        Returns:
            - str: Path to a modified file or directory
            - Sequence[str]: List of paths to modified files
            - bool: True if changes were made, False otherwise
            - None: No changes were made

        Raises:
            NotImplementedError: If not implemented in child class.
        """
        raise NotImplementedError(
            "The implement_utility function must be implemented in the child class."
        )
