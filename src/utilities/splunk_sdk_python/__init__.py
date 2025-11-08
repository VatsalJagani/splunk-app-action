import os
import re
import shutil
from typing import override

import github_action_toolkit as gat

from utilities.base_utility import BaseUtility


class SplunkPythonSDKUtility(BaseUtility):
    """
    Utility to add the Splunk Python SDK to a Splunk app.

    Installs the Splunk SDK for Python into the app's lib directory, enabling
    apps to interact with Splunk's REST API and services programmatically.
    """

    def _get_splunklib_version(self, file_path: str) -> str | None:
        """
        Extract the version number from the splunklib __init__.py file.

        Args:
            file_path: Path to the splunklib __init__.py file.

        Returns:
            Version string if found, None otherwise.
        """
        try:
            with open(file_path) as f:
                match = re.search(r"\n__version_info__\s*=\s*([^\n]+)", f.read())
                if match:
                    version = match.group(1)
                    return version
        except Exception:
            gat.info("Error with getting the splunklib version.")
        return None

    def remove_pycache(self, directory: str) -> None:
        """
        Remove Python cache files and directories from the specified directory.

        Args:
            directory: Root directory to clean cache files from.
        """
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".pyc"):
                    os.remove(os.path.join(root, file))
            for dir in dirs:
                if dir == "__pycache__":
                    shutil.rmtree(os.path.join(root, dir))

    def get_installed_packages(self, directory: str) -> dict[str, list[str]]:
        """
        Get a mapping of installed packages to their versions.
        Returns a dict like {'package_name': ['1.0.0', '2.0.0']}.
        """
        if not os.path.exists(directory):
            return {}

        packages: dict[str, list[str]] = {}

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            # Check for metadata directories
            if os.path.isdir(item_path) and (
                item.endswith(".dist-info") or item.endswith(".egg-info")
            ):
                # Extract package name and version
                # e.g., splunk_sdk-1.7.0.dist-info -> package: splunk_sdk, version: 1.7.0
                version_match = re.search(r"^(.+?)-(\d+(?:\.\d+)*)\.(?:dist-info|egg-info)$", item)
                if version_match:
                    package_name = version_match.group(1)
                    version = version_match.group(2)

                    if package_name not in packages:
                        packages[package_name] = []
                    packages[package_name].append(version)

        return packages

    def cleanup_old_package_files(
        self, directory: str, packages_before: dict[str, list[str]] | None = None
    ) -> None:
        """
        Remove old package metadata files from previous installations.
        This includes old .dist-info and .egg-info directories for splunk-sdk
        and its dependencies.

        If packages_before is provided, removes old versions of all packages that
        have newer versions. Otherwise, only removes old splunk-sdk versions.
        """
        if not os.path.exists(directory):
            return

        current_packages = self.get_installed_packages(directory)
        items_to_remove: list[str] = []

        # If we have before/after state, clean up old versions of any upgraded package
        if packages_before is not None:
            for package_name, versions_before in packages_before.items():
                if package_name in current_packages:
                    # Get current versions after upgrade
                    versions_after = current_packages[package_name]

                    # For each version that existed before
                    for old_version in versions_before:
                        # If this version still exists after upgrade, and there are newer versions,
                        # we should remove the old one
                        if old_version in versions_after and len(versions_after) > 1:
                            # Find the metadata directory for this old version
                            for item in os.listdir(directory):
                                item_path = os.path.join(directory, item)
                                if os.path.isdir(item_path) and (
                                    item.endswith(".dist-info") or item.endswith(".egg-info")
                                ):
                                    # Check if this is the old version we want to remove
                                    pattern = rf"^{re.escape(package_name)}-{re.escape(old_version)}\.(?:dist-info|egg-info)$"
                                    if re.match(pattern, item):
                                        items_to_remove.append(item_path)
                                        gat.debug(
                                            f"Marking old metadata directory for removal: {item}"
                                        )
        else:
            # Backward compatibility: only clean up old splunk-sdk versions
            # when we don't have before/after state
            # In this mode, keep only the highest version and remove others
            for item in os.listdir(directory):
                item_path: str = os.path.join(directory, item)

                # Check for old dist-info or egg-info directories related to splunk-sdk
                if os.path.isdir(item_path) and (
                    item.startswith("splunk_sdk-") or item.startswith("splunk-sdk-")
                ):
                    # Check if it's a metadata directory
                    if item.endswith(".dist-info") or item.endswith(".egg-info"):
                        # Extract version from the directory name
                        version_match = re.search(r"-(\d+(?:\.\d+)*)\.(?:dist-info|egg-info)", item)
                        if version_match:
                            dir_version = version_match.group(1)
                            # If multiple versions exist, remove all except the latest
                            if "splunk_sdk" in current_packages:
                                versions = current_packages["splunk_sdk"]
                                if len(versions) > 1:
                                    # Sort versions and keep only the latest
                                    # Simple string comparison works for most version numbers
                                    latest_version = sorted(
                                        versions, key=lambda v: [int(x) for x in v.split(".")]
                                    )[-1]
                                    if dir_version != latest_version:
                                        items_to_remove.append(item_path)
                                        gat.debug(
                                            f"Marking old metadata directory for removal: {item}"
                                        )

        # Remove the marked items
        for item_path in items_to_remove:
            try:
                gat.info(f"Removing old package metadata: {os.path.basename(item_path)}")
                shutil.rmtree(item_path)
            except Exception as e:
                gat.warning(f"Failed to remove {item_path}: {e}")

    @override
    def implement_utility(self) -> str | bool | None:
        gat.info("📚 Adding SplunkPythonSDKUtility - Installing/Updating Splunk Python SDK")
        gat.warning(
            "⚠️  DEPRECATION WARNING: The splunk_python_sdk utility is deprecated and will be "
            "removed in v6. Please use the new dynamic library installation feature in v5 instead, "
            "which allows installing splunklib and other libraries without copying them into the repository."
        )
        splunk_python_sdk_install_path = gat.get_user_input("splunk_python_sdk_install_path")
        gat.debug(f"Install path: {splunk_python_sdk_install_path}")
        if not splunk_python_sdk_install_path or splunk_python_sdk_install_path == "NONE":
            splunk_python_sdk_install_path = "bin"

        is_remove_pyc_from_splunklib_dir = gat.get_user_input_as(
            "is_remove_pyc_from_splunklib_dir", bool, True
        )
        gat.debug(f"Remove .pyc files: {is_remove_pyc_from_splunklib_dir}")

        folder_to_install_splunklib = os.path.join(
            self.app_write_dir, splunk_python_sdk_install_path
        )

        if not os.path.exists(folder_to_install_splunklib):
            os.mkdir(folder_to_install_splunklib)

        os.chdir(folder_to_install_splunklib)

        # Check if splunklib exist already
        already_exist = False
        previous_version = None

        splunklib_dir = os.path.join(folder_to_install_splunklib, "splunklib")
        init_file = os.path.join(splunklib_dir, "__init__.py")

        print(f"init_file inside code = {init_file}")

        if (
            os.path.exists(splunklib_dir)
            and os.path.isdir(splunklib_dir)
            and os.path.isfile(init_file)
        ):
            already_exist = True
            previous_version = self._get_splunklib_version(init_file)
            gat.info(f"Found existing splunklib version: {previous_version}")

        # Capture package state before upgrade/install
        packages_before = self.get_installed_packages(folder_to_install_splunklib)

        if already_exist:
            gat.info("Upgrading existing splunklib installation...")
            os.system(f'pip install splunk-sdk --upgrade --target "{folder_to_install_splunklib}"')
        else:
            gat.info("Installing splunklib for the first time...")
            os.system(f'pip install splunk-sdk --target "{folder_to_install_splunklib}"')

        new_version = self._get_splunklib_version(init_file)
        gat.info(f"Splunk Python SDK installation completed - version: {new_version}")

        # Clean up old package metadata files if we upgraded
        if already_exist and previous_version != new_version:
            gat.info("Cleaning up old package metadata files...")
            self.cleanup_old_package_files(folder_to_install_splunklib, packages_before)

        # Removing .pyc and __pycache__
        if is_remove_pyc_from_splunklib_dir:
            self.remove_pycache(folder_to_install_splunklib)

        if not already_exist or previous_version != new_version:
            return init_file
