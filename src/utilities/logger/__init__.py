import os
from typing import override

import github_action_toolkit as gat

from helpers.file_manager import FullRawFileHandler, PartConfFileHandler
from helpers.saved_values import SavedPaths
from utilities.base_utility import BaseUtility


class LoggerUtility(BaseUtility):
    """
    Utility to add logging functionality to a Splunk app.

    Adds a logger manager module and configures props.conf for log indexing,
    enabling structured logging within Splunk apps with customizable log file
    prefixes and sourcetypes.
    """

    words_for_replacement: dict[str, str]

    def __init__(self, saved_paths: SavedPaths, app_read_dir: str, app_write_dir: str) -> None:
        """
        Initialize the logger utility.

        Args:
            app_read_dir: Directory to read the original app files from.
            app_write_dir: Directory to write modified app files to.
        """
        super().__init__(saved_paths, app_read_dir, app_write_dir)
        self.pr_title: str = "Added/Updated Logger Utility via splunk-app-action"
        self.words_for_replacement = {}

    @override
    def implement_utility(self) -> str | list[str] | None:
        """
        Add logger manager and props configuration to the app.

        Retrieves user inputs for log file prefix and sourcetype, adds the logger
        manager Python module, and configures props.conf for log indexing.

        Returns:
            List of modified file paths if changes were made, False if required
            inputs are missing, None if no changes were needed.
        """
        gat.info("📝 Adding LoggerUtility")
        should_execute = True

        log_files_prefix = gat.get_user_input("logger_log_files_prefix")
        gat.debug(f"Log files prefix: {log_files_prefix}")
        if not log_files_prefix or log_files_prefix == "NONE":
            gat.error("Skipping logger setup - logger_log_files_prefix not provided")
            should_execute = False

        logger_sourcetype = gat.get_user_input("logger_sourcetype")
        gat.debug(f"Logger sourcetype: {logger_sourcetype}")
        if not logger_sourcetype or logger_sourcetype == "NONE":
            gat.error("Skipping logger setup - logger_sourcetype not provided")
            should_execute = False

        self.words_for_replacement = {
            "<<<log_files_prefix>>>": log_files_prefix or "",
            "<<<logger_sourcetype>>>": logger_sourcetype or "",
        }

        if not should_execute:
            return None

        update1 = self.add_logger_manager_py()
        update2 = self.add_props_content()

        if update1 or update2:
            gat.info("Logger utility setup completed successfully")
            return [
                os.path.join(self.app_write_dir, "bin", "logger_manager.py"),
                os.path.join(self.app_write_dir, "default", "props.conf"),
            ]
        gat.info("Logger utility - no changes needed")

    def add_logger_manager_py(self) -> bool:
        """
        Add logger_manager.py file to the app's bin directory.

        Returns:
            True if the file was added or updated, False otherwise.
        """
        return FullRawFileHandler(
            os.path.join(os.path.dirname(__file__), "logger_manager.py"),
            os.path.join(self.app_write_dir, "bin", "logger_manager.py"),
            self.words_for_replacement,
        ).validate_file_content()

    def add_props_content(self) -> bool:
        """
        Add logger configuration to the app's default/props.conf file.

        Returns:
            True if the configuration was added or updated, False otherwise.
        """
        return PartConfFileHandler(
            os.path.join(os.path.dirname(__file__), "props.conf"),
            os.path.join(self.app_write_dir, "default", "props.conf"),
            self.words_for_replacement,
        ).validate_config()
