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
from helpers.saved_values import AppInfo, SavedPaths, keep_working_dir_unchanged


def main():
    gat.print_all_user_inputs()

    # Change to workspace directory where repodir/ exists
    workspace_dir = os.environ.get("GITHUB_WORKSPACE")
    if workspace_dir:
        gat.info(f"Changing working directory to workspace: {workspace_dir}")
        os.chdir(workspace_dir)
    else:
        gat.error("GITHUB_WORKSPACE not set, assuming current directory has repodir/")

    app_dir = gat.get_user_input("app_dir")
    assert app_dir is not None, "app_dir must be provided"
    saved_paths = SavedPaths(app_dir)

    # Build Add-on with UCC
    use_ucc_gen = gat.get_user_input_as("use_ucc_gen", bool, False)

    if use_ucc_gen:
        global_config_json_file_path = os.path.join(saved_paths.app_dir_path, "globalConfig.json")
        app_package_id = splunk_app_details.fetch_app_package_id_from_global_config_json(
            global_config_json_file_path
        )
        app_version = splunk_app_details.fetch_app_version_from_global_config_json(
            global_config_json_file_path
        )
    else:
        app_conf_file_path = os.path.join(saved_paths.app_dir_path, "default", "app.conf")
        app_package_id = splunk_app_details.fetch_app_package_id_from_app_conf(
            app_conf_file_path, saved_paths.app_dir_name
        )
        app_version = splunk_app_details.fetch_app_version_number_from_app_conf(app_conf_file_path)

    app_info = AppInfo(app_package_id, app_version)

    app_build_dir_name = None
    app_build_dir_path = None

    if use_ucc_gen:
        with keep_working_dir_unchanged():
            app_build_dir_name = ucc_gen.build(saved_paths, app_info)

    else:
        gat.info("Starting app build preparation without ucc-gen...")
        app_build_dir_name = "without_ucc_build"
        os.system(f"rm -rf {app_build_dir_name}")
        shutil.copytree(saved_paths.app_dir_path, app_build_dir_name)
        gat.info("App build preparation completed successfully")

    app_build_dir_path = os.path.join(saved_paths.root_dir_path, app_build_dir_name)

    app_build_number = splunk_app_details.fetch_app_build_number_from_app_conf(
        app_conf_file_path=os.path.join(app_build_dir_path, "default", "app.conf")
    )
    app_info.set_build_number(app_build_number)

    try:
        app_write_dir = (
            os.path.join(saved_paths.app_dir_name, "package")
            if use_ucc_gen
            else saved_paths.app_dir_path
        )
        with keep_working_dir_unchanged():
            SplunkAppUtilities(
                saved_paths, app_info, app_read_dir=app_build_dir_path, app_write_dir=app_write_dir
            )
    except Exception as e:
        gat.error(f"Error adding Splunk app utilities: {e}")
        gat.error(traceback.format_exc())

    try:
        with keep_working_dir_unchanged():
            # Generate Build
            build_path = app_build_generate.generate_build(
                saved_paths, app_info, app_build_dir_name
            )

        # Run App Inspect
        is_app_inspect_check = gat.get_user_input_as("is_app_inspect_check", bool, True)
        gat.debug(f"App inspect check enabled: {is_app_inspect_check}")

        if is_app_inspect_check:
            splunkbase_username = gat.get_user_input("splunkbase_username")
            splunkbase_password = gat.get_user_input("splunkbase_password")

            if splunkbase_username is None or splunkbase_password is None:
                gat.error(
                    "splunkbase_username and splunkbase_password are required for app inspect."
                )
                return

            SplunkAppInspect(
                saved_paths, app_info, build_path, splunkbase_username, splunkbase_password
            ).run_all_checks()
        else:
            gat.info("App inspect checks disabled - skipping")
            return

    except Exception as e:
        gat.error(f"Error in build generation or app inspect checks: {e}")
        gat.error(traceback.format_exc())

        sys.exit(5)
        # Failure in build generation or App Inspect means failure for Workflow


if __name__ == "__main__":
    main()
