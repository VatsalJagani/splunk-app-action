import os
import sys

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_whats_inside import SplunkAppWhatsInsideDetail
from helper_github_pr import GitHubPR



if __name__ == "__main__":
    LOCAL_TEST = False
    if len(sys.argv) > 1 and sys.argv[1] == "local_test":
        LOCAL_TEST = True
        utils.set_input('app_dir', 'test_app')
        utils.set_input('app_build_name', 'test_app')
        # Get user input for splunkbase_username
        splunkbase_username = input("Enter your Splunkbase username: ")
        utils.set_input('splunkbase_username', splunkbase_username)

        # Get user input for splunkbase_password (masked input)
        import getpass
        splunkbase_password = getpass.getpass("Enter your Splunkbase password: ")
        utils.set_input('splunkbase_password', splunkbase_password)



    REPO_DIR = os.path.join(os.getcwd(), 'repodir')

    # This is just for testing
    # utils.info("Files under current working directory:- {}".format(os.getcwd()))
    # utils.list_files(os.getcwd())


    try:
        readme_file_path = SplunkAppWhatsInsideDetail().update_readme()
        if readme_file_path:
            GitHubPR(repo_dir=REPO_DIR).commit_and_pr(file_to_generate_hash=readme_file_path, local_test=LOCAL_TEST)
    except:
        pass

    try:
        build_path = SplunkAppBuildGenerator().generate()
        SplunkAppInspect(build_path).run_all_checks()
    except:
        pass
