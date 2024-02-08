
import os
import shutil

import helper_github_action as utils
from helper_splunk_config_parser import SplunkConfigParser


def fetch_app_package_id(app_dir_path, app_dir_input):
    utils.info("Fetching app package id. from app.conf file.")

    config = SplunkConfigParser(os.path.join(app_dir_path, 'default', 'app.conf'))
    # utils.info("app.conf sections: {}".format(config.sections()))
    if 'package' in config and 'id' in config['package']:
        utils.info(
            "Using app package id found in app.conf - {}".format(config['package']['id']))
        return config['package']['id']
    elif app_dir_input == ".":
        utils.error(
            "It is recommended to have `id` attribute in the app.conf's [package] stanza.")
        raise Exception(
            "Add `id` attribute in the app.conf's [package] stanza.")
    else:
        return app_dir_input


def remove_git_folders():
    utils.info("Removing .git and .github directory from repo.")
    utils.execute_system_command("rm -rf .github")
    utils.execute_system_command("rm -rf .git")
    utils.execute_system_command("rm -rf .gitignore")


def util_generate_build_commands(app_package_id):
    to_make_permission_changes = utils.str_to_boolean(
            utils.get_input("to_make_permission_changes"))

    if to_make_permission_changes:
        # Permission Changes
        utils.execute_system_command(
            "find {} -type f -exec chmod 644 '{{}}' \;".format(app_package_id))
        utils.execute_system_command(
            "find {} -type f -name *.sh -exec chmod 755 '{{}}' \;".format(app_package_id))
        utils.execute_system_command(
            "find {} -type d -exec chmod 755 '{{}}' \;".format(app_package_id))

    # Generate Build
    utils.execute_system_command(
        "tar -czf {}.tgz {}".format(app_package_id, app_package_id))


def run_custom_user_defined_commands():
    utils.info("Executing custom user defined commands.")
    for no in range(1, 100):
        try:
            cmd = utils.get_input(f"APP_ACTION_{no}")
            if cmd:
                utils.execute_system_command(cmd)
        except Exception as e:
            utils.warning("Error ")


def generate_build(app_package_id, app_build_dir_name, app_build_dir_path):
    utils.info(f"Generating the app build., app_dir_path={app_build_dir_path}, app_package_id={app_package_id}")

    is_generate_build = utils.str_to_boolean(
        utils.get_input('is_generate_build'))
    utils.info("is_generate_build: {}".format(is_generate_build))

    direct_app_build_path = utils.get_input('app_build_path')
    utils.info("app_build_path: {}".format(direct_app_build_path))

    if not is_generate_build:
        return direct_app_build_path
    
    os.chdir(utils.CommonDirPaths.MAIN_DIR)
    os.chdir(app_build_dir_path)

    remove_git_folders()
    run_custom_user_defined_commands()

    os.chdir(utils.CommonDirPaths.MAIN_DIR)
    utils.execute_system_command(
            f'mv {app_build_dir_name} {app_package_id}')

    util_generate_build_commands(app_package_id)

    return '{}.tgz'.format(app_package_id)
