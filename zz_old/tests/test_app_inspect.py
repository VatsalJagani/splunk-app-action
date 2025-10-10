import unittest
from unittest.mock import patch
import pytest

from .helper import setup_action_yml
from main import main

# import os
# SPLUNKBASE_USERNAME_FOR_TEST = os.environ["SPLUNKBASE_USERNAME_FOR_TEST"]
# SPLUNKBASE_PASSWORD_FOR_TEST = os.environ["SPLUNKBASE_PASSWORD_FOR_TEST"]

SPLUNKBASE_USERNAME_FOR_TEST = "sample"
SPLUNKBASE_PASSWORD_FOR_TEST = "sample"



class TestAppInspect(unittest.TestCase):

    def test_my_app_inspect_failure_integration(self):
        # Mock the App Inspect API related function _perform_checks
        patcher_app_inspect_perform_checks = patch("app_inspect.SplunkAppInspect._perform_checks")
        mock_app_inspect_perform_checks = patcher_app_inspect_perform_checks.start()

        def mock_app_inspect_perform_checks_fn(check_type="APP_INSPECT"):
            print(f"Mocked app_inspect.SplunkAppInspect._perform_checks called with args: check_type={check_type}")
            return "Failure"
        mock_app_inspect_perform_checks.side_effect = mock_app_inspect_perform_checks_fn

        with setup_action_yml("my_app_inspect_fail", app_dir=".", is_app_inspect_check="true", splunkbase_username=SPLUNKBASE_USERNAME_FOR_TEST, splunkbase_password=SPLUNKBASE_PASSWORD_FOR_TEST):
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                main()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code == 5


    def test_app_inspect_success_integration(self):
        # Mock the App Inspect API related function _perform_checks
        patcher_app_inspect_perform_checks = patch("app_inspect.SplunkAppInspect._perform_checks")
        mock_app_inspect_perform_checks = patcher_app_inspect_perform_checks.start()

        def mock_app_inspect_perform_checks_fn(check_type="APP_INSPECT"):
            print(f"Mocked app_inspect.SplunkAppInspect._perform_checks called with args: check_type={check_type}")
            return "Passed"
        mock_app_inspect_perform_checks.side_effect = mock_app_inspect_perform_checks_fn

        with setup_action_yml("my_app_inspect_pass", app_dir=".", to_make_permission_changes="true", is_app_inspect_check="true", splunkbase_username=SPLUNKBASE_USERNAME_FOR_TEST, splunkbase_password=SPLUNKBASE_PASSWORD_FOR_TEST):
            main()
