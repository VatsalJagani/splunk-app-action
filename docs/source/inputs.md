# Inputs

Below are the available inputs for the splunk-app-action GitHub Action. See workflow examples for usage.

## app_dir
- Directory of your app/add-on. Default: "." (repo root)

## to_make_permission_changes
- Whether to apply file/folder permission changes for Splunk App Inspect. Default: false

## use_ucc_gen
- Use ucc-gen for Add-on build. Requires `package` subfolder and `globalConfig.json`.

## is_app_inspect_check
- Whether to perform Splunk app-inspect checks. Default: true

## splunkbase_username / splunkbase_password
- Credentials for Splunkbase API (use GitHub secrets)

## app_utilities
- Comma-separated list of utilities to use. Valid: whats_in_the_app, logger, splunk_python_sdk, common_js_utilities, ucc_additional_packaging

## my_github_token
- GitHub token for creating PRs (use secrets)

## logger_log_files_prefix / logger_sourcetype
- Logger utility options

## splunk_python_sdk_install_path
- Path for Splunklib SDK install. Default: "bin"

## is_remove_pyc_from_splunklib_dir
- Remove `.pyc` and `__pycache__` from SDK install path. Default: true
