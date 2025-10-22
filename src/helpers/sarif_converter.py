"""
Convert Splunk AppInspect JSON reports to SARIF format for GitHub Code Scanning.

SARIF (Static Analysis Results Interchange Format) is a standard JSON format
for representing static analysis results. GitHub Code Scanning supports SARIF
uploads for inline annotations and quality gates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import github_action_toolkit as gat


class SARIFConverter:
    """Convert AppInspect JSON reports to SARIF format."""

    SARIF_VERSION = "2.1.0"
    SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

    def __init__(
        self,
        tool_name: str = "Splunk AppInspect",
        tool_version: str = "4.0.2",
    ) -> None:
        """
        Initialize SARIF converter.

        Args:
            tool_name: Name of the analysis tool
            tool_version: Version of the analysis tool
        """
        self.tool_name = tool_name
        self.tool_version = tool_version

    def convert_to_sarif(
        self,
        appinspect_json_path: str | Path,
        check_type: str = "APP_INSPECT",
    ) -> dict[str, Any]:
        """
        Convert AppInspect JSON report to SARIF format.

        Args:
            appinspect_json_path: Path to AppInspect JSON report
            check_type: Type of check (APP_INSPECT, CLOUD_INSPECT, SSAI_INSPECT)

        Returns:
            SARIF report as dictionary
        """
        gat.debug(f"Converting AppInspect report to SARIF: {appinspect_json_path}")

        # Load AppInspect report
        with open(appinspect_json_path) as f:
            appinspect_data_raw = json.load(f)
            if not isinstance(appinspect_data_raw, dict):
                gat.error("Unexpected AppInspect report format: root is not a dict")
                return self._create_empty_sarif()
            appinspect_data: dict[str, Any] = cast(dict[str, Any], appinspect_data_raw)

        # Create SARIF structure
        sarif = {
            "$schema": self.SARIF_SCHEMA,
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": f"{self.tool_name} ({check_type})",
                            "version": self.tool_version,
                            "informationUri": "https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/",
                            "rules": self._extract_rules(appinspect_data),
                        }
                    },
                    "results": self._convert_results(appinspect_data),
                }
            ],
        }

        return sarif

    def _create_empty_sarif(self) -> dict[str, Any]:
        """Create an empty SARIF report."""
        return {
            "$schema": self.SARIF_SCHEMA,
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "version": self.tool_version,
                            "informationUri": "https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

    def _extract_rules(self, appinspect_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract rules from AppInspect report, handling nested groups/checks.
        Each unique check name becomes a SARIF rule.
        """
        reports = appinspect_data.get("reports", [])
        if not isinstance(reports, list):
            return []

        rules: dict[str, dict[str, Any]] = {}
        for report in reports:
            if not isinstance(report, dict):
                continue
            # Handle nested groups/checks
            groups = report.get("groups")
            if isinstance(groups, list):
                for group in groups:
                    checks = group.get("checks") if isinstance(group, dict) else None
                    if isinstance(checks, list):
                        for check in checks:
                            if not isinstance(check, dict):
                                continue
                            check_name = str(check.get("name", "unknown_check"))
                            if check_name not in rules:
                                description = str(check.get("description", ""))
                                tags = check.get("tags", [])
                                if not isinstance(tags, list):
                                    tags = []
                                rules[check_name] = {
                                    "id": check_name,
                                    "name": check_name,
                                    "shortDescription": {"text": description[:100] if description else check_name},
                                    "fullDescription": {"text": description if description else check_name},
                                    "helpUri": "https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/",
                                    "properties": {
                                        "tags": [str(t) for t in tags],
                                    },
                                }
        return list(rules.values())

    def _convert_results(self, appinspect_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Convert AppInspect check results to SARIF results, handling nested groups/checks.
        """
        reports = appinspect_data.get("reports", [])
        if not isinstance(reports, list):
            return []

        sarif_results: list[dict[str, Any]] = []

        for report in reports:
            if not isinstance(report, dict):
                continue
            groups = report.get("groups")
            if isinstance(groups, list):
                for group in groups:
                    checks = group.get("checks") if isinstance(group, dict) else None
                    if isinstance(checks, list):
                        for check in checks:
                            if not isinstance(check, dict):
                                continue
                            result_type = str(check.get("result", "unknown"))
                            check_name = str(check.get("name", "unknown_check"))
                            if result_type not in ["failure", "error", "warning", "manual_check"]:
                                continue
                            level = self._map_result_to_level(result_type)
                            description = str(check.get("description", ""))
                            messages = check.get("messages", [])
                            if not isinstance(messages, list):
                                messages = []
                            for msg in messages:
                                if not isinstance(msg, dict):
                                    continue
                                # Compose SARIF message as description + message
                                message_text = str(msg.get("message", ""))
                                sarif_message = description + ("\n" if description and message_text else "") + message_text
                                # Prefer message_filename and message_line for location
                                msg_file = msg.get("message_filename")
                                msg_line = msg.get("message_line")
                                if msg_file and msg_line:
                                    location = {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": str(msg_file)},
                                            "region": {"startLine": int(msg_line)},
                                        }
                                    }
                                elif msg_file:
                                    location = {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": str(msg_file)},
                                        }
                                    }
                                else:
                                    # fallback to filename/line or extract from message text
                                    file_path = msg.get("filename") or msg.get("file_path")
                                    line_number = msg.get("line_number") or msg.get("line")
                                    location = {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": str(file_path) if file_path else "app/"},
                                        }
                                    }
                                    if line_number:
                                        try:
                                            location["physicalLocation"]["region"] = {"startLine": int(line_number)}
                                        except Exception:
                                            pass
                                sarif_result = {
                                    "ruleId": check_name,
                                    "level": level,
                                    "message": {"text": sarif_message},
                                    "locations": [location],
                                }
                                sarif_results.append(sarif_result)
        return sarif_results

    def _map_result_to_level(self, result_type: str) -> str:
        """
        Map AppInspect result type to SARIF level.

        SARIF levels: error, warning, note, none
        """
        mapping = {
            "failure": "error",
            "error": "error",
            "warning": "warning",
            "manual_check": "note",
        }
        return mapping.get(result_type, "warning")

    def save_sarif(self, sarif_data: dict[str, Any], output_path: str | Path) -> None:
        """
        Save SARIF data to file.

        Args:
            sarif_data: SARIF report dictionary
            output_path: Path to save SARIF file
        """
        with open(output_path, "w") as f:
            json.dump(sarif_data, f, indent=2)
        gat.info(f"SARIF report saved to: {output_path}")

    def convert_and_save(
        self,
        appinspect_json_path: str | Path,
        output_path: str | Path,
        check_type: str = "APP_INSPECT",
    ) -> None:
        """
        Convert AppInspect JSON to SARIF and save to file.

        Args:
            appinspect_json_path: Path to AppInspect JSON report
            output_path: Path to save SARIF file
            check_type: Type of check (APP_INSPECT, CLOUD_INSPECT, SSAI_INSPECT)
        """
        sarif_data = self.convert_to_sarif(appinspect_json_path, check_type)
        self.save_sarif(sarif_data, output_path)
