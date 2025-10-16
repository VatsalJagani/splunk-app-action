# Examples & Usage Scenarios

This page provides comprehensive examples for different use cases of the splunk-app-action.

## Basic Examples

### Simple App Build
Basic build generation for a single app:

```yaml
name: Build My Splunk App
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
```

### Build with App-Inspect
Include Splunkbase app-inspect checks:

```yaml
name: Build and Inspect
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

## Multi-App Repository

Build multiple apps from a single repository:

```yaml
name: Multi-App Build
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app: ["my_splunk_app", "my_splunk_addon", "another_app"]
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: ${{ matrix.app }}
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

## UCC Add-on Examples

### Basic UCC Build
```yaml
name: UCC Add-on Build
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "TA_my_addon"
          use_ucc_gen: true
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### UCC with Additional Packaging Utility
```yaml
name: UCC with Utilities
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "."
          use_ucc_gen: true
          app_utilities: "ucc_additional_packaging"
          my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

## Python Dependency Management Examples

### Basic Python Dependencies
```yaml
name: Build with Python Dependencies
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          python_requirements_file: "requirements.txt"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### With GitHub Dependabot
Set up automatic dependency updates by adding `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/my_app"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

Then use the action:
```yaml
name: Build with Managed Dependencies
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          python_requirements_file: "requirements.txt"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Custom Requirements Path
```yaml
name: Build with Custom Requirements
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          python_requirements_file: "requirements/production.txt"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Multi-Environment Dependencies
For different dependency sets (dev/prod):
```yaml
name: Multi-Environment Build
on:
  push:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Determine requirements file
        id: reqs
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "file=requirements/production.txt" >> $GITHUB_OUTPUT
          else
            echo "file=requirements/development.txt" >> $GITHUB_OUTPUT
          fi
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          python_requirements_file: ${{ steps.reqs.outputs.file }}
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

## File Permission Examples

### Automatic Permission Fixes
```yaml
name: Build with Auto Permissions
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          to_make_permission_changes: true
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Custom Permission Commands
```yaml
name: Custom Permissions
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        env:
          SPLUNK_APP_ACTION_1: "find . -type f -exec chmod 644 '{}' \\;"
          SPLUNK_APP_ACTION_2: "find . -type f -name '*.sh' -exec chmod +x '{}' \\;"
          SPLUNK_APP_ACTION_3: "find . -type f -name '*.py' -exec chmod 644 '{}' \\;"
          SPLUNK_APP_ACTION_4: "find . -type d -exec chmod 755 '{}' \\;"
        with:
          app_dir: "my_app"
```

## User-Defined Commands Examples

### Remove Test Files
```yaml
name: Build without Test Files
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        env:
          SPLUNK_APP_ACTION_1: "rm -rf tests/"
          SPLUNK_APP_ACTION_2: "rm -rf .pytest_cache/"
          SPLUNK_APP_ACTION_3: "find . -name '*.pyc' -delete"
          SPLUNK_APP_ACTION_4: "find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
        with:
          app_dir: "my_app"
```

### Add Custom Content
```yaml
name: Build with Custom Content
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        env:
          SPLUNK_APP_ACTION_1: "echo 'version=${{ github.sha }}' >> default/app.conf"
          SPLUNK_APP_ACTION_2: "cp ../LICENSE.txt ."
          SPLUNK_APP_ACTION_3: "mkdir -p lookups && echo 'name,value' > lookups/custom.csv"
        with:
          app_dir: "my_app"
```

## Utility Examples

### Complete Utility Setup
```yaml
name: Build with All Utilities
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "whats_in_the_app,logger,splunk_python_sdk,common_js_utilities"
          my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
          logger_log_files_prefix: "my_app"
          logger_sourcetype: "my_app:logs"
          splunk_python_sdk_install_path: "bin/lib"
```

### Logger Utility Only
```yaml
name: Add Logger to App
on: [push]

jobs:
  add-logger:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "logger"
          my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
          logger_log_files_prefix: "my_custom_app"
          logger_sourcetype: "my_custom_app:internal"
```

### Splunk SDK with Custom Path
```yaml
name: Install SDK in Custom Location
on: [push]

jobs:
  sdk-install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "splunk_python_sdk"
          my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
          splunk_python_sdk_install_path: "bin/lib"
          is_remove_pyc_from_splunklib_dir: true
```

## Advanced Workflows

### Conditional Builds
```yaml
name: Conditional Build
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          # Only run app-inspect on main branch
          is_app_inspect_check: ${{ github.ref == 'refs/heads/main' }}
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Matrix Strategy for Multiple Apps
```yaml
name: Matrix Build Strategy
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - app_dir: "my_splunk_app"
            utilities: "whats_in_the_app,logger"
            ucc: false
          - app_dir: "TA_my_addon" 
            utilities: "ucc_additional_packaging"
            ucc: true
          - app_dir: "another_app"
            utilities: "splunk_python_sdk,common_js_utilities"
            ucc: false
    
    steps:
      - uses: actions/checkout@v4
      - uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: ${{ matrix.app_dir }}
          use_ucc_gen: ${{ matrix.ucc }}
          app_utilities: ${{ matrix.utilities }}
          my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

### Branch-Specific Behavior
```yaml
name: Branch-Specific Build
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Development branch - utilities only
      - name: Add Utilities (dev branch)
        if: github.ref == 'refs/heads/develop'
        uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          app_utilities: "whats_in_the_app,logger,splunk_python_sdk"
          my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
          is_app_inspect_check: false
      
      # Main branch - full build with inspect
      - name: Full Build (main branch)
        if: github.ref == 'refs/heads/main'
        uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

## Repository Structure Examples

### Standard App Structure
```
my-splunk-app/
├── .github/
│   └── workflows/
│       └── build.yml
├── my_app/                    # app_dir: "my_app"
│   ├── default/
│   │   ├── app.conf
│   │   └── props.conf
│   ├── bin/
│   │   └── my_script.py
│   └── static/
│       └── appIcon.png
└── README.md
```

### Multi-App Repository
```
my-splunk-apps/
├── .github/
│   └── workflows/
│       └── build.yml
├── app1/                      # app_dir: "app1"
│   ├── default/
│   └── bin/
├── TA_addon1/                 # app_dir: "TA_addon1", use_ucc_gen: true
│   ├── globalConfig.json
│   └── package/
└── legacy_app/                # app_dir: "legacy_app"
    ├── default/
    └── bin/
```

### Root-as-App Structure
```
my-app-repo/
├── .github/
│   └── workflows/
│       └── build.yml          # app_dir: "." (root)
├── default/
│   ├── app.conf
│   └── props.conf
├── bin/
│   └── my_script.py
└── static/
    └── appIcon.png
```

## Secrets Configuration

### Required Secrets Setup
1. **Repository Settings** → **Secrets and variables** → **Actions**
2. **Add the following secrets:**

```bash
# For App-Inspect (required)
SPLUNKBASE_USERNAME = "your_splunkbase_username"
SPLUNKBASE_PASSWORD = "your_splunkbase_password"

# For Utilities (optional, needed only if using utilities)
MY_GITHUB_TOKEN = "gha_xxxxxxxxxxxx"
```

### GitHub Token Permissions
When creating `MY_GITHUB_TOKEN`:
- Go to GitHub Settings → Developer settings → Personal access tokens
- Select **repo** permissions (Full control of private repositories)
- Select **workflow** permissions (Update GitHub Action workflows)

```{tip}
Test your workflow on a feature branch first to ensure all secrets are correctly configured before applying to your main branch.
```