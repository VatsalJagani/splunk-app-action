

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

## UCC Add-on Generator Support

Supports Add-on build with **UCC Add-on Generator** using the `ucc-gen build` command.

- Reference: [Splunk Add-on UCC Framework](https://splunk.github.io/addonfactory-ucc-generator/)
- The `app_dir` folder must have a sub-folder named `package` and a file named `globalConfig.json`
- You need to use `ucc-gen init` command locally first to initialize the Add-on/Repository before using this action

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "TA_my_addon"
        use_ucc_gen: true
```

```{warning}
You must run `ucc-gen init` locally first to set up the proper UCC structure before using this GitHub Action. See the [UCC Framework documentation](https://splunk.github.io/addonfactory-ucc-generator/quickstart/) for details.
```

---

## File and Folder Permission Management

### Avoid File and Folder Permission Issues

```{danger}
**IMPORTANT:** This might break your App if you have executable files other than `.sh` and `.exe`.

- Avoid this parameter if your App has executable files other than `.sh` and `.exe`
- Linux executables are generally without extension - avoid this parameter in that case
- Alternatively, use the "User Defined Commands" section below to assign proper permissions manually
```

You can add `to_make_permission_changes: true` to automatically fix file and folder permission issues for Splunk App Inspect:

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        to_make_permission_changes: true
        splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
        splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

This runs the following commands automatically:
```bash
find my_app -type f -exec chmod 644 '{}' \;
find my_app -type f -name '*.sh' -exec chmod 755 '{}' \;
find my_app -type f -name '*.exe' -exec chmod 755 '{}' \;
find my_app -type f -name '*.bat' -exec chmod 755 '{}' \;
find my_app -type f -name '*.msi' -exec chmod 755 '{}' \;
find my_app -type f -name '*.cmd' -exec chmod 755 '{}' \;
find my_app -type d -exec chmod 755 '{}' \;
```

## Running User Defined Commands

```{note}
**v4 Change:** Commands now run in the context of your App's root directory instead of the repo's root directory.
```

Run custom Linux commands before generating the App build by setting environment variables `SPLUNK_APP_ACTION_<n>`:

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    env:
        SPLUNK_APP_ACTION_1: "find . -type f -exec chmod 644 '{}' \\;"
        SPLUNK_APP_ACTION_2: "find . -type f -name '*.sh' -exec chmod +x '{}' \\;"
        SPLUNK_APP_ACTION_3: "find . -type d -exec chmod 755 '{}' \\;"
    with:
        app_dir: "my_app"
```

**Key Features:**
- Commands run in your App's root directory context
- Maximum 99 commands supported (`SPLUNK_APP_ACTION_1` to `SPLUNK_APP_ACTION_99`)
- Commands execute in incremental order
- Useful for removing unwanted files, changing permissions, or preprocessing

**Example - Remove test files:**
```yaml
- uses: VatsalJagani/splunk-app-action@v4
    env:
        SPLUNK_APP_ACTION_1: "rm -rf extra_test_folder"
        SPLUNK_APP_ACTION_2: "rm -rf tests/"
    with:
        app_dir: "my_app"
```

If your app has executable files other than `.sh`, avoid enabling `to_make_permission_changes`.
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

The action runs comprehensive app-inspect checks using the **Splunkbase API** for the most accurate and up-to-date validation.

### Why Splunkbase API?
```{note}
We use the Splunkbase API instead of CLI versions because:
- CLI versions are often outdated compared to the Splunkbase API
- You would fail checks when uploading to Splunkbase if using outdated CLI tools
- This provides the same validation as the actual Splunkbase submission process
```

### Features:
- **App-Inspect checks** - Core Splunk app validation
- **Cloud-Inspect checks** - Splunk Cloud compatibility validation  
- **SSAI checks** - Splunk Security Analytics Integration validation
- **HTML reports** generated as GitHub artifacts (available in Actions tab)
- **Workflow failure** on any inspect errors or failures

### Requirements:
- `splunkbase_username`: Your Splunkbase account username
- `splunkbase_password`: Your Splunkbase account password (use GitHub secrets!)

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
        splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Disable App Inspect (Optional):

- You can use this for PRs and other than default branch if you don't want Splunkbase AppInspect checks to run on all changes.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app" 
        is_app_inspect_check: false
```

---

## Utilities

The action provides several utilities that automatically enhance your Splunk Apps and Add-ons by adding common functionality and keeping dependencies updated.

```{important}
**Automatic Pull Requests:** Utilities make code changes and create pull requests for you to review and merge. All utilities require `my_github_token` for creating PRs.
```

### Available Utilities:

1. **`whats_in_the_app`** - Adds information about your app (dashboards, alerts, etc.) to README.md
2. **`logger`** - Adds Python logger manager with proper configuration
3. **`splunk_python_sdk`** - Installs/upgrades Splunk Python SDK (splunklib)
4. **`common_js_utilities`** - Adds common JavaScript utilities for Splunk apps
5. **`ucc_additional_packaging`** - Helper for UCC Add-on input handler generation

You can use multiple utilities at once:
```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "whats_in_the_app,logger,splunk_python_sdk"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
```

### `whats_in_the_app` - Auto-Generate App Information

Automatically adds information about your app to the README.md file, including:
- Number of dashboards, alerts, saved searches
- Data inputs and other components
- Helps users understand what's inside your app

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "whats_in_the_app"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
```

### `logger` - Python Logger Setup

Adds a complete Python logging solution including:
- Logger manager Python file
- `props.conf` configuration for proper sourcetype assignment
- Internal log file handling

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "logger"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
        logger_log_files_prefix: "my_app"
        logger_sourcetype: "my_app:logs"
```

**Required Parameters:**
- `logger_log_files_prefix`: Prefix for your log files
- `logger_sourcetype`: Sourcetype for internal app logs (not required but recommended)

### `splunk_python_sdk` - Splunk SDK Management

Automatically installs and upgrades the Splunk Python SDK (splunklib):
- Installs latest version if not present
- Upgrades to newer versions automatically
- Removes `.pyc` files and `__pycache__` directories by default
- Cleans up old package metadata files (`.dist-info` and `.egg-info`) after upgrade
- Also cleans up old versions of splunk-sdk dependencies (e.g., `deprecation`, `packaging`)

```yaml
# Default installation (bin folder)
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "splunk_python_sdk"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}

# Custom installation path
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "splunk_python_sdk"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
        splunk_python_sdk_install_path: "bin/lib"
```

**Optional Parameters:**
- `splunk_python_sdk_install_path`: Custom path (default: "bin")
- `is_remove_pyc_from_splunklib_dir`: Remove .pyc files (default: true)

### `common_js_utilities` - JavaScript Utilities

Adds a JavaScript file with commonly used functionality for Splunk App development:
- Common JavaScript utilities and helper functions
- Ready-to-use code for typical Splunk app needs

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "common_js_utilities"
        my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
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
