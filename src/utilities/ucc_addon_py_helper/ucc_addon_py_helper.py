import splunk.rest as rest
import time
import copy
import os
import splunk
import json
import datetime
import os.path as op
import requests as rq
from solnlib import conf_manager
from splunklib import modularinput as smi
from solnlib.modular_input import checkpointer
import sys

APP_NAME = __file__.split(op.sep)[-3]
HEADER_X_LS_INTEGRATION_ID = "74b877ec-ed06-48fb-9e18-6733ea0cf9bb"

def get_account_details(session_key, account_name, logger):
    """
    This function retrieves account details from addon configuration file.
    :param session_key: session key for particular modular input.
    :param account_name: account name configured in the addon.
    :param logger: provides logger of current input.
    :return : account details in form of a dictionary.    
    """
    try:
        cfm = conf_manager.ConfManager(
            session_key, APP_NAME, realm='__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_account'.format(APP_NAME))
        account_conf_file = cfm.get_conf('ta_lansweeper_add_on_for_splunk_account')
    except Exception as exception:
        logger.error("Failed to fetch account details from configuration, error={}".format(exception))
        sys.exit(1)

    logger.info("Fetched configured account details")
    return {
        "client_id": account_conf_file.get(account_name).get('client_id'),
        "client_secret": account_conf_file.get(account_name).get('client_secret'),
        "access_token": account_conf_file.get(account_name).get('access_token'),
        "refresh_token": account_conf_file.get(account_name).get('refresh_token')
    }

def update_access_token(access_token, refresh_token, client_secret, session_key, stanza_name):
    """
    Updates the latest access_token and refresh token in the ta_lansweeper_add_on_for_splunk_account.conf
    :param access_token: Access Token of the Lansweeper Account
    :param refresh_token: Refresh Token of the Lansweeper Account
    :param client_secret: Client Secret of the Lansweeper Account
    :param session_key: Splunk session key
    :param stanza_name: Stanza name of the account to be updated
    :return : True on successfully updating the account configurations
    """
    cfm = conf_manager.ConfManager(
            session_key, APP_NAME, realm='__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_account'.format(APP_NAME))
    conf = cfm.get_conf('ta_lansweeper_add_on_for_splunk_account')
    conf.update(stanza_name,
                {'access_token': access_token, 'client_secret': client_secret, 'refresh_token': refresh_token},
                ['access_token', 'client_secret', 'refresh_token'])
    return True

def get_proxy_settings(session_key, logger):
    """
    This function fetches proxy settings
    :param session_key: session key for particular modular input.
    :param logger: provides logger of current input.
    :return : proxy settings
    """

    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            APP_NAME,
            realm="__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_settings".format(APP_NAME))
        lansweeper_settings_conf = settings_cfm.get_conf(
            "ta_lansweeper_add_on_for_splunk_settings").get_all()
    except Exception as exception:
        logger.error("Failed to fetch proxy details from configuration. {}".format(exception))
        sys.exit(1)

    proxy_settings = None
    proxy_stanza = {}
    for key, value in lansweeper_settings_conf["proxy"].items():
        proxy_stanza[key] = value

    if int(proxy_stanza.get("proxy_enabled", 0)) == 0:
        return proxy_settings
    proxy_port = proxy_stanza.get('proxy_port')
    proxy_url = proxy_stanza.get('proxy_url')
    proxy_type = proxy_stanza.get('proxy_type')
    proxy_username = proxy_stanza.get('proxy_username', '')
    proxy_password = proxy_stanza.get('proxy_password', '')

    if proxy_username and proxy_password:
        proxy_username = rq.compat.quote_plus(proxy_username)
        proxy_password = rq.compat.quote_plus(proxy_password)
        proxy_uri = "%s://%s:%s@%s:%s" % (proxy_type, proxy_username,
                                          proxy_password, proxy_url, proxy_port)
    else:
        proxy_uri = "%s://%s:%s" % (proxy_type, proxy_url, proxy_port)

    proxy_settings = {
        "http": proxy_uri,
        "https": proxy_uri
    }
    logger.info("Fetched configured proxy details.")
    return proxy_settings

def get_log_level(session_key, logger):
    """
    This function returns the log level for the addon from configuration file.
    :param session_key: session key for particular modular input.
    :return : log level configured in addon.
    """
    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            APP_NAME,
            realm="__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_settings".format(APP_NAME))

        logging_details = settings_cfm.get_conf(
            "ta_lansweeper_add_on_for_splunk_settings").get("logging")

        log_level = logging_details.get('loglevel') if (
            logging_details.get('loglevel')) else 'INFO'
        return log_level

    except Exception as exception:
        logger.error(
            "Failed to fetch the log details from the configuration taking INFO as default level, error={}".format(exception))
        return 'INFO'


def write_event(asset_data, site_name, ew, index, logger):
    """
    This function write events to the Splunk
    :param asset_data: list of assets
    :param site_name: Site name associated with the assets
    :param ew: Event Writer object
    :param index: Index on which data will be written
    :param logger: Logger object
    """

    sourcetype = 'lansweeper:asset:v2'
    try:
        logger.info('Writting assets data to Splunk for site={} asset_count={}'.format(site_name, len(asset_data)))
        for asset in asset_data:
            asset['site_name'] = site_name
            event = smi.Event(
                data=json.dumps(asset),
                sourcetype=sourcetype,
                index=index
            )
            ew.write_event(event)
        logger.info('Successfully indexed the asset data')
    except Exception as exception:
        logger.error("Error writing event to Splunk, error={}".format(exception))


def checkpoint_handler(checkpoint_name, session_key, logger):
    """
    This function handles checkpoint. This is not being used at this point but we will need this for future enhancements.
    :param checkpoint_name: represents checkpoint file name.
    :param session_key: session key for particular modular input.
    :param logger: provides logger of current input.
    :return : checkpoint object and start date of the query.
    """

    try:
        ck = checkpointer.KVStoreCheckpointer(
            checkpoint_name, session_key, APP_NAME)
        checkpoint_marker = ck.get(checkpoint_name)
        return ck, query_start_date
    except Exception as exception:
        logger.error("Error occurred while fetching checkpoint, error={}".format(exception))
        sys.exit(1)


def get_conf_stanza(session_key, conf_file, stanza):
    _, serverContent = rest.simpleRequest(
        "/servicesNS/nobody/{}/configs/conf-{}/{}?output_mode=json".format(APP_NAME, conf_file, stanza), 
        sessionKey=session_key
    )
    data = json.loads(serverContent)['entry']
    return data


# ========================================================================
# ========================================================================
# ========================================================================


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

