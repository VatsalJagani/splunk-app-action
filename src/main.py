import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_whats_inside import SplunkAppWhatsInsideDetail
from helper_github_pr import GitHubPR



if __name__ == "__main__":
    LOCAL_TEST = False
    LOCAL_TEST = True
    if LOCAL_TEST or (len(sys.argv) > 1 and sys.argv[1] == "local_test"):
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
    if LOCAL_TEST:
        REPO_DIR = os.path.dirname(os.path.dirname(__file__))

    # This is just for testing
    # utils.info("Files under current working directory:- {}".format(os.getcwd()))
    # utils.list_files(os.getcwd())


    try:
        readme_file_path = SplunkAppWhatsInsideDetail().update_readme()
        if readme_file_path:
            GitHubPR(repo_dir=REPO_DIR).commit_and_pr(file_to_generate_hash=readme_file_path, local_test=LOCAL_TEST)
    except Exception as e:
        utils.error("Error in Updating README: {}".format(e))
        utils.error(traceback.format_exc())

    try:
        build_path = SplunkAppBuildGenerator().generate()
        SplunkAppInspect(build_path).run_all_checks()
    except Exception as e:
        utils.error("Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())


# TODO - Maybe use https://github.com/CrossRealms/Splunk-App-Common-Utility-Action/blob/main/main.py
# For common variables REPO_DIR, APP_DIR


# TODO - Make Whats Inside the App by default disable
# And always add the content to the readme file, if the header is not present, then add it to the end of the file

# TODO - What's inside the file, also, accept the end of file character, ensure that

# TODO - Ensure README changes not go in the build
