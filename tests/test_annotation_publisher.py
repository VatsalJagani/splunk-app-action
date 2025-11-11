# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportPrivateUsage=false
"""Tests for annotation_publisher module."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from src.helpers import annotation_publisher


@pytest.fixture
def sample_appinspect_data() -> dict[str, Any]:
    """Sample AppInspect JSON data for testing."""
    return {
        "reports": [
            {
                "groups": [
                    {
                        "checks": [
                            {
                                "name": "check_version_format",
                                "result": "failure",
                                "description": "Version must follow semver format",
                                "messages": [
                                    {
                                        "message": "Invalid version format found",
                                        "message_filename": "default/app.conf",
                                        "message_line": 10,
                                    }
                                ],
                            },
                            {
                                "name": "check_deprecated_api",
                                "result": "warning",
                                "description": "Using deprecated API",
                                "messages": [
                                    {
                                        "message": "Deprecated method usage detected",
                                        "message_filename": "bin/script.py",
                                        "message_line": "25",
                                    }
                                ],
                            },
                            {
                                "name": "check_passed",
                                "result": "success",
                                "description": "This check passed",
                                "messages": [],
                            },
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def temp_json_file(tmp_path: Path, sample_appinspect_data: dict[str, Any]) -> Path:
    """Create a temporary JSON file with sample data."""
    json_file = tmp_path / "appinspect.json"
    json_file.write_text(json.dumps(sample_appinspect_data))
    return json_file


def test_publish_appinspect_annotations_with_valid_data(temp_json_file: Path) -> None:
    """Test publishing annotations from valid AppInspect data."""
    with (
        patch("github_action_toolkit.error") as mock_error,
        patch("github_action_toolkit.warning") as mock_warning,
        patch("github_action_toolkit.info") as mock_info,
    ):
        annotation_publisher.publish_appinspect_annotations(temp_json_file, "app-inspect", "my_app")

        # Should publish 1 error and 1 warning
        assert mock_error.call_count == 1
        assert mock_warning.call_count == 1
        assert mock_info.call_count == 1

        # Verify error call
        error_call = mock_error.call_args
        assert error_call.kwargs["title"] == "APP: Check Version Format"
        assert "Invalid version format found" in error_call.kwargs["message"]
        assert error_call.kwargs["file"] == "my_app/default/app.conf"
        assert error_call.kwargs["line"] == 10

        # Verify warning call
        warning_call = mock_warning.call_args
        assert warning_call.kwargs["title"] == "APP: Check Deprecated Api"
        assert "Deprecated method usage detected" in warning_call.kwargs["message"]
        assert warning_call.kwargs["file"] == "my_app/bin/script.py"
        assert warning_call.kwargs["line"] == 25


def test_publish_appinspect_annotations_with_root_app_dir(temp_json_file: Path) -> None:
    """Test publishing annotations when app_dir is root ('.')."""
    with patch("github_action_toolkit.error") as mock_error:
        annotation_publisher.publish_appinspect_annotations(temp_json_file, "app-inspect", ".")

        # File path should not have prefix when app_dir is "."
        error_call = mock_error.call_args
        assert error_call.kwargs["file"] == "default/app.conf"


def test_publish_appinspect_annotations_nonexistent_file() -> None:
    """Test handling of nonexistent JSON file."""
    with patch("github_action_toolkit.debug") as mock_debug:
        annotation_publisher.publish_appinspect_annotations(
            "/nonexistent/file.json", "app-inspect", "my_app"
        )

        # Should log debug message
        assert mock_debug.call_count >= 1


def test_publish_appinspect_annotations_with_ucc_check_type(temp_json_file: Path) -> None:
    """Test annotation titles for different check types."""
    with patch("github_action_toolkit.error") as mock_error:
        annotation_publisher.publish_appinspect_annotations(
            temp_json_file, "cloud-inspect", "my_app"
        )

        error_call = mock_error.call_args
        assert error_call.kwargs["title"] == "CLOUD: Check Version Format"


def test_publish_check_annotation_without_location() -> None:
    """Test publishing annotation when message has no file/line info."""
    check_data = {
        "name": "test_check",
        "result": "error",
        "description": "Test description",
        "messages": [{"message": "Error message without location"}],
    }

    with patch("github_action_toolkit.error") as mock_error:
        count = annotation_publisher._publish_check_annotation(check_data, "app-inspect", ".")

        assert count == 1
        error_call = mock_error.call_args
        assert "message" in error_call.kwargs
        assert "title" in error_call.kwargs
        assert "file" not in error_call.kwargs  # No file location
        assert "line" not in error_call.kwargs  # No line number


def test_publish_check_annotation_with_invalid_line_number() -> None:
    """Test handling of invalid line numbers."""
    check_data = {
        "name": "test_check",
        "result": "warning",
        "description": "Test description",
        "messages": [
            {
                "message": "Message with invalid line",
                "message_filename": "file.py",
                "message_line": "not_a_number",
            }
        ],
    }

    with (
        patch("github_action_toolkit.warning") as mock_warning,
        patch("github_action_toolkit.debug") as mock_debug,
    ):
        annotation_publisher._publish_check_annotation(check_data, "app-inspect", ".")

        # Should still publish but without line number
        assert mock_warning.call_count == 1
        warning_call = mock_warning.call_args
        assert "file" in warning_call.kwargs
        assert "line" not in warning_call.kwargs  # Invalid line number skipped

        # Should log debug message about conversion failure
        assert any(
            "Line number conversion failed" in str(call) for call in mock_debug.call_args_list
        )


def test_publish_check_annotation_no_messages() -> None:
    """Test publishing annotation when check has no messages."""
    check_data = {
        "name": "test_check",
        "result": "failure",
        "description": "Check failed without specific messages",
        "messages": [],
    }

    with patch("github_action_toolkit.error") as mock_error:
        count = annotation_publisher._publish_check_annotation(check_data, "ssai-inspect", ".")

        # Should publish one generic annotation
        assert count == 1
        error_call = mock_error.call_args
        assert "Check failed without specific messages" in error_call.kwargs["message"]
        assert error_call.kwargs["title"] == "SSAI: Test Check"


def test_publish_annotations_from_data_empty_reports() -> None:
    """Test handling of empty reports."""
    empty_data = {"reports": []}

    with patch("github_action_toolkit.debug") as mock_debug:
        annotation_publisher._publish_annotations_from_data(empty_data, "app-inspect", ".")

        # Should log that no annotations were published
        assert any("No app-inspect annotations" in str(call) for call in mock_debug.call_args_list)


def test_publish_annotations_with_exception_handling(tmp_path: Path) -> None:
    """Test exception handling in publish_appinspect_annotations."""
    # Create invalid JSON file
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("not valid json {")

    with (
        patch("github_action_toolkit.warning") as mock_warning,
        patch("github_action_toolkit.debug"),
    ):
        # Should not raise exception
        annotation_publisher.publish_appinspect_annotations(invalid_json, "app-inspect", ".")

        # Should log warning about failure
        assert any(
            "Failed to publish app-inspect annotations" in str(call)
            for call in mock_warning.call_args_list
        )
