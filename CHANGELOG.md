# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## Changed
* **`splunk_python_version` Input** - Default value of the input for the Python Dependency Manager that controls which Python version is changed from `3.9` to `3.13` since Splunk is asking App developers to support 3.13 Python version.

### Developer & Internal Changes

* **Dependency Updates** - Updated all main and dev dependencies to their latest compatible versions (including `splunk-add-on-ucc-framework`, `splunk-appinspect`, `requests`, `pip`, `ruff`, `pytest`, `basedpyright`, and Sphinx tooling) and refreshed `uv.lock`. Github action dependacies update.
* **Deprecation Cleanup** - Replaced deprecated `os.system` / `os.popen` calls with `subprocess.run` (surfaced by the newer `basedpyright`) in `src/app_build_generate.py` and `devtools/release_notes.py`.


## [v6.1.2](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v6.1.2) - 2026-05-20

### Fixed

* **`is_remove_not_allowed_executables_from_lib` for Python Dependency Manager** - This input now also applies when using `python_requirements_file`. Previously it only worked for UCC builds. Use this to strip platform-specific compiled extensions (e.g. `charset-normalizer` `.so` files) that cause App Inspect `check_aarch64_compatibility` failures.

## [v6.1.1](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v6.1.1) - 2026-05-20

### Fixed

* **UCC Build - `.python-version` Removal** - `.python-version` is now removed from the build for all build types (UCC, Python dependency manager, and standard). Previously it was only removed by the Python Dependency Manager, so UCC add-ons that place `.python-version` inside `package/` (so Dependabot can read it) would have it copied into the ucc-gen output and fail App Inspect with `check_that_extracted_splunk_app_does_not_contain_prohibited_directories_or_files`.

## [v6.1.0](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v6.1.0) - 2026-05-19

### Added

