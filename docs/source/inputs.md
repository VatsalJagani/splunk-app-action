# Inputs

Complete reference of all available inputs for the splunk-app-action GitHub Action.

## Core Inputs

### `app_dir`
- **Description:** Provide app directory inside your repository. Do not provide the value if the repo's root directory itself is the app directory.
- **Required:** false
- **Default:** "." (meaning root folder of the repository)

### `to_make_permission_changes`
- **Description:** Whether to apply file and folder permission changes according to Splunk App Inspect expectation before generating the build.
- **Required:** false  
- **Default:** false
- **⚠️ Warning:** Read the file permission section in capabilities before enabling this. Can break apps with non-standard executable files.

### `use_ucc_gen`
- **Description:** Use ucc-gen command to generate the build for Add-on. The 'app_dir' folder must have a sub-folder named 'package', and a file named 'globalConfig.json' for this to work.
- **Required:** false
- **Default:** false
- **⚠️ Note:** Cannot be used together with `python_requirements_file` or `splunk_python_sdk` utility.

### `python_requirements_file`
- **Description:** Path to the requirements.txt file for Python dependency management. **Path is relative to app_dir.** Dependencies will be installed in the same directory as the requirements file. If the requirements file is in the app root, a `lib` subdirectory is automatically created. **Important:** The directory containing the requirements.txt file will be cleaned before installation, and the requirements.txt file itself will be removed after dependency installation.
- **Required:** false
- **Default:** "" (disabled)
- **Example:** `"lib/requirements.txt"` (recommended), `"dependencies/requirements.txt"`, or `"requirements.txt"` (auto-creates lib/)
- **Path behavior:**
  - `lib/requirements.txt` → installs dependencies to `lib/`
  - `dependencies/requirements.txt` → installs dependencies to `dependencies/`
  - `requirements.txt` → installs dependencies to `lib/` (auto-created)
- **Benefits:**
  - Enables GitHub Dependabot for automatic dependency updates
  - Keeps repository clean without third-party code
  - Automatically cleans up dangling code and cache files
  - Removes requirements.txt from the final build
- **⚠️ Note:** Cannot be used together with `use_ucc_gen` or `splunk_python_sdk` utility.

## App-Inspect Inputs

### `is_app_inspect_check`  
- **Description:** Whether to perform the Splunk app-inspect checks or not. This would include cloud-inspect checks as well.
- **Required:** false
- **Default:** true

### `splunkbase_username`
- **Description:** Username required to call the Splunkbase API for App-Inspect. Required when is_app_inspect_check is set to true.
- **Required:** false
- **Usage:** Always use via GitHub secrets: `${{ secrets.SPLUNKBASE_USERNAME }}`

### `splunkbase_password`
- **Description:** Password required to call the Splunkbase API for App-Inspect. Required when is_app_inspect_check is set to true. Strongly recommend to use via GitHub secrets only.
- **Required:** false  
- **Usage:** Always use via GitHub secrets: `${{ secrets.SPLUNKBASE_PASSWORD }}`

### `local_app_inspect`
- **Description:** Use local Splunk App Inspect validation with splunk-appinspect Python library instead of the Splunkbase API. This is faster but may not be as up-to-date as the Splunkbase API. When enabled, splunkbase_username and splunkbase_password are not required.
- **Required:** false
- **Default:** false
- **Note:** While local validation is faster, the Splunkbase API is recommended for production use as it reflects the most current validation rules used when submitting to Splunkbase.

### `publish_sarif`
- **Description:** Publish AppInspect results as SARIF (Static Analysis Results Interchange Format) for GitHub Code Scanning. Enables inline code annotations and security insights in Pull Requests.
- **Required:** false
- **Default:** true
- **Note:** Requires GitHub Code Scanning to be enabled. SARIF reports are automatically generated from AppInspect JSON results and uploaded. Can be disabled by setting to `false`.
- **Example:** `"true"`

### `fail_on`
- **Description:** Control when the action should fail based on AppInspect results.
- **Required:** false
- **Default:** "errors"
- **Options:**
  - `"errors"` - Fail only on errors and failures (default)
  - `"warnings"` - Fail on warnings, errors, or failures
  - `"none"` - Never fail based on AppInspect results (always succeed)
- **Note:** This setting allows you to make AppInspect checks informational while still gathering results. Useful for gradual adoption or when working on fixing existing issues.
- **Example:** `"warnings"`

## Utilities Inputs

### `app_utilities`
- **Description:** Add comma separated list of utilities to use. You need to enable read and write permission for workflow to create Pull Requests.
- **Required:** false
- **Default:** "" (no utilities)
- **Valid options:** `whats_in_the_app`, `logger`, `splunk_python_sdk`, `common_js_utilities`, `ucc_additional_packaging`
- **Example:** `"whats_in_the_app,logger,splunk_python_sdk"`
- **⚠️ Note:** The `splunk_python_sdk` utility cannot be used together with `python_requirements_file` or `use_ucc_gen`.

### `my_github_token`
- **Description:** GitHub Secret Token to automatically create Pull request. Make sure to put it in the Repo secret on GitHub as `MY_GITHUB_TOKEN` and then use it like `${{ secrets.MY_GITHUB_TOKEN }}`. Do not write it in plain text. Only required if app_utilities is being used.
- **Required:** false (but required when using utilities)
- **Usage:** `${{ secrets.MY_GITHUB_TOKEN }}`

## Logger Utility Inputs

### `logger_log_files_prefix`
- **Description:** Log files prefix. Only required for logger utility.
- **Required:** false (required when using logger utility)
- **Example:** `"my_app"` (creates log files like `my_app_error.log`)

### `logger_sourcetype`
- **Description:** Sourcetype for the internal app logs. Required only for logger utility.
- **Required:** false (recommended when using logger utility)
- **Example:** `"my_app:logs"`

## Splunk SDK Inputs

> [!WARNING]
> **DEPRECATED:** The `splunk_python_sdk` utility and its related inputs are deprecated and will be removed in v6. Please plan to migrate to the new dynamic library installation feature in v5.

### `splunk_python_sdk_install_path`
- **Description:** Path where you would like to install splunk-python-sdk (splunklib). Path is relative to App's root folder.
- **Required:** false
- **Default:** "bin"
- **Example:** `"bin/lib"`, `"lib"`

### `is_remove_pyc_from_splunklib_dir`
- **Description:** Remove `.pyc` files and `__pycache__` directory from splunk-python-sdk (splunklib) installation path before generating Pull Request. Do not turn this off unless you are facing any issues explicitly.
- **Required:** false
- **Default:** true
