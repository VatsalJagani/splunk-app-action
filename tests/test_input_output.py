# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false

import os
from typing import Any
from unittest import mock

import pytest

import github_action_toolkit as gat
import github_action_toolkit.input_output as gha_utils_input_output


def test__build_file_input() -> None:
    assert (
        gha_utils_input_output._build_file_input("test", "value")
        == b"test<<__ENV_DELIMITER__\nvalue\n__ENV_DELIMITER__\n"
    )


def test_set_output(tmpdir: Any) -> None:
    file = tmpdir.join("output_file")

    with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": file.strpath}):
        gat.set_output("test", "test")
        gat.set_output("another", 2)

    assert file.read() == (
        "test<<__ENV_DELIMITER__\n"
        "test\n__ENV_DELIMITER__\n"
        "another<<__ENV_DELIMITER__\n2\n"
        "__ENV_DELIMITER__\n"
    )


def test_set_output_deprecation_warning(tmpdir: Any) -> None:
    file = tmpdir.join("output_file")

    with pytest.deprecated_call():
        with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": file.strpath}):
            gat.set_output("test", "test", use_subprocess=True)


def test_save_state(tmpdir: Any) -> None:
    file = tmpdir.join("state_file")

    with mock.patch.dict(os.environ, {"GITHUB_STATE": file.strpath}):
        gat.save_state("test", "test")
        gat.save_state("another", 2)

    assert file.read() == (
        "test<<__ENV_DELIMITER__\n"
        "test\n__ENV_DELIMITER__\n"
        "another<<__ENV_DELIMITER__\n2\n"
        "__ENV_DELIMITER__\n"
    )


def test_save_state_deprecation_warning(tmpdir: Any) -> None:
    file = tmpdir.join("state_file")

    with pytest.deprecated_call():
        with mock.patch.dict(os.environ, {"GITHUB_STATE": file.strpath}):
            gat.save_state("test", "test", use_subprocess=True)


@mock.patch.dict(os.environ, {"STATE_test_state": "test", "abc": "another test"})
def test_get_state() -> None:
    assert gat.get_state("test_state") == "test"
    assert gat.get_state("abc") is None


@mock.patch.dict(
    os.environ,
    {
        "INPUT_USERNAME": "test_user",
        "INPUT_DEBUG": "true",
        "SOME_OTHER_ENV": "ignore_this",
    },
)
def test_get_all_user_inputs_returns_only_input_vars():
    result = gat.get_all_user_inputs()
    assert isinstance(result, dict)
    assert result == {
        "username": "test_user",
        "debug": "true",
    }


@mock.patch.dict(os.environ, {}, clear=True)
def test_get_all_user_inputs_with_no_inputs():
    assert gat.get_all_user_inputs() == {}


@mock.patch.dict(
    os.environ,
    {
        "INPUT_API_KEY": "abc123",
        "INPUT_VERBOSE": "yes",
    },
)
def test_print_all_user_inputs_outputs_correctly(capfd):
    gat.print_all_user_inputs()
    out, _ = capfd.readouterr()
    assert "User Inputs:" in out
    assert "api_key: abc123" in out
    assert "verbose: yes" in out


@mock.patch.dict(os.environ, {}, clear=True)
def test_print_all_user_inputs_when_no_env_vars(capfd):
    gat.print_all_user_inputs()
    out, _ = capfd.readouterr()
    assert "No user inputs found." in out


@mock.patch.dict(os.environ, {"INPUT_USERNAME": "test", "ANOTHER": "another test"})
def test_get_user_input() -> None:
    assert gat.get_user_input("username") == "test"
    assert gat.get_user_input("another") is None


@mock.patch.dict(os.environ, {"INPUT_AGE": "30", "INPUT_HEIGHT": "5.8"})
def test_get_user_input_as_basic_types():
    assert gat.get_user_input_as("age", int) == 30
    assert gat.get_user_input_as("height", float) == 5.8
    assert gat.get_user_input_as("age", str) == "30"


@mock.patch.dict(
    os.environ,
    {
        "INPUT_ACTIVE": "true",
        "INPUT_DISABLED": "no",
        "INPUT_UNKNOWN": "maybe",
    },
)
def test_get_user_input_as_boolean_true_false():
    assert gat.get_user_input_as("active", bool, default_value=False) is True
    assert gat.get_user_input_as("disabled", bool, default_value=True) is False
    # fallback to casting if not matching known true/false strings
    assert gat.get_user_input_as("unknown", bool) is True


@mock.patch.dict(os.environ, {"INPUT_EMPTY": ""})
def test_get_user_input_as_empty_string_returns_default():
    assert gat.get_user_input_as("empty", int, default_value=42) == 42
    assert gat.get_user_input_as("empty", str, default_value="default") == "default"


@mock.patch.dict(os.environ, {}, clear=True)
def test_get_user_input_as_missing_env_var():
    assert gat.get_user_input_as("nonexistent", int) is None
    assert gat.get_user_input_as("nonexistent", str, default_value="x") is None


@mock.patch.dict(os.environ, {"INPUT_BROKEN": "abc"})
def test_get_user_input_as_type_cast_error():
    with pytest.raises(ValueError):
        gat.get_user_input_as("broken", int)


def test_set_env(tmpdir: Any) -> None:
    file = tmpdir.join("envfile")

    with mock.patch.dict(os.environ, {"GITHUB_ENV": file.strpath}):
        gat.set_env("test", "test")
        gat.set_env("another", 2)

    assert file.read() == (
        "test<<__ENV_DELIMITER__\n"
        "test\n__ENV_DELIMITER__\n"
        "another<<__ENV_DELIMITER__\n2\n"
        "__ENV_DELIMITER__\n"
    )


def test_get_workflow_environment_variables(tmpdir: Any) -> None:
    file = tmpdir.join("envfile")

    with mock.patch.dict(os.environ, {"GITHUB_ENV": file.strpath}):
        gat.set_env("test", "test")
        gat.set_env("another", 2)
        data = gat.get_workflow_environment_variables()

    assert data == {"test": "test", "another": "2"}


@mock.patch.dict(os.environ, {"GITHUB_ACTOR": "test", "ANOTHER": "another test"})
def test_get_env() -> None:
    assert gat.get_env("GITHUB_ACTOR") == "test"
    assert gat.get_env("ANOTHER") == "another test"
