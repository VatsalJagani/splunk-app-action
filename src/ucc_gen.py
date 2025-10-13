import os
import shutil

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def build(saved_paths: SavedPaths, app_info: AppInfo):
    gat.info("Running ucc-gen command.")

    # copy folder to generate build, rather than affecting the original repo checkout
    os.system("rm -rf ucc_build_dir")
    shutil.copytree(saved_paths.repo_dir_name, "ucc_build_dir")

    ta_dir = os.path.join("ucc_build_dir", saved_paths.app_dir_name)
    os.chdir(ta_dir)
    os.system(f"ucc-gen build --ta-version {app_info.version_number}")
    os.chdir(saved_paths.root_dir_path)

    shutil.copytree(
        os.path.join(ta_dir, "output", app_info.package_id), "ucc_generated_build"
    )

    return "ucc_generated_build"
