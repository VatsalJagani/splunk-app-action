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
from typing import override

from utilities.base_utility import BaseUtility  # pyright: ignore[reportMissingImports]


class TestBaseUtility(unittest.TestCase):
    @override
    def setUp(self):
        self.app_read_dir = os.path.join(os.path.dirname(__file__), "test_app_repos")
        self.app_write_dir = os.path.join(os.path.dirname(__file__), "test_app_repos")
        self.base_utility = BaseUtility(self.app_read_dir, self.app_write_dir)

    def test_implement_utility_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.base_utility.implement_utility()
