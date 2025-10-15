import os
import re
from collections.abc import Iterator
from contextlib import contextmanager

import github_action_toolkit as gat


class SavedPaths:
    def __init__(self, app_dir_name: str) -> None:
        self.root_dir_path: str = os.getcwd()

        self.repo_dir_name: str = "repodir"
        self.repo_dir_path: str = os.path.join(self.root_dir_path, self.repo_dir_name)

        self.app_dir_name: str = app_dir_name
        self.app_dir_path: str = os.path.join(self.repo_dir_path, self.app_dir_name)


@contextmanager
def keep_working_dir_unchanged() -> Iterator[None]:
    _path = os.getcwd()
    yield
    os.chdir(_path)


class AppInfo:
    def encode(self, val: str) -> str:
        return re.sub("[^0-9a-zA-Z]+", "_", val)

    def __init__(self, package_id: str, version_number: str) -> None:
        self.package_id: str = package_id
        gat.set_env("app_package_id", package_id)

        self.version_number: str = version_number
        self.version_number_encoded: str = self.encode(version_number)
        gat.set_env("app_version_encoded", self.version_number_encoded)

        # These will be set later via set_build_number()
        self.build_number: str = ""
        self.build_number_encoded: str = ""

    def set_build_number(self, build_number: str) -> None:
        self.build_number = build_number
        self.build_number_encoded = self.encode(build_number)
        gat.set_env("app_build_number_encoded", self.build_number_encoded)
