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
from typing import override
from unittest.mock import patch

from helpers.saved_values import (  # pyright: ignore[reportMissingImports]
    AppInfo,
    keep_working_dir_unchanged,
)


class TestKeepWorkingDirUnchanged(unittest.TestCase):
    def test_restores_cwd_on_normal_exit(self):
        original = os.path.realpath(os.getcwd())
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_real = os.path.realpath(tmpdir)
            with keep_working_dir_unchanged():
                os.chdir(tmpdir)
                assert os.path.realpath(os.getcwd()) == tmpdir_real
            assert os.path.realpath(os.getcwd()) == original

    def test_restores_cwd_on_exception(self):
        original = os.path.realpath(os.getcwd())
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(RuntimeError):
                with keep_working_dir_unchanged():
                    os.chdir(tmpdir)
                    raise RuntimeError("boom")
            assert os.path.realpath(os.getcwd()) == original


class TestAppInfoConstruction(unittest.TestCase):
    """Test that AppInfo constructor does not publish to CI."""

    @override
    def setUp(self):
        self.package_id = "my_app"
        self.version = "1.2.3"

    @patch("helpers.saved_values.gat.set_output")
    @patch("helpers.saved_values.gat.set_env")
    def test_constructor_does_not_call_gat(self, mock_set_env, mock_set_output):
        app_info = AppInfo(self.package_id, self.version)
        mock_set_env.assert_not_called()
        mock_set_output.assert_not_called()
        assert app_info.package_id == self.package_id
        assert app_info.version_number == self.version
        assert app_info.build_number == ""

    @patch("helpers.saved_values.gat.set_output")
    @patch("helpers.saved_values.gat.set_env")
    def test_publish_calls_gat(self, mock_set_env, mock_set_output):
        app_info = AppInfo(self.package_id, self.version)
        mock_set_env.assert_not_called()
        mock_set_output.assert_not_called()

        app_info.publish()

        mock_set_env.assert_any_call("app_package_id", self.package_id)
        mock_set_output.assert_any_call("app_package_id", self.package_id)
        mock_set_env.assert_any_call("app_version_encoded", app_info.version_number_encoded)
        mock_set_output.assert_any_call("app_version", self.version)

    @patch("helpers.saved_values.gat.set_output")
    @patch("helpers.saved_values.gat.set_env")
    def test_set_build_number(self, mock_set_env, mock_set_output):
        app_info = AppInfo(self.package_id, self.version)
        app_info.set_build_number("42")
        assert app_info.build_number == "42"
        assert app_info.build_number_encoded == "42"
        mock_set_env.assert_any_call("app_build_number_encoded", "42")
        mock_set_output.assert_any_call("app_build_number", "42")

    def test_encode(self):
        app_info = AppInfo("pkg", "1.0.0-beta.1")
        assert app_info.version_number_encoded == "1_0_0_beta_1"
