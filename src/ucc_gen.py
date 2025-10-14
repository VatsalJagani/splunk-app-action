import os
import shutil

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def build(saved_paths: SavedPaths, app_info: AppInfo):
    with gat.group("🔧 Generating UCC build"):
        # copy folder to generate build, rather than affecting the original repo checkout
        gat.debug("Preparing temporary build directory")
        os.system("rm -rf ucc_build_dir")
        shutil.copytree(saved_paths.repo_dir_name, "ucc_build_dir")

        ta_dir = os.path.join("ucc_build_dir", saved_paths.app_dir_name)
        gat.debug(f"Executing ucc-gen build in directory: {ta_dir}")
        os.chdir(ta_dir)
        os.system(f"ucc-gen build --ta-version {app_info.version_number}")
        os.chdir(saved_paths.root_dir_path)

        gat.debug(f"Copying UCC output for package: {app_info.package_id}")
        shutil.copytree(os.path.join(ta_dir, "output", app_info.package_id), "ucc_generated_build")

        gat.info("UCC build generation completed successfully")
        return "ucc_generated_build"
