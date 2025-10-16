# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- New input parameter `local_app_inspect` to enable local Splunk App Inspect validation using the splunk-appinspect Python library instead of the Splunkbase API. This provides faster validation but may not be as up-to-date as the Splunkbase API. Default is `false`.

- New Documentation
  - Moved comprehensive documentation from README to dedicated Read the Docs site.
  - Enhanced documentation with dedicated troubleshooting section and debugging steps.


### Changed

- Logging Improvements
  - GitHub action now generates more readable logs.
  - GitHub action now also creates log groups, so not every single logs is visible at a time, user can expand the group and check more details if needed.
  - Emojis are used in important logs to easily distinguish logs.

- `logger_manager.py` file (from Logger Utility) is now following better code formatting and type-checking.

- `additional_packaging.py` file (from UCC Additional Packaging Utility) is now following better code formatting and type-checking.

- Enhanced working directory management for more consistent builds across different environments.

- Improved app build dependency handling for more reliable builds.

### Fixed

- Adding Utility Errors are now handled gracefully. So if one utility fails, rest of the utility continues to operate normal.

- Fixed various app build process issues and file handling problems.

### Developer & Internal Changes

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
