import github_action_toolkit as gat

from helpers.saved_values import SavedPaths
from utilities.common_splunk_js_utilities import CommonJSUtilitiesFile
from utilities.logger import LoggerUtility
from utilities.ucc_additional_packaging import UCCAdditionalPackagingUtility
from utilities.whats_inside_app import WhatsInsideTheAppUtility


class SplunkAppUtilities:
    """
    Manage and apply various utilities to Splunk Apps and Add-ons.

    This class processes user-configured utilities and applies them to the app,
    including features like logging, Python SDK integration, JavaScript utilities,
    and more. Each utility can modify the app structure or add additional files.
    """

    def __init__(
        self,
        saved_paths: SavedPaths,
        app_read_dir: str,
        app_write_dir: str,
        is_test: bool = False,
    ) -> None:
        """
        Initialize the SplunkAppUtilities manager.

        Args:
            app_read_dir: Directory to read the original app files from.
            app_write_dir: Directory to write modified app files to.
            is_test: Flag indicating if running in test mode. Defaults to False.
        """
        self.saved_paths: SavedPaths = saved_paths
        self.app_read_dir: str = app_read_dir
        self.app_write_dir: str = app_write_dir
        self.is_test: bool = is_test
        # Get Inputs
        app_utilities_input = gat.get_user_input("app_utilities")
        if not app_utilities_input or app_utilities_input == "NONE" or app_utilities_input == "":
            app_utilities_list: list[str] = []
        else:
            app_utilities_split = app_utilities_input.split(",")
            app_utilities_list = [u.strip() for u in app_utilities_split]

        self.result: bool = True
        self.add_utilities(app_utilities_list)

    def add_utilities(self, app_utilities: list[str]) -> None:
        """
        Add and configure utilities for the Splunk app.

        Processes the list of utility names and applies each one to the app.
        Supported utilities include whats_in_the_app, logger,
        common_js_utilities, and ucc_additional_packaging.

        Args:
            app_utilities: List of utility names to add to the app.
        """
        if not app_utilities:
            gat.info("🛠️ No utilities specified - skipping")
            return

        gat.info(f"🛠️ Installing app utilities - {app_utilities}")
        for utility in app_utilities:
            try:
                if utility == "whats_in_the_app":
                    WhatsInsideTheAppUtility(
                        self.saved_paths, self.app_read_dir, self.app_write_dir
                    ).add()

                elif utility == "logger":
                    LoggerUtility(self.saved_paths, self.app_read_dir, self.app_write_dir).add()

                elif utility == "splunk_python_sdk":
                    gat.error(
                        "The 'splunk_python_sdk' utility has been removed in v6. "
                        "Use the Python Dependency Manager feature (python_requirements_file input) instead."
                    )

                elif utility == "common_js_utilities":
                    CommonJSUtilitiesFile(
                        self.saved_paths, self.app_read_dir, self.app_write_dir
                    ).add()

                elif utility == "ucc_additional_packaging":
                    UCCAdditionalPackagingUtility(
                        self.saved_paths, self.app_read_dir, self.app_write_dir
                    ).add()

                else:
                    gat.error(
                        f"🛠️ Unsupported utility: '{utility}'. "
                        "Valid options: whats_in_the_app, logger, common_js_utilities, ucc_additional_packaging"
                    )

            except Exception as e:
                gat.error(f"Error in utility '{utility}': {e}")
                self.result = False

        gat.info("🛠️ App utilities installation completed.")
