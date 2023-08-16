
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

        self.to_make_permission_changes = utils.str_to_boolean(
            utils.get_input("to_make_permission_changes"))
        utils.set_env('to_make_permission_changes',
                      self.to_make_permission_changes)

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
        utils.execute_system_command('rm -rf repodir_for_build/.github')
        utils.execute_system_command('rm -rf repodir_for_build/.git')


    def _util_generate_build_commands(self):
        if self.to_make_permission_changes:
            # Permission Changes
            utils.execute_system_command(
                "find {} -type f -exec chmod 644 '{{}}' \;".format(self.app_package_id))
            utils.execute_system_command(
                "find {} -type f -name *.sh -exec chmod 755 '{{}}' \;".format(self.app_package_id))
            utils.execute_system_command(
                "find {} -type d -exec chmod 755 '{{}}' \;".format(self.app_package_id))

        # Generate Build
        utils.execute_system_command(
            "tar -czf {}.tgz {}".format(self.app_package_id, self.app_package_id))


    def run_custom_user_defined_commands(self):
        utils.info("Executing custom user defined commands.")
        for no in range(1, 100):
            try:
                cmd = utils.get_input(f"APP_ACTION_{no}")
                if cmd:
                    utils.execute_system_command(cmd)
            except Exception as e:
                utils.warning("Error ")


    def generate(self):
        utils.info("Generating the app build. app_dir={}, app_package_id={}".format(
            self.app_dir, self.app_package_id))

        if not self.is_generate_build:
            return self.direct_app_build_path, self.app_package_id

        # copy folder to generate build, rather than affecting the original repo checkout
        utils.execute_system_command("rm -rf repodir_for_build")
        shutil.copytree('repodir', 'repodir_for_build')

        self._remove_git_folders()

        if self.app_dir == '.':
            os.chdir('repodir_for_build')
            self.run_custom_user_defined_commands()
            os.chdir("..")

            utils.execute_system_command(
                'mv repodir_for_build {}'.format(self.app_package_id))
            self._util_generate_build_commands()
        else:
            os.chdir('repodir_for_build')
            self.run_custom_user_defined_commands()

            if self.app_dir != self.app_package_id:
                utils.execute_system_command(
                    'mv {} {}'.format(self.app_dir, self.app_package_id))

            self._util_generate_build_commands()
            utils.execute_system_command(
                'mv {}.tgz ..'.format(self.app_package_id))

            os.chdir('..')

        return '{}.tgz'.format(self.app_package_id), self.app_package_id
