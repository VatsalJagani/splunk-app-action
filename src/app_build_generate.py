import os

import github_action_toolkit as gat

from helpers.global_variables import GlobalVariables


def remove_unwanted_files():
    gat.info("Removing .git and .github directory from repo.")
    os.system("rm -rf .github")
    os.system("rm -rf .git")
    os.system("rm -rf .gitignore")
    os.system('find . -name "*.py[co]" -type f -delete')
    os.system('find . -name "__pycache__" -type d -delete')


def file_folder_permission_changes():
    to_make_permission_changes = gat.get_user_input_as("to_make_permission_changes", bool, False)

    if to_make_permission_changes:
        # Permission Changes
        os.system("find . -type f -exec chmod 644 '{}' \\;")

        for file_ext in [".sh", ".exe", ".cmd", ".msi", ".bat"]:
            os.system(f"find . -type f -name '*{file_ext}' -exec chmod 755 '{{}}' \\;")

        os.system("find . -type d -exec chmod 755 '{}' \\;")


def run_custom_user_defined_commands():
    gat.info("Executing custom user defined commands.")
    for no in range(1, 100):
        try:
            cmd = gat.get_user_input(f"APP_ACTION_{no}")
            if cmd:
                os.system(cmd)
        except Exception as e:
            gat.warning(f"Error - {e}")


def generate_build(app_build_dir_name, app_build_dir_path):
    gat.info(
        f"Generating the app build., app_dir_path={app_build_dir_path}, app_package_id={GlobalVariables.APP_PACKAGE_ID}, app_version_encoded={GlobalVariables.APP_VERSION_ENCODED}, app_build_number_encoded={GlobalVariables.APP_BUILD_NUMBER_ENCODED}"
    )

    os.chdir(GlobalVariables.ROOT_DIR_PATH)
    os.system(f"mv {app_build_dir_name} {GlobalVariables.APP_PACKAGE_ID}")

    os.chdir(GlobalVariables.APP_PACKAGE_ID)
    remove_unwanted_files()
    run_custom_user_defined_commands()
    file_folder_permission_changes()
    os.chdir(GlobalVariables.ROOT_DIR_PATH)

    # Generate Build
    build_name = f"{GlobalVariables.APP_PACKAGE_ID}_{GlobalVariables.APP_VERSION_ENCODED}_{GlobalVariables.APP_BUILD_NUMBER_ENCODED}.tgz"
    os.system(f"tar -czf {build_name} {GlobalVariables.APP_PACKAGE_ID}")
    return os.path.join(GlobalVariables.ROOT_DIR_PATH, build_name)
