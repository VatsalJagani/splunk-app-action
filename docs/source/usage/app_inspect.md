# App-Inspect & Cloud Checks

## Run App-Inspect (with Splunkbase API)

- Runs app-inspect with Splunkbase API.
- Generates HTML reports as GitHub artifacts (see Actions tab).
- Performs Splunk Cloud and SSAI checks.

Requires:
- `splunkbase_username` and `splunkbase_password` inputs (use GitHub secrets).

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
    splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```
