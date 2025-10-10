# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false

from typing import Any

import pytest

import github_action_toolkit as gat
import github_action_toolkit.print_messages as gat_print_messages


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            ["debug", "test debug", "test=1,test2=2"],
            "::debug test=1,test2=2::test debug\n",
        ),
        (["debug", "test debug", None], "::debug ::test debug\n"),
    ],
)
def test__print_command(capfd: Any, test_input: Any, expected: str) -> None:
    gat_print_messages._print_command(*test_input)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "test"),
        (1, "1"),
        (3.14, "3.14"),
        (["test", "test"], '["test", "test"]'),
        (
            (
                "test",
                "test",
            ),
            '["test", "test"]',
        ),
        ({"test": 3.14, "key": True}, '{"test": 3.14, "key": true}'),
    ],
)
def test__make_string(test_input: Any, expected: str) -> None:
    assert gat_print_messages._make_string(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "test"),
        ("test\n", "test%0A"),
        ("%test", "%25test"),
        ("\rtest", "%0Dtest"),
    ],
)
def test_escape_data(test_input: str, expected: str) -> None:
    assert gat_print_messages.escape_data(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "test"),
        ("test:", "test%3A"),
        ("test,", "test%2C"),
    ],
)
def test_escape_property(test_input: str, expected: str) -> None:
    assert gat_print_messages.escape_property(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test_string", "testString"),
        ("String_New", "stringNew"),
        ("One_two_Three", "oneTwoThree"),
    ],
)
def test__to_camel_case(test_input: str, expected: str) -> None:
    assert gat_print_messages._to_camel_case(test_input) == expected


@pytest.mark.parametrize(
    "input_kwargs,expected",
    [
        (
            {
                "title": "test  \ntitle",
                "file": "abc.py",
                "col": 1,
                "end_column": 2,
                "line": 4,
                "end_line": 5,
            },
            "title=test  %0Atitle,file=abc.py,col=1,endColumn=2,line=4,endLine=5",
        ),
        ({"name": "test-name"}, "name=test-name"),
        ({}, ""),
    ],
)
def test__build_options_string(input_kwargs: Any, expected: str) -> None:
    assert gat_print_messages._build_options_string(**input_kwargs) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "test\n"),
        ("test\n", "test\n\n"),
        ("%test", "%test\n"),
        ("\rtest", "\rtest\n"),
    ],
)
def test_echo(capfd: Any, test_input: str, expected: str) -> None:
    gat.echo(test_input)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "test\n"),
        ("test\n", "test\n\n"),
        ("%test", "%test\n"),
        ("\rtest", "\rtest\n"),
    ],
)
def test_info(capfd: Any, test_input: str, expected: str) -> None:
    gat.info(test_input)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "::debug ::test\n"),
        ("test\n", "::debug ::test\n\n"),
        ("%test", "::debug ::%test\n"),
        ("\rtest", "::debug ::\rtest\n"),
    ],
)
def test_debug(capfd: Any, test_input: str, expected: str) -> None:
    gat.debug(test_input)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "input_args,input_kwargs,expected",
    [
        (
            ["test notice"],
            {
                "title": "test  \ntitle",
                "file": "abc.py",
                "col": 1,
                "end_column": 2,
                "line": 4,
                "end_line": 5,
            },
            "::notice title=test  %0Atitle,file=abc.py,col=1,endColumn=2,line=4,endLine=5::test notice\n",
        ),
        (["test notice"], {}, "::notice ::test notice\n"),
    ],
)
def test_notice(
    capfd: Any,
    input_args: Any,
    input_kwargs: Any,
    expected: str,
) -> None:
    gat.notice(*input_args, **input_kwargs)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "input_args,input_kwargs,expected",
    [
        (
            ["test warning"],
            {
                "title": "test  \ntitle",
                "file": "abc.py",
                "col": 1,
                "end_column": 2,
                "line": 4,
                "end_line": 5,
            },
            "::warning title=test  %0Atitle,file=abc.py,col=1,endColumn=2,line=4,endLine=5::test warning\n",
        ),
        (["test warning"], {}, "::warning ::test warning\n"),
    ],
)
def test_warning(
    capfd: Any,
    input_args: Any,
    input_kwargs: Any,
    expected: str,
) -> None:
    gat.warning(*input_args, **input_kwargs)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "input_args,input_kwargs,expected",
    [
        (
            ["test error"],
            {
                "title": "test  \ntitle",
                "file": "abc.py",
                "col": 1,
                "end_column": 2,
                "line": 4,
                "end_line": 5,
            },
            "::error title=test  %0Atitle,file=abc.py,col=1,endColumn=2,line=4,endLine=5::test error\n",
        ),
        (["test error"], {}, "::error ::test error\n"),
    ],
)
def test_error(
    capfd: Any,
    input_args: Any,
    input_kwargs: Any,
    expected: str,
) -> None:
    gat.error(*input_args, **input_kwargs)
    out, err = capfd.readouterr()
    print(out)
    assert out == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "::add-mask ::test\n"),
        (1, "::add-mask ::1\n"),
        (3.14, "::add-mask ::3.14\n"),
        (["test", "test"], '::add-mask ::["test", "test"]\n'),
        (
            (
                "test",
                "test",
            ),
            '::add-mask ::["test", "test"]\n',
        ),
        ({"test": 3.14, "key": True}, '::add-mask ::{"test": 3.14, "key": true}\n'),
    ],
)
def test_add_mask(capfd: Any, test_input: str, expected: str) -> None:
    gat.add_mask(test_input)
    out, err = capfd.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "::group ::test\n"),
        ("test\n", "::group ::test\n\n"),
        ("%test", "::group ::%test\n"),
        ("\rtest", "::group ::\rtest\n"),
    ],
)
def test_start_group(capfd: Any, test_input: str, expected: str) -> None:
    gat.start_group(test_input)
    out, err = capfd.readouterr()
    assert out == expected


def test_end_group(capfd: Any) -> None:
    gat.end_group()
    out, err = capfd.readouterr()
    assert out == "::endgroup::\n"
