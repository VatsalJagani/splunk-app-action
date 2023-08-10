import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_utilities import SplunkAppUtilities



if __name__ == "__main__":
    utils.CommonDirPaths.generate_paths()

    try:
        build_path, app_package_id = SplunkAppBuildGenerator().generate()    # Generate Build
        SplunkAppInspect(build_path, app_package_id).run_all_checks()        # Run App Inspect
    except Exception as e:
        utils.error("Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())


    try:
        SplunkAppUtilities()
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())





# TODO - Maybe use https://github.com/CrossRealms/Splunk-App-Common-Utility-Action/blob/main/main.py
# For common variables REPO_DIR, APP_DIR


# TODO - Make Whats Inside the App by default disable
# And always add the content to the readme file, if the header is not present, then add it to the end of the file

# TODO - What's inside the file, also, accept the end of file character, ensure that

# TODO - Ensure README changes not go in the build
