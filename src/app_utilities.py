import os
import helper_github_action as utils
from helper_github_pr import GitHubPR
from utilities.whats_inside_app import SplunkAppWhatsInsideDetail


class SplunkAppUtilities:
    def __init__(self) -> None:
        # Get Inputs
        app_utilities = utils.get_input('app_utilities')
        if not app_utilities or app_utilities == "NONE" or app_utilities == "":
            self.app_utilities = []
        else:
            app_utilities = app_utilities.split(',')
            app_utilities = [u.strip() for u in app_utilities]

        self.add_utilities(app_utilities)


    def add_utilities(self, app_utilities):
        for utility in app_utilities:
            if utility == "whats_in_the_app":
                with GitHubPR() as github:
                    readme_file_path = SplunkAppWhatsInsideDetail().update_readme()
                    if readme_file_path:
                        github.commit_and_pr(file_to_generate_hash=readme_file_path)
            # elif utility == "logger":
            #     LoggerUtility(GITHUB_ACTION_DIR, REPO_DIR, app_package_dir, main_branch_name, local_test=local_test)
            # elif utility == "common_splunk_js_utilities":
            #     CommonSplunkJSUtility(GITHUB_ACTION_DIR, REPO_DIR, app_package_dir, main_branch_name, local_test=local_test)
            else:
                utils.error("utility={} is not supported.".format(utility))
