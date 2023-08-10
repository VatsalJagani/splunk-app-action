
import os

import helper_github_action as utils
import helper_github_pr
from helper_file_handler import FullRawFileHandler, PartConfFileHandler


class LoggerUtility:
    def __init__(self) -> None:
        self.should_execute = True

        log_files_prefix = utils.get_input('logger_log_files_prefix')
        utils.info("log_files_prefix: {}".format(log_files_prefix))
        if not log_files_prefix or log_files_prefix=="NONE":
            utils.error("skipping the logger adding as logger_log_files_prefix input is not defined.")
            self.should_execute = False

        logger_sourcetype = utils.get_input('logger_sourcetype')
        utils.info("logger_sourcetype: {}".format(logger_sourcetype))
        if not logger_sourcetype or logger_sourcetype=="NONE":
            utils.error("skipping the logger adding as logger_sourcetype input is not defined.")
            self.should_execute = False

        self.words_for_replacement = {
            '<<<log_files_prefix>>>': log_files_prefix,
            '<<<logger_sourcetype>>>': logger_sourcetype
        }


    def add_logger(self):
        if not self.should_execute:
            return False

        update1 = self.add_logger_manager_py()
        update2 = self.add_props_content()
        if update1 or update2:
            return helper_github_pr.get_multi_files_hash([
                os.path.join(utils.CommonDirPaths.APP_DIR, 'bin', 'logger_manager.py'),
                os.path.join(utils.CommonDirPaths.APP_DIR, 'default', 'props.conf')
            ])
        return False


    def add_logger_manager_py(self):
        return FullRawFileHandler(
            os.path.join(os.path.dirname(__file__), 'logger_manager.py'),
            os.path.join(utils.CommonDirPaths.APP_DIR, 'bin', 'logger_manager.py'),
            self.words_for_replacement
        ).validate_file_content()


    def add_props_content(self):
        return PartConfFileHandler(
            os.path.join(os.path.dirname(__file__), 'props.conf'),
            os.path.join(utils.CommonDirPaths.APP_DIR, 'default', 'props.conf'),
            self.words_for_replacement
        ).validate_config()