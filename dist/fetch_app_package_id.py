import os
import sys
import configparser
import traceback

sys.path.append(os.path.dirname(__file__))
import utils


utils.info("Started fetch_app_package_id.py")

# Read App Directory
app_dir = utils.get_input('app_dir')
utils.info("app_dir: {}".format(app_dir))

try:
    config = configparser.ConfigParser()
    config.read(os.path.join(app_dir, 'default', 'app.conf'))
    package_id = config['package']['id']
    utils.set_env("SPLUNK_FETCHED_APP_PACKAGE_ID", package_id)
except Exception as e:
    utils.error("Unable to fetch the app-package-id from app.conf. {}".format(e))
    utils.error(traceback.format_exc())
