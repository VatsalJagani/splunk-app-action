import os
import shutil

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


def print_dir_and_files():
    gat.info(f"TODO - current directory - {os.getcwd()}")
    with gat.group("DEBUG"):
        startpath = os.getcwd()
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)

            # only until level 2
            if level > 3:
                continue

            indent = ' ' * 4 * (level)
            gat.info('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                gat.info('{}{}'.format(subindent, f))


def build(saved_paths: SavedPaths, app_info: AppInfo):
    gat.info("Running ucc-gen command.")

    # copy folder to generate build, rather than affecting the original repo checkout
    os.system("rm -rf ucc_build_dir")
    shutil.copytree(saved_paths.repo_dir_name, "ucc_build_dir")

    gat.info("TODO - after coping files")
    print_dir_and_files()

    ta_dir = os.path.join("ucc_build_dir", saved_paths.app_dir_name)

    os.chdir(ta_dir)
    gat.info(f"TODO - after changing directory to org_ta_dir {ta_dir}")
    print_dir_and_files()
    os.system(f"ucc-gen build --ta-version {app_info.version_number}")
    os.chdir(saved_paths.root_dir_path)
    gat.info(f"TODO - after changing back to root_dir_path {saved_paths.root_dir_path}")
    print_dir_and_files()

    shutil.copytree(
        os.path.join(ta_dir, "output", app_info.package_id), "ucc_generated_build"
    )

    return "ucc_generated_build"
