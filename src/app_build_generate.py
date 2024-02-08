
import os
import shutil

import helper_github_action as utils
from helper_splunk_config_parser import SplunkConfigParser


def _read_app_conf(app_dir_path):
    return SplunkConfigParser(os.path.join(app_dir_path, 'default', 'app.conf'))


def fetch_app_package_id(app_dir_path, app_dir_input):
    app_config = _read_app_conf(app_dir_path)
    if 'package' in app_config and 'id' in app_config['package']:
        utils.info(
            "Using app package id found in app.conf - {}".format(app_config['package']['id']))
        return app_config['package']['id']
    elif app_dir_input == ".":
        utils.error(
            "It is recommended to have `id` attribute in the app.conf's [package] stanza.")
        raise Exception(
            "Add `id` attribute in the app.conf's [package] stanza.")
    else:
        return app_dir_input


def fetch_app_version_number(app_dir_path):
    app_config = _read_app_conf(app_dir_path)
    if 'launcher' in app_config and 'version' in app_config['launcher']:
        utils.info(
            "Using app version number found in app.conf [launcher] - {}".format(app_config['launcher']['version']))
        return app_config['launcher']['version']
    elif 'id' in app_config and 'version' in app_config['id']:
        utils.info(
            "Using app version number found in app.conf [id] - {}".format(app_config['id']['version']))
        return app_config['id']['version']
    else:
        utils.error(
            "It is recommended to have `version` attribute in the app.conf's [launcher] stanza.")
        raise Exception(
            "Add `id` attribute in the app.conf's [launcher] stanza.")


def fetch_app_build_number(app_dir_path):
    app_config = _read_app_conf(app_dir_path)
    if 'install' in app_config and 'build' in app_config['install']:
        utils.info(
            "Using app build number found in app.conf [install] - {}".format(app_config['install']['build']))
        return app_config['install']['build']
    else:
        utils.info("No app build number found, defaulting to 1.")
        return "1"


def remove_git_folders():
    utils.info("Removing .git and .github directory from repo.")
    utils.execute_system_command("rm -rf .github")
    utils.execute_system_command("rm -rf .git")
    utils.execute_system_command("rm -rf .gitignore")


def util_generate_build_commands(app_package_id, app_version_encoded, app_build_number_encoded):
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
    build_name = f"{app_package_id}_{app_version_encoded}_{app_build_number_encoded}.tgz"
    utils.execute_system_command(f"tar -czf {build_name} {app_package_id}")
    return build_name


def run_custom_user_defined_commands():
    utils.info("Executing custom user defined commands.")
    for no in range(1, 100):
        try:
            cmd = utils.get_input(f"APP_ACTION_{no}")
            if cmd:
                utils.execute_system_command(cmd)
        except Exception as e:
            utils.warning("Error ")


def generate_build(app_package_id, app_build_dir_name, app_build_dir_path, app_version_encoded, app_build_number_encoded):
    utils.info(f"Generating the app build., app_dir_path={app_build_dir_path}, app_package_id={app_package_id}, app_version_encoded={app_version_encoded}, app_build_number_encoded={app_build_number_encoded}")

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

    build_name = util_generate_build_commands(app_package_id, app_version_encoded, app_build_number_encoded)

    return build_name
