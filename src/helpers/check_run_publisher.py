# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
"""Publish AppInspect results as GitHub Check Runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import github_action_toolkit as gat


def create_check_run(
    check_name: str,
    title: str,
    summary: str,
    status: str = "Passed",
    details_url: str | None = None,
) -> None:
    """
    Create a GitHub Check Run for AppInspect results.

    Uses the GitHub Actions Toolkit to create check runs that appear
    in the PR checks UI.

    Args:
        check_name: Name of the check (e.g., "AppInspect", "Cloud-Inspect")
        title: Title for the check run
        summary: Summary text for the check
        status: Status from AppInspect (Passed, Failure, Error, etc.)
        details_url: Optional URL to detailed report
    """
    # Map AppInspect status to GitHub check conclusion
    status_lower = status.lower()
    if status_lower == "passed":
        conclusion = "success"
        emoji = "✅"
    elif status_lower in ["failure", "error"]:
        conclusion = "failure"
        emoji = "❌"
    elif status_lower == "timed-out":
        conclusion = "timed_out"
        emoji = "⏱️"
    elif status_lower == "skipped":
        conclusion = "skipped"
        emoji = "⏭️"
    else:
        conclusion = "neutral"
        emoji = "⚪"

    # Format the check output
    output_title = f"{emoji} {title}"
    output_summary = summary

    # Add details URL if available
    if details_url:
        output_summary += f"\n\n📄 [View detailed report]({details_url})"

    # GitHub Actions doesn't have direct check run API in the toolkit,
    # but we can use annotations and summaries to provide similar functionality
    gat.info(f"Check Run: {check_name} - {output_title}")
    gat.info(f"Summary: {output_summary}")

    # Add as notice/warning/error based on conclusion
    if conclusion == "success":
        gat.notice(f"{check_name}: {output_title}")
    elif conclusion == "failure":
        gat.error(f"{check_name}: {output_title}")
    else:
        gat.warning(f"{check_name}: {output_title}")


def publish_appinspect_check_runs(
    app_inspect_status: str,
    cloud_inspect_status: str,
    ssai_inspect_status: str,
    report_dir: str | Path,
) -> None:
    """
    Publish GitHub Check Runs for all AppInspect results.

    Args:
        app_inspect_status: Status of app-inspect check
        cloud_inspect_status: Status of cloud-inspect check
        ssai_inspect_status: Status of SSAI-inspect check
        report_dir: Directory containing AppInspect reports
    """
    report_path = Path(report_dir)

    # Get artifact URL if running in GitHub Actions
    artifacts_url = _get_artifacts_url()

    # Create check run for App-Inspect
    app_inspect_summary = _create_check_summary(
        report_path, "app_inspect_check.json", app_inspect_status
    )
    create_check_run(
        check_name="Splunk App-Inspect",
        title="App-Inspect Results",
        summary=app_inspect_summary,
        status=app_inspect_status,
        details_url=artifacts_url,
    )

    # Create check run for Cloud-Inspect
    cloud_inspect_summary = _create_check_summary(
        report_path, "cloud_inspect_check.json", cloud_inspect_status
    )
    create_check_run(
        check_name="Splunk Cloud-Inspect",
        title="Cloud-Inspect Results",
        summary=cloud_inspect_summary,
        status=cloud_inspect_status,
        details_url=artifacts_url,
    )

    # Create check run for SSAI-Inspect
    ssai_inspect_summary = _create_check_summary(
        report_path, "ssai_inspect_check.json", ssai_inspect_status
    )
    create_check_run(
        check_name="Splunk SSAI-Inspect",
        title="SSAI-Inspect Results",
        summary=ssai_inspect_summary,
        status=ssai_inspect_status,
        details_url=artifacts_url,
    )


def _create_check_summary(report_dir: Path, report_filename_suffix: str, status: str) -> str:
    """
    Create summary text for a check run from AppInspect JSON report.

    Args:
        report_dir: Directory containing AppInspect reports
        report_filename_suffix: Suffix of the report filename to look for
        status: Status string from AppInspect

    Returns:
        Summary text for the check
    """
    # Find the JSON report file
    json_files = list(report_dir.glob(f"*{report_filename_suffix}"))

    if not json_files:
        return f"Status: {status}\n\nNo detailed report available."

    try:
        with json_files[0].open() as f:
            report_data = json.load(f)

        summary_data = report_data.get("summary", {})
        if not isinstance(summary_data, dict):
            return f"Status: {status}"

        # Extract counts
        success = summary_data.get("success", 0)
        failure = summary_data.get("failure", 0)
        error = summary_data.get("error", 0)
        warning = summary_data.get("warning", 0)
        manual = summary_data.get("manual_check", 0)
        skipped = summary_data.get("skipped", 0)
        not_applicable = summary_data.get("not_applicable", 0)

        # Create summary
        lines = [
            f"**Status:** {status}",
            "",
            "**Check Results:**",
            f"- ✅ Success: {success}",
            f"- ❌ Failures: {failure}",
            f"- 🔴 Errors: {error}",
            f"- ⚠️ Warnings: {warning}",
            f"- 📋 Manual Check: {manual}",
            f"- ⏭️ Skipped: {skipped}",
            f"- ➖ Not Applicable: {not_applicable}",
        ]

        # Add information about failures/errors if any
        if failure > 0 or error > 0:
            lines.append("")
            lines.append("**Failed Checks:**")
            failed_checks = _extract_failed_checks(report_data)
            for check in failed_checks[:5]:  # Limit to first 5
                lines.append(f"- {check}")
            if len(failed_checks) > 5:
                lines.append(f"- ... and {len(failed_checks) - 5} more")

        return "\n".join(lines)

    except Exception as e:
        gat.warning(f"Could not parse report for summary: {e}")
        return f"Status: {status}"


def _extract_failed_checks(report_data: dict[str, Any]) -> list[str]:
    """Extract list of failed check names from AppInspect report."""
    failed_checks = []
    reports = report_data.get("reports", [])

    if not isinstance(reports, list):
        return failed_checks

    for report in reports:
        if not isinstance(report, dict):
            continue

        result = report.get("result", "").lower()
        if result in ["failure", "error"]:
            check_name = report.get("name", "unknown")
            failed_checks.append(check_name)

    return failed_checks


def _get_artifacts_url() -> str | None:
    """Get URL to workflow run artifacts if running in GitHub Actions."""
    github_server_url = os.environ.get("GITHUB_SERVER_URL")
    github_repository = os.environ.get("GITHUB_REPOSITORY")
    github_run_id = os.environ.get("GITHUB_RUN_ID")

    if github_server_url and github_repository and github_run_id:
        return f"{github_server_url}/{github_repository}/actions/runs/{github_run_id}"

    return None
