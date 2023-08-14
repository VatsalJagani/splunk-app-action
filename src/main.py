import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_utilities import SplunkAppUtilities



if __name__ == "__main__":
    utils.info("Running Python script main.py")

    utils.CommonDirPaths.generate_paths()

    try:
        build_path, app_package_id = SplunkAppBuildGenerator().generate()    # Generate Build
        # Run App Inspect
        SplunkAppInspect(build_path, app_package_id).run_all_checks()
    except Exception as e:
        utils.error(
            "Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())

    try:
        SplunkAppUtilities()
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())
