# splunk-app-action

GitHub Action to automatically generate Splunk App and Add-on builds, run app-inspect checks with the Splunkbase API, and add common utilities to your Splunk projects.

## Quick Start

```yaml
# Basic build generation
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "my_app"

# Build with app-inspect checks  
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "my_app"
    splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
    splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}

# Build with local app-inspect (faster, no credentials needed)
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "my_app"
    local_app_inspect: true

# Build with inline code annotations for PR feedback
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "my_app"
    local_app_inspect: true
    fail_on: "errors"  # Options: errors, warnings, none

# UCC Add-on build
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "TA_my_addon" 
    use_ucc_gen: true
    is_remove_not_allowed_executables_from_lib: true  # Default is false; set true for stricter cleanup

# With Python dependency management
# Note: Path relative to app_dir, installs to same directory as requirements file
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "my_app"
    python_requirements_file: "lib/requirements.txt"

# With app utilities (logger, etc.) - requires workflow permissions
- uses: VatsalJagani/splunk-app-action@v6
  permissions:
    contents: write
    pull-requests: write
  with:
    app_dir: "my_app"
    app_utilities: "logger"
    logger_log_files_prefix: "my_app"
    logger_sourcetype: "my_app:logs"

# Using action outputs in workflows
- id: build_step
  uses: VatsalJagani/splunk-app-action@v6
  with:
    app_dir: "my_app"
- name: Use build outputs
  run: |
    echo "Build: ${{ steps.build_step.outputs.artifact_name }}"
    echo "Path: ${{ steps.build_step.outputs.build_path }}"
```

## Workflow Permissions for App Utilities

When using `app_utilities`, the action needs permission to create branches and pull requests.

**Recommended: Repository-wide permissions**

1. Go to Repository Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"

![Workflow Permission Settings](https://raw.githubusercontent.com/VatsalJagani/splunk-app-action/develop/docs/source/_static/images/workflow_permission_for_pr_1.png)

![Workflow Permission Detail](https://raw.githubusercontent.com/VatsalJagani/splunk-app-action/develop/docs/source/_static/images/workflow_permission_for_pr_2.png)

**Alternative: Personal Access Token (Advanced)**

For cross-repo permissions or explicit token management:
```yaml
- uses: VatsalJagani/splunk-app-action@v6
  with:
    app_utilities: "logger"
    my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}  # PAT with repo scope
```

See [Troubleshooting](https://splunk-app-action.readthedocs.io/en/latest/troubleshooting.html) for more details.

## Requirements

- **Operating System:** Linux-based GitHub Actions runners (ubuntu-latest, ubuntu-22.04, ubuntu-20.04)
- **Note:** Windows and macOS runners are not supported

## Key Features

- ✅ **Automatic Build Generation** - Creates `.tgz` artifacts for Splunk apps/add-ons
- ✅ **Action Outputs** - Provides build path, artifact name, and app metadata for workflow integration
- ✅ **Splunkbase App-Inspect** - Runs official app-inspect, cloud-inspect, and SSAI checks  
- ✅ **Local App-Inspect** - Fast local validation with splunk-appinspect library (no credentials needed)
- ✅ **GitHub Annotations** - app-inspect results appear as inline annotations in Files Changed tab
- ✅ **GitHub Job Summary** - Comprehensive build summary with metadata and results in Actions UI
- ✅ **Flexible Failure Modes** - Control workflow failure based on errors, warnings, or never fail
- ✅ **UCC Add-on Support** - Full integration with UCC Generator framework
- ✅ **Python Dependency Manager** - Manage dependencies via requirements.txt with Dependabot support
- ✅ **Multi-App Repositories** - Build multiple apps using GitHub Actions matrix strategy
- ✅ **App Utilities** - Auto-add logger, SDK, documentation, and more via PRs
- ✅ **Custom Commands** - Run user-defined shell commands before build
- ✅ **File Permissions** - Automatic permission fixes for app-inspect compliance

## Documentation

📚 **Complete Documentation:** [https://splunk-app-action.readthedocs.io/](https://splunk-app-action.readthedocs.io/)


### Note from actions/upload-artifact - Zipped Artifact Downloads
During a workflow run, files are uploaded and downloaded individually using the upload-artifact and download-artifact actions. However, when a workflow run finishes and an artifact is downloaded from either the UI or through the download api, a zip is dynamically created with all the file contents that were uploaded. There is currently no way to download artifacts after a workflow run finishes in a format other than a zip or to download artifact contents individually. One of the consequences of this limitation is that if a zip is uploaded during a workflow run and then downloaded from the UI, there will be a double zip created.



## Project Docs

For development workflows, see [development.md](devtools/development.md).

For instructions on release process, see [release.md](devtools/release.md).
