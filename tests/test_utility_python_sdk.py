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
