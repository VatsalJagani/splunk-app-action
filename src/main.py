import os
import shutil
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

import github_action_toolkit as gat

import app_build_generate
import job_summary
import python_dependency_manager
import ucc_gen
from app_inspect import SplunkAppInspect, SplunkLocalAppInspect
from app_utilities import SplunkAppUtilities
from helpers import splunk_app_details
from helpers.saved_values import AppInfo, SavedPaths, keep_working_dir_unchanged


def _should_fail_on_status(
    fail_on: str, app_inspect: str, cloud_inspect: str, ssai_inspect: str
) -> bool:
    """
    Determine if the workflow should fail based on fail_on setting and status values.

    Args:
        fail_on: "errors", "warnings", or "none"
        app_inspect: Status of app-inspect check
        cloud_inspect: Status of cloud-inspect check
        ssai_inspect: Status of SSAI-inspect check

    Returns:
        True if workflow should fail, False otherwise
    """
    if fail_on == "none":
        return False

    statuses = [app_inspect.lower(), cloud_inspect.lower(), ssai_inspect.lower()]

    # Always fail on errors
    if any(s in ["failure", "error"] for s in statuses):
        return True

    # If fail_on is "warnings", also fail on warnings
    if fail_on == "warnings" and any(s == "warning" for s in statuses):
        return True

    return False


def validate_mutually_exclusive_features() -> None:
    """Validate that only one build feature is enabled at a time."""
    use_ucc_gen = gat.get_user_input_as("use_ucc_gen", bool, False)
    python_requirements_file = gat.get_user_input("python_requirements_file")

    # Check if Python dependency manager is being used
    use_python_deps = python_requirements_file and python_requirements_file != ""

    if use_ucc_gen and use_python_deps:
        gat.error(
            "Error: Both UCC-Gen and Python Dependency Manager are enabled. "
            "You can only use one at a time:\n"
            "  - UCC-Gen (use_ucc_gen: true)\n"
            "  - Python-Dependency-Management (python_requirements_file)\n"
            "Please update your workflow configuration to use only one feature."
        )
        sys.exit(1)


