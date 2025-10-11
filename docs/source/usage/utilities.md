# Utilities

## Provided Utilities

- `whats_in_the_app`: Adds app info to README.md
- `logger`: Adds Python logger and config
- `splunk_python_sdk`: Adds/updates Splunklib SDK
- `common_js_utilities`: Adds common JS utilities
- `ucc_additional_packaging`: Adds helper for UCC input handler

All utilities require the `my_github_token` input for creating pull requests.

### Example: Add App Info Utility

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    app_utilities: "whats_in_the_app"
    my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
```

### Example: Add Logger Utility

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    app_utilities: "logger"
    my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
    logger_log_files_prefix: "my_app"
    logger_sourcetype: "my_app:logs"
```
