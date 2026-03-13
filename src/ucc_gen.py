import os
import shutil

import github_action_toolkit as gat
import magic

from helpers.saved_values import AppInfo, SavedPaths


def build(
    saved_paths: SavedPaths,
    app_info: AppInfo,
    is_remove_not_allowed_executables_from_lib: bool = True,
) -> str:
    """
    Build UCC-based add-on using the ucc-gen command and return the build directory name.

    Creates a temporary build directory, copies the repository, executes the ucc-gen
    build command with the appropriate version, and copies the generated output to
    the final build location.

    Args:
        saved_paths: Container for directory paths used during the build process.
        app_info: Application metadata including package ID and version number.
        is_remove_not_allowed_executables_from_lib: Whether to remove files with
            mimetype application/x-executable or application/x-sharedlib from the generated UCC `lib` folder.

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

    if is_remove_not_allowed_executables_from_lib:
        # Remove files with mimetype application/x-executable or application/x-sharedlib from UCC lib directory.
        ucc_lib_dir = os.path.join(ta_dir, "output", app_info.package_id, "lib")
        removed_files_count = 0
        if os.path.isdir(ucc_lib_dir):
            for root, _, files in os.walk(ucc_lib_dir):
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
                            f"UCC - Removed not allowed executable type: {file_path} ({mimetype_val})"
                        )
        else:
            gat.info(f"UCC lib directory not found, skipping executable cleanup: {ucc_lib_dir}")

        gat.debug(f"Removed not allowed executables count: {removed_files_count}")
    else:
        gat.info("UCC executables cleanup disabled via input")

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
