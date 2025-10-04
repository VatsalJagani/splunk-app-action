
import os
import shutil
import github_action_toolkit as gat
from helpers.global_variables import GlobalVariables


def build():
    gat.info("Running ucc-gen command.")

    # copy folder to generate build, rather than affecting the original repo checkout
    os.system("rm -rf ucc_build_dir")
    shutil.copytree(GlobalVariables.ORIGINAL_REPO_DIR_NAME, "ucc_build_dir")

    org_ta_dir = os.path.join(GlobalVariables.ORIGINAL_REPO_DIR_NAME, GlobalVariables.APP_DIR_NAME)

    os.chdir(org_ta_dir)

    os.system(f"ucc-gen build --ta-version {GlobalVariables.APP_VERSION}")

    os.chdir(GlobalVariables.ROOT_DIR_PATH)

    shutil.copytree(os.path.join(org_ta_dir, 'output', GlobalVariables.APP_PACKAGE_ID), "ucc_generated_build")

    return "ucc_generated_build"
