import os
import shutil
import subprocess

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def get_permission_preview() -> str:
    """
    Generate a preview of what permission changes would be made.

    Returns:
        String containing the preview of permission changes
    """
    preview = ["=== Permission Changes Preview ===\n"]

    file_mode = gat.get_user_input("permission_file_mode") or "644"
    dir_mode = gat.get_user_input("permission_dir_mode") or "755"
    script_mode = gat.get_user_input("permission_script_mode") or "755"
    owner = gat.get_user_input("permission_owner") or ""
    group = gat.get_user_input("permission_group") or ""

    preview.append(f"File mode: {file_mode}\n")
    preview.append(f"Directory mode: {dir_mode}\n")
    preview.append(f"Script mode: {script_mode}\n")

    if owner:
        preview.append(f"Owner: {owner}\n")
    if group:
        preview.append(f"Group: {group}\n")

    preview.append("\nScript file extensions that will get executable permissions:\n")
    for ext in [".sh", ".exe", ".cmd", ".msi", ".bat"]:
        preview.append(f"  - *{ext}\n")

    preview.append("\nFiles and directories affected:\n")

    # List files
    result = subprocess.run(
        ["find", ".", "-type", "f", "-not", "-path", "./.git/*"],
        capture_output=True,
        text=True,
        check=False,
    )
    files = [f for f in result.stdout.strip().split("\n") if f]
    preview.append(f"  Files: {len(files)}\n")

    # List directories
    result = subprocess.run(
        ["find", ".", "-type", "d", "-not", "-path", "./.git/*"],
        capture_output=True,
        text=True,
        check=False,
    )
    dirs = [d for d in result.stdout.strip().split("\n") if d and d != "."]
    preview.append(f"  Directories: {len(dirs)}\n")

    return "".join(preview)


def remove_unwanted_files() -> None:
    """Remove unwanted files and directories from the app build."""
    dry_run = gat.get_user_input_as("dry_run", bool, False)

    if dry_run:
        gat.info(
            "DRY-RUN: Would cleanup unwanted files (.github, .git, .gitignore, *.pyc, __pycache__)"
        )
        return

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
    dry_run = gat.get_user_input_as("dry_run", bool, False)

    if not to_make_permission_changes:
        gat.debug("File permission changes disabled - skipping")
        return

    file_mode = gat.get_user_input("permission_file_mode") or "644"
    dir_mode = gat.get_user_input("permission_dir_mode") or "755"
    script_mode = gat.get_user_input("permission_script_mode") or "755"
    owner = gat.get_user_input("permission_owner") or ""
    group = gat.get_user_input("permission_group") or ""

    if dry_run:
        gat.info("DRY-RUN: Would adjust file permissions")
        gat.info(f"  File mode: {file_mode}")
        gat.info(f"  Directory mode: {dir_mode}")
        gat.info(f"  Script mode: {script_mode}")
        if owner:
            gat.info(f"  Owner: {owner}")
        if group:
            gat.info(f"  Group: {group}")
        return

    gat.info("📝 Adjusting file permissions")
    gat.debug(f"Setting default file permissions ({file_mode})")
    subprocess.run(["find", ".", "-type", "f", "-exec", "chmod", file_mode, "{}", ";"], check=False)

    gat.debug(f"Setting executable permissions for script files ({script_mode})")
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
                script_mode,
                "{}",
                ";",
            ],
            check=False,
        )

    gat.debug(f"Setting directory permissions ({dir_mode})")
    subprocess.run(["find", ".", "-type", "d", "-exec", "chmod", dir_mode, "{}", ";"], check=False)

    # Apply owner/group if specified
    if owner or group:
        chown_spec = f"{owner}:{group}" if owner and group else (owner if owner else f":{group}")
        gat.debug(f"Setting ownership: {chown_spec}")
        subprocess.run(["find", ".", "-exec", "chown", chown_spec, "{}", ";"], check=False)

    gat.info("File permission adjustments completed successfully")


def run_custom_user_defined_commands():
    dry_run = gat.get_user_input_as("dry_run", bool, False)

    if dry_run:
        gat.info("DRY-RUN: Would execute custom user-defined commands")
        commands_to_execute = 0
        for no in range(1, 100):
            cmd = os.environ.get(f"SPLUNK_APP_ACTION_{no}")
            if cmd:
                gat.info(f"  Command {no}: {cmd}")
                commands_to_execute += 1
        if commands_to_execute == 0:
            gat.debug("  No custom commands found")
        return

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
    dry_run = gat.get_user_input_as("dry_run", bool, False)

    with gat.group("🏗️ Generating app build package"):
        gat.debug(
            f"Build parameters - package_id: {app_info.package_id}, version: {app_info.version_number_encoded}, build: {app_info.build_number_encoded}"
        )

        if dry_run:
            gat.info("=" * 60)
            gat.info("DRY-RUN MODE ENABLED - Preview of planned actions")
            gat.info("=" * 60)

        gat.debug(f"Renaming build directory: {app_build_dir_name} -> {app_info.package_id}")

        if not dry_run:
            os.system(f"mv {app_build_dir_name} {app_info.package_id}")
            os.chdir(app_info.package_id)

        # For dry-run, we need to change to the build directory to get accurate preview
        if dry_run:
            os.chdir(app_build_dir_name)

        # Collect dry-run preview
        preview_lines: list[str] = []
        if dry_run:
            preview_lines.append("=" * 60)
            preview_lines.append("DRY-RUN PREVIEW - Planned Actions")
            preview_lines.append("=" * 60)
            preview_lines.append("")
            preview_lines.append(f"Package ID: {app_info.package_id}")
            preview_lines.append(f"Version: {app_info.version_number_encoded}")
            preview_lines.append(f"Build Number: {app_info.build_number_encoded}")
            preview_lines.append("")

        remove_unwanted_files()
        run_custom_user_defined_commands()

        # Get permission preview before applying changes
        to_make_permission_changes = gat.get_user_input_as(
            "to_make_permission_changes", bool, False
        )
        if dry_run and to_make_permission_changes:
            preview_lines.append(get_permission_preview())

        file_folder_permission_changes()

        if dry_run:
            os.chdir(saved_paths.root_dir_path)
            # Write preview to file
            preview_content = "\n".join(preview_lines)
            with open("dry_run_preview.txt", "w") as f:
                f.write(preview_content)
            gat.info("Dry-run preview saved to dry_run_preview.txt")
            gat.info("\n" + preview_content)
            gat.info("=" * 60)
            gat.info("DRY-RUN: Build would be created but skipping actual build generation")
            gat.info("=" * 60)
            # Return a dummy path for dry-run
            build_name = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}.tgz"
            build_path = os.path.join(saved_paths.root_dir_path, build_name)
            gat.set_output("build_path", build_path)
            gat.set_output("artifact_name", build_name)
            return build_path

        os.chdir(saved_paths.root_dir_path)

        # Generate Build
        build_name = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}.tgz"
        gat.debug(f"Creating tarball: {build_name}")
        os.system(f"tar -czf {build_name} {app_info.package_id}")

        build_path = os.path.join(saved_paths.root_dir_path, build_name)
        gat.set_output("build_path", build_path)
        gat.set_output("artifact_name", build_name)
        gat.info("App build generation completed successfully")
        return build_path
