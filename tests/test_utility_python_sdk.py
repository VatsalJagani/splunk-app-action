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
from unittest.mock import patch

from utilities.splunk_sdk_python import (  # pyright: ignore[reportMissingImports]
    SplunkPythonSDKUtility,
)

from .helper_test import get_temp_directory, setup_temporary_env_vars


def check_no_pycache(folder_path):
    for _root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pyc"):
                return False
        for dir in dirs:
            if dir == "__pycache__":
                return False
    return True


def test_splunk_sdk_utility_installed_new():
    with get_temp_directory() as temp_dir:
        sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
        result = sdk_utility.implement_utility()

        # Validate the result
        folder_path = os.path.join(temp_dir, "bin")
        splunklib_dir = os.path.join(folder_path, "splunklib")
        init_file = os.path.join(splunklib_dir, "__init__.py")

        assert result == init_file
        assert os.path.exists(init_file)
        assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_installed_new_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_SPLUNK_PYTHON_SDK_INSTALL_PATH": "lib",
                "INPUT_IS_REMOVE_PYC_FROM_SPLUNKLIB_DIR": "true",
            }
        ):
            sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
            result = sdk_utility.implement_utility()

            # Validate the result
            folder_path = os.path.join(temp_dir, "lib")
            splunklib_dir = os.path.join(folder_path, "splunklib")
            init_file = os.path.join(splunklib_dir, "__init__.py")

            assert result == init_file
            assert os.path.exists(init_file)
            assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_upgraded_existing():
    with get_temp_directory() as temp_dir:
        # Prepare the temporary directory
        folder_path = os.path.join(temp_dir, "bin")
        os.makedirs(folder_path)
        splunklib_dir = os.path.join(folder_path, "splunklib")
        os.makedirs(splunklib_dir)
        init_file = os.path.join(splunklib_dir, "__init__.py")
        with open(init_file, "w") as f:
            f.write('__version_info__ = "1.0.0"')

        # Initialize SplunkPythonSDKUtility instance
        sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)

        result = sdk_utility.implement_utility()

        # Validate the result
        assert os.path.exists(init_file)
        assert result == init_file
        assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_upgraded_existing_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_SPLUNK_PYTHON_SDK_INSTALL_PATH": "bin/lib",
            }
        ):
            # Prepare the temporary directory
            folder_path = os.path.join(temp_dir, "bin", "lib")
            os.makedirs(folder_path)
            splunklib_dir = os.path.join(folder_path, "splunklib")
            os.makedirs(splunklib_dir)
            init_file = os.path.join(splunklib_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write('__version_info__ = "1.0.0"')

            # Initialize SplunkPythonSDKUtility instance
            sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)

            result = sdk_utility.implement_utility()

            # Validate the result
            assert os.path.exists(init_file)
            assert result == init_file
            assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_skipped_due_to_existing_and_same_version():
    with get_temp_directory() as temp_dir:
        # Prepare the temporary directory
        folder_path = os.path.join(temp_dir, "bin")
        os.makedirs(folder_path)
        splunklib_dir = os.path.join(folder_path, "splunklib")
        os.makedirs(splunklib_dir)
        init_file = os.path.join(splunklib_dir, "__init__.py")
        with open(init_file, "w") as f:
            f.write('__version_info__ = "1.2.3"')

        with patch.object(SplunkPythonSDKUtility, "_get_splunklib_version", return_value="1.2.3"):
            # Initialize SplunkPythonSDKUtility instance
            sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
            # Call implement_utility function
            result = sdk_utility.implement_utility()

        # Validate the result
        assert not os.path.exists(os.path.join(folder_path, "splunk-sdk"))
        assert result is None
        assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_skipped_due_to_existing_and_same_version_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_SPLUNK_PYTHON_SDK_INSTALL_PATH": "lib",
            }
        ):
            # Prepare the temporary directory
            folder_path = os.path.join(temp_dir, "lib")
            os.makedirs(folder_path)
            splunklib_dir = os.path.join(folder_path, "splunklib")
            os.makedirs(splunklib_dir)
            init_file = os.path.join(splunklib_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write('__version_info__ = "1.2.3"')

            with patch.object(
                SplunkPythonSDKUtility, "_get_splunklib_version", return_value="1.2.3"
            ):
                # Initialize SplunkPythonSDKUtility instance
                sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
                # Call implement_utility function
                result = sdk_utility.implement_utility()

            # Validate the result
            assert not os.path.exists(os.path.join(folder_path, "splunk-sdk"))
            assert result is None
            assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_error_upgrading_existing():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_IS_REMOVE_PYC_FROM_SPLUNKLIB_DIR": "true",
            }
        ):
            # Prepare the temporary directory
            folder_path = os.path.join(temp_dir, "bin")
            os.makedirs(folder_path)
            splunklib_dir = os.path.join(folder_path, "splunklib")
            os.makedirs(splunklib_dir)
            init_file = os.path.join(splunklib_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write('__version_info__ = "1.0.0"')

            # Initialize SplunkPythonSDKUtility instance
            sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)

            # Call implement_utility function with failing upgrade
            with patch.object(
                SplunkPythonSDKUtility, "_get_splunklib_version", return_value="2.2.2"
            ):
                result = sdk_utility.implement_utility()

            # Validate the result
            assert result is None
            assert check_no_pycache(folder_path)


