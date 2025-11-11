# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
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

    # Navigate the nested structure: reports > groups > checks
    reports = appinspect_data.get("reports", [])
    if not isinstance(reports, list):
        reports = []

    for report in reports:
        if not isinstance(report, dict):
            continue

        # Get groups from each report
        groups = report.get("groups", [])
        if not isinstance(groups, list):
            continue

        for group in groups:
            if not isinstance(group, dict):
                continue

            # Get checks from each group
            checks = group.get("checks", [])
            if not isinstance(checks, list):
                continue

            for check in checks:
                if not isinstance(check, dict):
                    continue

                result_status = check.get("result", "").lower()
                # Only include failures, errors, and warnings in SARIF
                if result_status not in ["failure", "error", "warning"]:
                    continue

                check_name = check.get("name", "unknown-check")
                rule_id = f"splunk-appinspect/{check_name}"

                # Add rule definition if not already added
                if rule_id not in rule_ids_seen:
                    rule_ids_seen.add(rule_id)
                    rules.append(_create_rule(check, rule_id, check_type))

                # Add results for this check
                check_results = _create_result(check, rule_id)
                results.extend(check_results)

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

    # Add documentation URL
    rule["helpUri"] = _get_check_documentation_url()

    return rule


def _create_result(report: dict[str, Any], rule_id: str) -> list[dict[str, Any]]:
    """Create SARIF result(s) from AppInspect check report. Returns a list of results, one per message."""
    results = []
    messages = report.get("messages", [])
    if not isinstance(messages, list):
        messages = []

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

    description = report.get("description", "")

    # Create a SARIF result for each message
    for msg in messages:
        if not isinstance(msg, dict):
            continue

        msg_text = msg.get("message", "")
        if not msg_text:
            continue

        # Combine description and message text
        combined_message = description + "\n" + msg_text if description else msg_text

        result: dict[str, Any] = {
            "ruleId": rule_id,
            "level": level,
            "message": {"text": combined_message},
        }

        # Add file location from message_filename/message_line
        file_path = msg.get("message_filename")
        line_number = msg.get("message_line")
        if file_path:
            location = {"physicalLocation": {"artifactLocation": {"uri": file_path}}}
            if line_number:
                # Convert line_number to int (it might be a string in the JSON)
                try:
                    if isinstance(line_number, int):
                        line_num_int = line_number
                    else:
                        line_number = line_number.strip().strip('"')
                        line_num_int = int(line_number)
                    location["physicalLocation"]["region"] = {"startLine": line_num_int}
                except (ValueError, TypeError):
                    # If conversion fails, skip adding the region
                    gat.warning(f"Line number to integer conversion failed: {line_number}")
                    pass

            result["locations"] = [location]

        results.append(result)

    # If no messages, create a single result
    if not results:
        results.append(
            {"ruleId": rule_id, "level": level, "message": {"text": "AppInspect check failed"}}
        )

    return results


def _get_check_documentation_url() -> str:
    """
    Get documentation URL for AppInspect checks.

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
