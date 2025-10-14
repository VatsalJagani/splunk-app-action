import os

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def remove_unwanted_files():
    gat.info("Starting cleanup of unwanted files...")
    os.system("rm -rf .github")
    os.system("rm -rf .git")
    os.system("rm -rf .gitignore")
    os.system('find . -name "*.py[co]" -type f -delete')
    os.system('find . -name "__pycache__" -type d -delete')
    gat.info("File cleanup completed successfully")


def file_folder_permission_changes():
    to_make_permission_changes = gat.get_user_input_as("to_make_permission_changes", bool, False)

    if to_make_permission_changes:
        with gat.group("📝 Adjusting file permissions"):
            gat.debug("Setting default file permissions (644)")
            os.system("find . -type f -exec chmod 644 '{}' \\;")

            gat.debug("Setting executable permissions for script files")
            for file_ext in [".sh", ".exe", ".cmd", ".msi", ".bat"]:
                os.system(f"find . -type f -name '*{file_ext}' -exec chmod 755 '{{}}' \\;")

            gat.debug("Setting directory permissions (755)")
            os.system("find . -type d -exec chmod 755 '{}' \\;")
            gat.info("File permission adjustments completed successfully")
    else:
        gat.debug("File permission changes disabled - skipping")


def run_custom_user_defined_commands():
    with gat.group("⚙️ Executing custom user-defined commands"):
        commands_executed = 0
        for no in range(1, 100):
            try:
                cmd = os.environ.get(f"SPLUNK_APP_ACTION_{no}")
                if cmd:
                    gat.debug(f"Executing custom command {no}: {cmd}")
                    os.system(cmd)
                    commands_executed += 1
            except Exception as e:
                gat.warning(f"Failed to execute custom command {no}: {e}")

        if commands_executed > 0:
            gat.info(
                f"Custom commands execution completed successfully ({commands_executed} commands)"
            )
        else:
            gat.debug("No custom commands found - skipping")


def generate_build(saved_paths: SavedPaths, app_info: AppInfo, app_build_dir_name: str) -> str:
    with gat.group("🏗️ Generating app build package"):
        gat.debug(
            f"Build parameters - package_id: {app_info.package_id}, version: {app_info.version_number_encoded}, build: {app_info.build_number_encoded}"
        )

        gat.debug(f"Renaming build directory: {app_build_dir_name} -> {app_info.package_id}")
        os.system(f"mv {app_build_dir_name} {app_info.package_id}")
        os.chdir(app_info.package_id)

        remove_unwanted_files()
        run_custom_user_defined_commands()
        file_folder_permission_changes()
        os.chdir(saved_paths.root_dir_path)

        # Generate Build
        build_name = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}.tgz"
        gat.debug(f"Creating tarball: {build_name}")
        os.system(f"tar -czf {build_name} {app_info.package_id}")

        build_path = os.path.join(saved_paths.root_dir_path, build_name)
        gat.info("App build generation completed successfully")
        return build_path