* **`splunk_python_version` Input** - New input for the Python Dependency Manager that controls which Python version is targeted when installing dependencies. Defaults to `3.9` (Splunk's current default runtime). Pass a different version (e.g., `"3.13"`) if your Splunk platform uses a newer Python. This ensures installed packages are resolved against the correct Python version and prevents installing incompatible library versions.
* **`.python-version` Auto-Exclusion** - The Python Dependency Manager now automatically removes `.python-version` from the app build. This file can be placed in the app directory to constrain Github Dependabot to Python-version-compatible package suggestions, without it ending up in the final Splunk package.

### Fixed

* **Python Dependency Manager - uv Artifact Cleanup** - The `.lock` file and `bin/` directory created by `uv pip install --target` are now removed from the build. These are not needed at Splunk runtime and caused Splunk App Inspect failures (`check_that_extracted_splunk_app_does_not_contain_prohibited_directories_or_files`). The `bin/` directory is only removed if all files within it are console entry point scripts (identified by shebang `#!`); if any non-script file, subdirectory, or symlink/special file is found, the directory is preserved and a warning is logged.

## [v6.0.2](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v6.0.2) - 2026-04-24

### Fixed

* **UCC Additional Packaging - Handler Signature** - Generated `<input>_handler.py` now includes `session_key: str` as the first parameter in both `validate_input` and `stream_events`, making the session key available without requiring access to internal script attributes.
* **UCC Additional Packaging - Regex Robustness** - Regex patterns for `validate_input` and `stream_events` replacement are now non-greedy, preventing incorrect matches when multiple methods are present. Each substitution now raises `RuntimeError` if the pattern does not match, surfacing UCC output format changes instead of silently producing a broken file.
* **UCC Additional Packaging - `validate_input` Session Key Source** - Fixed incorrect use of `self._input_definition.metadata['session_key']` inside `validate_input`; now correctly uses `definition.metadata['session_key']`.

## [v6.0.1](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v6.0.1) - 2026-04-18

### Fixed

* **`setup-uv@v5` Compatibility** - Removed `python-version` from `astral-sh/setup-uv@v5` step to prevent venv activation failure in composite action context. Python 3.12 is now explicitly installed in a separate step scoped to the action's own directory.
* **Duplicate Utility PR** - Utility PR creation is now skipped when the remote branch already exists (same content hash), preventing a non-fast-forward `git push` failure on repeated workflow runs.
* **Python Dependency Manager Metadata Cleanup** - `.dist-info` directories created by `pip install --target` are now removed from `lib/` after installation. These pip metadata directories are not needed at Splunk runtime and unnecessarily bloat the app package.

### Developer & Internal Changes

* Bumped `softprops/action-gh-release` from v2 to v3 (Node 20 → Node 24 runtime) in `release.yml`.
* Bumped `VatsalJagani/pytest-cov-action` from v1.3 to v1.4 in `test.yml`.
* Bumped `actions/upload-artifact` from v6 to v7 in `action.yml`.
* Applied `setup-uv@v5` fix to `release.yml` and `test.yml` as well.

## [v6](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v6) - 2026-04-06

### Changed

* **AppInspect Warning Status** - AppInspect checks now return "Warning" status when warnings exist but no errors/failures, enabling `fail_on: warnings` to work correctly.
* **UCC Additional Packaging** - Reduced manual code writing for UCC-based Add-on input handlers.
* **Build Logging** - Improved debugging logs during app build generation.
* **Job Summary** - Added Warning emoji (`⚠️`), distinct Exception emoji (`💥`), and `fail_on` mode display in AppInspect results table.
* **Actionable Error Messages** - Improved error messages for missing Splunkbase credentials, dependency installation failures, and unsupported utilities with specific guidance.

### Added

* **`is_remove_not_allowed_executables_from_lib` Input** - Controls removal of executable/shared-library files from UCC-generated `lib/` before packaging (default: `false`). Set to `true` for stricter AppInspect compliance.
* **Troubleshooting** - Added entry for common first-time user issue when `is_app_inspect_check` defaults to `true` without credentials.

### Removed

* **`splunk_python_sdk` Utility** - Removed the deprecated Splunk Python SDK utility and its inputs (`splunk_python_sdk_install_path`, `is_remove_pyc_from_splunklib_dir`). Use the Python Dependency Manager (`python_requirements_file`) with `splunk-sdk` in your requirements.txt instead.

### Fixed

* **UCC Utility Paths** - Fixed file/folder path resolution when running UCC-based utilities.
* **UCC Build Detection** - Fixed silent build generation failure when app folder name matches app package ID.
* **Action Failure Handling** - Missing inputs and utility failures now correctly fail the Github workflow.
* **Python Dependency Manager** - Fixed path construction bug where dependencies were installed into the original checkout instead of the build copy.
* **Context Manager Safety** - Fixed `keep_working_dir_unchanged` missing `try/finally`, which could leave the process in the wrong directory after an exception.
* **Shell Injection Prevention** - Replaced `os.system()` calls with `shutil.move()` and `subprocess.run()` to prevent potential shell injection via user-controlled `app.conf` values.
* **File Handle Leak** - Fixed unclosed file handle during AppInspect API submission.
* **Thread Error Handling** - AppInspect thread exceptions now properly set "Error" status instead of leaving stale "Running" status.
* **Documentation** - Fixed YAML indentation in examples, version references, duplicate sections, expression delimiters, and `upload-artifact` references.

### Developer & Internal Changes

* Extracted `AppInfo.publish()` from constructor to separate object creation from CI side effects.
* Made `BaseUtility` an ABC with `@abstractmethod` for `implement_utility`.
* Added `usedforsecurity=False` to `hashlib.md5()` for FIPS compliance.
* Removed dead code: unused constants, dead fields, prohibited `if __name__` block, stray `print()`.
* Improved CI: expanded changelog check scope, added concurrency group, reduced `fetch-depth`, removed redundant steps.
* Fixed `devtools/lint.py` DOC_PATHS to use correct `devtools/` prefix.
* Added ~30 unit tests covering mutual exclusivity validation, duplicate stanza handling, and previously untested modules.
* Added integration tests for error cases (missing `app.conf`, invalid `app_dir`) and `fail_on=warnings` behavior.
* Fixed integration test validation to accept "Warning" as a non-failing status alongside "Passed".


## [v5](https://github.com/VatsalJagani/splunk-app-action/releases/tag/v5) - 2025-11-19

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
