import os
import shutil
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

from helpers.global_variables import GlobalVariables
from helpers import splunk_app_details
import helpers.github_action_utils as utils
from app_inspect import SplunkAppInspect
import ucc_gen
import app_build_generate
from app_utilities import SplunkAppUtilities



def main():
    utils.info("Running Python script main.py")

    app_dir_input = utils.get_input('app_dir')
    utils.info("app_dir_input: {}".format(app_dir_input))

    GlobalVariables.initiate(app_dir_name=app_dir_input)


    # Build Add-on with UCC
    utils.debug(f"Input use_ucc_gen value = {utils.get_input('use_ucc_gen')}")
    use_ucc_gen = utils.str_to_boolean_default_false(
            utils.get_input('use_ucc_gen'))
    utils.info("use_ucc_gen: {}".format(use_ucc_gen))


    if use_ucc_gen:
        global_config_json_file_path = os.path.join(GlobalVariables.ORIGINAL_APP_DIR_PATH, 'globalConfig.json')
        app_package_id = splunk_app_details.fetch_app_package_id_from_global_config_json(
            global_config_json_file_path
        )
        app_version = splunk_app_details.fetch_app_version_from_global_config_json(
            global_config_json_file_path
        )
    else:
        app_conf_file_path = os.path.join(GlobalVariables.ORIGINAL_APP_DIR_PATH, 'default', 'app.conf')
        app_package_id = splunk_app_details.fetch_app_package_id_from_app_conf(
            app_conf_file_path, app_dir_input
        )
        app_version = splunk_app_details.fetch_app_version_number_from_app_conf(
            app_conf_file_path
        )

    GlobalVariables.set_app_package_id(app_package_id)
    GlobalVariables.set_app_version(app_version)
    # For yml file to artifact build and app-inspect report
    utils.set_env("app_package_id", GlobalVariables.APP_PACKAGE_ID)
    utils.set_env("app_version_encoded", GlobalVariables.APP_VERSION_ENCODED)


    app_build_dir_name = None
    app_build_dir_path = None

    if use_ucc_gen:
        app_build_dir_name = ucc_gen.build()
        utils.info("ucc-gen command Completed.")

    else:
        app_build_dir_name = "without_ucc_build"

        os.chdir(GlobalVariables.ROOT_DIR_PATH)
        utils.execute_system_command(f"rm -rf {app_build_dir_name}")

        shutil.copytree(GlobalVariables.ORIGINAL_APP_DIR_PATH, app_build_dir_name)
        utils.info("Copied the code for build process.")

    app_build_dir_path = os.path.join(GlobalVariables.ROOT_DIR_PATH, app_build_dir_name)


    # For yml file to artifact build and app-inspect report
    app_build_number = splunk_app_details.fetch_app_build_number_from_app_conf(
        app_conf_file_path = os.path.join(app_build_dir_path, 'default', 'app.conf')
    )
    GlobalVariables.set_app_build_number(app_build_number)
    utils.set_env("app_build_number_encoded", GlobalVariables.APP_BUILD_NUMBER_ENCODED)


    try:
        app_write_dir = os.path.join(GlobalVariables.ORIGINAL_APP_DIR_PATH, 'package') if use_ucc_gen else GlobalVariables.ORIGINAL_APP_DIR_PATH
        SplunkAppUtilities(app_read_dir=app_build_dir_path, app_write_dir=app_write_dir)
        utils.info("SplunkAppUtilities completed.")
    except Exception as e:
        utils.error("Error Adding Splunk App Utilities: {}".format(e))
        utils.error(traceback.format_exc())


    try:
        # Generate Build
        build_path = app_build_generate.generate_build(app_build_dir_name, app_build_dir_path)

        utils.info("generate_build Completed.")

        # Run App Inspect
        is_app_inspect_check = utils.str_to_boolean_default_true(
            utils.get_input('is_app_inspect_check')
        )
        utils.info("is_app_inspect_check: {}".format(is_app_inspect_check))

        if is_app_inspect_check:
            splunkbase_username = utils.get_input('splunkbase_username')
            splunkbase_password = utils.get_input('splunkbase_password')

            SplunkAppInspect(build_path, splunkbase_username, splunkbase_password).run_all_checks()
            utils.info("SplunkAppInspect Completed.")
        else:
            utils.info("Ignoring App-inspect checks.")
            return


    except Exception as e:
        utils.error(
            "Error in SplunkBase Build Generator or App Inspect Checks: {}".format(e))
        utils.error(traceback.format_exc())

        sys.exit(5)
        # Failure in build generation or App Inspect means failure for Workflow


if __name__ == "__main__":
    main()
