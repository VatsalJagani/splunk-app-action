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

import os
import tarfile
import unittest
from unittest.mock import MagicMock, patch

from main import main  # pyright: ignore[reportMissingImports]

from .helper_test import setup_action_yml


def extract_app_build(tgz_file):
    """Extract app build and return files and folders."""
    extract_dir = "temp_extraction"
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with tarfile.open(tgz_file, "r:gz") as tar:
            tar.extractall(extract_dir)

        all_files = []
        all_folders = []
        is_root = True

        for root, dirs, files in os.walk(extract_dir):
            if is_root:
                is_root = False
                continue

            for file in files:
                if file.startswith("._") or file == ".DS_Store":
                    continue
                relative_path = os.path.relpath(os.path.join(root, file), extract_dir)
                all_files.append(relative_path)

            for dir in dirs:
                relative_path = os.path.relpath(os.path.join(root, dir), extract_dir)
                all_folders.append(relative_path)

        return len(all_files), len(all_folders), all_files, all_folders

    finally:
        if os.path.exists(extract_dir):
            for root, dirs, files in os.walk(extract_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(extract_dir)


class TestPythonDependencyManager(unittest.TestCase):
    def test_python_deps_basic(self):
        """Test basic Python dependency installation. Requires network access for pip install."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            try:
                main()
            except RuntimeError as e:
                # Network issues can cause this test to fail
                if "Read timed out" in str(e) or "Failed to install dependencies" in str(e):
                    self.skipTest("Network connectivity required for this test")
                raise

            app_build_name = "my_app_3_1_2_3_1.tgz"
            assert os.path.isfile(app_build_name), f"App build {app_build_name} not found"

            file_count, folder_count, all_files, all_folders = extract_app_build(app_build_name)

            # Verify basic app structure
            assert "my_app_3/default/app.conf" in all_files
            assert "my_app_3/README.md" in all_files
            # requirements.txt should be removed from build
            assert "my_app_3/lib/requirements.txt" not in all_files

            # Verify lib folder was created
            assert "my_app_3/lib" in all_folders

            # Verify dependencies were installed
            # Check for requests library
            requests_files = [f for f in all_files if "my_app_3/lib/requests" in f]
            assert len(requests_files) > 0, "requests library not found in lib folder"

            # Check for certifi library
            certifi_files = [f for f in all_files if "my_app_3/lib/certifi" in f]
            assert len(certifi_files) > 0, "certifi library not found in lib folder"

            # Verify no .pyc or __pycache__ files
            pyc_files = [f for f in all_files if f.endswith(".pyc")]
            assert len(pyc_files) == 0, "Found .pyc files in build"

            pycache_folders = [f for f in all_folders if "__pycache__" in f]
            assert len(pycache_folders) == 0, "Found __pycache__ folders in build"

    def test_mutually_exclusive_ucc_and_python_deps(self):
        """Test that UCC and Python dependency manager cannot be used together."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            use_ucc_gen="true",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            # Should exit with error code 1
            with self.assertRaises(SystemExit) as cm:
                main()
            assert cm.exception.code == 1

    def test_requirements_file_not_found(self):
        """Test error when requirements.txt file doesn't exist."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/nonexistent_requirements.txt",
            is_app_inspect_check="false",
        ):
            # Should raise FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                main()


class TestPathJoinBug(unittest.TestCase):
    def test_absolute_app_dir_path_discards_prefix(self):
        """Verify os.path.join with absolute path discards the prefix (the bug)."""
        absolute_path = "/workspace/repodir/my_app"
        # This is the buggy behavior: absolute path discards "python_deps_build_dir"
        result = os.path.join("python_deps_build_dir", absolute_path)
        assert result == absolute_path

    def test_app_dir_name_produces_correct_path(self):
        """Verify os.path.join with relative name produces the correct path."""
        app_dir_name = "my_app"
        result = os.path.join("python_deps_build_dir", app_dir_name)
        assert result == "python_deps_build_dir/my_app"

    def test_app_dir_name_dot_produces_correct_path(self):
        """When app_dir_name is '.', the path should still be under the build dir."""
        result = os.path.join("python_deps_build_dir", ".")
        assert result == "python_deps_build_dir/."


class TestPythonVersionInput(unittest.TestCase):
    def _capture_subprocess(self, pip_install_calls):
        def side_effect(cmd, **kwargs):
            if "install" in cmd:
                pip_install_calls.append(list(cmd))
            return MagicMock(returncode=0, stdout="", stderr="")

        return side_effect

    def test_pip_install_uses_python_39_by_default(self):
        """uv pip install should target Python 3.9 when splunk_python_version is not specified."""
        pip_install_calls: list[list[str]] = []
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=self._capture_subprocess(pip_install_calls),
            ):
                main()

        assert len(pip_install_calls) == 1
        cmd = pip_install_calls[0]
        assert cmd[0] == "uv"
        assert "--python" in cmd
        assert cmd[cmd.index("--python") + 1] == "3.9"

    def test_pip_install_uses_custom_splunk_python_version(self):
        """uv pip install should use the splunk_python_version input when explicitly specified."""
        pip_install_calls: list[list[str]] = []
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
            splunk_python_version="3.11",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=self._capture_subprocess(pip_install_calls),
            ):
                main()

        assert len(pip_install_calls) == 1
        cmd = pip_install_calls[0]
        assert cmd[0] == "uv"
        assert "--python" in cmd
        assert cmd[cmd.index("--python") + 1] == "3.11"
