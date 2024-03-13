import os
import unittest
import pytest

from .helper import setup_action_yml
from main import main



SPLUNKBASE_USERNAME_FOR_TEST = os.environ["SPLUNKBASE_USERNAME_FOR_TEST"]
SPLUNKBASE_PASSWORD_FOR_TEST = os.environ["SPLUNKBASE_PASSWORD_FOR_TEST"]


class TestAppInspect(unittest.TestCase):

    def test_app_inspect_failure_integration(self):
        with setup_action_yml("repo_1_regular_build", app_dir="my_app_1", is_app_inspect_check="true", splunkbase_username=SPLUNKBASE_USERNAME_FOR_TEST, splunkbase_password=SPLUNKBASE_PASSWORD_FOR_TEST):
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                main()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code == 5


    def test_app_inspect_success_integration(self):
        with setup_action_yml("app_inspect_pass", app_dir=".", to_make_permission_changes="true", is_app_inspect_check="true", splunkbase_username=SPLUNKBASE_USERNAME_FOR_TEST, splunkbase_password=SPLUNKBASE_PASSWORD_FOR_TEST):
            main()
