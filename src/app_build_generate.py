
import os
import traceback

import helper_github_action as utils
from helper_splunk_config_parser import SplunkConfigParser


class SplunkAppBuildGenerator:

    def __init__(self) -> None:
        self.app_dir = utils.get_input('app_dir')
        utils.info("app_dir: {}".format(self.app_dir))

        self.direct_app_build_path = utils.get_input('app_build_path')
        utils.info("app_build_path: {}".format(self.direct_app_build_path))

        self.app_package_id = self._fetch_app_package_id()
        utils.set_env('app_package_id', self.app_package_id)

        # TODO - ensure that you are in a right folder to execute the code


    def _fetch_app_package_id(self):
        utils.info("Fetching app package id. from app.conf file.")

        config = SplunkConfigParser(os.path.join('repodir', self.app_dir, 'default', 'app.conf'))
        utils.info("app.conf sections: {}".format(config.sections()))
        if 'package' in config and 'id' in config['package']:
            utils.info("Using app package id found in app.conf - {}".format(config['package']['id']))
            return config['package']['id']
        elif self.app_dir == ".":
            utils.error("It is recommended to have `id` attribute in the app.conf's [package] stanza.")
            raise Exception("Add `id` attribute in the app.conf's [package] stanza.")
        else:
            return self.app_dir

        # TODO - If the repo root folder is App's root folder then app.conf has to have [package] id parameter.
        # TODO - Do not do exception handling here, handle it at main.py file

        # TODO - Use app package id before folder name from Repo


    def _remove_git_folders(self):
        utils.info("Removing .git and .github directory from repo.")
        os.system('rm -rf repodir/.github')
        os.system('rm -rf repodir/.git')


    def generate(self):
        utils.info("Generating the app build. app_dir={}, app_package_id={}".format(self.app_dir, self.app_package_id))

        # TODO - ensure that you are in a right directory
        # utils.list_files(os.getcwd())

        if self.direct_app_build_path and self.direct_app_build_path != "NONE":
            return self.direct_app_build_path, self.app_package_id

        self._remove_git_folders()

        if self.app_dir == '.':
            os.system('mv repodir {}'.format(self.app_package_id))
            os.system("find {} -type f -exec chmod 644 '{{}}' \;".format(self.app_package_id))
            os.system("find {} -type d -exec chmod 755 '{{}}' \;".format(self.app_package_id))
            os.system("tar -czf {}.tgz {}".format(self.app_package_id, self.app_package_id))
        else:
            os.chdir('repodir')

            utils.info("updated cwd={}".format(os.getcwd()))
            # utils.list_files(os.getcwd())
            
            if self.app_dir != self.app_package_id:
                os.system('mv {} {}'.format(self.app_dir, self.app_package_id))
            
            os.system("find {} -type f -exec chmod 644 '{{}}' \;".format(self.app_package_id))
            os.system("find {} -type d -exec chmod 755 '{{}}' \;".format(self.app_package_id))
            os.system("tar -czf {}.tgz {}".format(self.app_package_id, self.app_package_id))
            os.system('mv {}.tgz ..'.format(self.app_package_id))

            os.chdir('..')

        utils.info("final cwd={}".format(os.getcwd()))
        utils.list_files(os.getcwd())

        return '{}.tgz'.format(self.app_package_id), self.app_package_id

