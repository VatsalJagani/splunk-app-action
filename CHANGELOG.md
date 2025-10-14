# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [v4.3.2](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.3.2) - 2025-10-14

- Logging Improvements
- Fixed warnings by uv command in installing python.

## [v4.3.1](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.3.1) - 2025-10-14

## [v4.3.0](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.3.0) - 2025-10-14

### Changed

- Logging improved for better troubleshooting and user readability.


## [v4.2.3](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.2.3) - 2025-10-14

## [v4.2.2](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.2.2) - 2025-10-14

## [v4.2.1](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.2.1) - 2025-10-14

### Added

### Changed

- Full codebase is now properly formatted.
- Full source-code is now properly type-checked and properly annotated.

### Fixed

### Removed



## [v4.2.0](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v4.2.0) - 2025-10-13

### Added
- Support for version file test cases.
- New GitHub workflows for CI/CD and release.
- Dependabot configuration.
- Developer tools and related documentation.
- `pyproject.toml` and `Makefile` for standardized developer ease.
- Agent rules and issue templates for GitHub.

### Changed
- Replaced usage of `GlobalVariables` with standard classes.
- Input variable names are now capitalized and consistently named.
- Switched to `github_action_toolkit` for GitHub-related operations.
- Rearranged file-related functions for better maintainability.
- Improved handling of app-build dependencies.
- Changed temp file generation strategy for test cases.
- Improved working directory management for consistency across builds.

### Fixed
- Code formatting improved throughout the codebase.
- Fixed naming and parsing of GitHub Action inputs.
- Fixed bug in executing user-defined shell commands in workflows.
- Fixed coverage reporting and test failures.
- Minor fixes related to app build processes and file handling.

### Removed
- Redundant test cases.
- Unused or incorrect files from the repo.

### Documentation
- Moved Documentation from GitHub's README.md file to separate on read-the-docs.
- Major improvements and fixes to documentation.
- Added a dedicated troubleshooting section.
- Added support for building documentation separately.
- Included debugging steps and developer contribution help.


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
