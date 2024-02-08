
import os
import shutil
import json

import helper_github_action as utils


def fetch_app_package_id():
    utils.info("Fetching app package id from globalConfig.json file.")

    _app_package_id = None

    with open(os.path.join(utils.CommonDirPaths.REPO_DIR, 'globalConfig.json'), 'r') as f:
        global_config = json.loads(f.read())

        _app_package_id = global_config["meta"]["name"]

    if not _app_package_id:
        raise Exception("Unable to fetch the app package id from globalConfig.json file")

    return _app_package_id


def fetch_app_version():
    utils.info("Fetching app version number from globalConfig.json file.")

    _app_version = None

    with open(os.path.join(utils.CommonDirPaths.REPO_DIR, 'globalConfig.json'), 'r') as f:
        global_config = json.loads(f.read())

        _app_version = global_config["meta"]["version"]

    if not _app_version:
        raise Exception("Unable to fetch the app package id from globalConfig.json file")

    return _app_version


def build(app_package_id, app_version):
    utils.info("Running ucc-gen command.")

    # copy folder to generate build, rather than affecting the original repo checkout
    utils.execute_system_command(f"rm -rf {utils.CommonDirPaths.BUILD_DIR_NAME}")
    shutil.copytree(utils.CommonDirPaths.REPO_DIR_NAME, utils.CommonDirPaths.BUILD_DIR_NAME)

    os.chdir(utils.CommonDirPaths.BUILD_DIR_NAME)

    utils.execute_system_command(f"ucc-gen build --ta-version {app_version}")

    os.chdir(utils.CommonDirPaths.MAIN_DIR)

    shutil.copytree(os.path.join(utils.CommonDirPaths.BUILD_DIR_NAME, 'output', app_package_id), utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)

    return utils.CommonDirPaths.BUILD_FINAL_DIR_NAME, os.path.join(utils.CommonDirPaths.MAIN_DIR, utils.CommonDirPaths.BUILD_FINAL_DIR_NAME)