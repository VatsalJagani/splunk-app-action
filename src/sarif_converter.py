"""Convert AppInspect JSON results to SARIF format for GitHub Code Scanning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import github_action_toolkit as gat


def convert_appinspect_to_sarif(
    json_report_path: str | Path,
    output_sarif_path: str | Path,
    check_type: str = "app-inspect",
) -> None:
    """
    Convert AppInspect JSON report to SARIF format.

    Args:
        json_report_path: Path to the AppInspect JSON report
        output_sarif_path: Path where SARIF file should be written
        check_type: Type of check (app-inspect, cloud-inspect, ssai-inspect)
    """
    try:
        json_path = Path(json_report_path)
        sarif_path = Path(output_sarif_path)

        if not json_path.exists():
            gat.warning(f"AppInspect JSON report not found: {json_path}")
            return

        with json_path.open() as f:
            appinspect_data = json.load(f)

        sarif_report = _build_sarif_report(appinspect_data, check_type)

        sarif_path.parent.mkdir(parents=True, exist_ok=True)
        with sarif_path.open("w") as f:
            json.dump(sarif_report, f, indent=2)

        gat.info(f"SARIF report generated: {sarif_path}")

    except Exception as e:
        gat.error(f"Failed to convert AppInspect to SARIF: {e}")
        raise


def _build_sarif_report(appinspect_data: dict[str, Any], check_type: str) -> dict[str, Any]:
    """Build SARIF report structure from AppInspect data."""
    rules: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    rule_ids_seen: set[str] = set()

    reports = appinspect_data.get("reports", [])
    if not isinstance(reports, list):
        reports = []

    for report in reports:
        if not isinstance(report, dict):
            continue

        result_status = report.get("result", "").lower()
        # Only include failures, errors, and warnings in SARIF
        if result_status not in ["failure", "error", "warning"]:
            continue

        check_name = report.get("name", "unknown-check")
        rule_id = f"splunk-appinspect/{check_name}"

        # Add rule definition if not already added
        if rule_id not in rule_ids_seen:
            rule_ids_seen.add(rule_id)
            rules.append(_create_rule(report, rule_id, check_type))

        # Add result for this check
        result = _create_result(report, rule_id)
        if result:
            results.append(result)

    sarif_report = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Splunk AppInspect",
                        "informationUri": "https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/",
                        "version": appinspect_data.get("run_parameters", {}).get(
                            "appinspect_version", "unknown"
                        ),
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }

    return sarif_report


def _create_rule(report: dict[str, Any], rule_id: str, check_type: str) -> dict[str, Any]:
    """Create SARIF rule definition from AppInspect check."""
    check_name = report.get("name", "unknown-check")
    description = report.get("description", "AppInspect check")

    # Map AppInspect result to SARIF level
    result_status = report.get("result", "").lower()
    if result_status == "failure":
        default_level = "error"
    elif result_status == "error":
        default_level = "error"
    elif result_status == "warning":
        default_level = "warning"
    else:
        default_level = "note"

    rule = {
        "id": rule_id,
        "name": check_name,
        "shortDescription": {"text": check_name.replace("_", " ").title()},
        "fullDescription": {"text": description},
        "defaultConfiguration": {"level": default_level},
        "help": {"text": description},
        "properties": {
            "tags": ["splunk", "appinspect", check_type],
        },
    }

    # Add documentation URL if available
    doc_url = _get_check_documentation_url(check_name)
    if doc_url:
        rule["helpUri"] = doc_url

    return rule


def _create_result(report: dict[str, Any], rule_id: str) -> dict[str, Any] | None:
    """Create SARIF result from AppInspect check report."""
    messages = report.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    # Combine all message texts
    message_texts = []
    for msg in messages:
        if isinstance(msg, dict):
            msg_text = msg.get("message", "")
            if msg_text:
                message_texts.append(msg_text)

    if not message_texts:
        message_texts = ["AppInspect check failed"]

    combined_message = "\n".join(message_texts)

    # Map AppInspect result to SARIF level
    result_status = report.get("result", "").lower()
    if result_status == "failure":
        level = "error"
    elif result_status == "error":
        level = "error"
    elif result_status == "warning":
        level = "warning"
    else:
        level = "note"

    result: dict[str, Any] = {
        "ruleId": rule_id,
        "level": level,
        "message": {"text": combined_message},
    }

    # Try to extract file location from messages
    file_path = _extract_file_path(messages)
    if file_path:
        result["locations"] = [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": file_path},
                }
            }
        ]

    return result


def _extract_file_path(messages: list[dict[str, Any]]) -> str | None:
    """
    Extract file path from AppInspect message.

    AppInspect messages may contain file paths in various formats.
    This attempts to extract them heuristically.
    """
    for msg in messages:
        if not isinstance(msg, dict):
            continue

        # Check if there's a file_path field
        if "file_path" in msg:
            return str(msg["file_path"])

        # Check message text for common file path patterns
        msg_text = msg.get("message", "")
        if isinstance(msg_text, str):
            # Look for patterns like "in file: path/to/file" or "File: path/to/file"
            import re

            # Pattern for "in <file>" or "file: <path>"
            patterns = [
                r"(?:in|file:?)\s+([^\s,]+\.\w+)",
                r"`([^`]+\.\w+)`",
                r'"([^"]+\.\w+)"',
            ]

            for pattern in patterns:
                match = re.search(pattern, msg_text, re.IGNORECASE)
                if match:
                    return match.group(1)

    return None


def _get_check_documentation_url(check_name: str) -> str | None:
    """
    Get documentation URL for a specific AppInspect check.

    Returns the general AppInspect documentation URL as we don't have
    check-specific URLs readily available.
    """
    return "https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/appinspectreferencetopics/"


def merge_sarif_reports(sarif_paths: list[str | Path], output_path: str | Path) -> None:
    """
    Merge multiple SARIF reports into a single report.

    Args:
        sarif_paths: List of paths to SARIF files to merge
        output_path: Path where merged SARIF file should be written
    """
    try:
        all_rules: list[dict[str, Any]] = []
        all_results: list[dict[str, Any]] = []
        rule_ids_seen: set[str] = set()

        # Read and merge all SARIF reports
        for sarif_path in sarif_paths:
            path = Path(sarif_path)
            if not path.exists():
                gat.warning(f"SARIF file not found: {path}")
                continue

            with path.open() as f:
                sarif_data = json.load(f)

            runs = sarif_data.get("runs", [])
            if not isinstance(runs, list) or not runs:
                continue

            run = runs[0]
            driver = run.get("tool", {}).get("driver", {})
            rules = driver.get("rules", [])
            results = run.get("results", [])

            # Add unique rules
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                rule_id = rule.get("id", "")
                if rule_id and rule_id not in rule_ids_seen:
                    rule_ids_seen.add(rule_id)
                    all_rules.append(rule)

            # Add all results
            if isinstance(results, list):
                all_results.extend(results)

        # Create merged SARIF report
        merged_report = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Splunk AppInspect",
                            "informationUri": "https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/",
                            "version": "merged",
                            "rules": all_rules,
                        }
                    },
                    "results": all_results,
                }
            ],
        }

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w") as f:
            json.dump(merged_report, f, indent=2)

        gat.info(f"Merged SARIF report generated: {output}")

    except Exception as e:
        gat.error(f"Failed to merge SARIF reports: {e}")
        raise
