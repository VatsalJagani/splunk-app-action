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
import github_action_toolkit.job_summary as gat_job_summary


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("# test", "# test"),
        ("# test%0A", "# test\n"),
        ("- %25test", "- %test"),
        ("**%0Dtest**", "**\rtest**"),
    ],
)
def test__clean_markdown_string(test_input: str, expected: str) -> None:
    assert gat_job_summary._clean_markdown_string(test_input) == expected


def test_append_job_summary(tmpdir: Any) -> None:
    file = tmpdir.join("summary")

    with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": file.strpath}):
        gat.append_job_summary("# TEST")
        gat.append_job_summary("- point 1")

    assert file.read() == "# TEST\n- point 1\n"


def test_overwrite_job_summary(tmpdir: Any) -> None:
    file = tmpdir.join("summary")

    with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": file.strpath}):
        gat.append_job_summary("# TEST")
        gat.overwrite_job_summary("- point 1")

    assert file.read() == "- point 1\n"


def test_remove_job_summary(tmpdir: Any) -> None:
    file = tmpdir.join("summary")

    with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": file.strpath}):
        gat.remove_job_summary()

    assert os.path.isfile(file.strpath) is False
