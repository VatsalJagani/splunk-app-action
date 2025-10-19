# Overview

Welcome to **splunk-app-action**!

This documentation covers the usage, capabilities, and development of the custom GitHub Action for Splunk Apps and Add-ons. It is designed for ReadTheDocs and uses MyST/Markdown formatting.

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
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
```

## Action Outputs

The action provides several output variables that can be used in subsequent workflow steps:

### Available Outputs

- `build_path` - Full path to the generated build artifact (.tgz file)
- `artifact_name` - Name of the generated build artifact (e.g., `my_app_1.0.0_1.tgz`)
- `app_package_id` - The Splunk app package ID extracted from app.conf or globalConfig.json
- `app_version` - The app version number extracted from app.conf or globalConfig.json  
- `app_build_number` - The app build number extracted from app.conf
- `stdout` - Program stdout
- `stderr` - Program stderr
- `error` - A string of 'true' or 'false' indicating if there were errors

### Using Outputs in Workflows

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - id: build_app
        uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
      
      - name: Display build info
        run: |
          echo "Build created: ${{ steps.build_app.outputs.artifact_name }}"
          echo "App ID: ${{ steps.build_app.outputs.app_package_id }}"
          echo "Version: ${{ steps.build_app.outputs.app_version }}"
          echo "Build number: ${{ steps.build_app.outputs.app_build_number }}"
          echo "Build path: ${{ steps.build_app.outputs.build_path }}"
      
      - name: Upload to release
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: splunk-app-${{ steps.build_app.outputs.app_version }}
          path: ${{ steps.build_app.outputs.build_path }}
```

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
