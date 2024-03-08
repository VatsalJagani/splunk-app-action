import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)

from helpers.github_action_utils import str_to_boolean_default_false, str_to_boolean_default_true


def test_str_to_boolean_default_true_positive_cases():
    assert str_to_boolean_default_true("true") is True
    assert str_to_boolean_default_true("T") is True
    assert str_to_boolean_default_true("1") is True
    assert str_to_boolean_default_true("YES") is True

def test_str_to_boolean_default_true_negative_cases():
    assert str_to_boolean_default_true("false") is False
    assert str_to_boolean_default_true("f") is False
    assert str_to_boolean_default_true("0") is False
    assert str_to_boolean_default_true("no") is False
    assert str_to_boolean_default_true("") is True  # Empty string defaults to True

def test_str_to_boolean_default_false_positive_cases():
    assert str_to_boolean_default_false("true") is True
    assert str_to_boolean_default_false("t") is True
    assert str_to_boolean_default_false("1") is True
    assert str_to_boolean_default_false("yes") is True

def test_str_to_boolean_default_false_negative_cases():
    assert str_to_boolean_default_false("false") is False
    assert str_to_boolean_default_false("f") is False
    assert str_to_boolean_default_false("0") is False
    assert str_to_boolean_default_false("no") is False
    assert str_to_boolean_default_false("") is False  # Empty string defaults to False
