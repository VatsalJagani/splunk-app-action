import github_action_toolkit as gat

from helpers.saved_values import AppInfo, SavedPaths
from utilities.common_splunk_js_utilities import CommonJSUtilitiesFile
from utilities.logger import LoggerUtility
from utilities.splunk_sdk_python import SplunkPythonSDKUtility
from utilities.ucc_additional_packaging import UCCAdditionalPackagingUtility
from utilities.whats_inside_app import WhatsInsideTheAppUtility


class SplunkAppUtilities:
    def __init__(
        self,
        saved_paths: SavedPaths,
        app_info: AppInfo,
        app_read_dir: str,
        app_write_dir: str,
        is_test: bool = False,
    ) -> None:
        self.app_read_dir: str = app_read_dir
        self.app_write_dir: str = app_write_dir
        self.is_test: bool = is_test
        # Get Inputs
        app_utilities_input = gat.get_user_input("app_utilities")
        if not app_utilities_input or app_utilities_input == "NONE" or app_utilities_input == "":
            self.app_utilities: list[str] = []
            app_utilities_list: list[str] = []
        else:
            app_utilities_split = app_utilities_input.split(",")
            app_utilities_list = [u.strip() for u in app_utilities_split]

        self.add_utilities(app_utilities_list)

    def add_utilities(self, app_utilities: list[str]) -> None:
        if not app_utilities:
            gat.debug("No utilities specified - skipping")
            return

        with gat.group("🛠️ Installing app utilities"):
            gat.debug(f"Utilities to install: {app_utilities}")

            for utility in app_utilities:
                if utility == "whats_in_the_app":
                    WhatsInsideTheAppUtility(self.app_read_dir, self.app_write_dir)

                elif utility == "logger":
                    LoggerUtility(self.app_read_dir, self.app_write_dir).add()

                elif utility == "splunk_python_sdk":
                    SplunkPythonSDKUtility(self.app_read_dir, self.app_write_dir).add()

                elif utility == "common_js_utilities":
                    CommonJSUtilitiesFile(self.app_read_dir, self.app_write_dir).add()

                elif utility == "ucc_additional_packaging":
                    UCCAdditionalPackagingUtility(self.app_read_dir, self.app_write_dir).add()

                else:
                    gat.error(f"Unsupported utility: {utility}")

            gat.info("App utilities installation completed successfully")
