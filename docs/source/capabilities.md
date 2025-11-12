

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

```{important}
**Mutually Exclusive Feature:** UCC-Gen cannot be used together with Python Dependency Manager (`python_requirements_file`) or Splunk Python SDK utility (`splunk_python_sdk`). The workflow will fail if multiple features are enabled.
```

---

## Python Dependency Manager

Manage Python dependencies for your Splunk Apps and Add-ons using a `requirements.txt` file. Dependencies are automatically installed at build time, keeping your repository clean and enabling automated dependency updates through GitHub Dependabot.

### Key Benefits

- ✅ **GitHub Dependabot Integration** - Automatically receive pull requests for dependency updates
- ✅ **Clean Repository** - No third-party code committed to your repository
- ✅ **Automatic Cleanup** - Removes dangling code and cache files (`.pyc`, `__pycache__`)
- ✅ **Build-Time Installation** - Dependencies installed to `lib` folder during build process
- ✅ **Easy Maintenance** - Single file to manage all Python dependencies

### Basic Usage

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    python_requirements_file: "lib/requirements.txt"  # Path relative to app_dir
```

### Setup Instructions

1. Create a `requirements.txt` file in a subdirectory within your app (e.g., `lib/requirements.txt`):
   ```
   requests==2.31.0
   beautifulsoup4==4.12.2
   lxml==4.9.3
   ```
   
   **Note:** The path to requirements.txt should be relative to your app_dir. Dependencies will be installed in the same directory as the requirements file.

2. Add the action to your workflow with the `python_requirements_file` parameter:
   ```yaml
   - uses: VatsalJagani/splunk-app-action@v4
     with:
       app_dir: "my_splunk_app"
       python_requirements_file: "lib/requirements.txt"  # Path relative to app_dir
       splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
       splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
   ```

3. (Optional) Enable GitHub Dependabot by adding `.github/dependabot.yml`:
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/my_splunk_app"
       schedule:
         interval: "weekly"
   ```

### Advanced Configuration

You can specify a different requirements file path (always relative to app_dir):
```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    python_requirements_file: "dependencies/production.txt"  # Dependencies installed to dependencies/
```

**Note:** Dependencies will be installed in the same directory as the requirements file. For example:
- `lib/requirements.txt` → installs to `lib/`
- `dependencies/requirements.txt` → installs to `dependencies/`
- `requirements.txt` → installs to `lib/` (creates lib subdirectory automatically)

### How It Works

1. The action copies your app directory to a temporary build location
2. Determines the target directory from the requirements file path (e.g., `lib/requirements.txt` → target is `lib/`)
3. Cleans the target directory (removes all existing files)
4. Runs `pip install -r requirements.txt --target <target_directory>` to install dependencies
5. Cleans up `.pyc` files and `__pycache__` directories
6. Removes requirements.txt file from the build
7. Proceeds with normal build generation

**Path Handling:**
- The `python_requirements_file` path is **relative to app_dir**
- Dependencies are installed in the same directory as the requirements file
- If requirements.txt is in the app root, a `lib/` subdirectory is automatically created.

The target folder is automatically added to Python's import path in Splunk, so your scripts can import the dependencies normally:
```python
import requests
from bs4 import BeautifulSoup
```

```{note}
**Cleanup Behavior:**
- The directory containing requirements.txt will be cleaned before installing dependencies
- The requirements.txt file will be removed from the final build package
- This ensures a clean build without any leftover files or dependencies
```

### Important Notes

```{important}
**Mutually Exclusive Feature:** Python Dependency Manager cannot be used together with:
- UCC-Gen (`use_ucc_gen: true`)
- Splunk Python SDK utility (`app_utilities: splunk_python_sdk`)

The workflow will fail with a clear error message if multiple features are enabled.
```

```{tip}
**Replicating Splunk Python SDK Installation:**
You can use the Python Dependency Manager instead of the Splunk Python SDK utility by adding `splunk-sdk` to your requirements.txt:
```text
splunk-sdk==2.1.1
```
This provides the same functionality with the added benefits of Dependabot integration and version control.
```

```{note}
The `lib` folder is automatically added to Python's import path in Splunk, so your scripts can import the dependencies normally:
```python
import requests
from bs4 import BeautifulSoup
# Or use Splunk SDK
import splunklib.client as client
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

---

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

The action runs comprehensive app-inspect checks using either the **Splunkbase API** (recommended) or **local validation** with the splunk-appinspect Python library.

### GitHub Annotations & Job Summary

AppInspect results are published as inline GitHub annotations and comprehensive job summaries for immediate feedback in Pull Requests.

