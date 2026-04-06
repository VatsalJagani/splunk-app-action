# Overview

Welcome to **splunk-app-action**!

This documentation covers the usage, capabilities, and development of the custom GitHub Action for Splunk Apps and Add-ons.

## What is splunk-app-action?

**splunk-app-action** is a comprehensive GitHub Action that automates the build, validation, and packaging process for Splunk Apps and Add-ons. It streamlines your development workflow by:

- **Automated Build Generation** - Creates production-ready `.tgz` packages from your source code
- **Quality Validation** - Runs Splunk AppInspect checks to ensure your app meets Splunk's quality standards
- **Cloud Compatibility** - Validates apps for Splunk Cloud deployment
- **UCC Support** - Seamlessly integrates with the Splunk Add-on UCC Framework for building modern add-ons, and generates Add-on build dynamically without putting 3rd part library code into the Add-on Repo.
- **Python Dependency Management** - Automatically installs Python dependencies at build time
- **Utility Integration** - Adds common utilities like logging, Python SDK, and JavaScript helpers

## Key Features

### Build Automation
- Generate builds from any branch or pull request
- Support for multiple apps in a single repository
- Customizable build process with user-defined commands
- Automatic file permission management for AppInspect compliance

### Quality Assurance
- **AppInspect** - Core Splunk app validation
- **Cloud-Inspect** - Splunk Cloud compatibility checks
- **SSAI-Inspect** - Self-Service App Installation validation
- Configurable failure thresholds (errors, warnings, or never fail)
- GitHub annotations for inline code feedback on AppInspect findings

### Developer Productivity
- Automatic PR creation when using app utilities
- Comprehensive job summaries with build metadata
- Detailed output variables for workflow integration
- Support for GitHub Dependabot with Python dependency management

## Supported Operating Systems

This GitHub Action is designed to run on **Linux-based GitHub Actions runners** and has been extensively tested on:

- ✅ **ubuntu-latest** (recommended)
- ✅ **ubuntu-22.04**
- ✅ **ubuntu-20.04**

```{warning}
**Windows and macOS runners are not supported.** The action relies on Linux-specific commands like `tar`, `find`, and `chmod`, which are not available or behave differently on Windows and macOS. Always use `runs-on: ubuntu-latest` or another Linux runner in your workflows.
```

### Example Workflow Configuration

```yaml
jobs:
  build:
    runs-on: ubuntu-latest  # Required - must be Linux
    steps:
      - uses: actions/checkout@v5
      - uses: VatsalJagani/splunk-app-action@v6
        with:
          app_dir: "my_app"
```

## Action Outputs

The action provides several output variables that can be used in subsequent workflow steps:

### Available Outputs

#### Build Metadata
- `build_path` - Full path to the generated build artifact (.tgz file)
- `artifact_name` - Name of the generated build artifact (e.g., `my_app_1.0.0_1.tgz`)
- `app_package_id` - The Splunk app package ID extracted from app.conf or globalConfig.json
- `app_version` - The app version number extracted from app.conf or globalConfig.json  
- `app_build_number` - The app build number extracted from app.conf

#### AppInspect Status
- `app_inspect_status` - Status of app-inspect check (Passed, Warning, Failure, Error, Timed-out, Exception, Skipped, or Not Run)
- `cloud_inspect_status` - Status of cloud-inspect check (Passed, Warning, Failure, Error, Timed-out, Exception, Skipped, or Not Run)
- `ssai_inspect_status` - Status of SSAI-inspect check (Passed, Warning, Failure, Error, Timed-out, Exception, Skipped, or Not Run)


### Using Outputs in Workflows

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - id: build_app
        uses: VatsalJagani/splunk-app-action@v6
        with:
          app_dir: "my_app"
      
      - name: Display build info
        run: |
          echo "Build created: ${{ steps.build_app.outputs.artifact_name }}"
          echo "App ID: ${{ steps.build_app.outputs.app_package_id }}"
          echo "Version: ${{ steps.build_app.outputs.app_version }}"
          echo "Build number: ${{ steps.build_app.outputs.app_build_number }}"
          echo "Build path: ${{ steps.build_app.outputs.build_path }}"
          echo "App Inspect: ${{ steps.build_app.outputs.app_inspect_status }}"
          echo "Cloud Inspect: ${{ steps.build_app.outputs.cloud_inspect_status }}"
          echo "SSAI Inspect: ${{ steps.build_app.outputs.ssai_inspect_status }}"
      
      - name: Upload to release
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v6
        with:
          name: splunk-app-${{ steps.build_app.outputs.app_version }}
          path: ${{ steps.build_app.outputs.build_path }}
