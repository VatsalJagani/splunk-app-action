
import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)

from helpers.global_variables import GlobalVariables

def test_initiate_valid_args():
    # Set up
    app_dir_name = "my_app"
    repodir_name = "custom_repo"
    root_dir_path = "/path/to/project"

    # Call the method
    GlobalVariables.initiate(app_dir_name, repodir_name, root_dir_path)

    # Assertions
    assert GlobalVariables.ROOT_DIR_PATH == root_dir_path
    assert GlobalVariables.ORIGINAL_REPO_DIR_NAME == repodir_name
    assert GlobalVariables.ORIGINAL_REPO_DIR_PATH == os.path.join(root_dir_path, repodir_name)
    assert GlobalVariables.APP_DIR_NAME == app_dir_name
    assert GlobalVariables.ORIGINAL_APP_DIR_PATH == os.path.join(GlobalVariables.ORIGINAL_REPO_DIR_PATH, app_dir_name)

    # Cleanup (optional, reset variables)
    GlobalVariables.ROOT_DIR_PATH = None
    GlobalVariables.ORIGINAL_REPO_DIR_NAME = None
    GlobalVariables.ORIGINAL_REPO_DIR_PATH = None
    GlobalVariables.APP_DIR_NAME = None
    GlobalVariables.ORIGINAL_APP_DIR_PATH = None

def test_initiate_missing_args():
    # Set up
    app_dir_name = "my_app"

    # Call the method
    GlobalVariables.initiate(app_dir_name)

    # Assertions (using os.getcwd() for current working directory)
    assert GlobalVariables.ROOT_DIR_PATH == os.getcwd()
    assert GlobalVariables.ORIGINAL_REPO_DIR_NAME == "repodir"
    assert GlobalVariables.ORIGINAL_REPO_DIR_PATH == os.path.join(GlobalVariables.ROOT_DIR_PATH, "repodir")
    assert GlobalVariables.APP_DIR_NAME == app_dir_name
    assert GlobalVariables.ORIGINAL_APP_DIR_PATH == os.path.join(GlobalVariables.ORIGINAL_REPO_DIR_PATH, app_dir_name)

    # Cleanup (optional, reset variables)
    GlobalVariables.ROOT_DIR_PATH = None
    GlobalVariables.ORIGINAL_REPO_DIR_NAME = None
    GlobalVariables.ORIGINAL_REPO_DIR_PATH = None
    GlobalVariables.APP_DIR_NAME = None
    GlobalVariables.ORIGINAL_APP_DIR_PATH = None

def test_set_app_package_id():
    package_id = "my_app_id"
    GlobalVariables.set_app_package_id(package_id)
    assert GlobalVariables.APP_PACKAGE_ID == package_id

def test_set_app_version():
    version = "1.2.3"
    GlobalVariables.set_app_version(version)
    assert GlobalVariables.APP_VERSION == version
    assert GlobalVariables.APP_VERSION_ENCODED == "1_2_3"  # Encoded version

    # Cleanup (optional, reset variables)
    GlobalVariables.APP_VERSION = None
    GlobalVariables.APP_VERSION_ENCODED = None

def test_set_app_build_number():
    build_number = "456"
    GlobalVariables.set_app_build_number(build_number)
    assert GlobalVariables.APP_BUILD_NUMBER == build_number
    assert GlobalVariables.APP_BUILD_NUMBER_ENCODED == "456"  # Encoded build number

    # Cleanup (optional, reset variables)
    GlobalVariables.APP_BUILD_NUMBER = None
    GlobalVariables.APP_BUILD_NUMBER_ENCODED = None
