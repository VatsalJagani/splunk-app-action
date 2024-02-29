
import os

import helper_github_action as utils
from helpers.file_manager import FullRawFileHandler, PartConfFileHandler
from utilities.base_utility import BaseUtility


class LoggerUtility(BaseUtility):

    def implement_utility(self):
        utils.info("Adding LoggerUtility.")
        should_execute = True

        log_files_prefix = utils.get_input('logger_log_files_prefix')
        utils.info("log_files_prefix: {}".format(log_files_prefix))
        if not log_files_prefix or log_files_prefix == "NONE":
            utils.error(
                "skipping the logger adding as logger_log_files_prefix input is not defined.")
            should_execute = False

        logger_sourcetype = utils.get_input('logger_sourcetype')
        utils.info("logger_sourcetype: {}".format(logger_sourcetype))
        if not logger_sourcetype or logger_sourcetype == "NONE":
            utils.error(
                "skipping the logger adding as logger_sourcetype input is not defined.")
            should_execute = False

        self.words_for_replacement = {
            '<<<log_files_prefix>>>': log_files_prefix,
            '<<<logger_sourcetype>>>': logger_sourcetype
        }

        if not should_execute:
            return False

        update1 = self.add_logger_manager_py()
        update2 = self.add_props_content()

        if update1 or update2:
            utils.info("Updated logger related files.")
            return [
                os.path.join(self.app_write_dir,
                             'bin', 'logger_manager.py'),
                os.path.join(self.app_write_dir,
                             'default', 'props.conf')
            ]
        utils.info("No change in logger related files.")


    def add_logger_manager_py(self):
        return FullRawFileHandler(
            os.path.join(os.path.dirname(__file__), 'logger_manager.py'),
            os.path.join(self.app_write_dir,
                         'bin', 'logger_manager.py'),
            self.words_for_replacement
        ).validate_file_content()


    def add_props_content(self):
        return PartConfFileHandler(
            os.path.join(os.path.dirname(__file__), 'props.conf'),
            os.path.join(self.app_write_dir,
                         'default', 'props.conf'),
            self.words_for_replacement
        ).validate_config()
