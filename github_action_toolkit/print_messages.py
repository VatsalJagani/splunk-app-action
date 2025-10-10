import json
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal

CommandTypes = Literal[
    "add-mask",
    "debug",
    "error",
    "group",
    "notice",
    "save-state",
    "set-output",
    "stop-commands",
    "warning",
]
LogCommandTypes = Literal["debug", "error", "notice", "warning"]


from .consts import COMMAND_MARKER, COMMANDS_USE_SUBPROCESS


def _make_string(data: Any) -> str:
    """
    Converts a value to a string.

    :param data: data to convert
    :returns: string representation of the value
    """
    if isinstance(data, (list, tuple, dict)):
        return json.dumps(data)
    return str(data)


def escape_data(data: Any) -> str:
    """
    Removes `%, \r, \n` characters from a string.

    Copied from: https://github.com/actions/runner/blob/407a347f831483f85b88eea0f0ac12f7ddbab5a8/src/Runner.Common/ActionCommand.cs#L19-L24

    :param data: Any type of data to be escaped e.g. string, number, list, dict
    :returns: string after escaping
    """
    return _make_string(data).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(data: Any) -> str:
    """
    Removes `%, \r, \n, :, ,` characters from a string.

    Copied from: https://github.com/actions/runner/blob/407a347f831483f85b88eea0f0ac12f7ddbab5a8/src/Runner.Common/ActionCommand.cs#L26-L33

    :param data: Any type of data to be escaped e.g. string, number, list, dict
    :returns: string after escaping
    """
    return escape_data(data).replace(":", "%3A").replace(",", "%2C")


def _to_camel_case(text: str) -> str:
    """
    Transforms a snake case string to camel case.

    :param text: snake cased string
    :returns: camel cased string
    """
    return f"{text[:1].lower()}{text.title().replace('_', '')[1:]}"


def _build_options_string(**kwargs: Any) -> str:
    return ",".join(
        f"{_to_camel_case(key)}={escape_property(value)}"
        for key, value in kwargs.items()
        if value is not None
    )


def _print_command(
    command: CommandTypes,
    command_message: str,
    options_string: str | None = "",
    use_subprocess: bool = False,
    escape_message: bool = True,
) -> None:
    """
    Helper function to print GitHub action commands to the shell.
    Docs: https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions

    :param command: command name from `CommandTypes`
    :param command_message: message string
    :param options_string: string containing extra options
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    if escape_message:
        command_message = escape_data(command_message)

    full_command = (
        f"{COMMAND_MARKER}{command} {options_string or ''}{COMMAND_MARKER}{command_message}"
    )

    if use_subprocess or COMMANDS_USE_SUBPROCESS:
        subprocess.run(["echo", full_command])
    else:
        print(full_command)


def echo(message: Any, use_subprocess: bool = False) -> None:
    """
    prints a message to the GitHub Actions shell.

    Template: {message}
    Example: echo "info message"

    :param message: Any type of message e.g. string, number, list, dict
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    message = str(message)

    if use_subprocess or COMMANDS_USE_SUBPROCESS:
        subprocess.run(["echo", message])
    else:
        print(message)


def info(message: Any, use_subprocess: bool = False) -> None:
    """
    prints a message to the GitHub Actions shell.

    Template: {message}
    Example: info "info message"

    :param message: Any type of message e.g. string, number, list, dict
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    echo(message=message, use_subprocess=use_subprocess)


def debug(message: str, use_subprocess: bool = False) -> None:
    """
    prints a debug message in the GitHub Actions shell.

    Template: ::debug::{message}
    Example: echo "::debug::Set the Octocat variable"

    :param message: message string
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    _print_command("debug", message, use_subprocess=use_subprocess, escape_message=False)


