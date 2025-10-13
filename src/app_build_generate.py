import os

import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths


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
            cmd = os.environ.get(f"SPLUNK_APP_ACTION_{no}")
            if cmd:
                os.system(cmd)
        except Exception as e:
            gat.warning(f"Error - {e}")


def generate_build(
    saved_paths: SavedPaths, app_info: AppInfo, app_build_dir_name, app_build_dir_path
):
    gat.info(
        f"Generating the app build., app_dir_path={app_build_dir_path}, app_package_id={app_info.package_id}, app_version_encoded={app_info.version_number_encoded}, app_build_number_encoded={app_info.build_number_encoded}"
    )
    os.system(f"mv {app_build_dir_name} {app_info.package_id}")
    os.chdir(app_info.package_id)
    remove_unwanted_files()
    run_custom_user_defined_commands()
    file_folder_permission_changes()
    os.chdir(saved_paths.root_dir_path)

    # Generate Build
    build_name = f"{app_info.package_id}_{app_info.version_number_encoded}_{app_info.build_number_encoded}.tgz"
    os.system(f"tar -czf {build_name} {app_info.package_id}")
    return os.path.join(saved_paths.root_dir_path, build_name)
