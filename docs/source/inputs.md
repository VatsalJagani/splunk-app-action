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
- **⚠️ Note:** Cannot be used together with `python_requirements_file`.


### `is_remove_not_allowed_executables_from_lib`
- **Description:** Remove files with mimetype `application/x-executable` or `application/x-sharedlib` from the `lib/` folder before packaging. Works for both UCC (`use_ucc_gen`) and Python dependency manager (`python_requirements_file`) builds. This helps avoid Splunk AppInspect failures due to platform-specific compiled binaries (e.g. x86_64 `.so` files failing the `check_aarch64_compatibility` check). Set to `true` only if you want stricter cleanup; default is `false` for compatibility.
- **Required:** false
- **Default:** false
- **When to enable:** Set to `true` if your dependencies install platform-specific compiled extensions (e.g. `charset-normalizer`, `mypyc`-compiled packages) that cause AArch64 App Inspect failures. Leave as `false` if your add-on runtime requires such files.


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
- **⚠️ Note:** Cannot be used together with `use_ucc_gen`.

### `splunk_python_version`
- **Description:** Python version to target when installing dependencies from `python_requirements_file`. Should match the Python version used by your Splunk platform so that dependency resolution selects compatible package versions.
- **Required:** false
- **Default:** `"3.13"` (Splunk's current default runtime)
- **Example:** `"3.9"`, `"3.13"`
- **Note:** Only relevant when `python_requirements_file` is set. Has no effect otherwise.
- **⚠️ Upgrade note:** The default became `3.13` in the `v7` major tag (previously `3.9`). Only upgrade to `v7` if your app supports Python 3.13 on Splunk and has `python.version = latest` and `python.required = 3.13` set in **all** Python-related conf files (e.g. `inputs.conf`, `commands.conf`, `restmap.conf`, `alert_actions.conf`). If your app is not yet ready for Python 3.13, stay on `v6` or explicitly pass `splunk_python_version: "3.9"`.
- **Dependabot:** Add a `.python-version` file containing the same version (e.g., `3.13`) so Dependabot also constrains its suggestions to packages compatible with that Python version. Placement depends on app type:
  - **Non-UCC apps:** place `.python-version` in the app directory (e.g., `my_app/.python-version`) and point Dependabot `directory` at the app root (e.g., `/my_app`).
  - **UCC apps (`use_ucc_gen: true`):** place `.python-version` in the `package/` subdirectory (e.g., `my_app/package/.python-version`) and point Dependabot `directory` at `package/` (e.g., `/my_app/package`). Dependabot only scans one level deep, and for UCC apps `requirements.txt` lives at `package/lib/requirements.txt`.
  - See [Dependabot examples](examples.md#with-github-dependabot) for full configuration.

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
- **Valid options:** `whats_in_the_app`, `logger`, `common_js_utilities`, `ucc_additional_packaging`
- **Example:** `"whats_in_the_app,logger"`

### `my_github_token`
- **Description:** GitHub token to create pull requests for app utilities. **OPTIONAL** - the action automatically uses the built-in `GITHUB_TOKEN`. Only provide this if you want to use a Personal Access Token (PAT) for cross-repo permissions or explicit token management.
- **Required:** false
- **Default:** Uses workflow's automatic `GITHUB_TOKEN`
- **Usage (if providing PAT):** `my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}`
- **Recommended:** Configure repository-wide permissions:
  1. Go to Repository Settings → Actions → General
  2. Scroll to "Workflow permissions"
  3. Select "Read and write permissions"
  4. Check "Allow GitHub Actions to create and approve pull requests"

## Logger Utility Inputs

### `logger_log_files_prefix`
- **Description:** Log files prefix. Required when using the `logger` utility.
- **Required:** false
- **Default:** `"NONE"` (must be set when using logger utility)
- **Example:** `"my_app"` (creates log files like `my_app_error.log`)

### `logger_sourcetype`
- **Description:** Sourcetype for the internal app logs. Recommended when using the `logger` utility.
- **Required:** false
- **Default:** `"NONE"` (should be set when using logger utility)
- **Example:** `"my_app:logs"`

