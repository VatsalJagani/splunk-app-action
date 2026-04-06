# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed

* Improved UCC additional_packaging.py file for reduced manual code writing for UCC based Add-on code.
* Improved debugging logs in app build generation.
* Added `is_remove_not_allowed_executables_from_lib` input (default: `false`) to control removal of files with mimetype `application/x-executable` or `application/x-sharedlib` from UCC-generated `lib/` before packaging. Set to `true` for stricter AppInspect compliance; default is `false` for compatibility.
* **AppInspect Warning Status** - AppInspect checks now return "Warning" status when warnings exist but no errors/failures, enabling `fail_on: warnings` to work correctly.

### Removed

* **`splunk_python_sdk` Utility** - Removed the deprecated Splunk Python SDK utility and its inputs (`splunk_python_sdk_install_path`, `is_remove_pyc_from_splunklib_dir`). Use the Python Dependency Manager (`python_requirements_file`) with `splunk-sdk` in your requirements.txt instead.

### Fixed

* Fixed the issue with file/folder paths when running UCC based utilities.
* Improved Action Failure condition, when missing inputs or utility adding fails, github workflow will now show failure.
* Fixed silent ucc build generation issue when app folder name in the repo and app package id is same.
* **Python Dependency Manager** - Fixed path construction bug where dependencies were installed into the original checkout instead of the build copy.
* **Context Manager Safety** - Fixed `keep_working_dir_unchanged` missing `try/finally`, which could leave the process in the wrong directory after an exception.
* **Shell Injection Prevention** - Replaced `os.system()` calls with `shutil.move()` and `subprocess.run()` to prevent potential shell injection via user-controlled `app.conf` values.
* **File Handle Leak** - Fixed unclosed file handle during AppInspect API submission.
* **Thread Error Handling** - AppInspect thread exceptions now properly set "Error" status instead of leaving stale "Running" status.
* **Documentation Fixes** - Fixed YAML indentation in code examples, version contradictions for deprecated utility (v5 → v6), removed duplicate section, added expression delimiters to workflow examples, updated `upload-artifact` references to v6.
* **Troubleshooting** - Added entry for common first-time user issue when `is_app_inspect_check` defaults to `true` without credentials.
* **Actionable Error Messages** - Improved error messages for missing Splunkbase credentials (suggests `local_app_inspect` or disabling), dependency installation failures (shows pip exit code and package details), and unsupported utilities (lists valid options).

### Developer & Internal Changes

* Extracted `AppInfo.publish()` from constructor to separate object creation from CI side effects.
* Made `BaseUtility` an ABC with `@abstractmethod` for `implement_utility`.
* Added `usedforsecurity=False` to `hashlib.md5()` for FIPS compliance.
* Removed dead code: unused constants, dead fields, prohibited `if __name__` block, stray `print()`.
* Expanded changelog check to cover docs, action.yml, and workflow changes.
* Fixed `devtools/lint.py` DOC_PATHS to use correct `devtools/` prefix.
* Removed redundant CI steps, added concurrency group, reduced `fetch-depth`.
* Added ~24 new unit tests covering previously untested modules.
* Fixed integration test validation to accept "Warning" as a non-failing status alongside "Passed".
* Added unit tests for `validate_mutually_exclusive_features` and conf parser duplicate stanza handling.
* Added `fail_on=warnings` integration test to verify action fails when warnings are present.


## [v5](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v5.0.0) - 2025-11-19

### Upgrade Notes

- **`my_github_token` No Longer Required for App Utilities** - The action now uses the workflow's automatic `GITHUB_TOKEN` by default
  - **Breaking Change:** The `my_github_token` input is now optional - you can omit it entirely
  - **Required:** Grant repository-wide permissions for the action to create branches and pull requests:
    1. Go to Repository Settings → Actions → General
    2. Scroll to "Workflow permissions"
    3. Select "Read and write permissions"
    4. Check "Allow GitHub Actions to create and approve pull requests"
  - **Alternative:** Continue using `my_github_token` with a Personal Access Token (PAT) for cross-repo permissions or explicit token management
  - **Migration:** Remove `my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}` from your workflow and configure repository permissions
  - **Note:** Workflow-level `permissions:` blocks do not work for composite actions
  - See updated examples in documentation for the new simplified configuration

- **Migrate from `splunk_python_sdk` utility** - Consider migrating to the new `python_requirements_file` feature for better dependency management.

### Deprecated

- **Splunk Python SDK Utility (`splunk_python_sdk`)** - Deprecated and will be removed in v6
  - Users should migrate to the new Python Dependency Manager feature
  - Allows installing splunklib and other libraries without copying them into the repository
  - Deprecation warning is now displayed when using this utility

### Added

