# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false

import os
import unittest
from unittest.mock import patch

from helper import stdout_capture

from utilities.base_utility import BaseUtility


class TestBaseUtility(unittest.TestCase):
    def setUp(self):
        self.app_read_dir = os.path.join(os.path.dirname(__file__), "app_repos_for_test")
        self.app_write_dir = os.path.join(os.path.dirname(__file__), "app_repos_for_test")
        self.base_utility = BaseUtility(self.app_read_dir, self.app_write_dir)

    def test_implement_utility_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.base_utility.implement_utility()
