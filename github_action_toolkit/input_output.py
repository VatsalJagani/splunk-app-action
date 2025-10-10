import os
from typing import Any
from warnings import warn

from .consts import ACTION_ENV_DELIMITER
from .print_messages import echo, escape_data, escape_property, group


def _build_file_input(name: str, value: Any) -> bytes:
    return (
        f"{escape_property(name)}"
        f"<<{ACTION_ENV_DELIMITER}\n"
        f"{escape_data(value)}\n"
        f"{ACTION_ENV_DELIMITER}\n".encode()
    )


def get_all_user_inputs() -> dict[str, str]:
    """
    Retrieves all environment variables that start with 'INPUT_'.

    :returns: Dictionary of input names and their values.
    """
    return {key[6:].lower(): value for key, value in os.environ.items() if key.startswith("INPUT_")}


def print_all_user_inputs() -> None:
    """
    Prints all user inputs (from environment variables) to the console.
    """
    inputs = get_all_user_inputs()
    if not inputs:
        echo("No user inputs found.")
        return

    with group("User Inputs:"):
        for name, value in inputs.items():
            echo(f"  {name}: {value}")


def get_user_input(name: str) -> str | None:
    """
    gets user input from environment variables.

    :param name: Name of the user input
    :returns: input value or None
    """
    return os.environ.get(f"INPUT_{name.upper()}")


def get_user_input_as(name: str, input_type: type, default_value: Any = None) -> Any:
    """
    gets user input from environment variables and casts it to the specified type.

    :param name: Name of the user input
    :param input_type: Type to cast the input value to (e.g., str, int, float, bool)
    :param default_value: In case the input is not provided return this as default value (e.g., True, False, 0, etc)
    :returns: input value cast to the specified type or None
    """
    value = get_user_input(name)
    if value is None:
        return None

    try:
        if input_type is bool:
            if default_value is True:
                if value in ("false", "f", "0", "n", "no"):
                    return False
                else:
                    return True
            elif default_value is False:
                if value in ("true", "t", "1", "y", "yes"):
                    return True
                else:
                    return False
            else:
                return input_type(value)

        else:
            if value == "":
                return default_value
            else:
                return input_type(value)

    except ValueError as e:
        raise ValueError(f"Cannot convert input '{name}' to {input_type}: {e}") from e


def set_output(name: str, value: Any, use_subprocess: bool | None = None) -> None:
    """
    sets out for your workflow using GITHUB_OUTPUT file.

    :param name: name of the output
    :param value: value of the output
    :returns: None
    """
    if use_subprocess is not None:
        warn(
            "Argument `use_subprocess` for `set_output()` is deprecated and "
            "going to be removed in the next version.",
            DeprecationWarning,
            stacklevel=2,
        )

    with open(os.environ["GITHUB_OUTPUT"], "ab") as f:
        f.write(_build_file_input(name, value))


def get_state(name: str) -> str | None:
    """
    gets environment variable value for the state.

    :param name: Name of the state environment variable (e.g: STATE_{name})
    :returns: state value or None
    """
    return os.environ.get(f"STATE_{name}")


def save_state(name: str, value: Any, use_subprocess: bool | None = None) -> None:
    """
    sets state for your workflow using $GITHUB_STATE file
    for sharing it with your workflow's pre: or post: actions.

    :param name: Name of the state environment variable (e.g: STATE_{name})
    :param value: value of the state environment variable
    :returns: None
    """
    if use_subprocess is not None:
        warn(
            "Argument `use_subprocess` for `save_state()` is deprecated and "
            "going to be removed in the next version.",
            DeprecationWarning,
            stacklevel=2,
        )

    with open(os.environ["GITHUB_STATE"], "ab") as f:
        f.write(_build_file_input(name, value))


def get_workflow_environment_variables() -> dict[str, Any]:
    """
    get a dictionary of all environment variables set in the GitHub Actions workflow.

    :returns: dictionary of all environment variables
    """
    environment_variable_dict: dict[str, str] = {}
    marker = f"<<{ACTION_ENV_DELIMITER}"

    with open(os.environ["GITHUB_ENV"], "rb") as file:
        for line in file:
            decoded_line: str = line.decode("utf-8")

            if marker in decoded_line:
                name, *_ = decoded_line.strip().split("<<")

                try:
                    decoded_value = next(file).decode("utf-8").strip()
                    environment_variable_dict[name] = decoded_value  # ← move inside try
                except StopIteration:
                    break

    return environment_variable_dict


def get_env(name: str) -> Any:
    """
    gets the value of an environment variable set in the GitHub Actions workflow.

    :param name: name of the environment variable
    :returns: value of the environment variable or None
    """
    return os.environ.get(name) or get_workflow_environment_variables().get(name)


def set_env(name: str, value: Any) -> None:
    """
    sets an environment variable for your workflows $GITHUB_ENV file.

    :param name: name of the environment variable
    :param value: value of the environment variable
    :returns: None
    """
    with open(os.environ["GITHUB_ENV"], "ab") as f:
        f.write(_build_file_input(name, value))
