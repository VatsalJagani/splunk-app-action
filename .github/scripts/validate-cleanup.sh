#!/bin/bash
# Common validation script for .pyc and __pycache__ cleanup
# Usage: validate-cleanup.sh <extraction_path> <strict_mode>

set -e

EXTRACTION_PATH="${1:-}"
STRICT_MODE="${2:-false}"  # Set to "true" to fail on any .pyc or __pycache__ found

if [ -z "$EXTRACTION_PATH" ] || [ ! -d "$EXTRACTION_PATH" ]; then
  echo "❌ Error: Invalid extraction path: $EXTRACTION_PATH"
  exit 1
fi

echo "### Cleanup Validation"

# Verify .pyc files are cleaned up
PYC_COUNT=$(find "$EXTRACTION_PATH" -name "*.pyc" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYC_COUNT" -eq 0 ]; then
  echo "✅ No .pyc files found (cleanup successful)"
else
  echo "Found $PYC_COUNT .pyc files"
  if [ "$STRICT_MODE" = "true" ]; then
    echo "❌ ERROR: Found $PYC_COUNT .pyc files (should be cleaned up)"
    exit 1
  else
    echo "⚠️ WARNING: Found $PYC_COUNT .pyc files (cleanup recommended)"
  fi
fi

# Verify __pycache__ directories are cleaned up
PYCACHE_COUNT=$(find "$EXTRACTION_PATH" -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYCACHE_COUNT" -eq 0 ]; then
  echo "✅ No __pycache__ directories found (cleanup successful)"
else
  echo "Found $PYCACHE_COUNT __pycache__ directories"
  if [ "$STRICT_MODE" = "true" ]; then
    echo "❌ ERROR: Found $PYCACHE_COUNT __pycache__ directories (should be cleaned up)"
    exit 1
  else
    echo "⚠️ WARNING: Found $PYCACHE_COUNT __pycache__ directories (cleanup recommended)"
  fi
fi

echo "✅ Cleanup validation completed"
exit 0
