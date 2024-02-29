
import os

import helpers.github_action_utils as utils
from helpers.global_variables import GlobalVariables



def remove_unwanted_files():
    utils.info("Removing .git and .github directory from repo.")
    utils.execute_system_command("rm -rf .github")
    utils.execute_system_command("rm -rf .git")
    utils.execute_system_command("rm -rf .gitignore")
    utils.execute_system_command('find . -name "*.py[co]" -type f -delete')
    utils.execute_system_command('find . -name "__pycache__" -type d -delete')


def file_folder_permission_changes():
    to_make_permission_changes = utils.str_to_boolean_default_false(
            utils.get_input("to_make_permission_changes"))

    if to_make_permission_changes:
        # Permission Changes
        utils.execute_system_command(
            "find . -type f -exec chmod 644 '{}' \;")

        for file_ext in [".sh", ".exe", ".cmd", ".msi", ".bat"]:
            utils.execute_system_command(
                "find . -type f -name '*{}' -exec chmod 755 '{}' \;".format(file_ext))

        utils.execute_system_command(
            "find . -type d -exec chmod 755 '{}' \;")


def run_custom_user_defined_commands():
    utils.info("Executing custom user defined commands.")
    for no in range(1, 100):
        try:
            cmd = utils.get_input(f"APP_ACTION_{no}")
            if cmd:
                utils.execute_system_command(cmd)
        except Exception as e:
            utils.warning("Error ")


def generate_build(app_build_dir_name, app_build_dir_path):
    utils.info(f"Generating the app build., app_dir_path={app_build_dir_path}, app_package_id={GlobalVariables.APP_PACKAGE_ID}, app_version_encoded={GlobalVariables.APP_VERSION_ENCODED}, app_build_number_encoded={GlobalVariables.APP_BUILD_NUMBER_ENCODED}")

    is_generate_build = utils.str_to_boolean_default_true(
        utils.get_input('is_generate_build'))
    utils.info("is_generate_build: {}".format(is_generate_build))

    direct_app_build_path = utils.get_input('app_build_path')
    utils.info("app_build_path: {}".format(direct_app_build_path))

    if not is_generate_build:
        return direct_app_build_path

    os.chdir(GlobalVariables.ROOT_DIR_PATH)
    utils.execute_system_command(
            f'mv {app_build_dir_name} {GlobalVariables.APP_PACKAGE_ID}')
    os.chdir(GlobalVariables.APP_PACKAGE_ID)

    remove_unwanted_files()
    run_custom_user_defined_commands()
    file_folder_permission_changes()

    # Generate Build
    build_name = f"{GlobalVariables.APP_PACKAGE_ID}_{GlobalVariables.APP_VERSION_ENCODED}_{GlobalVariables.APP_BUILD_NUMBER_ENCODED}.tgz"
    utils.execute_system_command(f"tar -czf {build_name} {GlobalVariables.APP_PACKAGE_ID}")
    return os.path.join(GlobalVariables.ROOT_DIR_PATH, build_name)
