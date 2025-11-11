#!/bin/bash
# Write action outputs to GitHub Step Summary
# Usage: write-outputs-summary.sh <step_outputs_json>

# This function expects JSON from: toJson(steps.step_id.outputs)
OUTPUTS_JSON="${1:-}"

echo "### Action Outputs:" >> $GITHUB_STEP_SUMMARY

# Extract and display key outputs
if [ -n "$OUTPUTS_JSON" ]; then
  # Parse JSON and display outputs (simplified version without jq)
  echo "- build_path: \`${2:-N/A}\`" >> $GITHUB_STEP_SUMMARY
  echo "- artifact_name: \`${3:-N/A}\`" >> $GITHUB_STEP_SUMMARY
  echo "- app_package_id: \`${4:-N/A}\`" >> $GITHUB_STEP_SUMMARY
  echo "- app_version: \`${5:-N/A}\`" >> $GITHUB_STEP_SUMMARY
  echo "- app_build_number: \`${6:-N/A}\`" >> $GITHUB_STEP_SUMMARY
  echo "- app_inspect_status: \`${7:-N/A}\`" >> $GITHUB_STEP_SUMMARY
else
  echo "⚠️ No outputs provided" >> $GITHUB_STEP_SUMMARY
fi

echo "" >> $GITHUB_STEP_SUMMARY
