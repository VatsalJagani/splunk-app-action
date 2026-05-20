import os
import shutil
import subprocess

import github_action_toolkit as gat
import magic

from helpers.saved_values import AppInfo, SavedPaths


def _is_console_script(filepath: str) -> bool:
    """Return True if the file starts with a shebang, indicating a uv/pip entry point script."""
    try:
        with open(filepath, "rb") as f:
            return f.read(2) == b"#!"
    except Exception:
        return False


def install_dependencies(
    saved_paths: SavedPaths,
    app_info: AppInfo,  # pyright: ignore[reportUnusedParameter]
    is_remove_not_allowed_executables_from_lib: bool = False,
) -> str:
    """Install Python dependencies from requirements.txt and return the build directory name.

    Note: app_info parameter is kept for API consistency with other build functions (e.g., ucc_gen.build).
    """
    python_requirements_file = gat.get_user_input("python_requirements_file")
    splunk_python_version = gat.get_user_input("splunk_python_version") or "3.9"

    if not python_requirements_file or python_requirements_file == "":
        gat.error("python_requirements_file must be provided when using Python dependency manager")
        raise ValueError("python_requirements_file is required")

    gat.debug(f"Preparing Python dependency installation from: {python_requirements_file}")

    # Copy folder to generate build, rather than affecting the original repo checkout
    gat.debug("Preparing temporary build directory")
    if os.path.exists("python_deps_build_dir"):
        shutil.rmtree("python_deps_build_dir")
    shutil.copytree(saved_paths.repo_dir_path, "python_deps_build_dir")

    app_dir = os.path.join("python_deps_build_dir", saved_paths.app_dir_name)
    requirements_file_path = os.path.join(app_dir, python_requirements_file)

    # Validate requirements.txt exists
    if not os.path.exists(requirements_file_path):
        gat.error(f"Requirements file not found at: {requirements_file_path}")
        raise FileNotFoundError(f"Requirements file not found: {requirements_file_path}")

    gat.debug(f"Installing dependencies from: {requirements_file_path}")

    # Get the directory containing the requirements file - this is where dependencies will be installed
    target_dir = os.path.dirname(requirements_file_path)

    # If requirements file is in app root, create lib subdirectory
    if target_dir == app_dir:
        target_dir = os.path.join(app_dir, "lib")
        gat.info(f"Requirements file is in app root, using lib subdirectory: {target_dir}")

    # Clean up the directory containing requirements.txt before installing dependencies
    gat.info(f"Cleaning directory: {target_dir}")
    if os.path.exists(target_dir):
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            # Skip the requirements file itself
            if item == os.path.basename(python_requirements_file):
                continue
            # Skip essential Splunk directories if we're cleaning the app root
            if target_dir == app_dir and item in [
                "default",
                "metadata",
                "static",
                "appserver",
                "bin",
                "local",
                "lookups",
            ]:
                continue
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                gat.debug(f"Removed: {item_path}")
            except Exception as e:
                gat.warning(f"Failed to remove {item_path}: {e}")
    else:
        # Create the target directory if it doesn't exist
        os.makedirs(target_dir)

    gat.info(f"Installing Python dependencies to: {target_dir}")

    # Run pip install with requirements.txt, targeting the Splunk platform Python version
    result = subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            splunk_python_version,
            "-r",
            requirements_file_path,
            "--target",
            target_dir,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        gat.error(
            f"Failed to install Python dependencies from '{python_requirements_file}'.\n"
            f"  uv pip exit code: {result.returncode}\n"
            f"  stderr: {result.stderr}\n"
            "Verify that all packages in the requirements file exist and have compatible versions."
        )
        raise RuntimeError(f"Dependency installation failed (exit code {result.returncode})")

    gat.debug(result.stdout)

    # Clean up pip metadata and cache files not needed at runtime
    gat.debug("Cleaning up pip metadata and cache files...")
    subprocess.run(["find", target_dir, "-name", "*.py[co]", "-type", "f", "-delete"], check=False)
    subprocess.run(
        ["find", target_dir, "-name", "__pycache__", "-type", "d", "-delete"], check=False
    )
    subprocess.run(
        ["find", target_dir, "-name", "*.dist-info", "-type", "d", "-exec", "rm", "-rf", "{}", "+"],
        check=False,
    )

    # Remove uv .lock file — not needed in Splunk builds and flagged by App Inspect
    uv_lock_file = os.path.join(target_dir, ".lock")
    if os.path.exists(uv_lock_file):
        gat.info("Removing uv .lock file from target directory")
        os.remove(uv_lock_file)

    # Remove bin/ at target dir root if it contains only console entry point scripts
    # (identified by shebang #!). These are created by uv for packages with console_scripts
    # entry points and are not needed at Splunk runtime. Skipped if any subdirectory,
    # non-script file, or symlink is found, which would indicate real content to preserve.
    uv_bin_dir = os.path.join(target_dir, "bin")
    if os.path.exists(uv_bin_dir) and os.path.isdir(uv_bin_dir):
        bin_items = os.listdir(uv_bin_dir)
        bin_files = [f for f in bin_items if os.path.isfile(os.path.join(uv_bin_dir, f))]
        bin_subdirs = [f for f in bin_items if os.path.isdir(os.path.join(uv_bin_dir, f))]
        bin_symlinks_or_special = [
            f
            for f in bin_items
            if not os.path.isfile(os.path.join(uv_bin_dir, f))
            and not os.path.isdir(os.path.join(uv_bin_dir, f))
        ]
        non_scripts = [f for f in bin_files if not _is_console_script(os.path.join(uv_bin_dir, f))]
        unexpected = bin_subdirs + non_scripts + bin_symlinks_or_special
        if unexpected:
            gat.warning(
                f"bin/ in target directory contains unexpected items "
                f"(subdirs={bin_subdirs}, non_scripts={non_scripts}, special={bin_symlinks_or_special}) — skipping removal"
            )
        else:
            gat.info(
                f"Removing bin/ from target directory ({len(bin_files)} console entry point script(s))"
            )
            shutil.rmtree(uv_bin_dir)

    # Remove requirements.txt file after installing dependencies
    gat.info(f"Removing requirements file: {requirements_file_path}")
    try:
        os.remove(requirements_file_path)
    except Exception as e:
        gat.warning(f"Failed to remove requirements file: {e}")

    # Remove .python-version file — used by Dependabot for version constraints, not needed in Splunk build
    python_version_file_path = os.path.join(app_dir, ".python-version")
    if os.path.exists(python_version_file_path):
        gat.info(
            "Removing .python-version file from build (Dependabot helper, not needed at runtime)"
        )
        try:
            os.remove(python_version_file_path)
        except Exception as e:
            gat.warning(f"Failed to remove .python-version: {e}")

    # Remove files with mimetype application/x-executable or application/x-sharedlib from lib directory
    if is_remove_not_allowed_executables_from_lib:
        removed_files_count = 0
        if os.path.isdir(target_dir):
            for root, _, files in os.walk(target_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        magic_mime = magic.Magic(mime=True)
                        mimetype_val = magic_mime.from_file(file_path)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    except Exception as e:
                        gat.warning(f"magic failed for {file_path}: {e}")
                        continue
                    if mimetype_val in ("application/x-executable", "application/x-sharedlib"):
                        os.remove(file_path)
                        removed_files_count += 1
                        gat.info(
                            f"Removed not allowed executable type: {file_path} ({mimetype_val})"
                        )
        gat.debug(f"Removed not allowed executables count: {removed_files_count}")

    # Copy the build to final location
    final_build_dir = "python_deps_generated_build"
    if os.path.exists(final_build_dir):
        shutil.rmtree(final_build_dir)
    shutil.copytree(app_dir, final_build_dir, symlinks=True)

    gat.info("Python dependency installation completed successfully")
    return final_build_dir
