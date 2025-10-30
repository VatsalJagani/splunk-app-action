# Security Best Practices

This page documents security best practices for using the splunk-app-action GitHub Action.

## Authentication

### Token-Based Authentication (Recommended)

For Splunkbase API authentication, we **strongly recommend** using token-based authentication instead of username/password:

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    splunkbase_token: ${{ secrets.SPLUNKBASE_TOKEN }}
```

**Benefits of token authentication:**
- More secure than username/password
- Easier to rotate credentials
- Reduces exposure of your Splunkbase account password
- Can be scoped to specific permissions (if supported by Splunkbase API)

### How to Get a Splunkbase Token

1. Log into your Splunkbase account at [https://splunkbase.splunk.com](https://splunkbase.splunk.com)
2. Navigate to your account settings
3. Look for API tokens or authentication tokens section
4. Generate a new token for use with app-inspect API
5. Store the token securely in GitHub Secrets (see below)

### Username/Password Authentication (Legacy)

While still supported, username/password authentication is considered legacy:

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
    splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

## GitHub Secrets Management

### Using GitHub Environments (Recommended)

GitHub Environments provide an additional layer of security and control:

1. **Create an Environment:**
   - Go to your repository Settings → Environments
   - Click "New environment"
   - Name it (e.g., "production" or "splunkbase")

2. **Add Secrets to Environment:**
   - In the environment settings, add your secrets:
     - `SPLUNKBASE_TOKEN` (recommended)
     - OR `SPLUNKBASE_USERNAME` and `SPLUNKBASE_PASSWORD` (legacy)

3. **Configure Environment Protection:**
   - Add required reviewers for deployments
   - Set deployment branch rules
   - Configure wait timers if needed

4. **Use in Workflow:**
   ```yaml
   jobs:
     build:
       runs-on: ubuntu-latest
       environment: production  # Reference your environment
       steps:
         - uses: VatsalJagani/splunk-app-action@v4
           with:
             app_dir: "my_app"
             splunkbase_token: ${{ secrets.SPLUNKBASE_TOKEN }}
   ```

**Benefits of GitHub Environments:**
- Require manual approval before using secrets
- Restrict which branches can access secrets
- Audit log of when secrets are used
- Better separation of staging vs production secrets

### Using Repository Secrets (Basic)

For simpler setups, you can use repository-level secrets:

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add your secret:
   - Name: `SPLUNKBASE_TOKEN`
   - Value: Your Splunkbase API token
4. Use in workflow as shown above

## Minimal Required Permissions

### For the Action Itself

The action requires minimal permissions to run. In your workflow, use:

```yaml
permissions:
  contents: read  # Required to checkout code
```

### When Using App Utilities Feature

If you use the `app_utilities` feature that creates Pull Requests, additional permissions are needed:

```yaml
permissions:
  contents: write        # Required to push changes
  pull-requests: write   # Required to create PRs
```

### Complete Example with Minimal Permissions

```yaml
name: Build and Validate Splunk App

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Minimal permissions - only what's needed
permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    environment: production  # Use environment for secret management
    
    steps:
      - name: Build and Inspect
        uses: VatsalJagani/splunk-app-action@v4
        with:
          app_dir: "my_app"
          splunkbase_token: ${{ secrets.SPLUNKBASE_TOKEN }}
```

## Supply Chain Security

### Action Pinning

All reusable GitHub Actions used by splunk-app-action are pinned to specific commit SHAs for supply chain security:

- `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` (v4.2.2)
- `astral-sh/setup-uv@50cb469c430ff56d9c7f512b7f3c4a20980d3387` (v4.0.0)
- `actions/upload-artifact@ea165f8b308b8b1f8b5acc8f7b5085c5a557c1fc` (v4.6.0)

This prevents supply chain attacks where malicious code could be injected via tag updates.

### Recommended Practice

When using splunk-app-action in your workflows, consider:

1. **Pin to a specific version:**
   ```yaml
   uses: VatsalJagani/splunk-app-action@v4.2.0
   ```

2. **Or pin to a commit SHA for maximum security:**
   ```yaml
   uses: VatsalJagani/splunk-app-action@abc123def456...
   ```

3. **Use Dependabot to keep actions up to date:**
   ```yaml
   # .github/dependabot.yml
   version: 2
   updates:
     - package-ecosystem: "github-actions"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

## Local App Inspect Alternative

For maximum security and to avoid sharing credentials, consider using local app inspect:

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
    local_app_inspect: true
```

**Benefits:**
- No credentials required
- Faster validation
- No network calls to external APIs
- Runs entirely within your GitHub Actions runner

**Trade-offs:**
- May not be as up-to-date as Splunkbase API validation
- Uses the splunk-appinspect Python library version included in the action

## Secret Rotation

Regularly rotate your Splunkbase credentials:

1. **For tokens:**
   - Generate a new token in Splunkbase
   - Update the GitHub secret
   - Revoke the old token

2. **For username/password:**
   - Change your Splunkbase password
   - Update the GitHub secret immediately

3. **Audit your secrets usage:**
   - Review GitHub Actions logs
   - Check for any unauthorized access
   - Monitor Splunkbase API usage

## Additional Security Measures

1. **Principle of Least Privilege:**
   - Only grant permissions that are absolutely necessary
   - Use environments to restrict access to production secrets

2. **Branch Protection:**
   - Require pull request reviews before merging
   - Require status checks to pass
   - Restrict who can push to protected branches

3. **Audit Logging:**
   - Enable audit logging in your organization
   - Review Actions logs regularly
   - Monitor for suspicious activity

4. **Keep Actions Updated:**
   - Subscribe to security advisories for actions you use
   - Update promptly when security patches are released
   - Use Dependabot to automate updates

## Reporting Security Issues

If you discover a security vulnerability in splunk-app-action:

1. **DO NOT** open a public GitHub issue
2. Contact the maintainers privately
3. Provide details about the vulnerability
4. Allow time for a fix before public disclosure

See our [Security Policy](https://github.com/VatsalJagani/splunk-app-action/security/policy) for more information.
