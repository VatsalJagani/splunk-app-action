import os
import shutil
import subprocess

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def install_dependencies(
    saved_paths: SavedPaths,
    app_info: AppInfo,  # pyright: ignore[reportUnusedParameter]
) -> str:
    """Install Python dependencies from requirements.txt and return the build directory name.

    Note: app_info parameter is kept for API consistency with other build functions (e.g., ucc_gen.build).
    """
    python_requirements_file = gat.get_user_input("python_requirements_file")

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

    # Run pip install with requirements.txt
    result = subprocess.run(
        ["pip", "install", "-r", requirements_file_path, "--target", target_dir],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        gat.error(
            f"Failed to install Python dependencies from '{python_requirements_file}'.\n"
            f"  pip exit code: {result.returncode}\n"
            f"  stderr: {result.stderr}\n"
            "Verify that all packages in the requirements file exist and have compatible versions."
        )
        raise RuntimeError(f"Dependency installation failed (exit code {result.returncode})")

    gat.debug(result.stdout)

    # Clean up cache files
    gat.debug("Cleaning up cache files...")
    subprocess.run(["find", target_dir, "-name", "*.py[co]", "-type", "f", "-delete"], check=False)
    subprocess.run(
        ["find", target_dir, "-name", "__pycache__", "-type", "d", "-delete"], check=False
    )

    # Remove requirements.txt file after installing dependencies
    gat.info(f"Removing requirements file: {requirements_file_path}")
    try:
        os.remove(requirements_file_path)
    except Exception as e:
        gat.warning(f"Failed to remove requirements file: {e}")

    # Copy the build to final location
    final_build_dir = "python_deps_generated_build"
    if os.path.exists(final_build_dir):
        shutil.rmtree(final_build_dir)
    shutil.copytree(app_dir, final_build_dir)

    gat.info("Python dependency installation completed successfully")
    return final_build_dir
