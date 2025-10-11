# Permissions & User Commands

## Avoid File and Folder Permission Issues

- If your app has executable files other than `.sh`, avoid enabling `to_make_permission_changes` unless needed.
- You can use user-defined commands to set permissions as required.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    to_make_permission_changes: true
    splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
    splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

Example shell commands used:

```sh
find my_app -type f -exec chmod 644 '{}' \;
find my_app -type f -name '*.sh' -exec chmod 755 '{}' \;
find my_app -type d -exec chmod 755 '{}' \;
```

## Running User Defined Commands Before Build

Set environment variables `SPLUNK_APP_ACTION_<n>` to run commands before build generation.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  env:
    SPLUNK_APP_ACTION_1: "find . -type f -exec chmod 644 '{}' \;"
    SPLUNK_APP_ACTION_2: "find . -type f -name '*.sh' -exec chmod +x '{}' \;"
    SPLUNK_APP_ACTION_3: "find . -type d -exec chmod 755 '{}' \;"
  with:
    app_dir: "my_app"
```

- Maximum 99 commands: `SPLUNK_APP_ACTION_1` to `SPLUNK_APP_ACTION_99`.
- Commands run in the app's root directory context.
