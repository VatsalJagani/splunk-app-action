# Troubleshooting

### Unable to push changes into the branch

```
Unable to push changes into the branch=splunk_app_action_bbe00a4a32a796cc84b73b09abc09922
```

This error occurs when GitHub workflows don't have permission to create pull requests.

**Solution:**
1. Go to your Repository `Settings` > `Actions` > `General`
2. Scroll down to **Workflow permissions** section
3. Select **Read and write permissions**
4. Make sure **Allow GitHub Actions to create and approve pull requests** is checked

![Workflow Permission Settings](_static/images/workflow_permission_for_pr_1.png)

![Workflow Permission Detail](_static/images/workflow_permission_for_pr_2.png)

### App-Inspect Check Failures

#### Authentication Issues
```
Failed to authenticate with Splunkbase API
```

**Solution:** Verify your Splunkbase credentials:
- Ensure `splunkbase_username` and `splunkbase_password` are correctly set in GitHub secrets
- Test your credentials by logging into [Splunkbase](https://splunkbase.splunk.com) manually

#### Permission Issues with File Changes
```
App-inspect failed due to file permission issues
```

**Solution:** Enable automatic permission fixes:
```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    to_make_permission_changes: true
```

**⚠️ Warning:** Only use this if your app doesn't have custom executable files other than `.sh`, `.exe`, `.bat`, `.cmd`, `.msi`

### UCC Build Issues

#### Missing UCC Structure
```
globalConfig.json not found or package folder missing
```

**Solution:** 
1. Run `ucc-gen init` locally first to set up proper UCC structure
2. Ensure your app has both `globalConfig.json` and `package/` folder
3. Follow [UCC Framework documentation](https://splunk.github.io/addonfactory-ucc-generator/quickstart/)

### User Defined Commands Issues

#### Commands not executing
```
SPLUNK_APP_ACTION_1 command not found or failed
```

**Solution:**
- Ensure commands are valid Linux shell commands
- Remember: commands run in your app's root directory (not repo root)
- Use proper escaping for special characters: `\\;` instead of `;`

### Utility Issues

#### GitHub Token Problems
```
Failed to create pull request - authentication failed
```

**Solution:**
1. Create a personal access token in GitHub Settings > Developer settings > Personal access tokens
2. Add it to repository secrets as `MY_GITHUB_TOKEN`
3. Ensure the token has `repo` permissions

#### Logger Utility Issues
```
logger_log_files_prefix is required
```

**Solution:** Always provide required parameters for utilities:
```yaml
app_utilities: "logger"
logger_log_files_prefix: "my_app"
logger_sourcetype: "my_app:logs"  # recommended
```
