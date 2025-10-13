

# Capabilities & Usage

This action provides a comprehensive set of capabilities for building, inspecting, and packaging Splunk Apps/Add-ons in GitHub Actions workflows. All configuration details and workflow examples are included below.

---

## Build Generation

The action automatically generates build artifacts from your GitHub repo.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
```

- `app_dir` is optional if you want to generate the build from the repo root.
- Supports multiple Apps/Add-ons in a single repository.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_splunk_app"

- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_splunk_add-on"
```

### UCC Add-on Generator

- Supports Add-on build with UCC Add-on Generator (`ucc-gen`).
- Reference: [Splunk Add-on UCC Framework](https://splunk.github.io/addonfactory-ucc-generator/)
- The `app_dir` folder must have a sub-folder named `package` and a file named `globalConfig.json`.
- Use `ucc-gen init` locally before using this or `ucc-gen build` command.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "TA_my_addon"
        use_ucc_gen: true
```

---

## Permissions & User Commands

- Optionally fixes file/folder permissions for Splunk App Inspect.
- Allows running user-defined shell commands before build generation.

If your app has executable files other than `.sh`, avoid enabling `to_make_permission_changes` unless needed.
You can use user-defined commands to set permissions as required.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        to_make_permission_changes: true
        splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
        splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

Example shell commands used:
```sh
find my_app -type f -exec chmod 644 '{}' \;
find my_app -type f -name '*.sh' -exec chmod 755 '{}' \;
find my_app -type d -exec chmod 755 '{}' \;
```

### Running User Defined Commands Before Build

Set environment variables `SPLUNK_APP_ACTION_<n>` to run commands before build generation.

```text
- uses: VatsalJagani/splunk-app-action@v4
    env:
        SPLUNK_APP_ACTION_1: "find . -type f -exec chmod 644 '{}' \;"
        SPLUNK_APP_ACTION_2: "find . -type f -name '*.sh' -exec chmod +x '{}' \;"
        SPLUNK_APP_ACTION_3: "find . -type d -exec chmod 755 '{}' \;"
    with:
        app_dir: "my_app"
```

- Maximum 99 commands: `SPLUNK_APP_ACTION_1` to `SPLUNK_APP_ACTION_99`.
- Commands run in the app's root directory context.

---

## App-Inspect & Cloud Checks

- Runs app-inspect with Splunkbase API.
- Generates HTML reports as GitHub artifacts (see Actions tab).
- Performs Splunk Cloud and SSAI checks.

Requires:
- `splunkbase_username` and `splunkbase_password` inputs (use GitHub secrets).

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
        splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

---

## Utilities

- `whats_in_the_app`: Adds app info to README.md
- `logger`: Adds Python logger and config
- `splunk_python_sdk`: Adds/updates Splunklib SDK
- `common_js_utilities`: Adds common JS utilities
- `ucc_additional_packaging`: Adds helper for UCC input handler

All utilities require the `my_github_token` input for creating pull requests.

### Example: Add App Info Utility

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "whats_in_the_app"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
```

### Example: Add Logger Utility

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "logger"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
        logger_log_files_prefix: "my_app"
        logger_sourcetype: "my_app:logs"
```

---

## UCC Additional Packaging Utility

This utility adds `additional_packaging.py` for UCC-built Add-ons, helping generate input handler files for Splunk modular inputs.

### Example Usage

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "."
        use_ucc_gen: true
        app_utilities: "ucc_additional_packaging"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
```

The input handler file `<Input_Name>_handler.py` will start with:

```python
from splunklib import modularinput as smi

def validate_input(input_script: smi.Script, definition: smi.ValidationDefinition):
        return

def stream_events(input_script: smi.Script, inputs: smi.InputDefinition, event_writer: smi.EventWriter):
        return
```

- Update `validate_input` and `stream_events` as needed.
- `validate_input` is optional; `stream_events` is required for event ingestion.
