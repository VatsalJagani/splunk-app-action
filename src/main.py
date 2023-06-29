import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_utilities import SplunkAppUtilities




if __name__ == "__main__":
    '''
    LOCAL_TEST = False
    if LOCAL_TEST or (len(sys.argv) > 1 and sys.argv[1] == "local_test"):
        LOCAL_TEST = True
        utils.set_input('app_dir', 'test_app')
        # Get user input for splunkbase_username
        splunkbase_username = input("Enter your Splunkbase username: ")
        utils.set_input('splunkbase_username', splunkbase_username)

        # Get user input for splunkbase_password (masked input)
        import getpass
        splunkbase_password = getpass.getpass("Enter your Splunkbase password: ")
        utils.set_input('splunkbase_password', splunkbase_password)
    '''
    # Disabling the local test

    # Set REPO_DIR as environment variable
    utils.CommonDirPaths.generate_paths()
    # if LOCAL_TEST:
    #     utils.CommonDirPaths.REPO_DIR = os.path.dirname(os.path.dirname(__file__))

    # This is just for testing
    # utils.info("Files under current working directory:- {}".format(os.getcwd()))
    # utils.list_files(os.getcwd())


    try:
        SplunkAppUtilities()
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())


    try:
        build_path, app_package_id = SplunkAppBuildGenerator().generate()    # Generate Build
        SplunkAppInspect(build_path, app_package_id).run_all_checks()        # Run App Inspect
    except Exception as e:
        utils.error("Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())



# TODO - Maybe use https://github.com/CrossRealms/Splunk-App-Common-Utility-Action/blob/main/main.py
# For common variables REPO_DIR, APP_DIR


# TODO - Make Whats Inside the App by default disable
# And always add the content to the readme file, if the header is not present, then add it to the end of the file

# TODO - What's inside the file, also, accept the end of file character, ensure that

# TODO - Ensure README changes not go in the build
