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
from unittest.mock import patch, MagicMock

from helpers.saved_values import AppInfo, SavedPaths
from app_build_generate import generate_build


class TestGenerateBuild(unittest.TestCase):
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
