import os
import sys
import configparser
import traceback

sys.path.append(os.path.dirname(__file__))
import utils
import app_inspect


app_dir = utils.get_input('app_dir')
utils.info("app_dir: {}".format(app_dir))
app_build_name = utils.get_input('app_build_name')
utils.info("app_build_name: {}".format(app_build_name))

app_package_id = None


# This is just for testing
utils.info("Files under current working directory:- {}".format(os.getcwd()))
utils.list_files(os.getcwd())



def remove_git_folders():
    utils.info("Removing .git and .github directory from repo.")
    os.system('rm -rf repodir/.github')
    os.system('rm -rf repodir/.git')


def fetch_app_package_id():
    utils.info("Fetching app package id. from app.conf file.")
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join('repodir', app_dir, 'default', 'app.conf'))
        utils.info("app.conf sections: {}".format(config.sections()))
        if 'package' in config and 'id' in config['package']:
            return config['package']['id']
        else:
            utils.error("It is recommended to have id attribute in the app.conf's [package] stanza.")
            return None
    except Exception as e:
        utils.error("Unable to fetch the app-package-id from app.conf. {}".format(e))
        utils.error(traceback.format_exc())



def generate_app_build():
    global app_package_id

    if app_dir == '.':
        os.system('mv repodir {}'.format(app_package_id))
        os.system("find {} -type f -exec chmod 644 '{{}}' \;".format(app_package_id))
        os.system("find {} -type d -exec chmod 755 '{{}}' \;".format(app_package_id))
        os.system("tar -czf {}.tgz {}".format(app_build_name, app_package_id))
    else:
        os.system('cd repodir')
        
        if app_package_id and app_dir != app_package_id:
            os.system('mv {} {}'.format(app_dir, app_package_id))
        else:
            app_package_id = app_dir
        
        os.system("find {} -type f -exec chmod 644 '{{}}' \;".format(app_package_id))
        os.system("find {} -type d -exec chmod 755 '{{}}' \;".format(app_package_id))
        os.system("tar -czf {}.tgz {}".format(app_build_name, app_package_id))

        os.system('cd ..')



remove_git_folders()
app_package_id = fetch_app_package_id()
generate_app_build()
app_inspect.run_app_inspect_checks()
