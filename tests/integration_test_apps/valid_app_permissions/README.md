# Valid Test App (Permissions)

This is a valid Splunk app used for testing the splunk-app-action GitHub Action with file permission changes.

## Purpose
This app is used to test the `to_make_permission_changes` feature:

### Test Scenario
1. **Wrong permissions are intentionally created** by the workflow:
   - `default/` directory set to `777` (should be `755`)
   - `default/app.conf` set to `600` (should be `644`)
   - `bin/test_perms.py` set to `777` (should be `644` for non-shell scripts)

2. **First test - WITHOUT permission fix**:
   - Runs action with `to_make_permission_changes: false`
   - Runs local app-inspect
   - Expected: App-inspect should fail or warn about permissions

3. **Second test - WITH permission fix**:
   - Runs action with `to_make_permission_changes: true`
   - Runs local app-inspect
   - Expected: Permissions are corrected, app-inspect passes

### Validates
- ✅ Permission correction feature works correctly
- ✅ Files are set to proper permissions (644 for files, 755 for directories)
- ✅ Local app-inspect passes after permission fixes
- ✅ Build artifact contains files with correct permissions

## Expected Permissions
According to Splunk App-Inspect requirements:
- **Directories**: `755` (rwxr-xr-x)
- **Regular files**: `644` (rw-r--r--)
- **Shell scripts** (`.sh`): `755` (rwxr-xr-x)
- **Python/other scripts**: `644` (rw-r--r--)
