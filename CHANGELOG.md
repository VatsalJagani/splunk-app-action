# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- **Integration Test for UCC + SARIF** - Added integration test to verify SARIF file paths for UCC-based apps
  - Validates that SARIF file paths correctly include `app_dir/package/` prefix for UCC apps
  - Ensures GitHub Code Scanning annotations work correctly for UCC add-ons in subdirectories

### Fixed

- **SARIF File Paths** - Corrected file paths in SARIF reports for both regular and UCC-based apps
  - SARIF file paths now correctly prepend `app_dir` to make them relative to repository root
  - For UCC-based apps, file paths correctly point to `app_dir/package/` where source files reside
  - For regular apps, file paths point to `app_dir/` directory
  - Ensures GitHub Code Scanning annotations appear on correct files when app is in subdirectory
  - When `app_dir` is "." (repository root), appropriate paths are used (no prefix for regular, `package/` for UCC)

### Changed

- **AppInspect Report Generation** - Standardized on JSON-first approach for both API and local inspection
  - Both API-based and local AppInspect now generate JSON reports first, then convert to HTML
  - Uses centralized HTML converter module for consistent formatting across inspection modes
  - Ensures JSON is the canonical report format, making it easier to process and validate results
  - Eliminates duplicate HTML generation code (~100 lines removed)

- **SARIF Publishing** - Now enabled by default
  - Changed `publish_sarif` default value from `false` to `true`
  - SARIF reports will automatically be generated and uploaded to GitHub Code Scanning
  - Provides inline code annotations in Pull Requests without additional configuration
  - Can be disabled by setting `publish_sarif: false` if not desired

### Added

- **SARIF Code Scanning Support** - Publish AppInspect results for GitHub Code Scanning
  - New `publish_sarif` input to enable SARIF report generation from AppInspect JSON results
  - Converts AppInspect failures, errors, and warnings to SARIF 2.1.0 format
  - Enables inline code annotations in Pull Requests for quality issues
  - Automatically uploaded to GitHub Code Scanning via CodeQL action
  - Supports all three inspect types (app-inspect, cloud-inspect, ssai-inspect)
  - Merged into single SARIF file for unified reporting

- **GitHub Check Runs** - Display AppInspect status with summaries
  - Publishes check run summaries with error/warning counts
  - Shows detailed breakdown of success, failure, error, warning, manual check, skipped, and not applicable counts
  - Lists up to 5 failed checks with option to view full report
  - Includes direct links to AppInspect artifacts
  - Visible in PR checks UI for quick feedback

- **Flexible Failure Modes** - Control workflow failure based on AppInspect results
  - New `fail_on` input to control failure behavior (default: "errors")
  - Options:
    - `"errors"` - Fail only on errors and failures (default behavior)
    - `"warnings"` - Fail on warnings, errors, or failures (strict quality enforcement)
    - `"none"` - Never fail based on AppInspect results (informational mode)
  - Allows gradual adoption of AppInspect checks without breaking builds
  - Useful for collecting metrics while fixing existing issues

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

- **GitHub Job Summary** - Comprehensive build summary displayed in GitHub Actions UI
  - Automatically generates a job summary with build metadata and AppInspect results
  - Displays build information table with app package ID, version, build number, and artifact paths
  - Shows AppInspect results table with status indicators and emoji for easy visualization (✅ Passed, ❌ Failure, ⏭️ Skipped, etc.)
  - Includes direct link to download workflow artifacts
  - Written to `$GITHUB_STEP_SUMMARY` for visibility in GitHub Actions interface

- **Operating System Support Documentation** - Explicit documentation about supported platforms
  - Action is tested and supported on ubuntu-latest, ubuntu-22.04, and ubuntu-20.04
  - Windows and macOS runners are not supported due to Linux-specific dependencies
  - Clear guidance on required `runs-on` configuration

- **Artifact Naming Documentation** - Comprehensive documentation of artifact naming patterns
  - Build artifacts follow the pattern: `{app_package_id}_{version_encoded}_{build_number_encoded}.tgz`
  - GitHub artifact uploads use: `App-Build-{app_package_id}_{version_encoded}_{build_number_encoded}`
  - Inspect reports use: `App-Inspect-Reports-{app_package_id}_{version_encoded}_{build_number_encoded}`
  - All special characters are encoded to underscores for filesystem and URL safety

- **Python Dependency Manager** - New feature for managing Python dependencies from requirements.txt
  - New input parameter `python_requirements_file` to specify the path to requirements.txt file (relative to app_dir)
  - Dependencies are installed in the same directory as the requirements file (e.g., `lib/requirements.txt` → installs to `lib/`)
  - If requirements file is in app root, automatically creates and uses `lib/` subdirectory.
  - Cleans the target directory before installation to ensure clean state
  - Removes requirements.txt file from the final build package
  - Enables use of GitHub Dependabot for automatic dependency updates
  - Keeps repository clean by managing dependencies at build time instead of committing third-party code
  - Automatically cleans up `.pyc` files and `__pycache__` directories
  - Mutually exclusive with UCC-Gen and Splunk-Python-SDK utility to prevent conflicts
  - Can replicate splunk-python-sdk installation functionality by using `splunk-sdk` in requirements.txt

- **Comprehensive Code Documentation** - Added docstrings throughout the codebase
  - Added comprehensive docstrings to all previously undocumented classes and functions
  - Core modules: `app_build_generate.py`, `ucc_gen.py`, `app_utilities.py`
  - Helper modules: `file_manager.py` (all handler classes), `saved_values.py` (AppInfo, SavedPaths)
  - All utility classes: `BaseUtility`, `LoggerUtility`, `SplunkPythonSDKUtility`, `WhatsInsideTheAppUtility`, `UCCAdditionalPackagingUtility`, `CommonJSUtilitiesFile`
  - All docstrings follow consistent style with parameter descriptions, return value documentation, and behavioral context

