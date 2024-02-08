import os
import shutil
import sys
import re
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
        app_version = app_build_with_ucc.fetch_app_version()
    else:
        app_package_id = app_build_generate.fetch_app_package_id(utils.CommonDirPaths.APP_DIR, app_dir_input)
        app_version = app_build_generate.fetch_app_version_number(utils.CommonDirPaths.APP_DIR)


    if use_ucc_gen:
        app_build_dir_name, app_build_dir_path = app_build_with_ucc.build(app_package_id, app_version)
        utils.info("ucc-gen command Completed.")
        # utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

    else:
        utils.execute_system_command(f"rm -rf {utils.CommonDirPaths.BUILD_FINAL_DIR_NAME}")

        if app_dir_input == '.':
            shutil.copytree(utils.CommonDirPaths.REPO_DIR_NAME, utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)
        else:
            shutil.copytree(os.path.join(utils.CommonDirPaths.REPO_DIR_NAME, app_dir_input), utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)

        app_build_dir_name = utils.CommonDirPaths.BUILD_FINAL_DIR_NAME
        app_build_dir_path = os.path.join(utils.CommonDirPaths.MAIN_DIR, utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)

        utils.info("Copied the code for build process.")


    # For yml file to artifact build and app-inspect report
    utils.set_env("app_package_id", app_package_id)

    app_version_encoded = re.sub('[^0-9a-zA-Z]+', '_', app_version)
    utils.set_env("app_version_encoded", app_version_encoded)

    app_build_number = app_build_generate.fetch_app_build_number(utils.CommonDirPaths.APP_DIR)
    app_build_number_encoded = re.sub('[^0-9a-zA-Z]+', '_', app_build_number)
    utils.set_env("app_build_number_encoded", app_build_number_encoded)


    try:
        SplunkAppUtilities(app_read_dir=app_build_dir_path, app_write_dir=os.path.join(utils.CommonDirPaths.REPO_DIR, app_dir_input))
        # utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY
        utils.info("SplunkAppUtilities completed.")
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())


    try:
        # Generate Build
        build_path = app_build_generate.generate_build(app_package_id, app_build_dir_name, app_build_dir_path, app_version_encoded, app_build_number_encoded)

        utils.info("generate_build Completed.")
        utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

        # Run App Inspect
        SplunkAppInspect(build_path, app_package_id, app_version_encoded, app_build_number_encoded).run_all_checks()
        utils.info("SplunkAppInspect Completed.")
        # utils.list_files(utils.CommonDirPaths.MAIN_DIR)   # TODO - FOR TEST ONLY

    except Exception as e:
        utils.error(
            "Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())

        sys.exit(1)
        # Failure in build generation or App Inspect means failure for Workflow