def test_splunk_sdk_utility_error_upgrading_existing_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_SPLUNK_PYTHON_SDK_INSTALL_PATH": "bin/lib",
            }
        ):
            # Prepare the temporary directory
            folder_path = os.path.join(temp_dir, "bin", "lib")
            os.makedirs(folder_path)
            splunklib_dir = os.path.join(folder_path, "splunklib")
            os.makedirs(splunklib_dir)
            init_file = os.path.join(splunklib_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write('__version_info__ = "1.0.0"')

            # Initialize SplunkPythonSDKUtility instance
            sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)

            # Call implement_utility function with failing upgrade
            with patch.object(
                SplunkPythonSDKUtility, "_get_splunklib_version", return_value="2.2.2"
            ):
                result = sdk_utility.implement_utility()

            # Validate the result
            assert result is None
            assert check_no_pycache(folder_path)


def test_cleanup_old_package_files():
    """Test that old .dist-info and .egg-info directories are removed."""
    with get_temp_directory() as temp_dir:
        folder_path = os.path.join(temp_dir, "bin")
        os.makedirs(folder_path)

        # Create old metadata directories
        old_dist_info = os.path.join(folder_path, "splunk_sdk-1.7.0.dist-info")
        old_egg_info = os.path.join(folder_path, "splunk_sdk-1.7.0.egg-info")
        new_dist_info = os.path.join(folder_path, "splunk_sdk-2.0.0.dist-info")

        os.makedirs(old_dist_info)
        os.makedirs(old_egg_info)
        os.makedirs(new_dist_info)

        # Create some dummy files in the metadata directories
        with open(os.path.join(old_dist_info, "METADATA"), "w") as f:
            f.write("old metadata")
        with open(os.path.join(old_egg_info, "PKG-INFO"), "w") as f:
            f.write("old egg info")
        with open(os.path.join(new_dist_info, "METADATA"), "w") as f:
            f.write("new metadata")

        # Initialize SplunkPythonSDKUtility and call cleanup
        sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
        sdk_utility.cleanup_old_package_files(folder_path, "2.0.0")

        # Verify old directories are removed
        assert not os.path.exists(old_dist_info), "Old .dist-info should be removed"
        assert not os.path.exists(old_egg_info), "Old .egg-info should be removed"
        # Verify new directory is kept
        assert os.path.exists(new_dist_info), "New .dist-info should be kept"