def notice(
    message: str,
    title: str | None = None,
    file: str | None = None,
    col: int | None = None,
    end_column: int | None = None,
    line: int | None = None,
    end_line: int | None = None,
    use_subprocess: bool = False,
) -> None:
    """
    prints a notice message in the GitHub Actions shell.

    Template: ::notice file={name},line={line},endLine={endLine},title={title}::{message}
    Example: echo "::notice file=app.js,line=1,col=5,endColumn=7::Missing semicolon"

    :param message: Message to display
    :param title: Custom title
    :param file: Filename in the repository
    :param col: Column number, starting at 1
    :param end_column: End column number
    :param line: Line number, starting at 1
    :param end_line: End line number
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    _print_command(
        "notice",
        message,
        options_string=_build_options_string(
            title=title,
            file=file,
            col=col,
            end_column=end_column,
            line=line,
            end_line=end_line,
        ),
        use_subprocess=use_subprocess,
        escape_message=False,
    )


def warning(
    message: str,
    title: str | None = None,
    file: str | None = None,
    col: int | None = None,
    end_column: int | None = None,
    line: int | None = None,
    end_line: int | None = None,
    use_subprocess: bool = False,
) -> None:
    """
    prints a warning message in the GitHub Actions shell.

    Template: ::warning file={name},line={line},endLine={endLine},title={title}::{message}
    Example: echo "::warning file=app.js,line=1,col=5,endColumn=7::Missing semicolon"

    :param message: Message to display
    :param title: Custom title
    :param file: Filename in the repository
    :param col: Column number, starting at 1
    :param end_column: End column number
    :param line: Line number, starting at 1
    :param end_line: End line number
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    _print_command(
        "warning",
        message,
        options_string=_build_options_string(
            title=title,
            file=file,
            col=col,
            end_column=end_column,
            line=line,
            end_line=end_line,
        ),
        use_subprocess=use_subprocess,
        escape_message=False,
    )


def error(
    message: str,
    title: str | None = None,
    file: str | None = None,
    col: int | None = None,
    end_column: int | None = None,
    line: int | None = None,
    end_line: int | None = None,
    use_subprocess: bool = False,
) -> None:
    """
    prints an error message in the GitHub Actions shell.

    Template: ::error file={name},line={line},endLine={endLine},title={title}::{message}
    Example: echo "::error file=app.js,line=1,col=5,endColumn=7::Missing semicolon"

    :param message: Message to display
    :param title: Custom title
    :param file: Filename in the repository
    :param col: Column number, starting at 1
    :param end_column: End column number
    :param line: Line number, starting at 1
    :param end_line: End line number
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    _print_command(
        "error",
        message,
        options_string=_build_options_string(
            title=title,
            file=file,
            col=col,
            end_column=end_column,
            line=line,
            end_line=end_line,
        ),
        use_subprocess=use_subprocess,
        escape_message=False,
    )


def add_mask(value: Any, use_subprocess: bool = False) -> None:
    """
    masking a value prevents a string or variable from being printed in the log.

    Template: ::add-mask::{value}
    Example: echo "::add-mask::Mona The Octocat"

    :param value: value to mask
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    _print_command("add-mask", value, use_subprocess=use_subprocess)


def start_group(title: str, use_subprocess: bool = False) -> None:
    """
    creates an expandable group in GitHub Actions log.

    Template: ::group::{title}
    Example: echo "::group::My title"

    :param title: title of the group
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    _print_command("group", title, use_subprocess=use_subprocess, escape_message=False)


def end_group(use_subprocess: bool = False) -> None:
    """
    closes an expandable group in GitHub Actions log.

    Template: ::endgroup::
    Example: echo "::endgroup::"

    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    message = f"{COMMAND_MARKER}endgroup{COMMAND_MARKER}"

    if use_subprocess or COMMANDS_USE_SUBPROCESS:
        subprocess.run(["echo", message])
    else:
        print(message)


@contextmanager
def group(title: str, use_subprocess: bool = False) -> Generator[Any, None, None]:
    """
    creates and closes an expandable group in GitHub Actions log.

    :param title: title of the group
    :param use_subprocess: use subprocess module to echo command
    :returns: None
    """
    start_group(title, use_subprocess=use_subprocess)
    yield
    end_group(use_subprocess=use_subprocess)
