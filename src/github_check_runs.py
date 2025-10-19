"""
GitHub Check Runs API integration for quality gates.

Creates GitHub Check Runs to provide inline feedback and merge gating
based on AppInspect results.
"""

from __future__ import annotations

import os
from typing import Any, cast

import github_action_toolkit as gat
import requests


class GitHubCheckRun:
    """
    GitHub Check Runs API integration for quality gates.

    Creates check runs that appear in the PR interface and can block merges
    based on AppInspect results.
    """

    API_BASE = "https://api.github.com"

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        sha: str,
        github_token: str | None = None,
    ) -> None:
        """
        Initialize GitHub Check Run.

        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            sha: Git commit SHA
            github_token: GitHub token for API authentication
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.sha = sha

        # Get GitHub token from environment if not provided
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        if not self.github_token:
            gat.warning("No GitHub token provided - Check Runs will not be created")

        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def create_check_run(
        self,
        name: str,
        status: str = "in_progress",
        conclusion: str | None = None,
        title: str | None = None,
        summary: str | None = None,
        text: str | None = None,
        annotations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """
        Create or update a GitHub Check Run.

        Args:
            name: Name of the check run
            status: Status (queued, in_progress, completed)
            conclusion: Conclusion when completed (success, failure, neutral, cancelled, skipped, timed_out, action_required)
            title: Title of the check run
            summary: Summary text
            text: Detailed text
            annotations: List of code annotations

        Returns:
            Check run response or None if failed
        """
        if not self.github_token:
            gat.warning("Cannot create Check Run without GitHub token")
            return None

        url = f"{self.API_BASE}/repos/{self.repo_owner}/{self.repo_name}/check-runs"

        data: dict[str, Any] = {
            "name": name,
            "head_sha": self.sha,
            "status": status,
        }

        # Add optional fields
        if conclusion and status == "completed":
            data["conclusion"] = conclusion

        if title or summary or text:
            output: dict[str, Any] = {}
            if title:
                output["title"] = title
            if summary:
                output["summary"] = summary
            if text:
                output["text"] = text
            if annotations:
                # GitHub API limits annotations to 50 per request
                output["annotations"] = annotations[:50]
            data["output"] = output

        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            if response.status_code not in [200, 201]:
                gat.error(f"Failed to create Check Run: {response.status_code} - {response.text}")
                return None

            result = response.json()
            if isinstance(result, dict):
                return cast(dict[str, Any], result)
            return None

        except Exception as e:
            gat.error(f"Error creating Check Run: {e}")
            return None

    def create_appinspect_check_run(
        self,
        appinspect_summary: dict[str, Any],
        check_type: str = "APP_INSPECT",
        max_errors: int = 0,
        max_warnings: int = 10,
    ) -> dict[str, Any] | None:
        """
        Create a Check Run for AppInspect results.

        Args:
            appinspect_summary: AppInspect summary with counts
            check_type: Type of check (APP_INSPECT, CLOUD_INSPECT, SSAI_INSPECT)
            max_errors: Maximum allowed errors (0 = no errors allowed)
            max_warnings: Maximum allowed warnings

        Returns:
            Check run response or None if failed
        """
        failure_count = int(appinspect_summary.get("failure", 0))
        error_count = int(appinspect_summary.get("error", 0))
        warning_count = int(appinspect_summary.get("warning", 0))
        success_count = int(appinspect_summary.get("success", 0))
        manual_check_count = int(appinspect_summary.get("manual_check", 0))

        # Determine conclusion based on thresholds
        conclusion = "success"
        if failure_count > 0 or error_count > max_errors:
            conclusion = "failure"
        elif warning_count > max_warnings:
            conclusion = "failure"

        # Build summary text
        check_name_map = {
            "APP_INSPECT": "Splunk AppInspect",
            "CLOUD_INSPECT": "Splunk Cloud Inspect",
            "SSAI_INSPECT": "Splunk SSAI Inspect",
        }
        check_name = check_name_map.get(check_type, "Splunk AppInspect")

        summary_lines = [
            f"## {check_name} Results",
            "",
            f"- ✅ Success: {success_count}",
            f"- ❌ Failures: {failure_count}",
            f"- ⚠️ Errors: {error_count}",
            f"- ⚠️ Warnings: {warning_count}",
            f"- 📋 Manual Checks: {manual_check_count}",
            "",
        ]

        # Add quality gate information
        summary_lines.append("### Quality Gates")
        summary_lines.append("")
        summary_lines.append(f"- Maximum allowed errors: {max_errors}")
        summary_lines.append(f"- Maximum allowed warnings: {max_warnings}")
        summary_lines.append("")

        if conclusion == "failure":
            summary_lines.append("❌ **Quality gates failed**")
            if failure_count > 0:
                summary_lines.append(f"  - {failure_count} check(s) failed")
            if error_count > max_errors:
                summary_lines.append(
                    f"  - {error_count} error(s) exceeds threshold of {max_errors}"
                )
            if warning_count > max_warnings:
                summary_lines.append(
                    f"  - {warning_count} warning(s) exceeds threshold of {max_warnings}"
                )
        else:
            summary_lines.append("✅ **Quality gates passed**")

        summary = "\n".join(summary_lines)

        # Create title
        title = f"{check_name}: {conclusion.upper()}"

        return self.create_check_run(
            name=check_name,
            status="completed",
            conclusion=conclusion,
            title=title,
            summary=summary,
        )


def create_check_runs_for_appinspect(
    appinspect_summary_list: list[tuple[str, dict[str, Any]]],
    max_errors: int = 0,
    max_warnings: int = 10,
) -> None:
    """
    Create GitHub Check Runs for all AppInspect results.

    Args:
        appinspect_summary_list: List of (check_type, summary_dict) tuples
        max_errors: Maximum allowed errors
        max_warnings: Maximum allowed warnings
    """
    # Get GitHub context from environment
    github_repository = os.environ.get("GITHUB_REPOSITORY", "")
    github_sha = os.environ.get("GITHUB_SHA", "")

    if not github_repository or not github_sha:
        gat.warning(
            "GitHub context not available - Check Runs will not be created. "
            "This is expected when running locally."
        )
        return

    # Parse repository owner and name
    parts = github_repository.split("/")
    if len(parts) != 2:
        gat.error(f"Invalid GITHUB_REPOSITORY format: {github_repository}")
        return

    repo_owner, repo_name = parts

    gat.info(f"Creating GitHub Check Runs for {github_repository} @ {github_sha}")

    # Create Check Runs for each AppInspect result
    check_run = GitHubCheckRun(repo_owner, repo_name, github_sha)

    for check_type, summary in appinspect_summary_list:
        gat.info(f"Creating Check Run for {check_type}")
        result = check_run.create_appinspect_check_run(
            summary,
            check_type=check_type,
            max_errors=max_errors,
            max_warnings=max_warnings,
        )
        if result:
            gat.info(f"✅ Check Run created successfully for {check_type}")
        else:
            gat.warning(f"Failed to create Check Run for {check_type}")
