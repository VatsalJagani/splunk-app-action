
import os
import shutil

import helper_github_action as utils
from helper_splunk_config_parser import SplunkConfigParser


class SplunkAppBuildGenerator:

    def __init__(self) -> None:
        self.is_generate_build = utils.str_to_boolean(
            utils.get_input('is_generate_build'))
        utils.info("is_generate_build: {}".format(self.is_generate_build))

        self.app_dir = utils.get_input('app_dir')
        utils.info("app_dir: {}".format(self.app_dir))

        self.direct_app_build_path = utils.get_input('app_build_path')
        utils.info("app_build_path: {}".format(self.direct_app_build_path))

        self.app_package_id = self._fetch_app_package_id()
        utils.set_env('app_package_id', self.app_package_id)

        os.chdir(utils.CommonDirPaths.MAIN_DIR)


    def _fetch_app_package_id(self):
        utils.info("Fetching app package id. from app.conf file.")

        config = SplunkConfigParser(os.path.join(
            'repodir', self.app_dir, 'default', 'app.conf'))
        utils.info("app.conf sections: {}".format(config.sections()))
        if 'package' in config and 'id' in config['package']:
            utils.info(
                "Using app package id found in app.conf - {}".format(config['package']['id']))
            return config['package']['id']
        elif self.app_dir == ".":
            utils.error(
                "It is recommended to have `id` attribute in the app.conf's [package] stanza.")
            raise Exception(
                "Add `id` attribute in the app.conf's [package] stanza.")
        else:
            return self.app_dir


    def _remove_git_folders(self):
        utils.info("Removing .git and .github directory from repo.")
        os.system('rm -rf repodir_for_build/.github')
        os.system('rm -rf repodir_for_build/.git')


    def _util_generate_build_commands(self):
        os.system(
            "find {} -type f -exec chmod 644 '{{}}' \;".format(self.app_package_id))
        os.system(
            "find {} -type d -exec chmod 755 '{{}}' \;".format(self.app_package_id))
        os.system(
            "tar -czf {}.tgz {}".format(self.app_package_id, self.app_package_id))


    def generate(self):
        utils.info("Generating the app build. app_dir={}, app_package_id={}".format(
            self.app_dir, self.app_package_id))

        if not self.is_generate_build:
            return self.direct_app_build_path, self.app_package_id

        # copy folder to generate build, rather than affecting the original repo checkout
        shutil.copytree('repodir', 'repodir_for_build')

        self._remove_git_folders()

        if self.app_dir == '.':
            os.system('mv repodir_for_build {}'.format(self.app_package_id))
            self._util_generate_build_commands()
        else:
            os.chdir('repodir_for_build')

            if self.app_dir != self.app_package_id:
                os.system('mv {} {}'.format(self.app_dir, self.app_package_id))

            self._util_generate_build_commands()
            os.system('mv {}.tgz ..'.format(self.app_package_id))

            os.chdir('..')

        return '{}.tgz'.format(self.app_package_id), self.app_package_id
