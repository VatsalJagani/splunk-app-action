
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
            "find . -type f -exec chmod 644 '{}' \\;")

        for file_ext in [".sh", ".exe", ".cmd", ".msi", ".bat"]:
            utils.execute_system_command(
                f"find . -type f -name '*{file_ext}' -exec chmod 755 '{{}}' \\;")

        utils.execute_system_command(
            "find . -type d -exec chmod 755 '{}' \\;")


def run_custom_user_defined_commands():
    utils.info("Executing custom user defined commands.")
    for no in range(1, 100):
        try:
            cmd = utils.get_input(f"APP_ACTION_{no}")
            if cmd:
                utils.execute_system_command(cmd)
        except Exception as e:
            utils.warning(f"Error - {e}")


def generate_build(app_build_dir_name, app_build_dir_path):
    utils.info(f"Generating the app build., app_dir_path={app_build_dir_path}, app_package_id={GlobalVariables.APP_PACKAGE_ID}, app_version_encoded={GlobalVariables.APP_VERSION_ENCODED}, app_build_number_encoded={GlobalVariables.APP_BUILD_NUMBER_ENCODED}")

    os.chdir(GlobalVariables.ROOT_DIR_PATH)
    utils.execute_system_command(
            f'mv {app_build_dir_name} {GlobalVariables.APP_PACKAGE_ID}')

    os.chdir(GlobalVariables.APP_PACKAGE_ID)
    remove_unwanted_files()
    run_custom_user_defined_commands()
    file_folder_permission_changes()
    os.chdir(GlobalVariables.ROOT_DIR_PATH)

    # Generate Build
    build_name = f"{GlobalVariables.APP_PACKAGE_ID}_{GlobalVariables.APP_VERSION_ENCODED}_{GlobalVariables.APP_BUILD_NUMBER_ENCODED}.tgz"
    utils.execute_system_command(f"tar -czf {build_name} {GlobalVariables.APP_PACKAGE_ID}")
    return os.path.join(GlobalVariables.ROOT_DIR_PATH, build_name)
