# Capabilities & Usage

## Build Generation

- Automatically generates build artifacts from your GitHub repo.
- Supports multiple Apps/Add-ons in a single repository.
- Supports Add-on build with UCC Add-on Generator (`ucc-gen`).

## Permissions & User Commands

- Optionally fixes file/folder permissions for Splunk App Inspect.
- Allows running user-defined shell commands before build generation.

## App-Inspect & Cloud Checks

- Runs app-inspect with Splunkbase API.
- Generates HTML reports as GitHub artifacts.
- Performs Splunk Cloud and SSAI checks.

## Utilities

- `whats_in_the_app`: Adds app info to README.md
- `logger`: Adds Python logger and config
- `splunk_python_sdk`: Adds/updates Splunklib SDK
- `common_js_utilities`: Adds common JS utilities
- `ucc_additional_packaging`: Adds helper for UCC input handler

See the `Usage` section for workflow examples and configuration details.