- **App Inspect Inline Annotations** - AppInspect results now appear as inline annotations in the Files Changed tab - no configuration needed!
  - App-inspect failures and errors now appear as inline annotations on PR as comments, so you can act very fast.
  - Annotations work automatically with no additional configuration required.
  - Note: Annotations are published for app-inspect only, not for cloud-inspect or ssai-inspect.
  - Annotation titles now include group name: `"App-Inspect: <Group Name> : <Check Name>"`
  - Example: `"App-Inspect: Check Alert Actions Config : Check For Payload Format"`

- **Flexible Failure Modes** - Control workflow failure based on AppInspect results
  - New `fail_on` input to control failure behavior (default: "errors")
  - Options:
    - `"errors"` - Fail only on errors and failures (default behavior)
    - `"warnings"` - Fail on warnings, errors, or failures (strict quality enforcement)
    - `"none"` - Never fail based on AppInspect results (informational mode)
  - Allows gradual adoption of AppInspect checks without breaking builds
  - Useful for collecting metrics while fixing existing issues

- **Local App-Inspect Support** - New input parameter `local_app_inspect`
  - Enables local Splunk App Inspect validation using the splunk-appinspect Python library
  - Provides faster validation without requiring Splunkbase credentials
  - May not be as up-to-date as the Splunkbase API
  - Default is `false`

- **Github Action Summaries** - Comprehensive build summary displayed in GitHub Actions UI
  - Automatically generates a job summary with build metadata and AppInspect results
  - Displays build information table with app package ID, version, build number, and artifact paths
  - Shows AppInspect results table with status indicators and emoji for easy visualization (✅ Passed, ❌ Failure, ⏭️ Skipped, etc.)
  - Includes direct link to download workflow artifacts

- **Enhanced Action Outputs** - New output variables for better workflow integration
  - `build_path` - Full path to the generated build artifact (.tgz file)
  - `artifact_name` - Name of the generated build artifact (e.g., my_app_1.0.0_1.tgz)
  - `app_package_id` - The Splunk app package ID extracted from app.conf or globalConfig.json
  - `app_version` - The app version number extracted from app.conf or globalConfig.json
  - `app_build_number` - The app build number extracted from app.conf
  - `app_inspect_status` - Status of app-inspect check (Passed, Failure, Error, Timed-out, Exception, Skipped, or Not Run)
  - `cloud_inspect_status` - Status of cloud-inspect check (Passed, Failure, Error, Timed-out, Exception, Skipped, or Not Run)
  - `ssai_inspect_status` - Status of SSAI-inspect check (Passed, Failure, Error, Timed-out, Exception, Skipped, or Not Run)
  - These outputs can be used in subsequent workflow steps for custom processing, release automation, or artifact management

- **Python Dependency Manager** - New feature for managing Python dependencies from requirements.txt
  - New input parameter `python_requirements_file` to specify the path to requirements.txt file (relative to app_dir)
  - Dependencies are installed in the same directory as the requirements file (e.g., `lib/requirements.txt` → installs to `lib/`)
  - If requirements file is in app root, automatically creates and uses `lib/` subdirectory
  - Cleans the target directory before installation to ensure clean state
  - Removes requirements.txt file from the final build package
  - Enables use of GitHub Dependabot for automatic dependency updates
  - Keeps repository clean by managing dependencies at build time instead of committing third-party code
  - Automatically cleans up `.pyc` files and `__pycache__` directories
  - Mutually exclusive with UCC-Gen and Splunk-Python-SDK utility to prevent conflicts
  - Can replicate splunk-python-sdk installation functionality by using `splunk-sdk` in requirements.txt

- **Enhanced Documentation**
  - Moved comprehensive documentation from README to dedicated Read the Docs site
  - Enhanced `overview.md` with comprehensive introduction explaining action purpose, key features, and capabilities
  - Significantly expanded `troubleshooting.md` with 10+ additional issue scenarios
  - Rewrote `CONTRIBUTING.md` with detailed contribution workflow, development setup steps, coding standards, and testing guidelines
  - Added explicit OS support documentation (ubuntu-latest, ubuntu-22.04, ubuntu-20.04)
  - Added comprehensive artifact naming documentation.


### Changed

- **Simplified Authentication for App Utilities** - `my_github_token` is now optional
  - The action automatically uses the workflow's built-in `GITHUB_TOKEN` when `my_github_token` is not provided
  - Users must configure repository-wide permissions for automatic token usage (workflow-level `permissions:` blocks do not work for composite actions)
  - Personal Access Tokens (PAT) via `my_github_token` are still supported for advanced use cases
  - Simplifies workflow configuration - no need to create and manage custom GitHub tokens for basic usage

- **Utility PR Title Improvement** - Automatically generated PRs now contains more human readable PR titles instead of file hash as PR title.

- **Logging Improvements**
  - GitHub action now generates more readable logs
  - Log groups allow expanding/collapsing details as needed
  - Emojis used in important logs for easy distinction

