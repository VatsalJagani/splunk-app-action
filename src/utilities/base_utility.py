
import os
from helpers.git_manager import GitHubPR, get_file_hash, get_multi_files_hash, get_folder_hash
import helpers.github_action_utils as utils


class BaseUtility:
    def __init__(self, app_read_dir, app_write_dir) -> None:
        self.app_read_dir = app_read_dir
        self.app_write_dir = app_write_dir


    def add(self):
        with GitHubPR(self.app_write_dir) as github:
            files_or_folders_updated = self.implement_utility()
            hash = None

            if not files_or_folders_updated:
                utils.info(f"Utility={type(self).__name__} has no change.")
                return

            if type(files_or_folders_updated) == list:
                hash = get_multi_files_hash(files_or_folders_updated)

            else:
                if os.path.isfile(files_or_folders_updated):
                    hash = get_file_hash(files_or_folders_updated)
                elif os.path.isdir(files_or_folders_updated):
                    hash = get_folder_hash(files_or_folders_updated)
                else:
                    utils.error("File to generate has is invalid.")

            if hash:
                utils.debug("Committing and creating PR for the code change.")
                github.commit_and_pr(hash=hash)
            else:
                utils.error(
                    "Unable to get hash to generate PR for app utility.")


    def implement_utility(self):
        raise NotImplementedError(
            "The implement_utility function must be implemented in the child class.")
