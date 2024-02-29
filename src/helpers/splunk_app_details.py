import os
import json
import helpers.github_action_utils as utils
from helpers.splunk_config_parser import SplunkConfigParser


def fetch_app_package_id_from_global_config_json(global_config_file_path):
    utils.info("Fetching app package id from globalConfig.json file.")

    _app_package_id = None

    with open(global_config_file_path, 'r') as f:
        global_config = json.loads(f.read())

        _app_package_id = global_config["meta"]["name"]

    if not _app_package_id:
        raise Exception("Unable to fetch the app package id from globalConfig.json file")

    return _app_package_id


def fetch_app_version_from_global_config_json(global_config_file_path):
    utils.info("Fetching app version number from globalConfig.json file.")

    _app_version = None

    with open(global_config_file_path, 'r') as f:
        global_config = json.loads(f.read())

        _app_version = global_config["meta"]["version"]

    if not _app_version:
        raise Exception("Unable to fetch the app package id from globalConfig.json file")

    return _app_version


def _read_app_conf(app_dir_path):
    return SplunkConfigParser(os.path.join(app_build_dir, 'default', 'app.conf'))


def fetch_app_package_id_from_app_conf(app_conf_file_path, app_dir_input):
    app_config = SplunkConfigParser(app_conf_file_path)

    if 'package' in app_config and 'id' in app_config['package']:
        utils.info(
            "Using app package id found in app.conf - {}".format(app_config['package']['id']))
        return app_config['package']['id']
    elif app_dir_input == ".":
        utils.error(
            "It is recommended to have `id` attribute in the app.conf's [package] stanza.")
        raise Exception(
            "Add `id` attribute in the app.conf's [package] stanza.")
    else:
        return app_dir_input


def fetch_app_version_number_from_app_conf(app_conf_file_path):
    app_config = SplunkConfigParser(app_conf_file_path)

    if 'launcher' in app_config and 'version' in app_config['launcher']:
        utils.info(
            "Using app version number found in app.conf [launcher] - {}".format(app_config['launcher']['version']))
        return app_config['launcher']['version']
    elif 'id' in app_config and 'version' in app_config['id']:
        utils.info(
            "Using app version number found in app.conf [id] - {}".format(app_config['id']['version']))
        return app_config['id']['version']
    else:
        utils.error(
            "It is recommended to have `version` attribute in the app.conf's [launcher] stanza.")
        raise Exception(
            "Add `id` attribute in the app.conf's [launcher] stanza.")


def fetch_app_build_number_from_app_conf(app_conf_file_path):
    app_config = SplunkConfigParser(app_conf_file_path)

    if 'install' in app_config and 'build' in app_config['install']:
        utils.info(
            "Using app build number found in app.conf [install] - {}".format(app_config['install']['build']))
        return app_config['install']['build']
    else:
        utils.info("No app build number found, defaulting to 1.")
        return "1"
