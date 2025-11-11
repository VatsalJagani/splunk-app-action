# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
"""Publish AppInspect results as GitHub workflow annotations."""

from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

import github_action_toolkit as gat


def publish_appinspect_annotations(
    json_report_path: str | Path,
    check_type: str = "app-inspect",
    app_dir: str = ".",
) -> None:
    """
    Publish AppInspect results as GitHub annotations (warnings and errors).

    Args:
        json_report_path: Path to the AppInspect JSON report
        check_type: Type of check (app-inspect, cloud-inspect, ssai-inspect)
        app_dir: App directory path relative to repository root (e.g., "." or "my_app")
    """
    try:
        json_path = Path(json_report_path)

        if not json_path.exists():
            gat.debug(f"AppInspect JSON report not found: {json_path}")
            return

        with json_path.open() as f:
            appinspect_data = json.load(f)

        _publish_annotations_from_data(appinspect_data, check_type, app_dir)

    except Exception as e:
        gat.warning(f"Failed to publish {check_type} annotations: {e}")
        gat.debug(traceback.format_exc())
        # Don't fail the whole run if annotation publishing fails


def _publish_annotations_from_data(
    appinspect_data: dict[str, Any], check_type: str, app_dir: str
) -> None:
    """Publish GitHub annotations from AppInspect data."""
    annotation_count = 0

    # Navigate the nested structure: reports > groups > checks
    reports = appinspect_data.get("reports", [])
    if not isinstance(reports, list):
        reports = []

    for report in reports:
        if not isinstance(report, dict):
            continue

        groups = report.get("groups", [])
        if not isinstance(groups, list):
            continue

        for group in groups:
            if not isinstance(group, dict):
                continue

            checks = group.get("checks", [])
            if not isinstance(checks, list):
                continue

            for check in checks:
                if not isinstance(check, dict):
                    continue

                result_status = check.get("result", "").lower()
                # Only publish failures, errors, and warnings
                if result_status not in ["failure", "error", "warning"]:
                    continue

                annotation_count += _publish_check_annotation(check, check_type, app_dir)

    if annotation_count > 0:
        gat.info(f"Published {annotation_count} {check_type} annotations")
    else:
        gat.debug(f"No {check_type} annotations to publish")


def _publish_check_annotation(check: dict[str, Any], check_type: str, app_dir: str) -> int:
    """
    Publish a single check as GitHub annotation(s). Returns count of annotations published.

    Args:
        check: AppInspect check data
        check_type: Type of check (app-inspect, cloud-inspect, ssai-inspect)
        app_dir: App directory path to prepend to file paths
    """
    count = 0
    check_name = check.get("name", "unknown-check")
    description = check.get("description", "")
    result_status = check.get("result", "").lower()

    messages = check.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    # Determine title based on check type
    title_prefix = check_type.replace("-inspect", "").upper()
    title = f"{title_prefix}: {check_name.replace('_', ' ').title()}"

    # Publish annotation for each message
    for msg in messages:
        if not isinstance(msg, dict):
            continue

        msg_text = msg.get("message", "")
        if not msg_text:
            continue

        # Combine description and message text
        combined_message = description + "\n" + msg_text if description else msg_text

        # Get file location
        file_path = msg.get("message_filename")
        line_number = msg.get("message_line")

        # Prepare annotation parameters
        annotation_kwargs: dict[str, Any] = {
            "message": combined_message,
            "title": title,
        }

        if file_path:
            # Prepend app_dir to file path if app_dir is not "."
            if app_dir != ".":
                file_path = f"{app_dir}/{file_path}"
            annotation_kwargs["file"] = file_path

        if line_number:
            # Convert line_number to int
            try:
                if isinstance(line_number, int):
                    line_num_int = line_number
                else:
                    line_number = line_number.strip().strip('"')
                    line_num_int = int(line_number)
                annotation_kwargs["line"] = line_num_int
            except (ValueError, TypeError):
                gat.debug(f"Line number conversion failed: {line_number}")

        # Publish as error or warning based on result status
        if result_status in ["failure", "error"]:
            gat.error(**annotation_kwargs)
        else:
            gat.warning(**annotation_kwargs)

        count += 1

    # If no messages, publish a single annotation without location
    if count == 0:
        combined_message = description if description else "AppInspect check failed"
        if result_status in ["failure", "error"]:
            gat.error(message=combined_message, title=title)
        else:
            gat.warning(message=combined_message, title=title)
        count = 1

    return count
