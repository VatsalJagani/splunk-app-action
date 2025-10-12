import os

import github_action_toolkit as gat

from helpers.file_hash import get_file_hash, get_folder_hash, get_multi_files_hash


class BaseUtility:
    def __init__(self, app_read_dir, app_write_dir) -> None:
        self.app_read_dir = app_read_dir
        self.app_write_dir = app_write_dir

    def add(self):
        with gat.Repo(path=self.app_write_dir) as github:
            files_or_folders_updated = self.implement_utility()
            hash = None

            if not files_or_folders_updated:
                gat.info(f"Utility={type(self).__name__} has no change.")
                return

            if type(files_or_folders_updated) == list:
                hash = get_multi_files_hash(files_or_folders_updated)

            else:
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

    def implement_utility(self):
        raise NotImplementedError(
            "The implement_utility function must be implemented in the child class."
        )
