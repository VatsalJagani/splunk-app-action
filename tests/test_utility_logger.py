import os
from contextlib import contextmanager
from unittest.mock import patch
from .helper import get_temp_directory, setup_temporary_env_vars

from utilities.logger import LoggerUtility


# UTILITIES_FOLDER_PATH = os.path.join(os.path.dirname(__file__), os.path.pardir, 'src', 'utilities', 'common_splunk_js_utilities')


def test_logger_utility_skipped_due_to_missing_prefix_1():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "NONE", 
            "SPLUNK_logger_sourcetype": "sample_logger_sourcetype"
        }):
            logger = LoggerUtility("dummy", temp_dir)

            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing prefix
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert not os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))



def test_logger_utility_skipped_due_to_missing_prefix_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_sourcetype": "sample_logger_sourcetype"
        }):
            logger = LoggerUtility("dummy", temp_dir)

            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing prefix
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert not os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))


def test_logger_utility_skipped_due_to_missing_sourcetype_1():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "sample_prefix",
            "SPLUNK_logger_sourcetype": "NONE"
        }):
            logger = LoggerUtility("dummy", temp_dir)


            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing sourcetype
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert not os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))



def test_logger_utility_skipped_due_to_missing_sourcetype_2():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "sample_prefix",
        }):
            logger = LoggerUtility("dummy", temp_dir)


            # Exercise: Call the function
            result = logger.implement_utility()

            # Verify: Check if the utility was skipped due to missing sourcetype
            assert not result
            assert not os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert not os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))


def test_logger_utility_added():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "sample_log_file_prefix", 
            "SPLUNK_logger_sourcetype": "sample_logger_sourcetype"
        }):
            logger = LoggerUtility("dumpy", temp_dir)
            result = logger.implement_utility()

            # Verify: Check if the utility was successfully added
            assert result
            assert os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))
            with open(os.path.join(temp_dir, 'bin', 'logger_manager.py'), 'r') as f:
                assert "sample_log_file_prefix" in f.read()
            with open(os.path.join(temp_dir, 'default', 'props.conf'), 'r') as f:
                assert "sample_logger_sourcetype" in f.read()


def test_logger_utility_updated():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "sample_log_file_prefix", 
            "SPLUNK_logger_sourcetype": "sample_logger_sourcetype"
        }):
            logger = LoggerUtility("dumpy", temp_dir)
            result = logger.implement_utility()

            # Verify: Check if the utility was successfully added
            assert result
            assert os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))

        # Updating the logger
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "log_file_prefix_new", 
            "SPLUNK_logger_sourcetype": "logger_sourcetype_new"
        }):
            logger = LoggerUtility("dumpy", temp_dir)
            result = logger.implement_utility()

            # Verify: Check if the utility was successfully updated with new content
            assert result
            assert os.path.exists(os.path.join(temp_dir, 'bin', 'logger_manager.py'))
            assert os.path.exists(os.path.join(temp_dir, 'default', 'props.conf'))
            with open(os.path.join(temp_dir, 'bin', 'logger_manager.py'), 'r') as f:
                assert "log_file_prefix_new" in f.read()
                assert "sample_log_file_prefix" not in f.read()
            with open(os.path.join(temp_dir, 'default', 'props.conf'), 'r') as f:
                assert "logger_sourcetype_new" in f.read()
                assert "sample_logger_sourcetype" not in f.read()


def test_logger_utility_not_updated():
    with get_temp_directory() as temp_dir:
        with setup_temporary_env_vars({
            "SPLUNK_logger_log_files_prefix": "sample_log_file_prefix", 
            "SPLUNK_logger_sourcetype": "sample_logger_sourcetype"
        }):
            logger = LoggerUtility("dumpy", temp_dir)
            
            # Exercise: Call the function twice to simulate no changes
            result1 = logger.implement_utility()
            result2 = logger.implement_utility()

            # Verify: Check if the logger related files were not updated
            assert result1
            assert not result2
