
import os
import shutil
import json

import helper_github_action as utils


class SplunkAppBuildWithUCC:

    def __init__(self) -> None:
        self.use_ucc_gen = utils.str_to_boolean(
            utils.get_input('use_ucc_gen'))
        utils.info("use_ucc_gen: {}".format(self.use_ucc_gen))


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
        if not self.use_ucc_gen:
            return None, None

        utils.info("Running ucc-gen command.")
        os.chdir(utils.CommonDirPaths.MAIN_DIR)

        self.app_package_id = self._fetch_app_package_id()
        utils.set_env('app_package_id', self.app_package_id)

        self.app_version = self._fetch_app_version()
        utils.set_env('app_version', self.app_version)

        # copy folder to generate build, rather than affecting the original repo checkout
        utils.execute_system_command("rm -rf repodir_for_ucc")
        shutil.copytree('repodir', 'repodir_for_ucc')

        os.chdir('repodir_for_ucc')

        utils.execute_system_command(f"ucc-gen build --ta-version {self.app_version}")

        os.chdir(utils.CommonDirPaths.MAIN_DIR)
        shutil.copytree(os.path.join('repodir_for_ucc', 'output', self.app_package_id), 'ucc_gen_ta')

        return 'ucc_gen_ta', self.app_package_id