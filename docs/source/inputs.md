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

## Utilities Inputs

### `app_utilities`
- **Description:** Add comma separated list of utilities to use. You need to enable read and write permission for workflow to create Pull Requests.
- **Required:** false
- **Default:** "" (no utilities)
- **Valid options:** `whats_in_the_app`, `logger`, `splunk_python_sdk`, `common_js_utilities`, `ucc_additional_packaging`
- **Example:** `"whats_in_the_app,logger,splunk_python_sdk"`

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

### `splunk_python_sdk_install_path`
- **Description:** Path where you would like to install splunk-python-sdk (splunklib). Path is relative to App's root folder.
- **Required:** false
- **Default:** "bin"
- **Example:** `"bin/lib"`, `"lib"`

### `is_remove_pyc_from_splunklib_dir`
- **Description:** Remove `.pyc` files and `__pycache__` directory from splunk-python-sdk (splunklib) installation path before generating Pull Request. Do not turn this off unless you are facing any issues explicitly.
- **Required:** false
- **Default:** true
