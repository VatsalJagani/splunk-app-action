# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportFunctionMemberAccess=false
# pyright: reportUnannotatedClassAttribute=false
# pyright: reportUninitializedInstanceVariable=false


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
    is_remove_not_allowed_executables_from_lib="true",
    python_requirements_file="",
    splunk_python_version="3.9",
    to_make_permission_changes="false",
    is_app_inspect_check="true",
    splunkbase_username="NONE",
    splunkbase_password="NONE",
    local_app_inspect="false",
    app_utilities="",
    my_github_token="",  # Empty string matches action.yml default
    current_branch="NONE",
    logger_log_files_prefix="NONE",
    logger_sourcetype="NONE",
):
    print("Test Setup Steps")
    repo_root_dir_path = os.getcwd()
    temp_dir_for_test = "temp_for_test"
    temp_dir_for_test_path = os.path.join(repo_root_dir_path, temp_dir_for_test)
    repo_dir_path = os.path.join(temp_dir_for_test_path, "repodir")

    try:
        shutil.rmtree(temp_dir_for_test_path)
    except OSError:
        pass
    try:
        os.mkdir(temp_dir_for_test_path)
    except OSError:
        pass

    app_repo_path = os.path.join(os.path.dirname(__file__), "test_app_repos", test_app_repo)
    shutil.copytree(app_repo_path, repo_dir_path)

    os.chdir(temp_dir_for_test_path)

    # Save original environment variables
    original_github_workspace = os.environ.get("GITHUB_WORKSPACE")
    original_github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")

    # Create a temporary file for job summary
    summary_file_path = os.path.join(temp_dir_for_test_path, "job_summary.md")

    # setup inputs
    os.environ["INPUT_APP_DIR"] = app_dir
    os.environ["INPUT_USE_UCC_GEN"] = use_ucc_gen
    os.environ["INPUT_IS_REMOVE_NOT_ALLOWED_EXECUTABLES_FROM_LIB"] = (
        is_remove_not_allowed_executables_from_lib
    )
    os.environ["INPUT_PYTHON_REQUIREMENTS_FILE"] = python_requirements_file
    os.environ["INPUT_SPLUNK_PYTHON_VERSION"] = splunk_python_version
    os.environ["INPUT_TO_MAKE_PERMISSION_CHANGES"] = to_make_permission_changes
    os.environ["INPUT_IS_APP_INSPECT_CHECK"] = is_app_inspect_check
    os.environ["INPUT_SPLUNKBASE_USERNAME"] = splunkbase_username
    os.environ["INPUT_SPLUNKBASE_PASSWORD"] = splunkbase_password
    os.environ["INPUT_LOCAL_APP_INSPECT"] = local_app_inspect
    os.environ["INPUT_APP_UTILITIES"] = app_utilities
    os.environ["GITHUB_TOKEN"] = my_github_token
    os.environ["INPUT_CURRENT_BRANCH_NAME"] = current_branch
    os.environ["INPUT_LOGGER_LOG_FILES_PREFIX"] = logger_log_files_prefix
    os.environ["INPUT_LOGGER_SOURCETYPE"] = logger_sourcetype
    # Set GITHUB_WORKSPACE to the test directory so main() works correctly
    os.environ["GITHUB_WORKSPACE"] = temp_dir_for_test_path

    # Set GITHUB_STEP_SUMMARY for job summary writing
    os.environ["GITHUB_STEP_SUMMARY"] = summary_file_path

    try:
        yield
    finally:
        print("Test Cleanup after each test-case.")
        try:
            shutil.rmtree(temp_dir_for_test_path)
        except OSError:
            pass
        os.chdir(repo_root_dir_path)

        # Restore original environment variables
        if original_github_workspace is not None:
            os.environ["GITHUB_WORKSPACE"] = original_github_workspace
        else:
            os.environ.pop("GITHUB_WORKSPACE", None)

        if original_github_step_summary is not None:
            os.environ["GITHUB_STEP_SUMMARY"] = original_github_step_summary
        else:
            os.environ.pop("GITHUB_STEP_SUMMARY", None)


@contextmanager
def get_temp_directory():
    temp_dir = os.path.join(os.path.dirname(__file__), "tempdir")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    original_cwd = os.getcwd()

    try:
        yield temp_dir
    finally:
        os.chdir(original_cwd)
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
        for name, _value in vars.items():
            del os.environ[name]
