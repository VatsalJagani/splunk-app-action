import os
import shutil
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
import app_build_with_ucc
import app_build_generate
from app_utilities import SplunkAppUtilities



if __name__ == "__main__":
    utils.info("Running Python script main.py")

    utils.CommonDirPaths.generate_paths()

    app_dir_input = utils.get_input('app_dir')
    utils.info("app_dir_input: {}".format(app_dir_input))

    # Build Add-on with UCC
    use_ucc_gen = utils.str_to_boolean(
            utils.get_input('use_ucc_gen'))
    utils.info("use_ucc_gen: {}".format(use_ucc_gen))


    app_package_id = None
    app_version = None
    app_build_dir_name = None
    app_build_dir_path = None
    build_path = None


    if use_ucc_gen:
        app_package_id = app_build_with_ucc.fetch_app_package_id()
    else:
        app_package_id = app_build_generate.fetch_app_package_id(utils.CommonDirPaths.APP_DIR, app_dir_input)


    if use_ucc_gen:
        app_version = app_build_with_ucc.fetch_app_version()
        app_build_dir_name, app_build_dir_path = app_build_with_ucc.build(app_package_id, app_version)

        utils.info("ucc-gen command Completed.")
        utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

    else:
        utils.execute_system_command(f"rm -rf {utils.CommonDirPaths.BUILD_FINAL_DIR_NAME}")

        if app_dir_input == '.':
            shutil.copytree(utils.CommonDirPaths.REPO_DIR_NAME, utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)
        else:
            shutil.copytree(os.path.join(utils.CommonDirPaths.REPO_DIR_NAME, app_dir_input), utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)

        app_build_dir_name = utils.CommonDirPaths.BUILD_FINAL_DIR_NAME
        app_build_dir_path = os.path.join(utils.CommonDirPaths.MAIN_DIR, utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)


    try:
        SplunkAppUtilities(app_read_dir=app_build_dir_path, app_write_dir=os.path.join(utils.CommonDirPaths.REPO_DIR, app_dir_input))
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())

    utils.info("AppUtilities Completed.")
    utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY


    try:
        # Generate Build
        build_path = app_build_generate.generate_build(app_package_id, app_build_dir_name, app_build_dir_path)

        utils.info("generate_build Completed.")
        utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

        # Run App Inspect
        SplunkAppInspect(build_path, app_package_id).run_all_checks()

    except Exception as e:
        utils.error(
            "Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())

        sys.exit(1)
        # Failure in build generation or App Inspect means failure for Workflow
