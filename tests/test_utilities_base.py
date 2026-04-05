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
from collections.abc import Sequence
from typing import override

from helpers.saved_values import SavedPaths  # pyright: ignore[reportMissingImports]
from utilities.base_utility import BaseUtility  # pyright: ignore[reportMissingImports]


class TestBaseUtility(unittest.TestCase):
    def test_cannot_instantiate_abstract_class(self):
        saved_paths = SavedPaths("test_app")
        app_dir = os.path.join(os.path.dirname(__file__), "test_app_repos")
        with self.assertRaises(TypeError):
            BaseUtility(saved_paths, app_dir, app_dir)  # pyright: ignore[reportAbstractUsage]

    def test_concrete_subclass_can_be_instantiated(self):
        class ConcreteUtility(BaseUtility):
            @override
            def implement_utility(self) -> str | Sequence[str] | None:
                return None

        saved_paths = SavedPaths("test_app")
        app_dir = os.path.join(os.path.dirname(__file__), "test_app_repos")
        utility = ConcreteUtility(saved_paths, app_dir, app_dir)
        assert utility.implement_utility() is None
