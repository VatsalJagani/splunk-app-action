# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUninitializedInstanceVariable=false
# pyright: reportUnannotatedClassAttribute=false
# pyright: reportImplicitOverride=false

import os
import tempfile
import unittest
from pathlib import Path

from job_summary import write_build_summary  # pyright: ignore[reportMissingImports]


# Mock AppInfo for testing
class MockAppInfo:
    def __init__(self):
        self.package_id = "test_app"
        self.version_number = "1.2.3"
        self.build_number = "42"


class TestJobSummary(unittest.TestCase):
    def setUp(self):
        """Set up test environment with a temporary summary file."""
        self.temp_dir = tempfile.mkdtemp()
        self.summary_file = os.path.join(self.temp_dir, "summary.md")
        # Set the GITHUB_STEP_SUMMARY environment variable
        self.original_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        os.environ["GITHUB_STEP_SUMMARY"] = self.summary_file

    def tearDown(self):
        """Clean up test environment."""
        # Restore original GITHUB_STEP_SUMMARY
        if self.original_summary is not None:
            os.environ["GITHUB_STEP_SUMMARY"] = self.original_summary
        elif "GITHUB_STEP_SUMMARY" in os.environ:
            del os.environ["GITHUB_STEP_SUMMARY"]

        # Clean up temp directory
        if os.path.exists(self.summary_file):
            os.remove(self.summary_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_write_build_summary_basic(self):
        """Test basic job summary writing."""
        app_info = MockAppInfo()
        artifact_name = "test_app_1_2_3_42.tgz"

        write_build_summary(
            app_info=app_info,
            artifact_name=artifact_name,
        )

        # Verify summary file was created and has content
        assert os.path.exists(self.summary_file)
        summary_content = Path(self.summary_file).read_text()

        # Check for expected content
        assert "Splunk App Build Summary" in summary_content
        assert "test_app" in summary_content
        assert "1.2.3" in summary_content
        assert "42" in summary_content
        assert "test_app_1_2_3_42.tgz" in summary_content

    def test_write_build_summary_with_inspect_results(self):
        """Test job summary with AppInspect results."""
        app_info = MockAppInfo()
        artifact_name = "test_app_1_2_3_42.tgz"

        write_build_summary(
            app_info=app_info,
            artifact_name=artifact_name,
            app_inspect_status="Passed",
            cloud_inspect_status="Failure",
            ssai_inspect_status="Error",
        )

        summary_content = Path(self.summary_file).read_text()

        # Check for AppInspect section
        assert "AppInspect Results" in summary_content
        assert "Passed" in summary_content
        assert "Failure" in summary_content
        assert "Error" in summary_content

    def test_write_build_summary_with_skipped_inspect(self):
        """Test job summary when AppInspect is skipped."""
        app_info = MockAppInfo()
        artifact_name = "test_app_1_2_3_42.tgz"

        write_build_summary(
            app_info=app_info,
            artifact_name=artifact_name,
            app_inspect_status="Skipped",
            cloud_inspect_status="Skipped",
            ssai_inspect_status="Skipped",
        )

        summary_content = Path(self.summary_file).read_text()

        # Check that Skipped appears in the summary
        assert "Skipped" in summary_content

    def test_write_build_summary_with_github_env(self):
        """Test job summary with GitHub environment variables for artifact links."""
        # Set GitHub environment variables
        os.environ["GITHUB_SERVER_URL"] = "https://github.com"
        os.environ["GITHUB_REPOSITORY"] = "test-org/test-repo"
        os.environ["GITHUB_RUN_ID"] = "123456789"

        app_info = MockAppInfo()
        artifact_name = "test_app_1_2_3_42.tgz"

        write_build_summary(
            app_info=app_info,
            artifact_name=artifact_name,
        )

        summary_content = Path(self.summary_file).read_text()

        # Check for artifacts section with link
        assert "Artifacts" in summary_content
        assert "https://github.com/test-org/test-repo/actions/runs/123456789" in summary_content

        # Clean up
        del os.environ["GITHUB_SERVER_URL"]
        del os.environ["GITHUB_REPOSITORY"]
        del os.environ["GITHUB_RUN_ID"]


if __name__ == "__main__":
    unittest.main()
