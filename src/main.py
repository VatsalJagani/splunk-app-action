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


def validate_mutually_exclusive_features() -> None:
    """Validate that only one build feature is enabled at a time."""
    use_ucc_gen = gat.get_user_input_as("use_ucc_gen", bool, False)
    python_requirements_file = gat.get_user_input("python_requirements_file")
    app_utilities_input = gat.get_user_input("app_utilities")

    # Check if Splunk Python SDK utility is being used
    use_splunk_python_sdk = False
    if app_utilities_input and app_utilities_input != "NONE" and app_utilities_input != "":
        app_utilities_list = [u.strip() for u in app_utilities_input.split(",")]
        use_splunk_python_sdk = "splunk_python_sdk" in app_utilities_list

    # Check if Python dependency manager is being used
    use_python_deps = python_requirements_file and python_requirements_file != ""

    # Count active features
    active_features: list[str] = []
    if use_ucc_gen:
        active_features.append("UCC-Gen")
    if use_python_deps:
        active_features.append("Python-Dependency-Management")
    if use_splunk_python_sdk:
        active_features.append("Splunk-Python-SDK")

    if len(active_features) > 1:
        error_msg = (
            f"Error: Multiple build features detected: {', '.join(active_features)}. "
            "You can only use ONE of the following features at a time:\n"
            "  - UCC-Gen (use_ucc_gen: true)\n"
            "  - Python-Dependency-Management (python_requirements_file)\n"
            "  - Splunk-Python-SDK (app_utilities: splunk_python_sdk)\n"
            "Please update your workflow configuration to use only one feature."
        )
        gat.error(error_msg)
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

    app_build_dir_name = None
    app_build_dir_path = None

    if use_ucc_gen:
        with gat.group("🏗️ Preparing for App Build with UCC"):
            with keep_working_dir_unchanged():
                app_build_dir_name = ucc_gen.build(saved_paths, app_info)

    elif use_python_deps:
        with gat.group("🏗️ Installing dynamic Python Dependencies"):
            with keep_working_dir_unchanged():
                app_build_dir_name = python_dependency_manager.install_dependencies(
                    saved_paths, app_info
                )

    else:
        with gat.group("🏗️ Preparing for App Build without UCC"):
            app_build_dir_name = "without_ucc_build"
            os.system(f"rm -rf {app_build_dir_name}")
            shutil.copytree(saved_paths.app_dir_path, app_build_dir_name)
            gat.info("App build preparation completed successfully")

    app_build_dir_path = os.path.join(saved_paths.root_dir_path, app_build_dir_name)

    with gat.group("🔍 Getting the App Build Number"):
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
            SplunkAppUtilities(app_read_dir=app_build_dir_path, app_write_dir=app_write_dir)
    except Exception as e:
        gat.error(f"Error adding Splunk app utilities: {e}")
        gat.error(traceback.format_exc())

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

            try:
                if local_app_inspect:
                    # Use local app inspect with splunk-appinspect library
                    gat.info("Using local Splunk app inspect validation")
                    SplunkLocalAppInspect(saved_paths, app_info, build_path).run_all_checks()
                else:
                    # Use Splunkbase API for app inspect
                    gat.info("Using Splunkbase API for Splunk app inspect validation")
                    splunkbase_username = gat.get_user_input("splunkbase_username")
                    splunkbase_password = gat.get_user_input("splunkbase_password")

                    if splunkbase_username is None or splunkbase_password is None:
                        gat.error(
                            "✅ splunkbase_username and splunkbase_password are required for app inspect."
                        )
                        # Set statuses to Skipped
                        app_inspect_status = "Skipped"
                        cloud_inspect_status = "Skipped"
                        ssai_inspect_status = "Skipped"
                        gat.set_output("app_inspect_status", app_inspect_status)
                        gat.set_output("cloud_inspect_status", cloud_inspect_status)
                        gat.set_output("ssai_inspect_status", ssai_inspect_status)
                    else:
                        SplunkAppInspect(
                            saved_paths,
                            app_info,
                            build_path,
                            splunkbase_username,
                            splunkbase_password,
                        ).run_all_checks()
            except Exception as e:
                # Inspect checks may have set their own status outputs before failing
                # Store the exception to re-raise after writing summary
                inspect_exception = e

            # Post app inspect comments/annotations if enabled
            app_inspect_comment_on_pr = gat.get_user_input_as(
                "app_inspect_comment_on_pr", bool, True
            )
            if app_inspect_comment_on_pr:
                with gat.group("💬 Posting App Inspect Comments"):
                    try:
                        from helpers.app_inspect_report_commenter import AppInspectReportCommenter

                        app_inspect_comment_for_warnings = gat.get_user_input_as(
                            "app_inspect_comment_for_warnings", bool, False
                        )

                        # Determine the report directory
                        report_name_prefix = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}"
                        report_dir = f"{report_name_prefix}_reports"

                        # Create commenter and post comments
                        commenter = AppInspectReportCommenter(
                            report_dir=report_dir,
                            app_dir=saved_paths.app_dir_path,
                            include_warnings=app_inspect_comment_for_warnings,
                        )
                        commenter.post_comments()

                    except Exception as e:
                        gat.warning(f"Failed to post app inspect comments: {e}")

            # Get the statuses from outputs (they were set by the inspect classes)
            # If not set, they'll remain as default values
            try:
                # Try to get from environment variables which gat.set_output sets
                app_inspect_status = os.environ.get("OUTPUT_APP_INSPECT_STATUS", app_inspect_status)
                cloud_inspect_status = os.environ.get(
                    "OUTPUT_CLOUD_INSPECT_STATUS", cloud_inspect_status
                )
                ssai_inspect_status = os.environ.get(
                    "OUTPUT_SSAI_INSPECT_STATUS", ssai_inspect_status
                )
            except Exception:
                # Use defaults if there's any issue
                pass
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
                build_path=build_path,
                artifact_name=artifact_name,
                app_inspect_status=app_inspect_status,
                cloud_inspect_status=cloud_inspect_status,
                ssai_inspect_status=ssai_inspect_status,
            )

        # Re-raise inspect exception if it occurred
        if inspect_exception is not None:
            raise inspect_exception

    except Exception as e:
        gat.error(f"Error in build generation or app inspect checks: {e}")
        gat.error(traceback.format_exc())

        sys.exit(5)
        # Failure in build generation or App Inspect means failure for Workflow


if __name__ == "__main__":
    main()
