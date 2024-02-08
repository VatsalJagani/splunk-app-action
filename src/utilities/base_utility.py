
import os
from helper_github_pr import GitHubPR, get_file_hash, get_multi_files_hash, get_folder_hash
import helper_github_action as utils


class BaseUtility:
    def __init__(self, use_ucc_gen=False, new_app_dir=None) -> None:
        self.use_ucc_gen = use_ucc_gen
        self.new_app_dir = new_app_dir
        self.read_content_dir = new_app_dir if new_app_dir else utils.CommonDirPaths.REPO_DIR_FOR_UTILITIES

        with GitHubPR(utils.CommonDirPaths.REPO_DIR_FOR_UTILITIES) as github:
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
                github.commit_and_pr(hash=hash)
            else:
                utils.error(
                    "Unable to get hash to generate PR for app utility.")


    def implement_utility(self):
        raise NotImplementedError(
            "The implement_utility function must be implemented in the child class.")
