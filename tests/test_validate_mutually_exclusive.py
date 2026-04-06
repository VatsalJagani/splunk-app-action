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
import unittest
from unittest.mock import patch

from main import validate_mutually_exclusive_features  # pyright: ignore[reportMissingImports]


class TestValidateMutuallyExclusiveFeatures(unittest.TestCase):
    """Test mutual exclusivity validation between UCC-Gen and Python Dependency Manager."""

    @patch.dict(os.environ, {"INPUT_USE_UCC_GEN": "false", "INPUT_PYTHON_REQUIREMENTS_FILE": ""})
    def test_no_features_enabled(self):
        validate_mutually_exclusive_features()

    @patch.dict(os.environ, {"INPUT_USE_UCC_GEN": "true", "INPUT_PYTHON_REQUIREMENTS_FILE": ""})
    def test_only_ucc_gen(self):
        validate_mutually_exclusive_features()

    @patch.dict(
        os.environ,
        {"INPUT_USE_UCC_GEN": "false", "INPUT_PYTHON_REQUIREMENTS_FILE": "lib/requirements.txt"},
    )
    def test_only_python_deps(self):
        validate_mutually_exclusive_features()

    @patch.dict(
        os.environ,
        {"INPUT_USE_UCC_GEN": "true", "INPUT_PYTHON_REQUIREMENTS_FILE": "lib/requirements.txt"},
    )
    def test_ucc_and_python_deps_fails(self):
        with self.assertRaises(SystemExit) as cm:
            validate_mutually_exclusive_features()
        assert cm.exception.code == 1
