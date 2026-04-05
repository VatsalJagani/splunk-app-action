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
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from app_inspect import SplunkLocalAppInspect
from helpers.saved_values import AppInfo, SavedPaths


def _make_inspector(temp_dir):
    """Create a SplunkLocalAppInspect instance with mocked dependencies."""
    saved_paths = MagicMock(spec=SavedPaths)
    saved_paths.root_dir_path = temp_dir
    saved_paths.app_dir_name = "myapp"

    app_info = MagicMock(spec=AppInfo)
    app_info.package_id = "myapp"
    app_info.version_number_encoded = "1_0_0"
    app_info.build_number_encoded = "1"

    # Create a dummy build file
    build_path = os.path.join(temp_dir, "myapp_1_0_0_1.tgz")
    with open(build_path, "w") as f:
        f.write("fake")

    inspector = SplunkLocalAppInspect(saved_paths, app_info, build_path)
    return inspector


class TestThreadErrorHandling(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_perform_app_inspect_check_sets_error_on_exception(self):
        """When _perform_checks raises, result should be 'Error' not 'Running'."""
        inspector = _make_inspector(self.temp_dir)
        inspector._perform_checks = MagicMock(side_effect=RuntimeError("boom"))

        inspector._perform_app_inspect_check()

        assert inspector.app_inspect_result[0] == "Error"

    def test_perform_cloud_inspect_check_sets_error_on_exception(self):
        """When _perform_checks raises, cloud result should be 'Error'."""
        inspector = _make_inspector(self.temp_dir)
        inspector._perform_checks = MagicMock(side_effect=RuntimeError("boom"))

        inspector._perform_cloud_inspect_check()

        assert inspector.app_inspect_result[1] == "Error"

    def test_perform_ssai_inspect_check_sets_error_on_exception(self):
        """When _perform_checks raises, SSAI result should be 'Error'."""
        inspector = _make_inspector(self.temp_dir)
        inspector._perform_checks = MagicMock(side_effect=RuntimeError("boom"))

        inspector._perform_ssai_inspect_check()

        assert inspector.app_inspect_result[2] == "Error"

    def test_perform_app_inspect_check_sets_passed(self):
        """When _perform_checks returns 'Passed', result should be 'Passed'."""
        inspector = _make_inspector(self.temp_dir)
        inspector._perform_checks = MagicMock(return_value="Passed")

        inspector._perform_app_inspect_check()

        assert inspector.app_inspect_result[0] == "Passed"

    def test_run_all_checks_reflects_thread_results(self):
        """run_all_checks should surface thread results properly."""
        inspector = _make_inspector(self.temp_dir)
        inspector._perform_checks = MagicMock(return_value="Passed")

        inspector.run_all_checks()

        assert inspector.app_inspect_result == ["Passed", "Passed", "Passed"]
