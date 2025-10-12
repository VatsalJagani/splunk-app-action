import os
import shutil
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import github_action_toolkit as gat

import app_build_generate
import ucc_gen
from app_inspect import SplunkAppInspect
from app_utilities import SplunkAppUtilities
from helpers import splunk_app_details
from helpers.global_variables import GlobalVariables


def main():
    gat.info("Running Python script main.py")
    gat.print_all_user_inputs()

    app_dir_input = gat.get_user_input("app_dir")

    GlobalVariables.initiate(app_dir_name=app_dir_input)

    # Build Add-on with UCC
    use_ucc_gen = gat.get_user_input_as("use_ucc_gen", bool, False)
    gat.info(f"use_ucc_gen: {use_ucc_gen}")

    if use_ucc_gen:
        global_config_json_file_path = os.path.join(
            GlobalVariables.ORIGINAL_APP_DIR_PATH, "globalConfig.json"
        )
        app_package_id = splunk_app_details.fetch_app_package_id_from_global_config_json(
            global_config_json_file_path
        )
        app_version = splunk_app_details.fetch_app_version_from_global_config_json(
            global_config_json_file_path
        )
    else:
        app_conf_file_path = os.path.join(
            GlobalVariables.ORIGINAL_APP_DIR_PATH, "default", "app.conf"
        )
        app_package_id = splunk_app_details.fetch_app_package_id_from_app_conf(
            app_conf_file_path, app_dir_input
        )
        app_version = splunk_app_details.fetch_app_version_number_from_app_conf(app_conf_file_path)

    GlobalVariables.set_app_package_id(app_package_id)
    GlobalVariables.set_app_version(app_version)
    # For yml file to artifact build and app-inspect report
    gat.set_env("app_package_id", GlobalVariables.APP_PACKAGE_ID)
    gat.set_env("app_version_encoded", GlobalVariables.APP_VERSION_ENCODED)

    app_build_dir_name = None
    app_build_dir_path = None

    if use_ucc_gen:
        app_build_dir_name = ucc_gen.build()
        gat.info("ucc-gen command Completed.")

    else:
        app_build_dir_name = "without_ucc_build"

        os.chdir(GlobalVariables.ROOT_DIR_PATH)
        os.system(f"rm -rf {app_build_dir_name}")

        shutil.copytree(GlobalVariables.ORIGINAL_APP_DIR_PATH, app_build_dir_name)
        gat.info("Copied the code for build process.")

    app_build_dir_path = os.path.join(GlobalVariables.ROOT_DIR_PATH, app_build_dir_name)

    # For yml file to artifact build and app-inspect report
    app_build_number = splunk_app_details.fetch_app_build_number_from_app_conf(
        app_conf_file_path=os.path.join(app_build_dir_path, "default", "app.conf")
    )
    GlobalVariables.set_app_build_number(app_build_number)
    gat.set_env("app_build_number_encoded", GlobalVariables.APP_BUILD_NUMBER_ENCODED)

    try:
        app_write_dir = (
            os.path.join(GlobalVariables.ORIGINAL_APP_DIR_PATH, "package")
            if use_ucc_gen
            else GlobalVariables.ORIGINAL_APP_DIR_PATH
        )
        SplunkAppUtilities(app_read_dir=app_build_dir_path, app_write_dir=app_write_dir)
        gat.info("SplunkAppUtilities completed.")
    except Exception as e:
        gat.error(f"Error Adding Splunk App Utilities: {e}")
        gat.error(traceback.format_exc())

    try:
        # Generate Build
        build_path = app_build_generate.generate_build(app_build_dir_name, app_build_dir_path)

        gat.info("generate_build Completed.")

        # Run App Inspect
        is_app_inspect_check = gat.get_user_input_as("is_app_inspect_check", bool, True)
        gat.info(f"is_app_inspect_check: {is_app_inspect_check}")

        if is_app_inspect_check:
            splunkbase_username = gat.get_user_input("splunkbase_username")
            splunkbase_password = gat.get_user_input("splunkbase_password")

            SplunkAppInspect(build_path, splunkbase_username, splunkbase_password).run_all_checks()
            gat.info("SplunkAppInspect Completed.")
        else:
            gat.info("Ignoring App-inspect checks.")
            return

    except Exception as e:
        gat.error(f"Error in SplunkBase Build Generator or App Inspect Checks: {e}")
        gat.error(traceback.format_exc())

        sys.exit(5)
        # Failure in build generation or App Inspect means failure for Workflow


if __name__ == "__main__":
    main()
