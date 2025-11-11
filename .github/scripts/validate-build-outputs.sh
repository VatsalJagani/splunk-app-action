#!/bin/bash
# Common validation script for build outputs
# Usage: validate-build-outputs.sh <expected_app_id> <expected_version> <expected_build_number>

set -e

EXPECTED_APP_ID="${1:-}"
EXPECTED_VERSION="${2:-}"
EXPECTED_BUILD_NUMBER="${3:-}"
ARTIFACT_NAME="${4:-}"
APP_PACKAGE_ID="${5:-}"
APP_VERSION="${6:-}"
APP_BUILD_NUMBER="${7:-}"

VALIDATION_PASSED=true

echo "### Validating Build Outputs"

# Validate artifact_name
if [ -z "$ARTIFACT_NAME" ]; then
  echo "⚠️ artifact_name is empty (composite action output issue)"
  VALIDATION_PASSED=false
else
  echo "✅ artifact_name: $ARTIFACT_NAME"
fi

# Validate app_package_id
if [ -z "$APP_PACKAGE_ID" ]; then
  echo "⚠️ app_package_id is empty (composite action output issue)"
  VALIDATION_PASSED=false
elif [ -n "$EXPECTED_APP_ID" ] && [ "$APP_PACKAGE_ID" != "$EXPECTED_APP_ID" ]; then
  echo "❌ Expected app_package_id '$EXPECTED_APP_ID', got '$APP_PACKAGE_ID'"
  VALIDATION_PASSED=false
else
  echo "✅ app_package_id: $APP_PACKAGE_ID"
fi

# Validate app_version
if [ -z "$APP_VERSION" ]; then
  echo "⚠️ app_version is empty (composite action output issue)"
  VALIDATION_PASSED=false
elif [ -n "$EXPECTED_VERSION" ] && [ "$APP_VERSION" != "$EXPECTED_VERSION" ]; then
  echo "❌ Expected app_version '$EXPECTED_VERSION', got '$APP_VERSION'"
  VALIDATION_PASSED=false
else
  echo "✅ app_version: $APP_VERSION"
fi

# Validate app_build_number (optional)
if [ -n "$EXPECTED_BUILD_NUMBER" ]; then
  if [ -z "$APP_BUILD_NUMBER" ]; then
    echo "⚠️ app_build_number is empty (composite action output issue)"
    VALIDATION_PASSED=false
  elif [ "$APP_BUILD_NUMBER" != "$EXPECTED_BUILD_NUMBER" ]; then
    echo "❌ Expected app_build_number '$EXPECTED_BUILD_NUMBER', got '$APP_BUILD_NUMBER'"
    VALIDATION_PASSED=false
  else
    echo "✅ app_build_number: $APP_BUILD_NUMBER"
  fi
fi

# Return validation result
if [ "$VALIDATION_PASSED" = false ]; then
  echo ""
  echo "⚠️ Some output validations failed"
  exit 1
else
  echo ""
  echo "✅ All output validations passed"
  exit 0
fi
