
import sys
import logging
import traceback

import import_declare_test

from solnlib.modular_input import checkpointer
from solnlib import conf_manager
from splunktaucclib.rest_handler.admin_external import AdminExternalHandler

from addon_name import ADDON_NAME, NORMALIZED_ADDON_NAME
import logger_manager


class AddonInputCheckpointer:
    def __init__(self, session_key, logger, input_name) -> None:
        self.session_key = session_key
        self.logger = logger
        self.input_name = input_name

    def get(self):
        try:
            ck = checkpointer.KVStoreCheckpointer(
                self.input_name, self.session_key, ADDON_NAME)
            return ck.get(self.input_name)
        except Exception as exception:
            self.logger.error("Error occurred while fetching checkpoint, error={}".format(exception))

    def update(self, new_val):
        try:
            ck = checkpointer.KVStoreCheckpointer(
                self.input_name, self.session_key, ADDON_NAME)
            return ck.update(self.input_name, new_val)
        except Exception as exception:
            self.logger.exception("Error occurred while updating the checkpoint, error={}".format(exception))

    def delete(self):
        try:
            ck = checkpointer.KVStoreCheckpointer(
                self.input_name, self.session_key, ADDON_NAME)
            return ck.delete(self.input_name)
        except Exception as exception:
            self.logger.exception("Error occurred while deleting the checkpoint, error={}".format(exception))



def get_account_details(session_key: str, logger, account_name: str):
    cfm = conf_manager.ConfManager(
        session_key,
        ADDON_NAME,
        realm=f"__REST_CREDENTIAL__#{ADDON_NAME}#configs/conf-{NORMALIZED_ADDON_NAME}_account",
    )
    account_conf_file = cfm.get_conf(f"{NORMALIZED_ADDON_NAME}_account")
    return account_conf_file.get(account_name)


def get_log_level(session_key: str):
    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            ADDON_NAME,
            realm=f"__REST_CREDENTIAL__#{ADDON_NAME}#configs/conf-{NORMALIZED_ADDON_NAME}_settings")

        logging_details = settings_cfm.get_conf(
            f"{NORMALIZED_ADDON_NAME}_settings").get("logging")

        log_level = logging_details.get('loglevel') if (
            logging_details.get('loglevel')) else 'INFO'

        return log_level
    except:
        return logging.INFO



class AddonInput:
    '''
    Attributes accessible as class attributes
        - logger
        - session_key
        - event_writer
        - proxy_settings

    Attributes available as argument to collect() method
        - account_details
        - input_name
        - input_item
        - last_checkpoint
    '''
    def __init__(self, session_key, input_name, input_item, event_writer) -> None:
        self.input_name = input_name
        self.input_item = input_item
        self.normalized_input_name = input_name.split("/")[-1]

        self.session_key = session_key
        self.event_writer = event_writer

        log_level = get_log_level(self.session_key)
        self.logger = logger_manager.setup_logging(self.normalized_input_name, log_level)
        self.logger.info(f"Logger initiated. Logging level = {log_level}")

        try:
            self.logger.info(f'Modular input "{self.normalized_input_name}" started.')

            self.logger.debug(f"input_name={input_name}, input_item={input_item}")

            account_name = input_item.get('account')
            account_details = get_account_details(session_key, self.logger, account_name)

            # self.proxy_settings = get_proxy_settings(session_key, self.logger)
            self.proxy_settings = None

            input_checkpointer = AddonInputCheckpointer(session_key, self.logger, self.normalized_input_name)
            last_checkpoint = input_checkpointer.get()
            self.logger.info(f"input={self.normalized_input_name} -> last_checkpoint={last_checkpoint}")

            self.logger.debug("before self.collect()")
            updated_checkpoint = self.collect(account_details, last_checkpoint=last_checkpoint)
            self.logger.debug("after self.collect()")
            self.logger.info(f"input={self.normalized_input_name} -> updating the checkpoint to {updated_checkpoint}")
            if updated_checkpoint:
                input_checkpointer.update(updated_checkpoint)

            self.logger.info(f'Modular input "{self.normalized_input_name}" ended.')

        except Exception as e:
            self.logger.error(
                f'Exception raised while ingesting data for input="{self.normalized_input_name}" {e}. Traceback: {traceback.format_exc()}'
            )


    def collect(self, account_details, last_checkpoint):
        self.logger.error("This collect() function should not be called.")
        raise Exception("collect method has not been implemented.")



class InputHelperRestHandler(AdminExternalHandler):
    def __init__(self, *args, **kwargs):
        AdminExternalHandler.__init__(self, *args, **kwargs)

    def handleList(self, confInfo):
        AdminExternalHandler.handleList(self, confInfo)

    def handleEdit(self, confInfo):
        AdminExternalHandler.handleEdit(self, confInfo)

    def handleCreate(self, confInfo):
        AdminExternalHandler.handleCreate(self, confInfo)

    def handleRemove(self, confInfo):
        # Deleting the checkpoint to avoid issue when user tries to delete the input but then tries to recreate the input with the same name

        session_key = self.getSessionKey()
        log_level = get_log_level(session_key)
        input_name = self.callerArgs.id
        if input_name:
            logger = logger_manager.setup_logging(input_name, log_level)

            input_checkpointer = AddonInputCheckpointer(self.getSessionKey(), logger, input_name)
            last_checkpoint = input_checkpointer.get()

            if last_checkpoint:
                logger.info(f"Deleting the checkpoint for input={input_name} with last found checkpoint was {last_checkpoint}")
                input_checkpointer.delete()
                logger.info(f"Deleted the input checkpoint for input={input_name}")
            else:
                logger.info(f"No checkpoint present for input={input_name}")

            AdminExternalHandler.handleRemove(self, confInfo)

        else:
            logger = logger_manager.setup_logging("delete_input_error", log_level)
            err_msg = "Unable to find the input name in the handler."
            logger.error(err_msg)
            raise Exception(err_msg)
