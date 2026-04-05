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

from helpers.saved_values import keep_working_dir_unchanged  # pyright: ignore[reportMissingImports]


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
