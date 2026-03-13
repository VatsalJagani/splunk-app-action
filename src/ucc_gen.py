import os
import shutil

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def build(
    saved_paths: SavedPaths,
    app_info: AppInfo,
    is_remove_mypyc_from_ucc_lib: bool = True,
) -> str:
    """
    Build UCC-based add-on using the ucc-gen command and return the build directory name.

    Creates a temporary build directory, copies the repository, executes the ucc-gen
    build command with the appropriate version, and copies the generated output to
    the final build location.

    Args:
        saved_paths: Container for directory paths used during the build process.
        app_info: Application metadata including package ID and version number.
        is_remove_mypyc_from_ucc_lib: Whether to remove mypyc-generated shared objects
            from the generated UCC `lib` folder.

    Returns:
        Name of the directory containing the generated UCC build ("ucc_generated_build").
    """
    # copy folder to generate build, rather than affecting the original repo checkout
    gat.debug("Preparing temporary build directory")
    if os.path.exists("ucc_build_dir"):
        shutil.rmtree("ucc_build_dir")
    shutil.copytree(saved_paths.repo_dir_path, "ucc_build_dir")

    ta_dir = os.path.abspath(os.path.join("ucc_build_dir", saved_paths.app_dir_name))
    gat.debug(f"Executing ucc-gen build in directory: {ta_dir}")
    os.chdir(ta_dir)
    os.system(f"ucc-gen build --ta-version {app_info.version_number}")

    if is_remove_mypyc_from_ucc_lib:
        # Remove mypyc-generated shared objects to avoid Splunk AppInspect failures.
        ucc_lib_dir = os.path.join(ta_dir, "output", app_info.package_id, "lib")
        removed_files_count = 0
        if os.path.isdir(ucc_lib_dir):
            for root, _, files in os.walk(ucc_lib_dir):
                for file_name in files:
                    if "mypyc.cpython-" in file_name and file_name.endswith(".so"):
                        file_path = os.path.join(root, file_name)
                        os.remove(file_path)
                        removed_files_count += 1
                        gat.info(f"UCC - Removed mypyc shared object: {file_path}")
        else:
            gat.info(f"UCC lib directory not found, skipping mypyc cleanup: {ucc_lib_dir}")

        gat.debug(f"Removed mypyc shared objects count: {removed_files_count}")
    else:
        gat.info("UCC mypyc shared object cleanup disabled via input")

    os.chdir(saved_paths.root_dir_path)

    gat.debug(f"Copying UCC output for package: {app_info.package_id}")
    ucc_output_path = os.path.abspath(os.path.join(ta_dir, "output", app_info.package_id))
    ucc_generated_build_path = os.path.abspath("ucc_generated_build")
    gat.debug(
        f"UCC path details | output folder: {ucc_output_path} | ucc_generated_build: {ucc_generated_build_path}"
    )
    shutil.copytree(ucc_output_path, ucc_generated_build_path)

    gat.info("UCC build generation completed successfully")
    return "ucc_generated_build"
