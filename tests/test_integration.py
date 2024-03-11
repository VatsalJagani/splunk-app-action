import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)

import unittest
from unittest.mock import patch
import pytest

import os
import sys
import shutil
import tarfile
from main import main

from helpers.github_action_utils import set_env



class TestIntegration(unittest.TestCase):
    def setup_method(self, test_method):
        print("TestIntegration.setup_method")

        # Mock the set_env function during the test
        patcher = patch("helpers.github_action_utils.set_env")
        self.mock_set_env = patcher.start()

        def mock_set_env(name, value):
            print(f"Mocked set_env called with args: name={name}, value={value}")
            os.environ[name] = value
        self.mock_set_env.side_effect = mock_set_env


    def setup_action_yml_work(self,
                              test_app_repo,
                              app_dir=".",
                              is_generate_build="true",
                              use_ucc_gen="false",
                              to_make_permission_changes="false",
                              is_app_inspect_check="true",
                              splunkbase_username="NONE",
                              splunkbase_password="NONE",
                              app_build_path="NONE",
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
        os.environ["SPLUNK_is_generate_build"] = is_generate_build
        os.environ["SPLUNK_use_ucc_gen"] = use_ucc_gen
        os.environ["SPLUNK_to_make_permission_changes"] = to_make_permission_changes
        os.environ["SPLUNK_is_app_inspect_check"] = is_app_inspect_check
        os.environ["SPLUNK_splunkbase_username"] = splunkbase_username
        os.environ["SPLUNK_splunkbase_password"] = splunkbase_password
        os.environ["SPLUNK_app_build_path"] = app_build_path
        os.environ["SPLUNK_app_utilities"] = app_utilities
        os.environ["GITHUB_TOKEN"] = my_github_token
        os.environ["SPLUNK_current_branch_name"] = current_branch
        os.environ["SPLUNK_logger_log_files_prefix"] = logger_log_files_prefix
        os.environ["SPLUNK_logger_sourcetype"] = logger_sourcetype


    def teardown_method(self, test_method):
        print("TestIntegration.teardown_method")
        try:
            shutil.rmtree("repodir")
        except:
            pass
        
        try:
            shutil.rmtree("without_ucc_build")
        except:
            pass

        try:
            shutil.rmtree("with_ucc_build")
        except:
            pass

        try:
            shutil.rmtree("my_app_*")
        except:
            pass


    def extract_app_build(self, tgz_file):
        # Create a temporary directory to extract the contents
        extract_dir = "temp_extraction"
        os.makedirs(extract_dir, exist_ok=True)

        try:
            # Extract the contents of the .tgz file
            with tarfile.open(tgz_file, 'r:gz') as tar:
                tar.extractall(extract_dir)

            # Initialize counters
            file_count = 0
            folder_count = 0
            all_files = []
            is_root = True

            # Walk through the extracted directory
            for root, dirs, files in os.walk(extract_dir):
                if is_root:
                    is_root = False
                    continue

                folder_count += len(dirs)
                file_count += len(files)

                # Print relative paths of files
                for file in files:
                    relative_path = os.path.relpath(os.path.join(root, file), extract_dir)
                    # print("File:", relative_path)
                    all_files.append(relative_path)

            # print("Total Files:", file_count)
            # print("Total Folders:", folder_count)
            return file_count, folder_count, all_files

        finally:
            # Cleanup: Remove the temporary extraction directory
            if os.path.exists(extract_dir):
                for root, dirs, files in os.walk(extract_dir, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(extract_dir)



    def test_build_1(self):
        self.setup_action_yml_work("repo_1_regular_build", app_dir="my_app_1", is_app_inspect_check="false")
        main()
        shutil.rmtree("my_app_1")
        file_count, folder_count, all_files = self.extract_app_build("my_app_1_1_1_2_1.tgz")
        assert folder_count == 7
        assert file_count == 9
        assert "my_app_1/static/appIconAlt.png" in all_files
        assert "my_app_1/default/data/ui/views/assets.xml" in all_files
