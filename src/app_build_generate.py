
import os
import traceback

import helper_github_action as utils
from helper_splunk import SplunkConfigParser


class SplunkAppBuildGenerator:
    def __init__(self) -> None:
        self.app_dir = utils.get_input('app_dir')
        utils.info("app_dir: {}".format(self.app_dir))

        self.app_build_name = utils.get_input('app_build_name')
        utils.info("app_build_name: {}".format(self.app_build_name))

        self.direct_app_build_path = utils.get_input('app_build_path')
        utils.info("app_build_path: {}".format(self.direct_app_build_path))

        app_package_id_input = utils.get_input('app_package_id')
        utils.info("app_package_id: {}".format(app_package_id_input))
        self.app_package_id = self._fetch_app_package_id(app_package_id_input)

        # TODO - ensure that you are in a right folder to execute the code


    def _fetch_app_package_id(self, app_package_id_input):
        utils.info("Fetching app package id. from app.conf file.")
        if app_package_id_input != "NONE":
            utils.info("Using app package id provided by user - {}".format(app_package_id_input))
            return app_package_id_input
        try:
            config = SplunkConfigParser()
            config.read(os.path.join('repodir', self.app_dir, 'default', 'app.conf'))
            utils.info("app.conf sections: {}".format(config.sections()))
            if 'package' in config and 'id' in config['package']:
                utils.info("Using app package id found in app.conf - {}".format(config['package']['id']))
                return config['package']['id']
            else:
                utils.error("It is recommended to have id attribute in the app.conf's [package] stanza.")
                utils.info("Using app_build_name as app package id - {}".format(self.app_build_name))
                return self.app_build_name
        except Exception as e:
            utils.error("Unable to fetch the app-package-id from app.conf. {}".format(e))
            utils.error(traceback.format_exc())
            utils.info("Using app_build_name as app package id - {}".format(self.app_build_name))
            return self.app_build_name


    def _remove_git_folders(self):
        utils.info("Removing .git and .github directory from repo.")
        os.system('rm -rf repodir/.github')
        os.system('rm -rf repodir/.git')


    def generate(self):
        utils.info("Generating the app build. app_dir={}, app_package_id={}".format(self.app_dir, self.app_package_id))

        # TODO - ensure that you are in a right directory
        # utils.list_files(os.getcwd())

        if self.direct_app_build_path and self.direct_app_build_path != "NONE":
            return self.direct_app_build_path

        self._remove_git_folders()

        if self.app_dir == '.':
            os.system('mv repodir {}'.format(self.app_package_id))
            os.system("find {} -type f -exec chmod 644 '{{}}' \;".format(self.app_package_id))
            os.system("find {} -type d -exec chmod 755 '{{}}' \;".format(self.app_package_id))
            os.system("tar -czf {}.tgz {}".format(self.app_build_name, self.app_package_id))
        else:
            os.chdir('repodir')

            utils.info("updated cwd={}".format(os.getcwd()))
            # utils.list_files(os.getcwd())
            
            if self.app_dir != self.app_package_id:
                os.system('mv {} {}'.format(self.app_dir, self.app_package_id))
            
            os.system("find {} -type f -exec chmod 644 '{{}}' \;".format(self.app_package_id))
            os.system("find {} -type d -exec chmod 755 '{{}}' \;".format(self.app_package_id))
            os.system("tar -czf {}.tgz {}".format(self.app_build_name, self.app_package_id))
            os.system('mv {}.tgz ..'.format(self.app_build_name))

            os.chdir('..')

        utils.info("final cwd={}".format(os.getcwd()))
        utils.list_files(os.getcwd())

        return '{}.tgz'.format(self.app_build_name)

