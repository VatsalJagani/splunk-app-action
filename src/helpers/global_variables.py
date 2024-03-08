import os
import re


class GlobalVariables:
    ROOT_DIR_PATH = None

    ORIGINAL_REPO_DIR_NAME = None
    ORIGINAL_REPO_DIR_PATH = None

    APP_DIR_NAME = None
    ORIGINAL_APP_DIR_PATH = None

    APP_PACKAGE_ID = None
    APP_VERSION = None
    APP_VERSION_ENCODED = None
    APP_BUILD_NUMBER = None
    APP_BUILD_NUMBER_ENCODED = None


    @staticmethod
    def initiate(app_dir_name, repodir_name=None, root_dir_path=None) -> None:
        GlobalVariables.ROOT_DIR_PATH = root_dir_path if root_dir_path else os.getcwd()

        GlobalVariables.ORIGINAL_REPO_DIR_NAME = repodir_name if repodir_name else "repodir"
        GlobalVariables.ORIGINAL_REPO_DIR_PATH = os.path.join(GlobalVariables.ROOT_DIR_PATH, GlobalVariables.ORIGINAL_REPO_DIR_NAME)

        GlobalVariables.APP_DIR_NAME = app_dir_name
        GlobalVariables.ORIGINAL_APP_DIR_PATH = os.path.join(GlobalVariables.ORIGINAL_REPO_DIR_PATH, GlobalVariables.APP_DIR_NAME)


    @staticmethod
    def set_app_package_id(app_package_id) -> None:
        GlobalVariables.APP_PACKAGE_ID = app_package_id

    @staticmethod
    def set_app_version(version) -> None:
        GlobalVariables.APP_VERSION = version
        GlobalVariables.APP_VERSION_ENCODED = re.sub('[^0-9a-zA-Z]+', '_', version)

    @staticmethod
    def set_app_build_number(build_number) -> None:
        GlobalVariables.APP_BUILD_NUMBER = build_number
        GlobalVariables.APP_BUILD_NUMBER_ENCODED = re.sub('[^0-9a-zA-Z]+', '_', build_number)
