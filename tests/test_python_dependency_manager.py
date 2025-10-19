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
        """Test basic Python dependency installation."""
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

    def test_mutually_exclusive_python_sdk_and_python_deps(self):
        """Test that Splunk Python SDK and Python dependency manager cannot be used together."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            app_utilities="splunk_python_sdk",
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
