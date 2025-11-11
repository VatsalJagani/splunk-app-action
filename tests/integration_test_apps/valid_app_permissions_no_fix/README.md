# Valid Test App (Permissions - No Fix Test)

This is a copy of the permissions test app used specifically for testing WITHOUT the `to_make_permission_changes` feature.

## Purpose
This app is used in the first part of the permission test:
- Wrong permissions are created by the workflow
- Action runs with `to_make_permission_changes: false`
- App-inspect should fail or warn

This is a separate app directory to avoid artifact naming conflicts with the main permission test.

## Note
This app has a different `app_package_id` (`valid_test_app_permissions_no_fix`) to ensure unique artifact names.
