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
# pyright: reportMissingImports=false
# pyright: reportImplicitOverride=false

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from helpers.app_inspect_report_commenter import AppInspectReportCommenter


class TestAppInspectReportCommenter(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test reports
        self.test_dir = tempfile.mkdtemp()
        self.report_dir = os.path.join(self.test_dir, "reports")
        self.app_dir = os.path.join(self.test_dir, "app")
        os.makedirs(self.report_dir)
        os.makedirs(self.app_dir)

    def tearDown(self):
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.test_dir)

    def test_process_report_with_failures(self):
        # Create a sample JSON report with failures
        report_data = {
            "request_id": "test-123",
            "reports": [
                {
                    "app_package_id": "test_app",
                    "groups": [
                        {
                            "name": "test_group",
                            "checks": [
                                {
                                    "name": "check_config_file_parsing",
                                    "result": "failure",
                                    "messages": [
                                        {
                                            "message": "Trailing whitespace at line 100",
                                            "message_filename": "default/savedsearches.conf",
                                            "message_line": 100,
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        report_file = os.path.join(self.report_dir, "test_report.json")
        with open(report_file, "w") as f:
            json.dump(report_data, f)

        # Create the file referenced in the report
        conf_dir = os.path.join(self.app_dir, "default")
        os.makedirs(conf_dir)
        conf_file = os.path.join(conf_dir, "savedsearches.conf")
        with open(conf_file, "w") as f:
            f.write("[test]\nkey=value\n")

        # Mock the gat.error function to capture calls
        with (
            patch("helpers.app_inspect_report_commenter.gat.error") as mock_error,
            patch("helpers.app_inspect_report_commenter.gat.info"),
        ):
            commenter = AppInspectReportCommenter(
                report_dir=self.report_dir, app_dir=self.app_dir, include_warnings=False
            )
            commenter.post_comments()

            # Verify that error was called
            assert mock_error.called
            call_args = mock_error.call_args

            # Check that the message was posted
            assert "Trailing whitespace at line 100" in str(call_args)

    def test_process_report_with_warnings_excluded(self):
        # Create a sample JSON report with warnings
        report_data = {
            "request_id": "test-123",
            "reports": [
                {
                    "app_package_id": "test_app",
                    "groups": [
                        {
                            "name": "test_group",
                            "checks": [
                                {
                                    "name": "check_something",
                                    "result": "warning",
                                    "messages": [
                                        {
                                            "message": "This is a warning",
                                            "message_filename": "default/app.conf",
                                            "message_line": 10,
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        report_file = os.path.join(self.report_dir, "test_report.json")
        with open(report_file, "w") as f:
            json.dump(report_data, f)

        # Mock the gat functions
        with (
            patch("helpers.app_inspect_report_commenter.gat.warning") as mock_warning,
            patch("helpers.app_inspect_report_commenter.gat.error") as mock_error,
            patch("helpers.app_inspect_report_commenter.gat.info"),
        ):
            commenter = AppInspectReportCommenter(
                report_dir=self.report_dir, app_dir=self.app_dir, include_warnings=False
            )
            commenter.post_comments()

            # Warnings should not be posted when include_warnings is False
            assert not mock_warning.called
            assert not mock_error.called

    def test_process_report_with_warnings_included(self):
        # Create a sample JSON report with warnings
        report_data = {
            "request_id": "test-123",
            "reports": [
                {
                    "app_package_id": "test_app",
                    "groups": [
                        {
                            "name": "test_group",
                            "checks": [
                                {
                                    "name": "check_something",
                                    "result": "warning",
                                    "messages": [
                                        {
                                            "message": "This is a warning",
                                            "message_filename": "default/app.conf",
                                            "message_line": 10,
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        report_file = os.path.join(self.report_dir, "test_report.json")
        with open(report_file, "w") as f:
            json.dump(report_data, f)

        # Create the file referenced in the report
        conf_dir = os.path.join(self.app_dir, "default")
        os.makedirs(conf_dir)
        conf_file = os.path.join(conf_dir, "app.conf")
        with open(conf_file, "w") as f:
            f.write("[launcher]\nversion=1.0.0\n")

        # Mock the gat functions
        with (
            patch("helpers.app_inspect_report_commenter.gat.warning") as mock_warning,
            patch("helpers.app_inspect_report_commenter.gat.info"),
        ):
            commenter = AppInspectReportCommenter(
                report_dir=self.report_dir, app_dir=self.app_dir, include_warnings=True
            )
            commenter.post_comments()

            # Warnings should be posted when include_warnings is True
            assert mock_warning.called
            call_args = mock_warning.call_args
            assert "This is a warning" in str(call_args)

    def test_no_report_files(self):
        # Test when there are no JSON files in the report directory
        with patch("helpers.app_inspect_report_commenter.gat.debug") as mock_debug:
            commenter = AppInspectReportCommenter(
                report_dir=self.report_dir, app_dir=self.app_dir, include_warnings=False
            )
            commenter.post_comments()

            # Should log that no files were found
            assert mock_debug.called

    def test_message_without_file_details(self):
        # Create a report with a message that has no file details
        report_data = {
            "request_id": "test-123",
            "reports": [
                {
                    "app_package_id": "test_app",
                    "groups": [
                        {
                            "name": "test_group",
                            "checks": [
                                {
                                    "name": "check_general",
                                    "result": "error",
                                    "messages": [
                                        {
                                            "message": "General error without file details",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        report_file = os.path.join(self.report_dir, "test_report.json")
        with open(report_file, "w") as f:
            json.dump(report_data, f)

        # Mock the gat.error function
        with (
            patch("helpers.app_inspect_report_commenter.gat.error") as mock_error,
            patch("helpers.app_inspect_report_commenter.gat.info"),
        ):
            commenter = AppInspectReportCommenter(
                report_dir=self.report_dir, app_dir=self.app_dir, include_warnings=False
            )
            commenter.post_comments()

            # Error should still be posted, but without file/line info
            assert mock_error.called
            call_args = mock_error.call_args
            # file and line should be None
            assert call_args.kwargs.get("file") is None
            assert call_args.kwargs.get("line") is None
