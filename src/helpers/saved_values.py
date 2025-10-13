import os
import re
from contextlib import contextmanager

import github_action_toolkit as gat


class SavedPaths:
    def __init__(self, app_dir_name):
        self.root_dir_path = os.getcwd()

        self.repo_dir_name = "repodir"
        self.repo_dir_path = os.path.join(self.root_dir_path, self.repo_dir_name)

        self.app_dir_name = app_dir_name
        self.app_dir_path = os.path.join(self.repo_dir_path, self.app_dir_name)


@contextmanager
def keep_working_dir_unchanged():
    _path = os.getcwd()
    yield
    os.chdir(_path)


class AppInfo:
    def encode(self, val):
        return re.sub("[^0-9a-zA-Z]+", "_", val)

    def __init__(self, package_id, version_number):
        self.package_id = package_id
        gat.set_env("app_package_id", package_id)

        self.version_number = version_number
        self.version_number_encoded = self.encode(version_number)
        gat.set_env("app_version_encoded", self.version_number_encoded)

    def set_build_number(self, build_number):
        self.build_number = build_number
        self.build_number_encoded = self.encode(build_number)
        gat.set_env("app_build_number_encoded", self.build_number_encoded)
