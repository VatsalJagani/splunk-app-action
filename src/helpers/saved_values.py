import os
import re
from collections.abc import Generator
from contextlib import contextmanager

import github_action_toolkit as gat


class SavedPaths:
    """
    Container for directory paths used throughout the build process.

    Stores standardized paths for the root directory, repository directory,
    and application directory to ensure consistent path references across
    the build workflow.
    """

    def __init__(self, app_dir_name: str) -> None:
        """
        Initialize SavedPaths with the application directory name.

        Args:
            app_dir_name: Name of the application directory within the repository.
        """
        self.root_dir_path: str = os.getcwd()

        self.repo_dir_name: str = "repodir"
        self.repo_dir_path: str = os.path.join(self.root_dir_path, self.repo_dir_name)

        self.app_dir_name: str = app_dir_name
        self.app_dir_path: str = os.path.join(self.repo_dir_path, self.app_dir_name)


@contextmanager
def keep_working_dir_unchanged() -> Generator[None]:
    """
    Context manager to preserve the current working directory.

    Saves the current working directory before entering the context and
    restores it upon exit, ensuring operations within the context don't
    permanently change the working directory.

    Yields:
        None
    """
    _path = os.getcwd()
    try:
        yield
    finally:
        os.chdir(_path)


class AppInfo:
    """
    Container for Splunk application metadata and identifiers.

    Manages application package ID, version number, and build number,
    providing both raw and encoded versions suitable for file names
    and GitHub Actions outputs.
    """

    def encode(self, val: str) -> str:
        """
        Encode a string value for use in file names and identifiers.

        Replaces all non-alphanumeric characters with underscores to create
        filesystem-safe identifiers.

        Args:
            val: String value to encode.

        Returns:
            Encoded string with only alphanumeric characters and underscores.
        """
        return re.sub("[^0-9a-zA-Z]+", "_", val)

    def __init__(self, package_id: str, version_number: str) -> None:
        """
        Initialize AppInfo with package ID and version number.

        Args:
            package_id: Unique identifier for the Splunk app package.
            version_number: Version number of the application.
        """
        self.package_id: str = package_id
        self.version_number: str = version_number
        self.version_number_encoded: str = self.encode(version_number)
        self.build_number: str = ""
        self.build_number_encoded: str = ""

    def publish(self) -> None:
        """Publish app metadata to GitHub Actions environment variables and outputs."""
        gat.set_env("app_package_id", self.package_id)
        gat.set_output("app_package_id", self.package_id)
        gat.set_env("app_version_encoded", self.version_number_encoded)
        gat.set_output("app_version", self.version_number)

    def set_build_number(self, build_number: str) -> None:
        """
        Set the build number and update GitHub Actions outputs.

        Args:
            build_number: Build number for the application.
        """
        self.build_number = build_number
        self.build_number_encoded = self.encode(build_number)
        gat.set_env("app_build_number_encoded", self.build_number_encoded)
        gat.set_output("app_build_number", build_number)
