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
# pyright: reportUninitializedInstanceVariable=false

import os
import tempfile
import unittest
from pathlib import Path
from typing import override
from unittest.mock import patch

import ucc_gen  # pyright: ignore[reportMissingImports]
from helpers.saved_values import AppInfo, SavedPaths  # pyright: ignore[reportMissingImports]


class TestUccGen(unittest.TestCase):
    temp_dir: tempfile.TemporaryDirectory[str]
    original_cwd: str
    saved_paths: SavedPaths
    app_info: AppInfo

    @override
    def setUp(self) -> None:
        """
        Set up a temporary directory and app structure for each test.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

        self.saved_paths = SavedPaths("TA_test_addon")
        self.app_info = AppInfo("ta_test_addon", "1.0.0")

        os.makedirs(self.saved_paths.app_dir_path, exist_ok=True)

    @override
    def tearDown(self) -> None:
        """
        Restore original working directory and clean up temp resources.
        """
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def _mock_ucc_system_call(self, _command: str) -> int:
        """
        Simulate ucc-gen build output structure for testing.
        """
        output_lib_path = Path("output") / self.app_info.package_id / "lib"
        output_lib_path.mkdir(parents=True, exist_ok=True)

        # This file should be removed when cleanup is enabled (simulate executable/sharedlib).
        (output_lib_path / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").write_bytes(b"\x7fELF")
        # This file should always stay (simulate non-executable).
        (output_lib_path / "regular_extension.so").write_text("binary-content")
        (Path("output") / self.app_info.package_id / "README.txt").write_text("readme")
        return 0

    def test_remove_executables_enabled(self) -> None:
        """
        Test that executable/sharedlib files are removed when cleanup is enabled (is_remove_not_allowed_executables_from_lib=True).
        Default is False, so must set True explicitly.
        """
        with patch("ucc_gen.os.system", side_effect=self._mock_ucc_system_call):
            with patch("ucc_gen.magic.Magic.from_file") as mock_magic:

                def fake_mimetype(path):
                    if path.endswith("abc123__mypyc.cpython-312-x86_64-linux-gnu.so"):
                        return "application/x-executable"
                    return "text/plain"

                mock_magic.side_effect = fake_mimetype
                build_dir_name = ucc_gen.build(
                    self.saved_paths, self.app_info, is_remove_not_allowed_executables_from_lib=True
                )

        self.assertEqual(build_dir_name, "ucc_generated_build")
        generated_lib = Path("ucc_generated_build") / "lib"

        self.assertFalse((generated_lib / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").exists())
        self.assertTrue((generated_lib / "regular_extension.so").exists())

    def test_remove_executables_disabled(self) -> None:
        """
        Test that executable/sharedlib files are not removed when cleanup is disabled.
        """
        with patch("ucc_gen.os.system", side_effect=self._mock_ucc_system_call):
            build_dir_name = ucc_gen.build(
                self.saved_paths, self.app_info, is_remove_not_allowed_executables_from_lib=False
            )

        self.assertEqual(build_dir_name, "ucc_generated_build")
        generated_lib = Path("ucc_generated_build") / "lib"

        self.assertTrue((generated_lib / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").exists())
        self.assertTrue((generated_lib / "regular_extension.so").exists())

    def test_lib_directory_not_found(self) -> None:
        """
        Test behavior when UCC lib directory does not exist (should not raise error).
        Default is_remove_not_allowed_executables_from_lib=False.
        """

        def mock_system(_command: str) -> int:
            # No lib directory created
            output_path = Path("output") / self.app_info.package_id
            output_path.mkdir(parents=True, exist_ok=True)
            (output_path / "README.txt").write_text("readme")
            return 0

        with patch("ucc_gen.os.system", side_effect=mock_system):
            build_dir_name = ucc_gen.build(
                self.saved_paths, self.app_info, is_remove_not_allowed_executables_from_lib=True
            )
        self.assertEqual(build_dir_name, "ucc_generated_build")
        # Should not raise, lib folder missing
        generated_lib = Path("ucc_generated_build") / "lib"
        self.assertFalse(generated_lib.exists())

    def test_magic_failure(self) -> None:
        """
        Test that magic failure is handled gracefully and does not remove files.
        """
        with patch("ucc_gen.os.system", side_effect=self._mock_ucc_system_call):
            with patch("ucc_gen.magic.Magic", side_effect=Exception("magic error")):
                build_dir_name = ucc_gen.build(
                    self.saved_paths, self.app_info, is_remove_not_allowed_executables_from_lib=True
                )
        self.assertEqual(build_dir_name, "ucc_generated_build")
        generated_lib = Path("ucc_generated_build") / "lib"
        # Both files should remain since magic failed
        self.assertTrue((generated_lib / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").exists())
        self.assertTrue((generated_lib / "regular_extension.so").exists())

    def test_output_copy(self) -> None:
        """
        Test that output files are copied to ucc_generated_build.
        """
        with patch("ucc_gen.os.system", side_effect=self._mock_ucc_system_call):
            build_dir_name = ucc_gen.build(
                self.saved_paths, self.app_info, is_remove_not_allowed_executables_from_lib=True
            )
        self.assertEqual(build_dir_name, "ucc_generated_build")
        # README.txt should be copied
        self.assertTrue((Path("ucc_generated_build") / "README.txt").exists())
