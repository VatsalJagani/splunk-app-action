# splunk-app-action

GitHub Action to automatically generate Splunk App and Add-on builds, run app-inspect checks with the Splunkbase API, and add common utilities to your Splunk projects.

## Quick Start

```yaml
# Basic build generation
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"

# Build with app-inspect checks  
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
    splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}

# Build with local app-inspect (faster, no credentials needed)
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    local_app_inspect: true

# UCC Add-on build
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "TA_my_addon" 
    use_ucc_gen: true

# With Python dependency management
# Note: Path relative to app_dir, installs to same directory as requirements file
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    python_requirements_file: "lib/requirements.txt"

# Using action outputs in workflows
- id: build_step
  uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
- name: Use build outputs
  run: |
    echo "Build: ${{ steps.build_step.outputs.artifact_name }}"
    echo "Path: ${{ steps.build_step.outputs.build_path }}"
```

## Requirements

- **Operating System:** Linux-based GitHub Actions runners (ubuntu-latest, ubuntu-22.04, ubuntu-20.04)
- **Note:** Windows and macOS runners are not supported

## Key Features

- ✅ **Automatic Build Generation** - Creates `.tgz` artifacts for Splunk apps/add-ons
- ✅ **Action Outputs** - Provides build path, artifact name, and app metadata for workflow integration
- ✅ **Splunkbase App-Inspect** - Runs official app-inspect, cloud-inspect, and SSAI checks  
- ✅ **Local App-Inspect** - Fast local validation with splunk-appinspect library (no credentials needed)
- ✅ **SARIF Reports** - Generate SARIF format for GitHub Code Scanning with inline annotations
- ✅ **GitHub Check Runs** - Quality gates for merge blocking based on AppInspect thresholds
- ✅ **UCC Add-on Support** - Full integration with UCC Generator framework
- ✅ **Python Dependency Manager** - Manage dependencies via requirements.txt with Dependabot support
- ✅ **Multi-App Repositories** - Build multiple apps from single repository
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
