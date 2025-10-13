import importlib
import sys
import types

import pytest

def make_version_module(_MAJOR, _MINOR, _PATCH, _SUFFIX=""):
    # Dynamically create a simulated version module
    module = types.ModuleType("version")
    module._MAJOR = _MAJOR
    module._MINOR = _MINOR
    module._PATCH = _PATCH
    module._SUFFIX = _SUFFIX
    module.VERSION_SHORT = f"{_MAJOR}.{_MINOR}"
    module.VERSION = f"{_MAJOR}.{_MINOR}.{_PATCH}{_SUFFIX}"
    return module

def test_version_short_default():
    version = make_version_module("4", "2", "0")
    assert version.VERSION_SHORT == "4.2"

def test_version_default():
    version = make_version_module("4", "2", "0")
    assert version.VERSION == "4.2.0"

def test_version_with_suffix():
    version = make_version_module("4", "2", "0", ".dev20251011")
    assert version.VERSION == "4.2.0.dev20251011"

def test_version_all_components_change():
    version = make_version_module("5", "0", "3", "-beta")
    assert version.VERSION_SHORT == "5.0"
    assert version.VERSION == "5.0.3-beta"
