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

import unittest

from main import _should_fail_on_status  # pyright: ignore[reportMissingImports]


class TestShouldFailOnStatus(unittest.TestCase):
    def test_none_never_fails(self):
        for status in ["Passed", "Warning", "Failure", "Error"]:
            assert _should_fail_on_status("none", status, status, status) is False

    def test_errors_fails_on_failure(self):
        assert _should_fail_on_status("errors", "Failure", "Passed", "Passed") is True

    def test_errors_fails_on_error(self):
        assert _should_fail_on_status("errors", "Passed", "Error", "Passed") is True

    def test_errors_does_not_fail_on_passed(self):
        assert _should_fail_on_status("errors", "Passed", "Passed", "Passed") is False

    def test_errors_does_not_fail_on_warning(self):
        assert _should_fail_on_status("errors", "Warning", "Passed", "Passed") is False

    def test_warnings_fails_on_failure(self):
        assert _should_fail_on_status("warnings", "Failure", "Passed", "Passed") is True

    def test_warnings_fails_on_error(self):
        assert _should_fail_on_status("warnings", "Passed", "Error", "Passed") is True

    def test_warnings_fails_on_warning(self):
        assert _should_fail_on_status("warnings", "Passed", "Warning", "Passed") is True

    def test_warnings_does_not_fail_on_passed(self):
        assert _should_fail_on_status("warnings", "Passed", "Passed", "Passed") is False

    def test_mixed_statuses(self):
        assert _should_fail_on_status("warnings", "Passed", "Warning", "Failure") is True
        assert _should_fail_on_status("errors", "Passed", "Warning", "Failure") is True
