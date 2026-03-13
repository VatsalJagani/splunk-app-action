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
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

        self.saved_paths = SavedPaths("TA_test_addon")
        self.app_info = AppInfo("ta_test_addon", "1.0.0")

        os.makedirs(self.saved_paths.app_dir_path, exist_ok=True)

    @override
    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def _mock_ucc_system_call(self, _command: str) -> int:
        output_lib_path = Path("output") / self.app_info.package_id / "lib"
        output_lib_path.mkdir(parents=True, exist_ok=True)

        # This file should be removed when cleanup is enabled.
        (output_lib_path / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").write_text(
            "binary-content"
        )
        # This file should always stay.
        (output_lib_path / "regular_extension.so").write_text("binary-content")
        (Path("output") / self.app_info.package_id / "README.txt").write_text("readme")
        return 0

    def test_remove_mypyc_so_enabled(self) -> None:
        with patch("ucc_gen.os.system", side_effect=self._mock_ucc_system_call):
            build_dir_name = ucc_gen.build(
                self.saved_paths, self.app_info, is_remove_mypyc_from_ucc_lib=True
            )

        self.assertEqual(build_dir_name, "ucc_generated_build")
        generated_lib = Path("ucc_generated_build") / "lib"

        self.assertFalse((generated_lib / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").exists())
        self.assertTrue((generated_lib / "regular_extension.so").exists())

    def test_remove_mypyc_so_disabled(self) -> None:
        with patch("ucc_gen.os.system", side_effect=self._mock_ucc_system_call):
            build_dir_name = ucc_gen.build(
                self.saved_paths, self.app_info, is_remove_mypyc_from_ucc_lib=False
            )

        self.assertEqual(build_dir_name, "ucc_generated_build")
        generated_lib = Path("ucc_generated_build") / "lib"

        self.assertTrue((generated_lib / "abc123__mypyc.cpython-312-x86_64-linux-gnu.so").exists())
        self.assertTrue((generated_lib / "regular_extension.so").exists())
