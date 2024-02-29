
import os
import shutil
import helper_github_action as utils
from helpers.global_variables import GlobalVariables


def build():
    utils.info("Running ucc-gen command.")

    # copy folder to generate build, rather than affecting the original repo checkout
    utils.execute_system_command(f"rm -rf ucc_build_dir")
    shutil.copytree(GlobalVariables.ORIGINAL_REPO_DIR_NAME, "ucc_build_dir")

    org_ta_dir = os.path.join(GlobalVariables.ORIGINAL_REPO_DIR_NAME, GlobalVariables.APP_DIR_NAME)

    os.chdir(org_ta_dir)

    utils.execute_system_command(f"ucc-gen build --ta-version {GlobalVariables.APP_VERSION}")

    os.chdir(GlobalVariables.ROOT_DIR_PATH)

    shutil.copytree(os.path.join(org_ta_dir, 'output', GlobalVariables.APP_PACKAGE_ID), "ucc_generated_build")

    return "ucc_generated_build"
