import os
import re
import shutil
from typing import override

import github_action_toolkit as gat

from utilities.base_utility import BaseUtility


class SplunkPythonSDKUtility(BaseUtility):
    def _get_splunklib_version(self, file_path: str) -> str | None:
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
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".pyc"):
                    os.remove(os.path.join(root, file))
            for dir in dirs:
                if dir == "__pycache__":
                    shutil.rmtree(os.path.join(root, dir))

    def cleanup_old_package_files(self, directory: str, current_version: str | None) -> None:
        """
        Remove old package metadata files from previous installations.
        This includes old .dist-info and .egg-info directories.
        """
        if not os.path.exists(directory):
            return

        items_to_remove: list[str] = []

        for item in os.listdir(directory):
            item_path: str = os.path.join(directory, item)

            # Check for old dist-info or egg-info directories related to splunk-sdk
            if os.path.isdir(item_path) and (
                item.startswith("splunk_sdk-") or item.startswith("splunk-sdk-")
            ):
                # Check if it's a metadata directory
                if item.endswith(".dist-info") or item.endswith(".egg-info"):
                    # If we have a current version, only remove if it's different
                    if current_version:
                        # Extract version from the directory name
                        # e.g., splunk_sdk-1.7.0.dist-info -> 1.7.0
                        # Support various version formats (1.7.0, 2.0, 1.7.0.1, etc.)
                        version_match = re.search(r"-([\d.]+)\.(?:dist-info|egg-info)", item)
                        if version_match:
                            dir_version = version_match.group(1)
                            # Only remove if it's not the current version
                            if dir_version != current_version:
                                items_to_remove.append(item_path)
                                gat.debug(f"Marking old metadata directory for removal: {item}")
                    # else: No version info, keep all metadata directories

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
            self.cleanup_old_package_files(folder_to_install_splunklib, new_version)

        # Removing .pyc and __pycache__
        if is_remove_pyc_from_splunklib_dir:
            self.remove_pycache(folder_to_install_splunklib)

        if not already_exist or previous_version != new_version:
            return init_file
