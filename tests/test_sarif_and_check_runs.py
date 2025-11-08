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

import json
import os
import tempfile
import unittest
from pathlib import Path

from helpers.check_run_publisher import (  # pyright: ignore[reportMissingImports]
    _create_check_summary,
    _extract_failed_checks,
)
from helpers.sarif_converter import (  # pyright: ignore[reportMissingImports]
    _create_result,
    _create_rule,
    convert_appinspect_to_sarif,
    merge_sarif_reports,
)


class TestSarifConverter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_create_rule_from_appinspect_check(self):
        report = {
            "name": "check_test_example",
            "description": "This is a test check",
            "result": "failure",
        }
        rule_id = "splunk-appinspect/check_test_example"

        rule = _create_rule(report, rule_id, "app-inspect")

        assert rule["id"] == rule_id
        assert rule["name"] == "check_test_example"
        assert rule["defaultConfiguration"]["level"] == "error"
        assert "splunk" in rule["properties"]["tags"]
        assert "appinspect" in rule["properties"]["tags"]

    def test_create_result_from_appinspect_check(self):
        report = {
            "name": "check_test_example",
            "result": "failure",
            "messages": [{"message": "This check failed"}],
        }
        rule_id = "splunk-appinspect/check_test_example"

        results = _create_result(report, rule_id)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) == 1
        result = results[0]
        assert result["ruleId"] == rule_id
        assert result["level"] == "error"
        assert "This check failed" in result["message"]["text"]

    def test_convert_appinspect_to_sarif(self):
        # Create a sample AppInspect JSON report with the correct nested structure
        appinspect_data = {
            "run_parameters": {"appinspect_version": "4.0.0"},
            "summary": {"failure": 1, "error": 0, "warning": 1},
            "reports": [
                {
                    "groups": [
                        {
                            "name": "test_group",
                            "checks": [
                                {
                                    "name": "check_failure_example",
                                    "description": "Example failure check",
                                    "result": "failure",
                                    "messages": [{"message": "This check failed"}],
                                },
                                {
                                    "name": "check_warning_example",
                                    "description": "Example warning check",
                                    "result": "warning",
                                    "messages": [{"message": "This is a warning"}],
                                },
                                {
                                    "name": "check_success_example",
                                    "description": "Example success check",
                                    "result": "success",
                                    "messages": [],
                                },
                            ],
                        }
                    ]
                }
            ],
        }

        json_path = os.path.join(self.temp_dir, "appinspect.json")
        sarif_path = os.path.join(self.temp_dir, "appinspect.sarif")

        with open(json_path, "w") as f:
            json.dump(appinspect_data, f)

        convert_appinspect_to_sarif(json_path, sarif_path, "app-inspect")

        assert os.path.exists(sarif_path)

        with open(sarif_path) as f:
            sarif_data = json.load(f)

        assert sarif_data["version"] == "2.1.0"
        assert len(sarif_data["runs"]) == 1

        run = sarif_data["runs"][0]
        assert run["tool"]["driver"]["name"] == "Splunk AppInspect"

        # Should have 2 rules (failure and warning, success is excluded)
        assert len(run["tool"]["driver"]["rules"]) == 2

        # Should have 2 results (failure and warning)
        assert len(run["results"]) == 2

    def test_merge_sarif_reports(self):
        # Create two SARIF reports
        sarif1 = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Splunk AppInspect",
                            "rules": [
                                {
                                    "id": "rule1",
                                    "name": "Rule 1",
                                    "shortDescription": {"text": "Rule 1"},
                                }
                            ],
                        }
                    },
                    "results": [
                        {
                            "ruleId": "rule1",
                            "level": "error",
                            "message": {"text": "Error 1"},
                        }
                    ],
                }
            ],
        }

        sarif2 = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Splunk AppInspect",
                            "rules": [
                                {
                                    "id": "rule2",
                                    "name": "Rule 2",
                                    "shortDescription": {"text": "Rule 2"},
                                }
                            ],
                        }
                    },
                    "results": [
                        {
                            "ruleId": "rule2",
                            "level": "warning",
                            "message": {"text": "Warning 1"},
                        }
                    ],
                }
            ],
        }

        sarif1_path = os.path.join(self.temp_dir, "sarif1.sarif")
        sarif2_path = os.path.join(self.temp_dir, "sarif2.sarif")
        merged_path = os.path.join(self.temp_dir, "merged.sarif")

        with open(sarif1_path, "w") as f:
            json.dump(sarif1, f)
        with open(sarif2_path, "w") as f:
            json.dump(sarif2, f)

        merge_sarif_reports([sarif1_path, sarif2_path], merged_path)

        assert os.path.exists(merged_path)

        with open(merged_path) as f:
            merged_data = json.load(f)

        assert merged_data["version"] == "2.1.0"
        run = merged_data["runs"][0]

        # Should have 2 rules merged
        assert len(run["tool"]["driver"]["rules"]) == 2

        # Should have 2 results merged
        assert len(run["results"]) == 2


class TestCheckRunPublisher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_extract_failed_checks(self):
        report_data = {
            "reports": [
                {"name": "check1", "result": "failure"},
                {"name": "check2", "result": "error"},
                {"name": "check3", "result": "success"},
                {"name": "check4", "result": "warning"},
            ]
        }

        failed_checks = _extract_failed_checks(report_data)

        assert len(failed_checks) == 2
        assert "check1" in failed_checks
        assert "check2" in failed_checks
        assert "check3" not in failed_checks

    def test_create_check_summary(self):
        # Create a sample report
        report_data = {
            "summary": {
                "success": 10,
                "failure": 2,
                "error": 1,
                "warning": 3,
                "manual_check": 5,
                "skipped": 1,
                "not_applicable": 2,
            },
            "reports": [
                {"name": "failed_check_1", "result": "failure"},
                {"name": "error_check_1", "result": "error"},
            ],
        }

        report_path = Path(self.temp_dir)
        report_file = report_path / "test_app_inspect_check.json"

        with report_file.open("w") as f:
            json.dump(report_data, f)

        summary = _create_check_summary(report_path, "app_inspect_check.json", "Failure")

        assert "**Status:** Failure" in summary
        assert "Success: 10" in summary
        assert "Failures: 2" in summary
        assert "Errors: 1" in summary
        assert "Warnings: 3" in summary
        assert "**Failed Checks:**" in summary
        assert "failed_check_1" in summary
        assert "error_check_1" in summary


if __name__ == "__main__":
    unittest.main()
