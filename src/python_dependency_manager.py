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
    shutil.copytree(saved_paths.repo_dir_name, "python_deps_build_dir")

    app_dir = os.path.join("python_deps_build_dir", saved_paths.app_dir_name)
    requirements_file_path = os.path.join(app_dir, python_requirements_file)

    # Validate requirements.txt exists
    if not os.path.exists(requirements_file_path):
        gat.error(f"Requirements file not found at: {requirements_file_path}")
        raise FileNotFoundError(f"Requirements file not found: {requirements_file_path}")

    gat.debug(f"Installing dependencies from: {requirements_file_path}")

    # Install dependencies to lib folder by default
    lib_dir = os.path.join(app_dir, "lib")
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)

    gat.info(f"Installing Python dependencies to: {lib_dir}")

    # Run pip install with requirements.txt
    result = subprocess.run(
        ["pip", "install", "-r", requirements_file_path, "--target", lib_dir],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        gat.error(f"Failed to install dependencies: {result.stderr}")
        raise RuntimeError(f"Dependency installation failed: {result.stderr}")

    gat.debug(result.stdout)

    # Clean up cache files
    gat.debug("Cleaning up cache files...")
    subprocess.run(["find", lib_dir, "-name", "*.py[co]", "-type", "f", "-delete"], check=False)
    subprocess.run(["find", lib_dir, "-name", "__pycache__", "-type", "d", "-delete"], check=False)

    # Copy the build to final location
    final_build_dir = "python_deps_generated_build"
    if os.path.exists(final_build_dir):
        shutil.rmtree(final_build_dir)
    shutil.copytree(app_dir, final_build_dir)

    gat.info("Python dependency installation completed successfully")
    return final_build_dir
