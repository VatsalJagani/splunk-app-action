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

### Python Dependency Management Issues

#### Requirements File Not Found
```
Requirements file not found at: lib/requirements.txt
```

**Solution:**
- Ensure the requirements file path is relative to `app_dir`
- Verify the file exists in your repository
- Check that the file name matches exactly (case-sensitive)

#### Dependency Installation Failures
```
Failed to install dependencies: pip install error
```

**Solution:**
- Check requirements.txt for syntax errors
- Ensure all package names are spelled correctly
- Verify that packages are available on PyPI
- Consider adding version constraints (e.g., `requests>=2.31.0`)

#### Conflicting Dependencies
```
ERROR: Cannot install package-a and package-b because these package versions have conflicting dependencies
```

**Solution:**
- Review your requirements.txt for version conflicts
- Use specific version pinning to resolve conflicts
- Consider using a requirements lock file

### Build Generation Issues

#### Missing app.conf
```
Missing 'version' attribute in app.conf [launcher] stanza
```

**Solution:**
- Ensure `default/app.conf` exists in your app
- Add required fields to app.conf:
  ```ini
  [launcher]
  version = 1.0.0
  
  [id]
  name = MyApp
  
  [package]
  id = my_app
  ```

#### Build Path Issues
```
Build directory not found or access denied
```

**Solution:**
- Ensure your workflow checks out the repository first: `uses: actions/checkout@v4`
- Verify the `app_dir` path is correct and relative to repository root
- Check that the directory contains a valid Splunk app structure

### AppInspect Timeout Issues

#### Check Times Out
```
App-inspect check timed out after 240 seconds
```

**Solution:**
- Large apps may take longer to validate
- Consider using local AppInspect instead:
  ```yaml
  local_app_inspect: true
  ```
- For production, the Splunkbase API is recommended despite longer wait times

### Multiple Feature Conflicts

#### Mutually Exclusive Features Error
```
Error: Multiple build features detected: UCC-Gen, Python-Dependency-Management
```

**Solution:**
- Only use ONE of these features at a time:
  - UCC-Gen (`use_ucc_gen: true`)
  - Python Dependency Management (`python_requirements_file`)
  - Splunk Python SDK utility (`app_utilities: splunk_python_sdk`)
- Remove or disable the conflicting features from your workflow

### AppInspect Annotations

#### Annotations Not Appearing
```
AppInspect completed but no annotations visible in PR
```

**Root Cause:** Annotations only appear for files that changed in the PR, or when running on push/pull_request events.

**Solution:**
- Annotations only show up for **files modified in the current PR or push**
- They won't appear on files that haven't changed
- Make sure the workflow runs on `pull_request` or `push` events:
```yaml
on: [push, pull_request]
```
- Check the "Files changed" tab in your PR to see if annotations appear on modified files
- Review the workflow logs to confirm annotations were published
- Check the "Checks" tab for the "App-Inspect Check" summary

#### Understanding Annotation vs Check Runs
AppInspect results appear in two places:
1. **GitHub Annotations** - Inline comments on changed files showing errors/warnings at specific lines
2. **Check Runs** - Summary view in the PR "Checks" tab with overall status and error counts

Both are automatically published when AppInspect runs. Annotations require file locations in the AppInspect report to appear inline.

## Getting Help

If you encounter issues not covered here:

1. **Check the Examples** - Review the [examples page](examples.md) for working configurations
2. **Review Inputs** - Verify your inputs against the [inputs reference](inputs.md)
3. **Enable Debug Logging** - Add this to your workflow:
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
   ```
4. **Search Issues** - Look for similar problems in [GitHub Issues](https://github.com/VatsalJagani/splunk-app-action/issues)
5. **Open an Issue** - If you've found a bug or need help, create a new issue with:
   - Your workflow YAML
   - Relevant error messages
   - Steps to reproduce
   - Expected vs actual behavior
