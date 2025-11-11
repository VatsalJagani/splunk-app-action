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

import unittest
from unittest.mock import patch

import pytest

from main import main  # pyright: ignore[reportMissingImports]

from .helper_test import setup_action_yml

import os
SPLUNKBASE_USERNAME_FOR_TEST = os.environ["SPLUNKBASE_USERNAME_FOR_TEST"]
SPLUNKBASE_PASSWORD_FOR_TEST = os.environ["SPLUNKBASE_PASSWORD_FOR_TEST"]

# SPLUNKBASE_USERNAME_FOR_TEST = "sample"
# SPLUNKBASE_PASSWORD_FOR_TEST = "sample"


class TestAppInspect(unittest.TestCase):
    def test_my_app_inspect_failure_integration(self):
        # Mock the App Inspect API related function _perform_checks
        patcher_app_inspect_perform_checks = patch("app_inspect.SplunkAppInspect._perform_checks")
        mock_app_inspect_perform_checks = patcher_app_inspect_perform_checks.start()

        def mock_app_inspect_perform_checks_fn(check_type: str = "APP_INSPECT") -> str:
            print(
                f"Mocked app_inspect.SplunkAppInspect._perform_checks called with args: check_type={check_type}"
            )
            return "Failure"

        mock_app_inspect_perform_checks.side_effect = mock_app_inspect_perform_checks_fn

        with setup_action_yml(
            "my_app_inspect_fail",
            app_dir=".",
            use_ucc_gen="false",
            is_app_inspect_check="true",
            splunkbase_username=SPLUNKBASE_USERNAME_FOR_TEST,
            splunkbase_password=SPLUNKBASE_PASSWORD_FOR_TEST,
        ):
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                main()
            assert pytest_wrapped_e.type is SystemExit
            assert pytest_wrapped_e.value.code == 5

    def test_app_inspect_success_integration(self):
        # Mock the App Inspect API related function _perform_checks
        patcher_app_inspect_perform_checks = patch("app_inspect.SplunkAppInspect._perform_checks")
        mock_app_inspect_perform_checks = patcher_app_inspect_perform_checks.start()

        def mock_app_inspect_perform_checks_fn(check_type: str = "APP_INSPECT") -> str:
            print(
                f"Mocked app_inspect.SplunkAppInspect._perform_checks called with args: check_type={check_type}"
            )
            return "Passed"

        mock_app_inspect_perform_checks.side_effect = mock_app_inspect_perform_checks_fn

        with setup_action_yml(
            "my_app_inspect_pass",
            app_dir=".",
            use_ucc_gen="false",
            to_make_permission_changes="true",
            is_app_inspect_check="true",
            splunkbase_username=SPLUNKBASE_USERNAME_FOR_TEST,
            splunkbase_password=SPLUNKBASE_PASSWORD_FOR_TEST,
        ):
            main()

    def test_local_app_inspect_success_integration(self):
        # Mock the local App Inspect related function _run_local_inspect
        patcher_local_app_inspect = patch("app_inspect.SplunkLocalAppInspect._run_local_inspect")
        mock_local_app_inspect = patcher_local_app_inspect.start()

        def mock_local_app_inspect_fn(check_type: str = "APP_INSPECT") -> str:
            print(
                f"Mocked app_inspect.SplunkLocalAppInspect._run_local_inspect called with args: check_type={check_type}"
            )
            return "Passed"

        mock_local_app_inspect.side_effect = mock_local_app_inspect_fn

        with setup_action_yml(
            "my_app_inspect_pass",
            app_dir=".",
            use_ucc_gen="false",
            to_make_permission_changes="true",
            is_app_inspect_check="true",
            local_app_inspect="true",
        ):
            main()

    def test_local_app_inspect_failure_integration(self):
        # Mock the local App Inspect related function _run_local_inspect
        patcher_local_app_inspect = patch("app_inspect.SplunkLocalAppInspect._run_local_inspect")
        mock_local_app_inspect = patcher_local_app_inspect.start()

        def mock_local_app_inspect_fn(check_type: str = "APP_INSPECT") -> str:
            print(
                f"Mocked app_inspect.SplunkLocalAppInspect._run_local_inspect called with args: check_type={check_type}"
            )
            return "Failure"

        mock_local_app_inspect.side_effect = mock_local_app_inspect_fn

        with setup_action_yml(
            "my_app_inspect_fail",
            app_dir=".",
            use_ucc_gen="false",
            is_app_inspect_check="true",
            local_app_inspect="true",
        ):
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                main()
            assert pytest_wrapped_e.type is SystemExit
            assert pytest_wrapped_e.value.code == 5
