import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)

import json
import pytest

from helpers.splunk_app_details import (
    fetch_app_package_id_from_global_config_json,
    fetch_app_version_from_global_config_json,
    fetch_app_package_id_from_app_conf,
    fetch_app_version_number_from_app_conf,
    fetch_app_build_number_from_app_conf,
)


# Write mock globalConfig.json file
class WriteMockGlobalConfigJson():
    def __init__(self, json_data) -> None:
        self.json_data = json_data
        self.file_path = None

    def __enter__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), "globalConfig.json")
        with open(self.file_path, "w") as f:
            json.dump(self.json_data, f)
        return self.file_path

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
        os.remove(self.file_path)   # Cleanup


# Write mock app.conf file
class WriteMockAppConf():
    def __init__(self, content) -> None:
        self.content = content
        self.file_path = None

    def __enter__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), "app.conf")
        with open(self.file_path, "w") as f:
            f.write(self.content)
        return self.file_path

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.remove(self.file_path)   # Cleanup



def test_fetch_app_version_from_global_config_json_valid():
    with WriteMockGlobalConfigJson({"meta": {"name": "my_app", "version": "1.2.3"}}) as file_path:
        app_version = fetch_app_version_from_global_config_json(file_path)
        assert app_version == "1.2.3"


def test_fetch_app_version_from_global_config_json_missing_meta():
    with WriteMockGlobalConfigJson({"data": "some_data"}) as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_version_from_global_config_json(file_path)
        assert str(excinfo.value) == "Unable to fetch the app_version_number from globalConfig.json file."


def test_fetch_app_package_id_from_global_config_json_missing_name():
    with WriteMockGlobalConfigJson({"meta": {"version": "1.2.3"}}) as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_package_id_from_global_config_json(file_path)
        assert str(excinfo.value) == "Unable to fetch the app_package_id from globalConfig.json file."


def test_fetch_app_version_from_global_config_json_missing_version():
    with WriteMockGlobalConfigJson({"meta": {"name": "my_app"}}) as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_version_from_global_config_json(file_path)
        assert str(excinfo.value) == "Unable to fetch the app_version_number from globalConfig.json file."


def test_fetch_app_package_id_from_app_conf_valid():
    with WriteMockAppConf('''
[package]
id = my_app
''') as file_path:
        with pytest.raises(Exception) as excinfo:
            app_package_id = fetch_app_package_id_from_app_conf(file_path)
            assert app_package_id == "my_app"


def test_fetch_app_package_id_from_app_conf_empty_package():
    with WriteMockAppConf('''
[not_package]
id = not_relevant
                          ''') as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_package_id_from_app_conf(file_path, ".")
        assert "`id` attribute in the app.conf" in str(excinfo.value)


def test_fetch_app_package_id_from_app_conf_missing_id():
    with WriteMockAppConf('''
[package]
not_id = not_relevant
                          ''') as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_package_id_from_app_conf(file_path, ".")
        assert "`id` attribute in the app.conf" in str(excinfo.value)


def test_fetch_app_version_number_from_app_conf_missing_version():
    with WriteMockAppConf('''
[package]
id = my_app
''') as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_version_number_from_app_conf(file_path)
        assert "`id` attribute in the app.conf" in str(excinfo.value)


def test_fetch_app_version_number_from_app_conf_launcher_stanza():
    with WriteMockAppConf('''
[launcher]
version = 1.5.5
''') as file_path:
        app_version = fetch_app_version_number_from_app_conf(file_path)
        assert app_version == "1.5.5"


def test_fetch_app_version_number_from_app_conf_id_stanza():
    with WriteMockAppConf('''
[id]
version = 2.0.0
''') as file_path:
        app_version = fetch_app_version_number_from_app_conf(file_path)
        assert app_version == "2.0.0"


def test_fetch_app_version_number_from_app_conf_both_present_priority_launcher():
    with WriteMockAppConf('''
[launcher]
version = 1.0.0

[id]
version = 3.1.4
''') as file_path:
        app_version = fetch_app_version_number_from_app_conf(file_path)
        assert app_version == "1.0.0"


def test_fetch_app_version_number_from_app_conf_both_present_priority_launcher_2():
    with WriteMockAppConf('''
[id]
version = 3.1.4

[launcher]
version = 1.0.0
''') as file_path:
        app_version = fetch_app_version_number_from_app_conf(file_path)
        assert app_version == "1.0.0"


def test_fetch_app_version_number_from_app_conf_no_stanza():
    with WriteMockAppConf('''
[general]
some_key = some_value
''') as file_path:
        with pytest.raises(Exception) as excinfo:
            fetch_app_version_number_from_app_conf(file_path)
        assert "`id` attribute in the app.conf" in str(excinfo.value)


def test_fetch_app_build_number_from_app_conf_build_present():
    with WriteMockAppConf('''
[package]
id = my_app

[install]
build = 123
''') as file_path:
        app_build_number = fetch_app_build_number_from_app_conf(file_path)
        assert app_build_number == "123"


def test_fetch_app_build_number_from_app_conf_build_missing():
    with WriteMockAppConf('''
[package]
id = my_app
''') as file_path:
        app_build_number = fetch_app_build_number_from_app_conf(file_path)
        assert app_build_number == "1"

