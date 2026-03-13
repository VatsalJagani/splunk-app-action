import os
import shutil
import subprocess

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def remove_unwanted_files() -> None:
    """Remove unwanted files and directories from the app build."""
    gat.info("Starting cleanup of unwanted files...")

    # Remove directories using shutil for safety
    for dir_name in [".github", ".git"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    # Remove .gitignore file
    if os.path.exists(".gitignore"):
        os.remove(".gitignore")

    # Clean Python cache files using subprocess for better control
    subprocess.run(["find", ".", "-name", "*.py[co]", "-type", "f", "-delete"], check=False)
    subprocess.run(["find", ".", "-name", "__pycache__", "-type", "d", "-delete"], check=False)

    gat.info("File cleanup completed successfully")


def file_folder_permission_changes() -> None:
    """Apply file and folder permission changes for Splunk App Inspect requirements."""
    to_make_permission_changes = gat.get_user_input_as("to_make_permission_changes", bool, False)

    if to_make_permission_changes:
        gat.info("📝 Adjusting file permissions")
        gat.debug("Setting default file permissions (644)")
        subprocess.run(["find", ".", "-type", "f", "-exec", "chmod", "644", "{}", ";"], check=False)

        gat.debug("Setting executable permissions for script files")
        for file_ext in [".sh", ".exe", ".cmd", ".msi", ".bat"]:
            subprocess.run(
                [
                    "find",
                    ".",
                    "-type",
                    "f",
                    "-name",
                    f"*{file_ext}",
                    "-exec",
                    "chmod",
                    "755",
                    "{}",
                    ";",
                ],
                check=False,
            )

        gat.debug("Setting directory permissions (755)")
        subprocess.run(["find", ".", "-type", "d", "-exec", "chmod", "755", "{}", ";"], check=False)
        gat.info("File permission adjustments completed successfully")
    else:
        gat.debug("File permission changes disabled - skipping")


def run_custom_user_defined_commands() -> None:
    """
    Execute custom user-defined commands from environment variables.

    Looks for commands in environment variables named `SPLUNK_APP_ACTION_1` through
    `SPLUNK_APP_ACTION_100` and executes them sequentially. Logs warnings for any
    commands that fail but continues execution.
    """
    gat.info("⚙️ Executing custom user-defined commands")
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
            f"⚙️ Custom commands execution completed successfully ({commands_executed} commands)"
        )
    else:
        gat.debug("⚙️ No custom commands found - skipping")


def generate_build(saved_paths: SavedPaths, app_info: AppInfo, app_build_dir_name: str) -> str:
    """
    Generate the final Splunk app build package as a tarball.

    Renames the build directory to the package ID, performs cleanup operations,
    executes custom commands, adjusts file permissions if needed, and creates
    a compressed tarball of the app package.

    Args:
        saved_paths: Container for directory paths used during the build process.
        app_info: Application metadata including package ID, version, and build number.
        app_build_dir_name: Name of the directory containing the build files.

    Returns:
        Full path to the generated tarball (.tgz) file.
    """
    with gat.group("🏗️ Generating app build package"):
        gat.debug(
            f"Build parameters - package_id: {app_info.package_id}, version: {app_info.version_number_encoded}, build: {app_info.build_number_encoded}"
        )

        gat.debug(f"Renaming build directory: {app_build_dir_name} -> {app_info.package_id}")
        if os.path.exists(app_info.package_id):
            gat.debug(f"Removing existing directory before rename: {app_info.package_id}")
            shutil.rmtree(app_info.package_id)
        os.system(f"mv {app_build_dir_name} {app_info.package_id}")
        os.chdir(app_info.package_id)
        gat.debug(f"Current working directory after going to app package directory: {os.getcwd()}")

        remove_unwanted_files()
        run_custom_user_defined_commands()
        file_folder_permission_changes()
        os.chdir(saved_paths.root_dir_path)
        gat.debug(f"Current working directory after returning to root directory: {os.getcwd()}")

        # Generate Build
        build_name = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}.tgz"
        gat.debug(f"Creating tarball: {build_name}")
        gat.Debugging.print_directory_tree()

        os.system(f"tar -czf {build_name} {app_info.package_id}")

        build_path = os.path.join(saved_paths.root_dir_path, build_name)
        gat.set_output("build_path", build_path)
        gat.set_output("artifact_name", build_name)
        gat.info("App build generation completed successfully")
        return build_path
