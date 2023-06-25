import os
import sys
import configparser
import traceback

sys.path.append(os.path.dirname(__file__))

import helper_github_action as utils
from app_inspect import SplunkAppInspect
from app_build_generate import SplunkAppBuildGenerator
from app_whats_inside import SplunkAppWhatsInsideDetail



# This is just for testing
# utils.info("Files under current working directory:- {}".format(os.getcwd()))
# utils.list_files(os.getcwd())


try:
    SplunkAppWhatsInsideDetail().update_readme()
except:
    pass

try:
    build_path = SplunkAppBuildGenerator().generate()
    SplunkAppInspect(build_path).run_all_checks()
except:
    pass



# # Read App Build Name
# app_build_name = utils.get_input('app_build_name')
# utils.info("app_build_name: {}".format(app_build_name))

# direct_app_build_path = utils.get_input('app_build_path')
# utils.info("app_build_path: {}".format(direct_app_build_path))

# app_build_path = "{}.tgz".format(app_build_name)
# app_build_filename = app_build_path
# if direct_app_build_path != "NONE":
#     app_build_path = direct_app_build_path
#     app_build_filename = os.path.basename(app_build_path)
# utils.info("Current working directory: {}, app_build_path: {}".format(os.getcwd(), app_build_path))

