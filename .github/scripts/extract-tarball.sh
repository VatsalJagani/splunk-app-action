#!/bin/bash
# Extract and prepare tarball for inspection
# Usage: extract-tarball.sh <tarball_path> <output_dir>

set -e

TARBALL_PATH="${1:-}"
OUTPUT_DIR="${2:-/tmp/artifact_extract}"

if [ -z "$TARBALL_PATH" ]; then
  echo "❌ Error: Tarball path not provided"
  exit 1
fi

if [ ! -f "$TARBALL_PATH" ]; then
  echo "❌ Error: Tarball not found: $TARBALL_PATH"
  exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Extract tarball
echo "📦 Extracting: $TARBALL_PATH"
tar -xzf "$TARBALL_PATH" -C "$OUTPUT_DIR"

# Get the extracted app directory name (first directory in the tarball)
APP_DIR=$(tar -tzf "$TARBALL_PATH" | head -1 | cut -f1 -d"/")
EXTRACTED_PATH="$OUTPUT_DIR/$APP_DIR"

if [ ! -d "$EXTRACTED_PATH" ]; then
  echo "❌ Error: Extracted directory not found: $EXTRACTED_PATH"
  exit 1
fi

echo "✅ Extracted to: $EXTRACTED_PATH"
echo ""
echo "📋 Directory structure:"
ls -la "$EXTRACTED_PATH"

# Output the extracted path for use in calling script
echo "$EXTRACTED_PATH"
