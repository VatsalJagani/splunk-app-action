import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_build_with_ucc import SplunkAppBuildWithUCC
from app_utilities import SplunkAppUtilities



if __name__ == "__main__":
    utils.info("Running Python script main.py")

    utils.CommonDirPaths.generate_paths()

    # Build Add-on with UCC
    use_ucc_gen = utils.str_to_boolean(
            utils.get_input('use_ucc_gen'))
    utils.info("use_ucc_gen: {}".format(use_ucc_gen))

    _new_app_dir = None
    _new_app_package_id = None
    if use_ucc_gen:
        _new_app_dir, _new_app_package_id = SplunkAppBuildWithUCC().build()

    utils.info("ucc-gen Completed.")
    utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

    try:
        SplunkAppUtilities(use_ucc_gen=use_ucc_gen, new_app_dir=_new_app_dir)
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())

    utils.info("AppUtilities Completed.")
    utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

    try:
        # Generate Build
        build_path, app_package_id = SplunkAppBuildGenerator(app_dir=_new_app_dir, app_package_id=_new_app_package_id).generate()

        utils.info("AppBuildGenerator Completed.")
        utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

        # Run App Inspect
        SplunkAppInspect(build_path, app_package_id).run_all_checks()
    except Exception as e:
        utils.error(
            "Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())

        sys.exit(1)
        # Failure in build generation or App Inspect means failure for Workflow
