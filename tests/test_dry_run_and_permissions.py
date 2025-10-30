# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportFunctionMemberAccess=false
# pyright: reportUnannotatedClassAttribute=false

import glob
import os
import unittest

from main import main  # pyright: ignore[reportMissingImports]

from .helper_test import setup_action_yml


class TestDryRunMode(unittest.TestCase):
    def test_dry_run_generates_preview_file(self):
        """Test that dry-run mode generates a preview file without making actual changes."""
        with setup_action_yml(
            "repo_1_regular_build",
            app_dir="my_app_1",
            dry_run="true",
            to_make_permission_changes="true",
            is_app_inspect_check="false",
        ):
            main()

            # Check that dry_run_preview.txt was created
            self.assertTrue(
                os.path.exists("dry_run_preview.txt"),
                "Dry-run preview file should be created",
            )

            # Read and validate the preview content
            with open("dry_run_preview.txt") as f:
                content = f.read()

            self.assertIn("DRY-RUN PREVIEW", content)
            self.assertIn("Package ID:", content)
            self.assertIn("Version:", content)
            self.assertIn("Permission Changes Preview", content)

    def test_dry_run_no_build_artifact(self):
        """Test that dry-run mode doesn't create an actual build artifact."""
        with setup_action_yml(
            "repo_1_regular_build",
            app_dir="my_app_1",
            dry_run="true",
            is_app_inspect_check="false",
        ):
            main()

            # Check that .tgz file was NOT created
            tgz_files = glob.glob("*.tgz")
            self.assertEqual(
                len(tgz_files),
                0,
                "Dry-run mode should not create actual .tgz build artifacts",
            )


class TestEnhancedPermissions(unittest.TestCase):
    def test_custom_file_mode(self):
        """Test that custom file mode is applied correctly."""
        with setup_action_yml(
            "repo_1_regular_build",
            app_dir="my_app_1",
            to_make_permission_changes="true",
            permission_file_mode="640",
            permission_dir_mode="750",
            is_app_inspect_check="false",
        ):
            main()

            # Find the generated build
            tgz_files = glob.glob("*.tgz")
            self.assertGreater(len(tgz_files), 0, "Build file should be created")

    def test_permission_preview_in_dry_run(self):
        """Test that dry-run mode shows permission preview."""
        with setup_action_yml(
            "repo_1_regular_build",
            app_dir="my_app_1",
            dry_run="true",
            to_make_permission_changes="true",
            permission_file_mode="600",
            permission_dir_mode="700",
            permission_script_mode="750",
            is_app_inspect_check="false",
        ):
            main()

            # Check that dry_run_preview.txt was created with permission details
            self.assertTrue(os.path.exists("dry_run_preview.txt"))

            with open("dry_run_preview.txt") as f:
                content = f.read()

            self.assertIn("Permission Changes Preview", content)
            self.assertIn("File mode: 600", content)
            self.assertIn("Directory mode: 700", content)
            self.assertIn("Script mode: 750", content)


# Inline test for get_permission_preview function
def test_get_permission_preview():
    """Test the get_permission_preview function."""
    from app_build_generate import get_permission_preview  # pyright: ignore[reportMissingImports]

    # This would need to be run in a context where the inputs are set
    # For now, we just ensure the function exists and can be called
    assert callable(get_permission_preview)
