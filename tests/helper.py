import os
import shutil
from contextlib import contextmanager

@contextmanager
def setup_action_yml(test_app_repo,
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
                            logger_sourcetype="NONE"):

    app_dir_path = os.path.join(os.path.dirname(__file__), "test_app_repos", test_app_repo)
    print(f"TestIntegration.setup_action_yml_work -> app_dir_path={app_dir_path}")

    # copy the app module there
    shutil.copytree(app_dir_path, os.path.join("repodir"))

    # setup inputs
    os.environ["SPLUNK_app_dir"] = app_dir
    os.environ["SPLUNK_use_ucc_gen"] = use_ucc_gen
    os.environ["SPLUNK_to_make_permission_changes"] = to_make_permission_changes
    os.environ["SPLUNK_is_app_inspect_check"] = is_app_inspect_check
    os.environ["SPLUNK_splunkbase_username"] = splunkbase_username
    os.environ["SPLUNK_splunkbase_password"] = splunkbase_password
    os.environ["SPLUNK_app_utilities"] = app_utilities
    os.environ["GITHUB_TOKEN"] = my_github_token
    os.environ["SPLUNK_current_branch_name"] = current_branch
    os.environ["SPLUNK_logger_log_files_prefix"] = logger_log_files_prefix
    os.environ["SPLUNK_logger_sourcetype"] = logger_sourcetype

    try:
        yield
    finally:
        print("TestIntegration Cleanup after each test-case.")
        try:
            shutil.rmtree("repodir")
        except:
            pass

        try:
            shutil.rmtree("without_ucc_build")
        except:
            pass

        try:
            shutil.rmtree("ucc_build_dir")
        except:
            pass

        for filename in os.listdir():
            if filename.startswith("my_app_"):
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
