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

import os
import shutil
import tarfile
import tempfile
import unittest
from typing import override
from unittest.mock import MagicMock, patch

from app_build_generate import (  # pyright: ignore[reportMissingImports]
    file_folder_permission_changes,
    generate_build,
    remove_unwanted_files,
    run_custom_user_defined_commands,
)
from helpers.saved_values import AppInfo, SavedPaths  # pyright: ignore[reportMissingImports]


class TestGenerateBuild(unittest.TestCase):
    @override
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

        # Create minimal app directory structure
        self.app_build_dir = "my_app_build"
        os.makedirs(os.path.join(self.app_build_dir, "default"))
        with open(os.path.join(self.app_build_dir, "default", "app.conf"), "w") as f:
            f.write("[launcher]\nversion = 1.0.0\n")

        # Create SavedPaths pointing to temp dir
        self.saved_paths = MagicMock(spec=SavedPaths)
        self.saved_paths.root_dir_path = self.temp_dir

        # Create AppInfo with mocked gat calls
        self.app_info = MagicMock(spec=AppInfo)
        self.app_info.package_id = "my_test_app"
        self.app_info.version_number_encoded = "1_0_0"
        self.app_info.build_number_encoded = "1"

    @override
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("app_build_generate.run_custom_user_defined_commands")
    @patch("app_build_generate.file_folder_permission_changes")
    @patch("app_build_generate.remove_unwanted_files")
    def test_generate_build_no_shell_injection(
        self, mock_remove, mock_permissions, mock_custom_cmds
    ):
        """Verify generate_build uses safe subprocess calls, not os.system."""
        with patch("app_build_generate.os.system") as mock_os_system:
            build_path = generate_build(self.saved_paths, self.app_info, self.app_build_dir)

            # os.system should NOT have been called
            mock_os_system.assert_not_called()

        # A valid tgz file should have been produced
        assert os.path.exists(build_path)
        assert tarfile.is_tarfile(build_path)

        # Verify the tarball contains the expected app directory
        with tarfile.open(build_path, "r:gz") as tar:
            names = tar.getnames()
            assert any("my_test_app" in n for n in names)

    @patch("app_build_generate.run_custom_user_defined_commands")
    @patch("app_build_generate.file_folder_permission_changes")
    @patch("app_build_generate.remove_unwanted_files")
    def test_generate_build_produces_correct_filename(
        self, mock_remove, mock_permissions, mock_custom_cmds
    ):
        """Verify the generated tarball has the expected naming convention."""
        build_path = generate_build(self.saved_paths, self.app_info, self.app_build_dir)

        expected_name = "my_test_app_1_0_0_1.tgz"
        assert os.path.basename(build_path) == expected_name


class TestRemoveUnwantedFiles(unittest.TestCase):
    def test_removes_git_dirs_and_gitignore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs(".git")
                os.makedirs(".github")
                with open(".gitignore", "w") as f:
                    f.write("*.pyc\n")
                os.makedirs("__pycache__")
                with open("__pycache__/foo.pyc", "w") as f:
                    f.write("")

                remove_unwanted_files()

                assert not os.path.exists(".git")
                assert not os.path.exists(".github")
                assert not os.path.exists(".gitignore")
                assert not os.path.exists("__pycache__")
            finally:
                os.chdir(orig_cwd)

    def test_removes_python_version_file(self):
        """remove_unwanted_files removes .python-version so it is not included in the Splunk build.

        This covers UCC add-ons where .python-version lives in package/ and is copied into
        the ucc-gen output. Without this removal, App Inspect fails with
        check_that_extracted_splunk_app_does_not_contain_prohibited_directories_or_files.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with open(".python-version", "w") as f:
                    f.write("3.9\n")

                remove_unwanted_files()

                assert not os.path.exists(".python-version")
            finally:
                os.chdir(orig_cwd)

    def test_no_error_when_dirs_missing(self):
        """Calling remove_unwanted_files when targets don't exist should not raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                remove_unwanted_files()
            finally:
                os.chdir(orig_cwd)


class TestFileFolderPermissionChanges(unittest.TestCase):
    @patch("app_build_generate.subprocess.run")
    @patch("app_build_generate.gat.get_user_input_as", return_value=True)
    def test_permissions_applied_when_enabled(self, mock_input, mock_run):
        file_folder_permission_changes()

        # Should have called subprocess.run for file perms, script exts, and dir perms
        calls = mock_run.call_args_list
        # At least: 1 for files (644), 5 for script extensions (755 each), 1 for dirs (755)
        assert len(calls) >= 7
        # First call sets 644 on files
        assert "644" in calls[0].args[0]
        # Last call sets 755 on dirs
        assert "755" in calls[-1].args[0]
        assert "-type" in calls[-1].args[0]
        assert "d" in calls[-1].args[0]

    @patch("app_build_generate.subprocess.run")
    @patch("app_build_generate.gat.get_user_input_as", return_value=False)
    def test_permissions_skipped_when_disabled(self, mock_input, mock_run):
        file_folder_permission_changes()

        mock_run.assert_not_called()


class TestRunCustomUserDefinedCommands(unittest.TestCase):
    @patch("app_build_generate.os.system")
    def test_executes_env_commands(self, mock_system):
        env_vars = {
            "SPLUNK_APP_ACTION_1": "echo hello",
            "SPLUNK_APP_ACTION_2": "echo world",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            run_custom_user_defined_commands()

        assert mock_system.call_count == 2
        mock_system.assert_any_call("echo hello")
        mock_system.assert_any_call("echo world")

    @patch("app_build_generate.os.system")
    def test_no_commands_found(self, mock_system):
        clean_env = {k: v for k, v in os.environ.items() if not k.startswith("SPLUNK_APP_ACTION_")}
        with patch.dict(os.environ, clean_env, clear=True):
            run_custom_user_defined_commands()

        mock_system.assert_not_called()
