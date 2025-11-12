"""Module for generating GitHub Actions job summaries."""

import os

import github_action_toolkit as gat

from helpers.saved_values import AppInfo


def write_build_summary(
    app_info: AppInfo,
    artifact_name: str,
    app_inspect_status: str = "Not Run",
    cloud_inspect_status: str = "Not Run",
    ssai_inspect_status: str = "Not Run",
) -> None:
    """
    Write a GitHub Actions job summary with build information and AppInspect results.

    Creates a compact table with app metadata, artifact links, and AppInspect check status.
    """
    summary = gat.JobSummary()

    summary.add_heading("🎉 Splunk App Build Summary", 2)
    summary.add_eol()

    # Build Information Table
    summary.add_heading("Build Information", 3)
    build_table_data = [
        ["Property", "Value"],
        ["App Package ID", app_info.package_id],
        ["Version", app_info.version_number],
        ["Build Number", app_info.build_number],
        ["Artifact Name", artifact_name],
    ]
    summary.add_table(build_table_data)
    summary.add_eol()

    # AppInspect Results Table
    summary.add_heading("AppInspect Results", 3)

    def get_status_emoji(status: str) -> str:
        """Get emoji for status."""
        status_lower = status.lower()
        if status_lower == "passed":
            return "✅"
        elif status_lower in ["failure", "error"]:
            return "❌"
        elif status_lower == "timed-out":
            return "⏱️"
        elif status_lower == "exception":
            return "⚠️"
        elif status_lower == "skipped":
            return "⏭️"
        else:
            return "⚪"

    inspect_table_data = [
        ["Check Type", "Status"],
        ["App-Inspect", f"{get_status_emoji(app_inspect_status)} {app_inspect_status}"],
        ["Cloud-Inspect", f"{get_status_emoji(cloud_inspect_status)} {cloud_inspect_status}"],
        ["SSAI-Inspect", f"{get_status_emoji(ssai_inspect_status)} {ssai_inspect_status}"],
    ]
    summary.add_table(inspect_table_data)
    summary.add_eol()

    # Artifact Links (if running in GitHub Actions)
    github_server_url = os.environ.get("GITHUB_SERVER_URL")
    github_repository = os.environ.get("GITHUB_REPOSITORY")
    github_run_id = os.environ.get("GITHUB_RUN_ID")

    if github_server_url and github_repository and github_run_id:
        summary.add_heading("Artifacts", 3)
        artifacts_url = f"{github_server_url}/{github_repository}/actions/runs/{github_run_id}"
        summary.add_raw(f"📦 [Download artifacts from this run]({artifacts_url})")
        summary.add_eol()

    summary.write()
    gat.info("Job summary written successfully")
