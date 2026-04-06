#!/bin/bash
# Validate app-inspect results
# Usage: validate-appinspect.sh <app_inspect_status> <expected_result> <app_id> <version> <build_number>
#   expected_result: "pass" (Passed or Warning), "fail" (Failure/Error), "passed_only" (strict Passed)
# Returns: Prints validation results to stderr, exits with 0 on success, 1 on failure
# Note: All messages go to stderr to avoid polluting stdout

set -e

APP_INSPECT_STATUS="${1:-}"
EXPECTED_RESULT="${2:-pass}"  # "pass", "fail", or "passed_only"
APP_ID="${3:-}"
APP_VERSION="${4:-}"
APP_BUILD_NUMBER="${5:-}"

echo "" >&2
echo "### App-Inspect Status Validation:" >&2

if [ "$EXPECTED_RESULT" == "fail" ]; then
  # Expecting failure/error — status should not be Passed or Warning
  if [ "$APP_INSPECT_STATUS" == "Passed" ] || [ "$APP_INSPECT_STATUS" == "Warning" ]; then
    echo "❌ Expected app_inspect_status to be 'Failure' or 'Error', but got '$APP_INSPECT_STATUS'" >&2
    echo "This failing app should NOT pass inspection!" >&2
    exit 1
  else
    echo "✅ app_inspect_status correctly indicates failure: $APP_INSPECT_STATUS" >&2
  fi
elif [ "$EXPECTED_RESULT" == "passed_only" ]; then
  # Strict: only "Passed" is acceptable
  if [ "$APP_INSPECT_STATUS" != "Passed" ]; then
    echo "❌ Expected app_inspect_status to be 'Passed', but got '$APP_INSPECT_STATUS'" >&2
    exit 1
  else
    echo "✅ app_inspect_status: $APP_INSPECT_STATUS" >&2
  fi
else
  # Default "pass": accept Passed or Warning (non-failing statuses)
  if [ "$APP_INSPECT_STATUS" != "Passed" ] && [ "$APP_INSPECT_STATUS" != "Warning" ]; then
    echo "❌ Expected app_inspect_status to be 'Passed' or 'Warning', but got '$APP_INSPECT_STATUS'" >&2
    exit 1
  else
    echo "✅ app_inspect_status: $APP_INSPECT_STATUS" >&2
  fi
fi

# Check if inspect report exists
REPORT_DIR="${APP_ID}_${APP_VERSION}_${APP_BUILD_NUMBER}_reports"
REPORT_DIR=$(echo "$REPORT_DIR" | tr '.' '_')

if [ -d "$REPORT_DIR" ]; then
  echo "✅ App-inspect reports generated: $REPORT_DIR" >&2
else
  echo "⚠️ App-inspect reports not found: $REPORT_DIR" >&2
fi

echo "" >&2
if [ "$EXPECTED_RESULT" == "fail" ]; then
  echo "✅ Failure correctly detected and outputs validated!" >&2
else
  echo "✅ App-inspect passed and outputs validated!" >&2
fi

exit 0