```

## Job Summary

The action automatically generates a comprehensive job summary that appears in the GitHub Actions UI. This summary provides a quick overview of the build results without having to dig through logs.

### Summary Contents

The job summary includes:

- **Build Information Table** - Displays app package ID, version, build number, and artifact name
- **AppInspect Results Table** - Shows the status of all three inspect checks with color-coded emoji indicators:
  - ✅ Passed
  - ⚠️ Warning
  - ❌ Failure or Error  
  - ⏱️ Timed-out
  - 💥 Exception
  - ⏭️ Skipped
  - ⚪ Not Run
- **Fail Mode Display** - Shows the configured `fail_on` mode in the results table
- **Artifacts Section** - Provides a direct link to download workflow run artifacts

### Example Summary

When you view a completed workflow run in GitHub Actions, you'll see a summary like this:

```markdown
## 🎉 Splunk App Build Summary

### Build Information
| Property | Value |
|----------|-------|
| App Package ID | my_splunk_app |
| Version | 2.5.1 |
| Build Number | 123 |
| Artifact Name | my_splunk_app_2_5_1_123.tgz |

### AppInspect Results
| Check Type | Status |
|------------|--------|
| App-Inspect | ✅ Passed |
| Cloud-Inspect | ✅ Passed |
| SSAI-Inspect | ✅ Passed |
| Fail Mode | errors |

### Artifacts
📦 [Download artifacts from this run](https://github.com/org/repo/actions/runs/123456)
```

The summary is automatically written to `$GITHUB_STEP_SUMMARY` and appears in the workflow run page.

## Artifact Naming Convention

Build artifacts follow a consistent naming pattern to ensure uniqueness and traceability:

**Pattern:** `{app_package_id}_{version_encoded}_{build_number_encoded}.tgz`

**Example:** `my_app_1_0_0_1.tgz`

Where:
- `app_package_id` - The app's package ID from app.conf or globalConfig.json
- `version_encoded` - Version number with special characters replaced by underscores (e.g., `1.0.0` → `1_0_0`)
- `build_number_encoded` - Build number with special characters replaced by underscores

```{note}
The encoding replaces all non-alphanumeric characters with underscores to ensure the artifact name is filesystem and URL-safe.
```

### Artifact Upload Naming

When the action uploads artifacts to GitHub, they use the following naming patterns:

**Build Artifact:** `App-Build-{app_package_id}_{version_encoded}_{build_number_encoded}`

**Inspect Reports:** `App-Inspect-Reports-{app_package_id}_{version_encoded}_{build_number_encoded}`

This ensures all artifacts are uniquely named and easy to identify in the GitHub Actions UI.

## Flow Diagram - What does this GitHub Action do?

:::{mermaid}
graph TD
	A[Start] --> B([Push to GitHub])
	B --> C>Action Triggered]

	C --> D{Use UCC Gen?}
	D --> |Yes| E([ucc-gen build])
	E --> F([Optionally: Run User Defined Commands])

	D --> |No| F
	F --> G([Generate build with tar command])

	G --> H([App Inspect Check])
	H --> |Yes| I(Build Successful)
	H --> |No| J(Build Failed - App-Inspect Errors)

	I --> K{Is Add App Utilities?}
	J --> K

	K --> |Yes| L([Adding App Utilities])
	L --> M{Any changes to code?}
	M --> |Yes| N([Pull Request Created])
	M --> |No| O([Build Artifacts Created])
	N --> O

	K --> |No| O
:::

- Automatically generates Splunk App and Add-on builds
- Runs app-inspect checks (with the App-Inspect/Splunkbase API) on commit/push
- Performs Splunk cloud checks
- Supports UCC Generator for Add-ons
- Provides utilities for Splunk Apps and Add-ons
- Works in private repositories

See the following sections for details on capabilities, usage, inputs, troubleshooting, and release notes.
