# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false

import io
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager


@contextmanager
def setup_action_yml(
    test_app_repo,
    app_dir=".",
    use_ucc_gen="false",
    to_make_permission_changes="false",
    is_app_inspect_check="true",
    splunkbase_username="NONE",
    splunkbase_password="NONE",
    app_utilities="",
    my_github_token="NONE",
    current_branch="NONE",
    logger_log_files_prefix="NONE",
    logger_sourcetype="NONE",
    splunk_python_sdk_install_path="bin",
    is_remove_pyc_from_splunklib_dir="true",
):
    print("Test Setup Steps")
    repo_root_dir_path = os.getcwd()
    temp_dir_for_test = "temp_for_test"
    temp_dir_for_test_path = os.path.join(repo_root_dir_path, temp_dir_for_test)
    repo_dir_path = os.path.join(temp_dir_for_test_path, "repodir")

    try:
        shutil.rmtree(temp_dir_for_test_path)
    except:
        pass
    try:
        os.mkdir(temp_dir_for_test_path)
    except:
        pass

    app_repo_path = os.path.join(os.path.dirname(__file__), "app_repos_for_test", test_app_repo)
    shutil.copytree(app_repo_path, repo_dir_path)

    os.chdir(temp_dir_for_test_path)

    # setup inputs
    os.environ["INPUT_APP_DIR"] = app_dir
    os.environ["INPUT_USE_UCC_GEN"] = use_ucc_gen
    os.environ["INPUT_TO_MAKE_PERMISSION_CHANGES"] = to_make_permission_changes
    os.environ["INPUT_IS_APP_INSPECT_CHECK"] = is_app_inspect_check
    os.environ["INPUT_SPLUNKBASE_USERNAME"] = splunkbase_username
    os.environ["INPUT_SPLUNKBASE_PASSWORD"] = splunkbase_password
    os.environ["INPUT_APP_UTILITIES"] = app_utilities
    os.environ["GITHUB_TOKEN"] = my_github_token
    os.environ["INPUT_CURRENT_BRANCH_NAME"] = current_branch
    os.environ["INPUT_LOGGER_LOG_FILES_PREFIX"] = logger_log_files_prefix
    os.environ["INPUT_LOGGER_SOURCETYPE"] = logger_sourcetype
    os.environ["INPUT_SPLUNK_PYTHON_SDK_INSTALL_PATH"] = splunk_python_sdk_install_path
    os.environ["INPUT_IS_REMOVE_PYC_FROM_SPLUNKLIB_DIR"] = is_remove_pyc_from_splunklib_dir

    try:
        yield
    finally:
        print("Test Cleanup after each test-case.")
        try:
            shutil.rmtree(temp_dir_for_test_path)
        except:
            pass
        os.chdir(repo_root_dir_path)


@contextmanager
def get_temp_directory():
    temp_dir = os.path.join(os.path.dirname(__file__), "tempdir")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    try:
        yield temp_dir
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@contextmanager
def get_temp_git_repo(current_branch="my_current_branch"):
    temp_dir = os.path.join(os.path.dirname(__file__), "temprepo")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    original_pwd = os.getcwd()

    os.chdir(temp_dir)

    os.environ["GITHUB_TOKEN"] = "this_is_my_github_token"
    os.environ["INPUT_CURRENT_BRANCH_NAME"] = current_branch

    # Initialize a git repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)

    # Create some initial files and commit them
    with open("file1.txt", "w") as f:
        f.write("Initial content")
    subprocess.run(["git", "add", "file1.txt"], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

    # Create a branch
    subprocess.run(["git", "checkout", "-b", current_branch], check=True)

    try:
        yield temp_dir
    finally:
        del os.environ["GITHUB_TOKEN"]
        del os.environ["INPUT_CURRENT_BRANCH_NAME"]

        os.chdir(original_pwd)  # go back to original directory

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@contextmanager
def stdout_capture():
    # Redirect stdout to a StringIO object
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        yield captured_output
    finally:
        # Reset stdout to its original value
        sys.stdout = sys.__stdout__


@contextmanager
def setup_temporary_env_vars(vars):
    for name, value in vars.items():
        os.environ[name] = value
    try:
        yield
    finally:
        for name, value in vars.items():
            del os.environ[name]
