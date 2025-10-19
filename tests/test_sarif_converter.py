"""Tests for SARIF converter."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from src.sarif_converter import SARIFConverter


def test_sarif_converter_basic():
    """Test basic SARIF conversion."""
    # Create sample AppInspect JSON data
    appinspect_data = {
        "summary": {
            "success": 10,
            "failure": 2,
            "error": 1,
            "warning": 3,
            "manual_check": 1,
            "not_applicable": 5,
            "skipped": 0,
        },
        "reports": [
            {
                "name": "check_required_files",
                "result": "failure",
                "description": "Check that required files are present",
                "messages": [
                    {
                        "message": "Missing required file: README.md",
                        "filename": "app.conf",
                        "line_number": 1,
                    }
                ],
                "tags": ["packaging"],
            },
            {
                "name": "check_python_version",
                "result": "error",
                "description": "Check Python version compatibility",
                "messages": [{"message": "Python version not specified"}],
                "tags": ["python"],
            },
            {
                "name": "check_deprecated_features",
                "result": "warning",
                "description": "Check for deprecated features",
                "messages": [{"message": "Using deprecated API call"}],
                "tags": ["deprecation"],
            },
        ],
    }

    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(appinspect_data, f)
        temp_json_path = f.name

    try:
        # Convert to SARIF
        converter = SARIFConverter()
        sarif_data = converter.convert_to_sarif(temp_json_path, "APP_INSPECT")

        # Verify SARIF structure
        assert sarif_data["version"] == "2.1.0"
        assert "$schema" in sarif_data
        assert "runs" in sarif_data
        assert len(sarif_data["runs"]) == 1

        run = sarif_data["runs"][0]
        assert "tool" in run
        assert "results" in run

        # Verify tool info
        tool = run["tool"]["driver"]
        assert "Splunk AppInspect" in tool["name"]
        assert "rules" in tool

        # Verify rules
        rules = tool["rules"]
        assert len(rules) == 3
        rule_ids = [r["id"] for r in rules]
        assert "check_required_files" in rule_ids
        assert "check_python_version" in rule_ids
        assert "check_deprecated_features" in rule_ids

        # Verify results
        results = run["results"]
        assert len(results) == 3

        # Check that failures and errors are converted
        levels = [r["level"] for r in results]
        assert "error" in levels
        assert "warning" in levels

        # Verify location information
        result_with_location = [r for r in results if r["ruleId"] == "check_required_files"][0]
        assert "locations" in result_with_location
        assert len(result_with_location["locations"]) > 0

    finally:
        # Clean up
        os.unlink(temp_json_path)


def test_sarif_converter_empty_report():
    """Test SARIF conversion with empty report."""
    appinspect_data = {"summary": {}, "reports": []}

    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(appinspect_data, f)
        temp_json_path = f.name

    try:
        converter = SARIFConverter()
        sarif_data = converter.convert_to_sarif(temp_json_path, "APP_INSPECT")

        # Verify empty SARIF structure
        assert sarif_data["version"] == "2.1.0"
        assert len(sarif_data["runs"]) == 1
        assert len(sarif_data["runs"][0]["results"]) == 0

    finally:
        os.unlink(temp_json_path)


def test_sarif_converter_save():
    """Test saving SARIF to file."""
    appinspect_data = {
        "summary": {"success": 1},
        "reports": [
            {
                "name": "test_check",
                "result": "success",
                "description": "Test check",
                "messages": [],
            }
        ],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create JSON file
        json_path = Path(temp_dir) / "appinspect.json"
        with open(json_path, "w") as f:
            json.dump(appinspect_data, f)

        # Convert and save
        sarif_path = Path(temp_dir) / "appinspect.sarif"
        converter = SARIFConverter()
        converter.convert_and_save(json_path, sarif_path)

        # Verify file was created
        assert sarif_path.exists()

        # Verify file contains valid JSON
        with open(sarif_path) as f:
            sarif_data = json.load(f)
        assert sarif_data["version"] == "2.1.0"


def test_sarif_level_mapping():
    """Test that AppInspect result types are correctly mapped to SARIF levels."""
    appinspect_data = {
        "summary": {},
        "reports": [
            {"name": "check1", "result": "failure", "messages": [{"message": "Test"}]},
            {"name": "check2", "result": "error", "messages": [{"message": "Test"}]},
            {"name": "check3", "result": "warning", "messages": [{"message": "Test"}]},
            {
                "name": "check4",
                "result": "manual_check",
                "messages": [{"message": "Test"}],
            },
            {"name": "check5", "result": "success", "messages": []},  # Should not be included
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(appinspect_data, f)
        temp_json_path = f.name

    try:
        converter = SARIFConverter()
        sarif_data = converter.convert_to_sarif(temp_json_path)

        results = sarif_data["runs"][0]["results"]

        # Success should not be included
        assert len(results) == 4

        # Check level mappings
        result_levels = {r["ruleId"]: r["level"] for r in results}
        assert result_levels["check1"] == "error"
        assert result_levels["check2"] == "error"
        assert result_levels["check3"] == "warning"
        assert result_levels["check4"] == "note"

    finally:
        os.unlink(temp_json_path)
