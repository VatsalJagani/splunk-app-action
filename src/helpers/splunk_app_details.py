import json

import github_action_toolkit as gat

from helpers.splunk_config_parser import SplunkConfigParser


def fetch_app_package_id_from_global_config_json(global_config_file_path: str) -> str:
    gat.info("Starting app package ID extraction from globalConfig.json...")
    gat.debug(f"Reading globalConfig.json from: {global_config_file_path}")

    try:
        with open(global_config_file_path) as f:
            global_config = json.loads(f.read())
            _app_package_id = global_config["meta"]["name"]

        gat.debug(f"Found app package ID: {_app_package_id}")
        gat.info("App package ID extraction completed successfully")
        return _app_package_id

    except Exception as e:
        msg = f"Exception while fetching app_package_id from globalConfig.json file. {e}"
        gat.error(msg)
        raise Exception(msg) from e


def fetch_app_version_from_global_config_json(global_config_file_path: str) -> str:
    gat.info("Starting app version extraction from globalConfig.json...")
    gat.debug(f"Reading globalConfig.json from: {global_config_file_path}")

    try:
        with open(global_config_file_path) as f:
            global_config = json.loads(f.read())
            _app_version = global_config["meta"]["version"]

        gat.debug(f"Found app version: {_app_version}")
        gat.info("App version extraction completed successfully")
        return _app_version

    except Exception as e:
        gat.error(f"Failed to fetch app version from globalConfig.json: {e}")
        raise Exception("Failed to fetch app version from globalConfig.json.") from e


def fetch_app_package_id_from_app_conf(app_conf_file_path: str, app_dir_input: str) -> str:
    gat.info("Starting app package ID extraction from app.conf...")
    gat.debug(f"Reading app.conf from: {app_conf_file_path}")

    app_config = SplunkConfigParser(app_conf_file_path)

    if "package" in app_config and "id" in app_config["package"]:
        package_id = app_config["package"]["id"]
        gat.debug(f"Found package ID in app.conf: {package_id}")
        gat.info("App package ID extraction completed successfully")
        return package_id
    elif app_dir_input == ".":
        gat.error(
            "Missing 'id' attribute in app.conf [package] stanza (recommended for root directory apps)"
        )
        raise Exception("Add 'id' attribute in app.conf [package] stanza")
    else:
        gat.warning("No package ID found in app.conf, using directory name as fallback")
        gat.info("App package ID extraction completed (using fallback)")
        return app_dir_input


def fetch_app_version_number_from_app_conf(app_conf_file_path: str) -> str:
    gat.info("Starting app version extraction from app.conf...")
    gat.debug(f"Reading app.conf from: {app_conf_file_path}")

    app_config = SplunkConfigParser(app_conf_file_path)

    if "launcher" in app_config and "version" in app_config["launcher"]:
        version = app_config["launcher"]["version"]
        gat.debug(f"Found version in [launcher] stanza: {version}")
        gat.info("App version extraction completed successfully")
        return version
    elif "id" in app_config and "version" in app_config["id"]:
        version = app_config["id"]["version"]
        gat.debug(f"Found version in [id] stanza: {version}")
        gat.info("App version extraction completed successfully")
        return version
    else:
        gat.error("Missing 'version' attribute in app.conf [launcher] or [id] stanza")
        raise Exception("Add 'id' attribute in app.conf [launcher] stanza")


def fetch_app_build_number_from_app_conf(app_conf_file_path: str) -> str:
    gat.info("Starting app build number extraction from app.conf...")
    gat.debug(f"Reading app.conf from: {app_conf_file_path}")

    app_config = SplunkConfigParser(app_conf_file_path)

    if "install" in app_config and "build" in app_config["install"]:
        build_number = app_config["install"]["build"]
        gat.debug(f"Found build number in [install] stanza: {build_number}")
        gat.info("App build number extraction completed successfully")
        return build_number
    else:
        gat.debug("No build number found in app.conf, using default")
        gat.info("App build number extraction completed (using default)")
        return "1"
