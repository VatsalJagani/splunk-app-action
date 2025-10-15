import os
from collections.abc import Sequence

import github_action_toolkit as gat

from helpers.file_manager import get_file_hash, get_folder_hash, get_multi_files_hash


class BaseUtility:
    def __init__(self, app_read_dir: str, app_write_dir: str) -> None:
        self.app_read_dir: str = app_read_dir
        self.app_write_dir: str = app_write_dir

    def add(self):
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
        raise NotImplementedError(
            "The implement_utility function must be implemented in the child class."
        )
