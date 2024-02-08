
import os
import shutil
import json

import helper_github_action as utils


class SplunkAppBuildWithUCC:

    def __init__(self) -> None:
        os.chdir(utils.CommonDirPaths.MAIN_DIR)

        self.app_package_id = self._fetch_app_package_id()
        utils.set_env('app_package_id', self.app_package_id)

        self.app_version = self._fetch_app_version()
        utils.set_env('app_version', self.app_version)


    def _fetch_app_package_id(self):
        utils.info("Fetching app package id from globalConfig.json file.")

        _app_package_id = None

        with open(os.path.join(utils.CommonDirPaths.REPO_DIR, 'globalConfig.json'), 'r') as f:
            global_config = json.loads(f.read())

            _app_package_id = global_config["meta"]["name"]

        if not _app_package_id:
            raise Exception("Unable to fetch the app package id from globalConfig.json file")

        return _app_package_id


    def _fetch_app_version(self):
        utils.info("Fetching app version number from globalConfig.json file.")

        _app_version = None

        with open(os.path.join(utils.CommonDirPaths.REPO_DIR, 'globalConfig.json'), 'r') as f:
            global_config = json.loads(f.read())

            _app_version = global_config["meta"]["version"]

        if not _app_version:
            raise Exception("Unable to fetch the app package id from globalConfig.json file")

        return _app_version


    def build(self):
        utils.info("Running ucc-gen command.")

        # copy folder to generate build, rather than affecting the original repo checkout
        utils.execute_system_command(f"rm -rf {utils.CommonDirPaths.UCC_DIR_NAME}")
        shutil.copytree(utils.CommonDirPaths.REPO_DIR_NAME, utils.CommonDirPaths.UCC_DIR_NAME)

        os.chdir(utils.CommonDirPaths.UCC_DIR_NAME)

        utils.execute_system_command(f"ucc-gen build --ta-version {self.app_version}")

        os.chdir(utils.CommonDirPaths.MAIN_DIR)

        shutil.copytree(os.path.join(utils.CommonDirPaths.UCC_DIR_NAME, 'output', self.app_package_id), 'ucc_gen_ta')

        return 'ucc_gen_ta', self.app_package_id