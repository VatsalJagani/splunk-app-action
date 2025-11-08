"""
Module for posting app inspect reports as GitHub PR comments/annotations.

This module parses Splunk app inspect JSON reports and posts failures, errors,
and optionally warnings as GitHub Actions file annotations.
"""

# pyright: reportUnknownVariableType=false

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import github_action_toolkit as gat


class AppInspectReportCommenter:
    """
    Parse app inspect JSON reports and post findings as PR comments/annotations.
    """

    def __init__(
        self,
        report_dir: str,
        app_dir: str,
        include_warnings: bool = False,
    ) -> None:
        """
        Initialize the commenter.

        Args:
            report_dir: Directory containing the app inspect JSON reports
            app_dir: The app directory path (for resolving file paths)
            include_warnings: Whether to include warnings in addition to errors/failures
        """
        self.report_dir: str = report_dir
        self.app_dir: str = app_dir
        self.include_warnings: bool = include_warnings

    def post_comments(self) -> None:
        """
        Parse all JSON reports in the report directory and post comments.
        """
        report_dir_path = Path(self.report_dir)

        if not report_dir_path.exists():
            gat.debug(f"Report directory not found: {self.report_dir}")
            return

        json_files = list(report_dir_path.glob("*.json"))

        if not json_files:
            gat.debug(f"No JSON report files found in {self.report_dir}")
            return

        gat.info(f"Processing {len(json_files)} app inspect report(s)")

        total_issues_posted = 0

        for json_file in json_files:
            gat.debug(f"Processing report: {json_file.name}")
            try:
                issues_count = self._process_report(json_file)
                total_issues_posted += issues_count
            except Exception as e:
                gat.warning(f"Error processing report {json_file.name}: {e}")

        if total_issues_posted > 0:
            gat.info(f"Posted {total_issues_posted} app inspect issue(s) as annotations")
        else:
            gat.info("No app inspect issues to report")

    def _process_report(self, json_file: Path) -> int:
        """
        Process a single JSON report file and post comments.

        Args:
            json_file: Path to the JSON report file

        Returns:
            Number of issues posted
        """
        with json_file.open() as f:
            report_data_raw = json.load(f)

        if not isinstance(report_data_raw, dict):
            gat.warning(f"Unexpected report format in {json_file.name}: root is not a dict")
            return 0

        report_data: dict[str, Any] = cast(dict[str, Any], report_data_raw)

        # Get the reports array
        reports_val = report_data.get("reports", [])
        if not isinstance(reports_val, list):
            gat.debug(f"No reports array found in {json_file.name}")
            return 0

        reports: list[dict[str, Any]] = [
            cast(dict[str, Any], r) for r in reports_val if isinstance(r, dict)
        ]

        issues_count = 0

        for report in reports:
            # Get groups array from the report
            groups_val = report.get("groups", [])
            if not isinstance(groups_val, list):
                continue

            groups: list[dict[str, Any]] = [
                cast(dict[str, Any], g) for g in groups_val if isinstance(g, dict)
            ]

            for group in groups:
                # Get checks array from the group
                checks_val = group.get("checks", [])
                if not isinstance(checks_val, list):
                    continue

                checks: list[dict[str, Any]] = [
                    cast(dict[str, Any], c) for c in checks_val if isinstance(c, dict)
                ]

                for check in checks:
                    issues_count += self._process_check(check)

        return issues_count

    def _process_check(self, check: dict[str, Any]) -> int:
        """
        Process a single check and post comments for its messages.

        Args:
            check: The check dictionary

        Returns:
            Number of issues posted from this check
        """
        result = check.get("result", "")
        check_name = check.get("name", "Unknown check")

        # Determine if we should process this check based on result type
        should_process = False
        is_warning = False

        if result in ["failure", "error"]:
            should_process = True
        elif result == "warning" and self.include_warnings:
            should_process = True
            is_warning = True

        if not should_process:
            return 0

        messages_val = check.get("messages", [])
        if not isinstance(messages_val, list):
            return 0

        messages: list[dict[str, Any]] = [
            cast(dict[str, Any], m) for m in messages_val if isinstance(m, dict)
        ]

        issues_count = 0

        for message in messages:
            self._post_message_annotation(message, check_name, is_warning)
            issues_count += 1

        return issues_count

    def _post_message_annotation(
        self, message: dict[str, Any], check_name: str, is_warning: bool
    ) -> None:
        """
        Post a single message as a GitHub annotation.

        Args:
            message: Message dictionary from the report
            check_name: Name of the check that generated this message
            is_warning: Whether this is a warning (vs error/failure)
        """
        message_text = message.get("message", "No message provided")
        message_filename = message.get("message_filename")
        message_line = message.get("message_line")

        # Build the annotation title
        title = f"App Inspect: {check_name}"

        # Determine the full file path relative to repo root
        file_path = None
        if message_filename:
            # The message_filename is relative to app directory
            # We need to make it relative to the repo root
            file_path = self._resolve_file_path(message_filename)

        # Post the annotation
        if is_warning:
            gat.warning(
                message_text,
                title=title,
                file=file_path,
                line=message_line,
            )
        else:
            gat.error(
                message_text,
                title=title,
                file=file_path,
                line=message_line,
            )

    def _resolve_file_path(self, relative_path: str) -> str | None:
        """
        Resolve a file path from app-relative to repo-relative.

        Args:
            relative_path: File path relative to the app directory

        Returns:
            File path relative to the repository root, or None if cannot be resolved
        """
        # Construct the full path
        full_path = Path(self.app_dir) / relative_path

        # Check if the file exists
        if not full_path.exists():
            gat.debug(f"File not found: {full_path}")
            return None

        # Return the path as a string relative to the current working directory
        # (which should be the repo root)
        try:
            # Get current working directory
            cwd = Path.cwd()
            # Make the path relative to cwd
            relative_to_repo = full_path.relative_to(cwd)
            return str(relative_to_repo)
        except ValueError:
            # If the path is not relative to cwd, return the app-relative path
            return str(Path(self.app_dir) / relative_path)
