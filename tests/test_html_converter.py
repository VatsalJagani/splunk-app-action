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

from helpers.splunk_app_inspect_report_json_to_html_converter import (  # pyright: ignore[reportMissingImports]
    convert_json_file_to_html_file,
    convert_json_to_html,
    escape_html,
    get_status_icon,
)

MINIMAL_REPORT = {
    "request_id": "req-123",
    "reports": [
        {
            "app_name": "test_app",
            "app_description": "A test app",
            "app_author": "tester",
            "app_version": "1.0.0",
            "app_hash": "abc123",
            "run_parameters": {"appinspect_version": "2.0.0"},
            "metrics": {"execution_time": "5.5"},
            "summary": {
                "success": 10,
                "failure": 1,
                "error": 0,
                "warning": 2,
                "not_applicable": 3,
                "skipped": 0,
            },
            "groups": [
                {
                    "name": "basic_checks",
                    "description": "Basic validation checks",
                    "checks": [
                        {
                            "name": "check_app_conf",
                            "description": "Validates app.conf",
                            "result": "success",
                            "tags": ["splunk_appinspect"],
                            "messages": [],
                        }
                    ],
                }
            ],
        }
    ],
}


class TestEscapeHtml(unittest.TestCase):
    def test_escapes_special_characters(self):
        assert escape_html('<script>alert("xss")</script>') == (
            "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
        )

    def test_escapes_ampersand(self):
        assert escape_html("foo & bar") == "foo &amp; bar"

    def test_escapes_single_quotes(self):
        assert escape_html("it's") == "it&#39;s"

    def test_returns_empty_for_none(self):
        assert escape_html(None) == ""

    def test_returns_empty_for_empty(self):
        assert escape_html("") == ""


class TestGetStatusIcon(unittest.TestCase):
    def test_known_statuses_return_svg(self):
        for status in ["success", "failure", "error", "warning", "not_applicable", "skipped"]:
            icon = get_status_icon(status)
            assert "<svg" in icon, f"Expected SVG for status '{status}'"
            assert f"check_{status}" in icon

    def test_unknown_status_returns_empty(self):
        assert get_status_icon("unknown_status") == ""


class TestConvertJsonToHtml(unittest.TestCase):
    def test_minimal_report(self):
        html = convert_json_to_html(MINIMAL_REPORT)
        assert "<!DOCTYPE html>" in html
        assert "test_app" in html
        assert "A test app" in html
        assert "tester" in html
        assert "1.0.0" in html
        assert "abc123" in html
        assert "req-123" in html
        assert "basic_checks" in html
        assert "check_app_conf" in html

    def test_missing_reports_raises(self):
        with self.assertRaises(ValueError, msg="missing 'reports' field"):
            convert_json_to_html({})

    def test_empty_reports_raises(self):
        with self.assertRaises(ValueError):
            convert_json_to_html({"reports": []})

    def test_summary_counts_in_html(self):
        html = convert_json_to_html(MINIMAL_REPORT)
        assert "<td>10</td>" in html
        assert "<td>1</td>" in html
        assert "<td>2</td>" in html

    def test_tags_displayed(self):
        html = convert_json_to_html(MINIMAL_REPORT)
        assert "splunk_appinspect" in html


class TestConvertJsonFileToHtmlFile(unittest.TestCase):
    def test_file_io_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "report.json")
            html_path = os.path.join(tmpdir, "report.html")

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(MINIMAL_REPORT, f)

            convert_json_file_to_html_file(json_path, html_path)

            assert os.path.isfile(html_path)
            with open(html_path, encoding="utf-8") as f:
                content = f.read()
            assert "<!DOCTYPE html>" in content
            assert "test_app" in content