- **Build Feature Validation** - Added validation to ensure only one build feature is used at a time
  - Users can now only use ONE of: UCC-Gen, Python-Dependency-Management, or Splunk-Python-SDK utility
  - Workflow will fail with clear error message if multiple features are enabled
  - Prevents conflicting dependency management approaches

### Fixed

- **AppInspect Artifact Upload** - Upload conditions now properly check if app-inspect is enabled
  - App-inspect reports artifact only uploads when `is_app_inspect_check` is true
  - Prevents unnecessary upload attempts when app-inspect is disabled and showing warnings

- **Utility Error Handling** - Adding Utility Errors are now handled gracefully
  - If one utility fails, rest of the utilities continue to operate normally

- **Splunk Python SDK Cleanup** - Properly cleans up old package metadata files
  - Removes `.dist-info` and `.egg-info` directories after upgrading splunklib to a new version
  - Prevents accumulation of outdated files
  - Includes cleanup of old versions of splunk-sdk's dependencies (e.g., `deprecation`, `packaging`)

- **Various Build Process Fixes** - Fixed app build process issues and file handling problems

### Developer & Internal Changes

- **AppInspect Architecture** - Introduced `BaseAppInspect` abstract class, eliminating ~200 lines of code duplication and standardizing JSON-first approach with centralized HTML conversion

- **Dependency Updates** - Upgraded 12 dependencies including `basedpyright` (1.31.7→1.33.0), `github-action-toolkit` (0.7.0→0.8.0), `rich` (8.4.2→9.0.0), `ruff` (0.14.1→0.14.4), `splunk-appinspect` (4.0.2→4.1.0)

- **Code Quality** - Added comprehensive docstrings, improved formatting/type-checking across codebase, enhanced working directory and dependency handling

- **Project Infrastructure** - Added AI agent instructions, improved CI/CD workflows (`changelog_check.yml`, `test.yml`, `release.yml`), added `CONTRIBUTING.md`, issue templates, Dependabot, and developer tools (`lint.py`, `prepare_changelog.py`, etc.)

- **Refactoring** - Migrated to `github-action-toolkit` (removed `git_manager.py`, `github_action_utils.py`), replaced `GlobalVariables` with `SavedPaths`/`AppInfo` classes, reorganized file/folder hash functions, improved test infrastructure


## [v4.1](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.1) - 2024-04-09

### Added

- `splunk_python_sdk_install_path` parameter for `splunk_python_sdk` utility. Default is `bin`, but now user-configurable.
- Automatic removal of `.pyc` files and `__pycache__` directories from the `splunk_python_sdk` folder to keep them out of Pull Requests. Can be disabled via `is_remove_pyc_from_splunklib_dir` parameter.


## [v4](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4) - 2024-03-17

### Changed
- User-defined shell commands now run in the context of the app's root directory instead of the repository root.
- Default value of `to_make_permission_changes` is now `false`.

### Added
- Automatic file permission changes now also include `.msi`, `.exe`, `.cmd`, `.bat` files (in addition to `.sh`).

### Removed
- Input parameters `is_generate_build` and `app_build_path`.

### Upgrade Notes

* User-defined commands now run from app directory context:

Before:

```yaml
env:
  SPLUNK_APP_ACTION_1: "rm -rf my_app/extra_test_folder"
  SPLUNK_APP_ACTION_2: "cat 'abc,123' >> my_app/lookups/my_custom_lookup.csv"
with:
  app_dir: "my_app"
```

After:

```yaml
env:
  SPLUNK_APP_ACTION_1: "rm -rf extra_test_folder"
  SPLUNK_APP_ACTION_2: "cat 'abc,123' >> lookups/my_custom_lookup.csv"
with:
  app_dir: "my_app"
```

- Permission changes must now be explicitly enabled:
    - Set `to_make_permission_changes`: true in the workflow if required.

- Deprecated Parameters:
    - `is_generate_build` and `app_build_path` must be removed or updated in your workflow configuration.


## [v3](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v3) - 2024-02-19

### Added

- use_ucc_gen parameter for supporting UCC build Add-ons via `ucc-gen build` command.
- Utility: `ucc_additional_packaging` for Python input handler structure generation.
- Auto-detection of App Package ID, App Version, and App Build number.
- Improved build naming convention for Apps and Add-ons.
- Utilities run on the current branch for better support and cleaner codebase.
- Automatic cleanup of unwanted files from the build to pass App Inspect checks.

## [v2](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v2) - 2023-10-11

### Added

- Automatic file permission fix to resolve App Inspect failures.

- Utilities:

    - whats_in_the_app: App content info added to README.md.
    - logger: Adds logger and props.conf entries.
    - splunk_python_sdk: Auto-upgrades Splunklib Python SDK.
    - common_js_utilities: Adds common JavaScript utilities.

## [v1](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v1) - 2022-11-09

### Added

- Initial release of the GitHub Action for Splunk Apps.
- Generates builds for Splunk Apps and Add-ons.
- Automatically runs Splunk App Inspect on builds.
