import os
import unittest
import pytest

from .helper import setup_action_yml
from main import main
import app_inspect



class TestAppInspect(unittest.TestCase):

    def test_app_inspect_failure_integration(self):
        with setup_action_yml("repo_1_regular_build", app_dir="my_app_1", is_app_inspect_check="true", splunkbase_username="VatsalJagani", splunkbase_password="g9@PDP5Ktby%Q8"):
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                main()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code == 5


    def test_app_inspect_failure_unit(self):
        with self.assertRaisesRegex(Exception, "All status \\[app-inspect, cloud-checks, self-service-checks\\].*Failure.*"):
            build_path = os.path.join(os.path.dirname(__file__), "test_app_builds_for_app_inspect", "my_app_1_1_1_2_1.tgz")
            app_inspect.SplunkAppInspect(build_path).run_all_checks()


    def test_app_inspect_success_unit(self):
        build_path = os.path.join(os.path.dirname(__file__), "test_app_builds_for_app_inspect", "TA-defender-atp-status-check_1_1_0_1.tgz")
        app_inspect.SplunkAppInspect(build_path).run_all_checks()
