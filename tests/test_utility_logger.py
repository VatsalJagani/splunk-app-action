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

from utilities.logger import LoggerUtility

from .helper import get_temp_directory, setup_temporary_env_vars  # pyright: ignore


def test_logger_utility_skipped_due_to_missing_prefix_1():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_LOGGER_LOG_FILES_PREFIX": "NONE",
                "INPUT_LOGGER_SOURCETYPE": "sample_logger_sourcetype",
            }
        ):
            logger = LoggerUtility("dummy", temp_dir)

            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing prefix
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert not os.path.exists(os.path.join(temp_dir, "default", "props.conf"))


def test_logger_utility_skipped_due_to_missing_prefix_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({"INPUT_LOGGER_SOURCETYPE": "sample_logger_sourcetype"}):
            logger = LoggerUtility("dummy", temp_dir)

            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing prefix
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert not os.path.exists(os.path.join(temp_dir, "default", "props.conf"))


def test_logger_utility_skipped_due_to_missing_sourcetype_1():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {"INPUT_LOGGER_LOG_FILES_PREFIX": "sample_prefix", "INPUT_LOGGER_SOURCETYPE": "NONE"}
        ):
            logger = LoggerUtility("dummy", temp_dir)

            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing sourcetype
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert not os.path.exists(os.path.join(temp_dir, "default", "props.conf"))


def test_logger_utility_skipped_due_to_missing_sourcetype_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_LOGGER_LOG_FILES_PREFIX": "sample_prefix",
            }
        ):
            logger = LoggerUtility("dummy", temp_dir)

            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing sourcetype
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert not os.path.exists(os.path.join(temp_dir, "default", "props.conf"))


def test_logger_utility_added():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_LOGGER_LOG_FILES_PREFIX": "sample_log_file_prefix",
                "INPUT_LOGGER_SOURCETYPE": "sample_logger_sourcetype",
            }
        ):
            logger = LoggerUtility("dumpy", temp_dir)
            result = logger.implement_utility()

            # Verify: Check if the utility was successfully added
            assert result
            assert os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert os.path.exists(os.path.join(temp_dir, "default", "props.conf"))
            with open(os.path.join(temp_dir, "bin", "logger_manager.py")) as f:
                assert "sample_log_file_prefix" in f.read()
            with open(os.path.join(temp_dir, "default", "props.conf")) as f:
                assert "sample_logger_sourcetype" in f.read()


def test_logger_utility_updated():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_LOGGER_LOG_FILES_PREFIX": "sample_log_file_prefix",
                "INPUT_LOGGER_SOURCETYPE": "sample_logger_sourcetype",
            }
        ):
            logger = LoggerUtility("dumpy", temp_dir)
            result = logger.implement_utility()

            # Verify: Check if the utility was successfully added
            assert result
            assert os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert os.path.exists(os.path.join(temp_dir, "default", "props.conf"))

        # Updating the logger
        with setup_temporary_env_vars(
            {
                "INPUT_LOGGER_LOG_FILES_PREFIX": "log_file_prefix_new",
                "INPUT_LOGGER_SOURCETYPE": "logger_sourcetype_new",
            }
        ):
            logger = LoggerUtility("dumpy", temp_dir)
            result = logger.implement_utility()

            # Verify: Check if the utility was successfully updated with new content
            assert result
            assert os.path.exists(os.path.join(temp_dir, "bin", "logger_manager.py"))
            assert os.path.exists(os.path.join(temp_dir, "default", "props.conf"))
            with open(os.path.join(temp_dir, "bin", "logger_manager.py")) as f1:
                assert "log_file_prefix_new" in f1.read()
                assert "sample_log_file_prefix" not in f1.read()
            with open(os.path.join(temp_dir, "default", "props.conf")) as f2:
                assert "logger_sourcetype_new" in f2.read()
                assert "sample_logger_sourcetype" not in f2.read()


def test_logger_utility_not_updated():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars(
            {
                "INPUT_LOGGER_LOG_FILES_PREFIX": "sample_log_file_prefix",
                "INPUT_LOGGER_SOURCETYPE": "sample_logger_sourcetype",
            }
        ):
            logger = LoggerUtility("dumpy", temp_dir)

            # Exercise: Call the function twice to simulate no changes
            result1 = logger.implement_utility()
            result2 = logger.implement_utility()

            # Verify: Check if the logger related files were not updated
            assert result1
            assert not result2