def main() -> None:
    gat.print_all_user_inputs()

    # Validate mutually exclusive features
    with gat.group("🔍 Validating Build Configuration"):
        validate_mutually_exclusive_features()
        gat.info("✅ Build configuration is valid")

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
    is_remove_not_allowed_executables_from_lib = gat.get_user_input_as(
        "is_remove_not_allowed_executables_from_lib", bool, False
    )

    # Check if Python dependency manager is being used
    python_requirements_file = gat.get_user_input("python_requirements_file")
    use_python_deps = python_requirements_file and python_requirements_file != ""

    with gat.group("🔍 Getting the App Details"):
        if use_ucc_gen:
            global_config_json_file_path = os.path.join(
                saved_paths.app_dir_path, "globalConfig.json"
            )
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
            app_version = splunk_app_details.fetch_app_version_number_from_app_conf(
                app_conf_file_path
            )

    app_info = AppInfo(app_package_id, app_version)
    app_info.publish()

    app_build_dir_name = None
    app_build_dir_path = None

    if use_ucc_gen:
        with gat.group("🏗️ Preparing for App Build with UCC"):
            with keep_working_dir_unchanged():
                app_build_dir_name = ucc_gen.build(
                    saved_paths, app_info, is_remove_not_allowed_executables_from_lib
                )

    elif use_python_deps:
        with gat.group("🏗️ Installing dynamic Python Dependencies"):
            with keep_working_dir_unchanged():
                app_build_dir_name = python_dependency_manager.install_dependencies(
                    saved_paths, app_info
                )

    else:
        with gat.group("🏗️ Preparing for App Build without UCC"):
            app_build_dir_name = "without_ucc_build"
            if os.path.exists(app_build_dir_name):
                shutil.rmtree(app_build_dir_name)
            shutil.copytree(saved_paths.app_dir_path, app_build_dir_name)
            gat.info("App build preparation completed.")

    app_build_dir_path = os.path.join(saved_paths.root_dir_path, app_build_dir_name)

    with gat.group("🔍 Getting the App Build Number"):
        app_build_number = splunk_app_details.fetch_app_build_number_from_app_conf(
            app_conf_file_path=os.path.join(app_build_dir_path, "default", "app.conf")
        )
        app_info.set_build_number(app_build_number)

    utility_failed = False
    try:
        app_write_dir = (
            os.path.join(saved_paths.app_dir_path, "package")
            if use_ucc_gen
            else saved_paths.app_dir_path
        )
        with keep_working_dir_unchanged():
            sau = SplunkAppUtilities(
                saved_paths, app_read_dir=app_build_dir_path, app_write_dir=app_write_dir
            )
            if sau.result is False:
                utility_failed = True
    except Exception as e:
        gat.error(f"❌ Failed to add Splunk app utilities. {e}")
        gat.error(traceback.format_exc())
        utility_failed = True

    try:
        with keep_working_dir_unchanged():
            # Generate Build
            build_path = app_build_generate.generate_build(
                saved_paths, app_info, app_build_dir_name
            )

        # Get artifact name from outputs
        artifact_name = os.path.basename(build_path)

        # Track AppInspect statuses
        app_inspect_status = "Not Run"
        cloud_inspect_status = "Not Run"
        ssai_inspect_status = "Not Run"

        # Track if there was an inspect exception
        inspect_exception = None

        # Run App Inspect
        is_app_inspect_check = gat.get_user_input_as("is_app_inspect_check", bool, True)

        if is_app_inspect_check:
            local_app_inspect = gat.get_user_input_as("local_app_inspect", bool, False)

            # Initialize inspect objects to None
            inspect_obj_local: SplunkLocalAppInspect | None = None
            inspect_obj: SplunkAppInspect | None = None

            try:
                if local_app_inspect:
                    # Use local app inspect with splunk-appinspect library
                    gat.info("Using local Splunk app inspect validation")
                    inspect_obj_local = SplunkLocalAppInspect(
                        saved_paths, app_info, build_path, use_ucc_gen
                    )
                    inspect_obj_local.run_all_checks()
                    # Get statuses from the object
                    app_inspect_status = inspect_obj_local.app_inspect_result[0]
                    cloud_inspect_status = inspect_obj_local.app_inspect_result[1]
                    ssai_inspect_status = inspect_obj_local.app_inspect_result[2]
                else:
                    # Use Splunkbase API for app inspect
                    gat.info("Using Splunkbase API for Splunk app inspect validation")
                    splunkbase_username = gat.get_user_input("splunkbase_username")
                    splunkbase_password = gat.get_user_input("splunkbase_password")

                    if splunkbase_username is None or splunkbase_password is None:
                        _err_msg = (
                            "❌ splunkbase_username and splunkbase_password are required for "
                            "Splunkbase API app-inspect. Either provide credentials or use "
                            "'local_app_inspect: true' for local validation, or set "
                            "'is_app_inspect_check: false' to skip app-inspect entirely."
                        )
                        gat.error(_err_msg)
                        # Set statuses to Skipped
                        app_inspect_status = "Skipped"
                        cloud_inspect_status = "Skipped"
                        ssai_inspect_status = "Skipped"
                        gat.set_output("app_inspect_status", app_inspect_status)
                        gat.set_output("cloud_inspect_status", cloud_inspect_status)
                        gat.set_output("ssai_inspect_status", ssai_inspect_status)
                        inspect_exception = Exception(_err_msg)
                    else:
                        inspect_obj = SplunkAppInspect(
                            saved_paths,
                            app_info,
                            build_path,
                            splunkbase_username,
                            splunkbase_password,
                            use_ucc_gen,
                        )
                        inspect_obj.run_all_checks()
                        # Get statuses from the object
                        app_inspect_status = inspect_obj.app_inspect_result[0]
                        cloud_inspect_status = inspect_obj.app_inspect_result[1]
                        ssai_inspect_status = inspect_obj.app_inspect_result[2]
            except Exception as e:
                # Inspect checks set their status outputs before failing
                # Try to get statuses from the exception context if they were set
                # If we created an inspect object, get statuses from it
                if inspect_obj_local is not None:
                    app_inspect_status = inspect_obj_local.app_inspect_result[0]
                    cloud_inspect_status = inspect_obj_local.app_inspect_result[1]
                    ssai_inspect_status = inspect_obj_local.app_inspect_result[2]
                elif inspect_obj is not None:
                    app_inspect_status = inspect_obj.app_inspect_result[0]
                    cloud_inspect_status = inspect_obj.app_inspect_result[1]
                    ssai_inspect_status = inspect_obj.app_inspect_result[2]
                # Store the exception to re-raise after writing summary
                inspect_exception = e
        else:
            gat.info("✅ App inspect checks disabled - skipping")
            app_inspect_status = "Skipped"
            cloud_inspect_status = "Skipped"
            ssai_inspect_status = "Skipped"
            gat.set_output("app_inspect_status", app_inspect_status)
            gat.set_output("cloud_inspect_status", cloud_inspect_status)
            gat.set_output("ssai_inspect_status", ssai_inspect_status)

        # Write job summary
        with gat.group("📊 Writing job summary"):
            job_summary.write_build_summary(
                app_info=app_info,
                artifact_name=artifact_name,
                app_inspect_status=app_inspect_status,
                cloud_inspect_status=cloud_inspect_status,
                ssai_inspect_status=ssai_inspect_status,
            )

        # Handle failure mode based on fail_on parameter
        fail_on = gat.get_user_input("fail_on") or "errors"
        fail_on = fail_on.lower().strip()

        # Re-raise inspect exception if it occurred, unless fail_on is "none"
        if fail_on != "none":
            if inspect_exception is not None:
                gat.debug(
                    f"Exception in App-Inspect (re-raising here at the end): fail_on={fail_on}, statuses=[{app_inspect_status}, {cloud_inspect_status}, {ssai_inspect_status}]"
                )
                raise inspect_exception
            else:
                # No exception but check if we should fail based on statuses
                should_fail = _should_fail_on_status(
                    fail_on, app_inspect_status, cloud_inspect_status, ssai_inspect_status
                )
                if should_fail:
                    msg = f"AppInspect checks failed with fail_on={fail_on} - results: [app-inspect: {app_inspect_status}, cloud-checks: {cloud_inspect_status}, ssai-checks: {ssai_inspect_status}]"
                    gat.error(msg)
                    raise Exception(msg)

    except Exception as e:
        gat.error(f"Error in build generation or app inspect checks: {e}")
        gat.error(traceback.format_exc())
        sys.exit(5)
        # Failure in build generation or App Inspect means failure for Workflow

    if utility_failed:
        gat.error("❌ Workflow failed due to utility addition failure.")
        sys.exit(5)


if __name__ == "__main__":
    main()