#### GitHub Annotations
- App-inspect failures and errors appear as inline annotations on PR files
- Warnings appear as warning annotations
- No special permissions required - annotations work out of the box
- Click on annotations to see file location, line number, and detailed error messages
- Automatically published for app-inspect only (not for cloud-inspect or ssai-inspect)

#### GitHub Job Summary
- Comprehensive build summary displayed in the Actions UI
- Shows app metadata (package ID, version, build number, and artifact name)
- Displays AppInspect results for all check types (app-inspect, cloud-inspect, ssai-inspect)
- Includes status indicators with emojis for quick visual feedback
- Provides direct links to download artifacts
- Automatically generated for every workflow run

````

#### Failure Control
Control when the workflow fails based on AppInspect results:

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    local_app_inspect: true
    fail_on: "errors"  # Options: errors (default), warnings, none
```

- `"errors"` - Fail only on errors and failures (default)
- `"warnings"` - Fail on warnings, errors, or failures (strict mode)
- `"none"` - Never fail, useful for informational checks during development

### Splunkbase API (Recommended)

The Splunkbase API provides the most accurate and up-to-date validation as it's the same system used when submitting apps to Splunkbase.

#### Why Splunkbase API?
```{note}
We recommend the Splunkbase API because:
- CLI versions are often outdated compared to the Splunkbase API
- You would fail checks when uploading to Splunkbase if using outdated CLI tools
- This provides the same validation as the actual Splunkbase submission process
```

#### Features:
- **App-Inspect checks** - Core Splunk app validation
- **Cloud-Inspect checks** - Splunk Cloud compatibility validation  
- **SSAI checks** - Splunk Security Analytics Integration validation
- **HTML reports** generated as GitHub artifacts (available in Actions tab)
- **Workflow failure** on any inspect errors or failures

#### Requirements:
- `splunkbase_username`: Your Splunkbase account username
- `splunkbase_password`: Your Splunkbase account password (use GitHub secrets!)

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
        splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Local App Inspect (Faster Alternative)

For faster validation during development, you can use local app inspect with the splunk-appinspect Python library. This doesn't require Splunkbase credentials.

```{warning}
Local app inspect may not be as up-to-date as the Splunkbase API. For production releases, we recommend using the Splunkbase API to ensure your app will pass validation when submitting to Splunkbase.
```

#### Features:
- **Faster validation** - No API calls, runs locally
- **No credentials required** - Doesn't need Splunkbase username/password
- **Same check types** - Supports app-inspect, cloud-inspect, and SSAI checks
- **JSON and HTML reports** generated as GitHub artifacts

```yaml
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        local_app_inspect: true
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
**Automatic Pull Requests:** Utilities make code changes and create pull requests for you to review and merge.

**Required:** Grant workflow permissions for the action to create PRs:
```yaml
permissions:
  contents: write
  pull-requests: write
```

**Alternative:** Set repository-wide permissions in Settings → Actions → General → Workflow permissions → "Read and write permissions"
```

### Available Utilities:

1. **`whats_in_the_app`** - Adds information about your app (dashboards, alerts, etc.) to README.md
2. **`logger`** - Adds Python logger manager with proper configuration
3. **`splunk_python_sdk`** - Installs/upgrades Splunk Python SDK (splunklib)
4. **`common_js_utilities`** - Adds common JavaScript utilities for Splunk apps
5. **`ucc_additional_packaging`** - Helper for UCC Add-on input handler generation

You can use multiple utilities at once:
```yaml
permissions:
  contents: write
  pull-requests: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "whats_in_the_app,logger,splunk_python_sdk"
```

### `whats_in_the_app` - Auto-Generate App Information

Automatically adds information about your app to the README.md file, including:
- Number of dashboards, alerts, saved searches
- Data inputs and other components
- Helps users understand what's inside your app

```yaml
permissions:
  contents: write
  pull-requests: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "whats_in_the_app"
```

### `logger` - Python Logger Setup

Adds a complete Python logging solution including:
- Logger manager Python file
- `props.conf` configuration for proper sourcetype assignment
- Internal log file handling

```yaml
permissions:
  contents: write
  pull-requests: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "logger"
          logger_log_files_prefix: "my_app"
          logger_sourcetype: "my_app:logs"
```

**Required Parameters:**
- `logger_log_files_prefix`: Prefix for your log files
- `logger_sourcetype`: Sourcetype for internal app logs (not required but recommended)

### `splunk_python_sdk` - Splunk SDK Management

> [!WARNING]
> **DEPRECATED:** This utility is deprecated and will be removed in v5. Please plan to migrate to the new dynamic library installation feature in v5, which allows installing splunklib and other libraries without copying them into the repository.

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

# Custom installation path
- uses: VatsalJagani/splunk-app-action@v4
    with:
        app_dir: "my_app"
        app_utilities: "splunk_python_sdk"
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
