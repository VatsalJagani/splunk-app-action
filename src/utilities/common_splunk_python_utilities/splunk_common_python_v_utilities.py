import json
from six.moves.urllib.parse import quote
import splunk.entity as entity
from splunk import rest


APP_PACKAGE_ID = "<<<app_package_id>>>"



def is_true(val: str):
    return str(val).lower() in ('1', 'true', 'yes', 'y', 't')


def is_false(val: str):
    return str(val).lower() in ('0', 'false', 'no', 'n', 'f')



class VSplunkCredentialManager(object):
    '''
    Credential manager to store and retrieve password
    '''
    def __init__(self, session_key):
        '''
        Init for credential manager
        :param session_key: Splunk session key
        '''
        self.session_key = session_key

    def get_credential(self, username):
        '''
        Searches passwords using username and returns tuple of username and password if credentials are found else tuple of empty string
        :param username: Username used to search credentials.
        :return: username, password
        '''
        # list all credentials
        entities = entity.getEntities(["admin", "passwords"], search=APP_PACKAGE_ID, count=-1, namespace=APP_PACKAGE_ID, owner="nobody",
                                    sessionKey=self.session_key)

        # return first set of credentials
        for _, value in list(entities.items()):
            # if str(value["eai:acl"]["app"]) == APP_NAME and value["username"] == username:
            if value['username'].partition('`')[0] == username and not value.get('clear_password', '`').startswith('`'):
                try:
                    return json.loads(value.get('clear_password', '{}').replace("'", '"'))
                except:
                    return value.get('clear_password', '')

    def store_credential(self, username, password):
        '''
        Updates password if password is already stored with given username else create new password.
        :param username: Username to be stored.
        :param password: Password to be stored.
        :return: None
        '''
        old_password = self.get_credential(username)
        username = username + "``splunk_cred_sep``1"

        if old_password:
            postargs = {
                "password": json.dumps(password) if isinstance(password, dict) else password
            }
            username = username.replace(":", r"\:")
            realm = quote(APP_PACKAGE_ID + ":" + username + ":", safe='')

            rest.simpleRequest(
                f"/servicesNS/nobody/{APP_PACKAGE_ID}/storage/passwords/{realm}?output_mode=json",
                self.session_key, postargs=postargs, method='POST', raiseAllErrors=True)

            return True
        else:
            # when there is no existing password
            postargs = {
                "name": username,
                "password": json.dumps(password) if isinstance(password, dict) else password,
                "realm": APP_PACKAGE_ID
            }
            rest.simpleRequest(f"/servicesNS/nobody/{APP_PACKAGE_ID}/storage/passwords/?output_mode=json",
                                    self.session_key, postargs=postargs, method='POST', raiseAllErrors=True)



class VSplunkConfigManager:
    def __init__(self, logger, session_key) -> None:
        self.logger = logger
        self.session_key = session_key


    def _get_all_conf_stanza(self, path):
        self.logger.info(f'Getting conf all stanzas, app="{APP_PACKAGE_ID}", path="{path}"')
        _, serverContent = rest.simpleRequest(
            f"/servicesNS/-/{APP_PACKAGE_ID}/{path}?output_mode=json&count=0",
            sessionKey=self.session_key,
            raiseAllErrors=True,
        )
        return json.loads(serverContent)["entry"]
    

    def _get_conf_stanza_content(self, path, stanza_name):
        self.logger.info(f'Getting conf stanza, app="{APP_PACKAGE_ID}", path="{path}", stanza="{stanza_name}"')
        _stanza_name_quoted = quote(stanza_name, safe='')
        _, serverContent = rest.simpleRequest(
            f"/servicesNS/-/{APP_PACKAGE_ID}/{path}/{_stanza_name_quoted}?output_mode=json&count=0",
            sessionKey=self.session_key,
            raiseAllErrors=True,
        )
        return json.loads(serverContent)["entry"][0]["content"]
    

    def _update_conf_stanza_content(self, path, stanza_name, content_to_update):
        self.logger.info(f'Updating conf stanza, app="{APP_PACKAGE_ID}", path="{path}", stanza="{stanza_name}", data="{content_to_update}"')
        _stanza_name_quoted = quote(stanza_name, safe='')
        rest.simpleRequest(
            f"/servicesNS/nobody/{APP_PACKAGE_ID}/{path}/{_stanza_name_quoted}?output_mode=json&count=0",
            sessionKey=self.session_key,
            raiseAllErrors=True,
            method="POST",
            postargs=content_to_update,
        )


    def get_all_macros(self):
        return self._get_all_conf_stanza("admin/macros")


    def get_macro(self, macro_name):
        self._get_conf_stanza_content("admin/macros", macro_name)


    def get_all_macros_definitions_as_dict(self):
        data = self.get_all_macros()
        results = {}
        for item in data:
            try:
                results[item["name"]] = item["content"]["definition"]
            except Exception as err:
                self.logger.warning(f"Unable to get definition for {item["name"]}, content={item["content"]}")
        return results


    def update_macro(self, macro_name, data):
        self._update_conf_stanza_content("admin/macros", macro_name, data)


    def get_all_saved_searches(self):
        self._get_all_conf_stanza("saved/searches")


    def get_saved_search(self, savedsearch_name):
        self._get_conf_stanza_content("saved/searches", savedsearch_name)


    def update_saved_search(self, savedsearch_name, data):
        self._update_conf_stanza_content("saved/searches", savedsearch_name, data)


    def get_all_alert_actions(self):
        self._get_all_conf_stanza("configs/conf-alert_actions")


    def get_alert_action(self, alert_action_name):
        self._get_conf_stanza_content("configs/conf-alert_actions", alert_action_name)