def test_cleanup_old_package_files_no_version():
    """Test that cleanup doesn't remove metadata when no version is provided."""
    with get_temp_directory() as temp_dir:
        folder_path = os.path.join(temp_dir, "bin")
        os.makedirs(folder_path)

        # Create metadata directories
        dist_info = os.path.join(folder_path, "splunk_sdk-1.7.0.dist-info")
        os.makedirs(dist_info)

        with open(os.path.join(dist_info, "METADATA"), "w") as f:
            f.write("metadata")

        # Initialize SplunkPythonSDKUtility and call cleanup with no version
        sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
        sdk_utility.cleanup_old_package_files(folder_path, None)

        # Verify directory is kept when no version is provided
        assert os.path.exists(dist_info), "Metadata should be kept when no version provided"


def test_cleanup_old_package_files_different_packages():
    """Test that cleanup only removes splunk-sdk related metadata."""
    with get_temp_directory() as temp_dir:
        folder_path = os.path.join(temp_dir, "bin")
        os.makedirs(folder_path)

        # Create metadata directories for different packages
        splunk_old = os.path.join(folder_path, "splunk_sdk-1.7.0.dist-info")
        other_package = os.path.join(folder_path, "other_package-1.0.0.dist-info")
        splunk_new = os.path.join(folder_path, "splunk_sdk-2.0.0.dist-info")

        os.makedirs(splunk_old)
        os.makedirs(other_package)
        os.makedirs(splunk_new)

        with open(os.path.join(splunk_old, "METADATA"), "w") as f:
            f.write("old splunk metadata")
        with open(os.path.join(other_package, "METADATA"), "w") as f:
            f.write("other package metadata")
        with open(os.path.join(splunk_new, "METADATA"), "w") as f:
            f.write("new splunk metadata")

        # Initialize SplunkPythonSDKUtility and call cleanup
        sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
        sdk_utility.cleanup_old_package_files(folder_path, "2.0.0")

        # Verify only old splunk-sdk metadata is removed
        assert not os.path.exists(splunk_old), "Old splunk-sdk metadata should be removed"
        assert os.path.exists(other_package), "Other package metadata should be kept"
        assert os.path.exists(splunk_new), "New splunk-sdk metadata should be kept"


def test_cleanup_old_package_files_integration():
    """Test cleanup is called during upgrade process."""
    with get_temp_directory() as temp_dir:
        # Prepare the temporary directory with splunklib
        folder_path = os.path.join(temp_dir, "bin")
        os.makedirs(folder_path)
        splunklib_dir = os.path.join(folder_path, "splunklib")
        os.makedirs(splunklib_dir)
        init_file = os.path.join(splunklib_dir, "__init__.py")

        # Create old version
        with open(init_file, "w") as f:
            f.write("__version_info__ = (1, 7, 0)")

        # Create old metadata directory
        old_dist_info = os.path.join(folder_path, "splunk_sdk-1.7.0.dist-info")
        os.makedirs(old_dist_info)
        with open(os.path.join(old_dist_info, "METADATA"), "w") as f:
            f.write("old metadata")

        # Mock the version checks to simulate an upgrade
        def mock_get_version_side_effect(file_path):
            # First call returns old version, second call returns new version
            if not hasattr(mock_get_version_side_effect, "call_count"):
                mock_get_version_side_effect.call_count = 0
            mock_get_version_side_effect.call_count += 1

            if mock_get_version_side_effect.call_count == 1:
                return "(1, 7, 0)"
            else:
                # Create new metadata after "upgrade"
                new_dist_info = os.path.join(folder_path, "splunk_sdk-2.0.0.dist-info")
                if not os.path.exists(new_dist_info):
                    os.makedirs(new_dist_info)
                    with open(os.path.join(new_dist_info, "METADATA"), "w") as f:
                        f.write("new metadata")
                return "(2, 0, 0)"

        with patch.object(
            SplunkPythonSDKUtility,
            "_get_splunklib_version",
            side_effect=mock_get_version_side_effect,
        ):
            sdk_utility = SplunkPythonSDKUtility("nothing", temp_dir)
            result = sdk_utility.implement_utility()

            # Verify the upgrade happened and old metadata was cleaned up
            assert result == init_file
            # Old metadata should be removed
            assert not os.path.exists(old_dist_info), (
                "Old metadata should be cleaned up after upgrade"
            )