- **Enhanced Documentation Pages** - Improved documentation completeness and consistency
  - Enhanced `overview.md` with comprehensive introduction explaining action purpose, key features, and capabilities
  - Significantly expanded `troubleshooting.md` with 10+ additional issue scenarios including Python dependency failures, build errors, AppInspect timeouts, feature conflicts, and SARIF publishing issues
  - Rewrote `CONTRIBUTING.md` with detailed contribution workflow, development setup steps, coding standards, and testing guidelines

- New Documentation
  - Moved comprehensive documentation from README to dedicated Read the Docs site.
  - Enhanced documentation with dedicated troubleshooting section and debugging steps.

- New input parameter `local_app_inspect` to enable local Splunk App Inspect validation using the splunk-appinspect Python library instead of the Splunkbase API. This provides faster validation but may not be as up-to-date as the Splunkbase API. Default is `false`.


### Changed

- **Dependency Updates** - Upgraded dependencies to latest stable versions
  - `basedpyright`: 1.31.7 → 1.33.0 (improved type checking)
  - `coverage`: 7.11.0 → 7.11.1 (test coverage improvements)
  - `github-action-toolkit`: 0.7.0 → 0.8.0 (GitHub Actions integration)
  - `lxml`: 3.9 → 3.10 (XML processing)
  - `pip`: 25.2 → 25.3 (package installer)
  - `pydantic`: 2.12.3 → 2.12.4 (data validation)
  - `requests`: 2.41.4 → 2.41.5 (HTTP library)
  - `rich`: 8.4.2 → 9.0.0 (terminal formatting)
  - `ruff`: 0.14.1 → 0.14.4 (linter and formatter)
  - `splunk-appinspect`: 4.0.2 → 4.1.0 (AppInspect validation)
  - `starlette`: 0.48.0 → 0.50.0 (web framework)
  - `termcolor`: 3.1.0 → 3.2.0 (colored terminal output)

- **Build Feature Validation** - Added validation to ensure only one build feature is used at a time
  - Users can now only use ONE of: UCC-Gen, Python-Dependency-Management, or Splunk-Python-SDK utility
  - Workflow will fail with clear error message if multiple features are enabled
  - Prevents conflicting dependency management approaches

- Logging Improvements
  - GitHub action now generates more readable logs.
  - GitHub action now also creates log groups, so not every single logs is visible at a time, user can expand the group and check more details if needed.
  - Emojis are used in important logs to easily distinguish logs.

- `logger_manager.py` file (from Logger Utility) is now following better code formatting and type-checking.

- `additional_packaging.py` file (from UCC Additional Packaging Utility) is now following better code formatting and type-checking.

- Enhanced working directory management for more consistent builds across different environments.

- Improved app build dependency handling for more reliable builds.

### Deprecated

- **Splunk Python SDK Utility (`splunk_python_sdk`)** is now deprecated and will be removed in v6. Users should plan to migrate to the new dynamic library installation feature in v5, which allows installing splunklib and other libraries without copying them into the repository. A deprecation warning is now displayed when using this utility.

### Fixed

- Adding Utility Errors are now handled gracefully. So if one utility fails, rest of the utility continues to operate normal.

- Fixed various app build process issues and file handling problems.

- Splunk Python SDK Utility now properly cleans up old package metadata files (`.dist-info` and `.egg-info` directories) after upgrading splunklib to a new version, preventing accumulation of outdated files. This also includes cleanup of old versions of splunk-sdk's dependencies (e.g., `deprecation`, `packaging`).

### Developer & Internal Changes

- AI Agent's instruction files are added for AI Agents (Claude or GitHub Copilot) to generate good code and perform checks without explicit instructions all the time.

- Improved GitHub workflows for better CI/CD and release management.
  - `changelog_check.yml` - Validating changelogs.
  - `test.yml` - Linting checks, Type-checking, testing, and docs validation.
  - `release.yml` - For creating release on GitHub.
  - (Removed) `py_unit_tests.yml` - Old test workflow.

- Added `CONTRIBUTING.md` and `pull_request_template.md` files.
- Added GitHub issue templates.
- Added Dependabot configuration.
- Added `development.md` and `release.md` files for developer notes.
- Removed `DEV.md` file.

- Added developer tools and helper files for easy development workflow
  - create_tag.sh
  - lint.py
  - prepare_changelog.py
  - release_notes.py
  - Makefile
  - pyproject.toml

- Overall Coding Improvements
  - Full codebase code is now properly formatted.
  - Full codebase is now properly linted and type-checked.

- Source code changes:
  - file and folder hash related functions moved to file_manager.py
  - Removed git_manager.py (using `github-action-toolkit` lib instead.)
  - Removed github_action_utils.py (using `github-action-toolkit` lib instead.)
  - Replaced usage of `GlobalVariables` with standard classes (SavedPaths and AppInfo) for better code.
  - version.py file added.

- Test code changes:
  - Improved `setup_action_yml` contextmanager to handle all the different scenarios and possible issues.
  - Test-cases are now executed in a separate folder that works both locally and on GitHub workflow in the same way.
  - Removed redundant test cases and cleaned up unused files.
  - Changed temp file generation strategy for more reliable test cases.
  - Full codebase is now properly formatted and type-checked.


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
