
import os
import re
import subprocess
import hashlib
import helper_github_action as utils


def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_folder_hash(folder_path): 
    hash_md5 = hashlib.md5() 
    for root, dirs, files in os.walk(folder_path): 
        for file in files: 
            file_path = os.path.join(root, file) 
            file_hash = get_file_hash(file_path) 
            hash_md5.update(file_hash.encode('utf-8')) 
    return hash_md5.hexdigest()


def get_multi_files_hash(file_paths):
    hash_md5 = hashlib.md5()
    for file_path in file_paths:
        file_hash = get_file_hash(file_path)
        hash_md5.update(file_hash.encode('utf-8'))
    return hash_md5.hexdigest()



class GitHubPR:
    DEFAULT_BRANCH_NAME = None
    IS_GIT_CONFIGURED = False

    def __init__(self) -> None:
        os.chdir(utils.CommonDirPaths.REPO_DIR)

        GitHubPR.configure_git()
        GitHubPR.set_default_branch()


    def __enter__(self):
        # checkout default branch
        os.system(r'git checkout {}'.format(self.DEFAULT_BRANCH_NAME))
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        # checkout default branch
        os.system(r'git checkout {}'.format(self.DEFAULT_BRANCH_NAME))

        os.chdir(utils.CommonDirPaths.MAIN_DIR)


    @staticmethod
    def set_default_branch():
        utils.info("Finding default branch for the repo.")
        if GitHubPR.DEFAULT_BRANCH_NAME:
            return

        os.system(r"git remote show origin | sed -n '/HEAD branch/s/.*: //p'")

        _default_branch_name_input = utils.get_input('default_branch_name')
        if _default_branch_name_input and _default_branch_name_input!="NONE":
            GitHubPR.DEFAULT_BRANCH_NAME = _default_branch_name_input
        else:
            output = subprocess.check_output(['git', 'remote', 'show', 'origin'])
            utils.info("output of git remote show origin: {}".format(output))
            match = re.search(r"HEAD branch:\s*([^\n]+)", output.decode('utf-8'))
            utils.info(f"branch found: {match.group(1)}")
            GitHubPR.DEFAULT_BRANCH_NAME = match.group(1)

        utils.info("default_branch_name: {}".format(GitHubPR.DEFAULT_BRANCH_NAME))


    @staticmethod
    def configure_git():
        utils.info("Configuring git username & credentials.")
        if GitHubPR.IS_GIT_CONFIGURED:
            return

        if not os.environ.get("GITHUB_TOKEN"):
            raise ValueError("Please configure the GitHub Token in MY_GITHUB_TOKEN environment secret for actions in the Repo Settings.")

        os.system(r'gh auth setup-git')
        os.system(r'git config user.name splunk_app_action')
        os.system(r'git config user.email splunkappaction@gmail.com')

        GitHubPR.IS_GIT_CONFIGURED = True

        # TODO - Create this GitHub account specific for github action


    def _check_branch_does_not_exist(self, branch_name):
        # https://stackoverflow.com/questions/5167957/is-there-a-better-way-to-find-out-if-a-local-git-branch-exists
        os.system('git fetch')
        utils.info("Checking whether git branch already present or not.")
        # ret_code = os.system('git rev-parse --verify {}'.format(branch_name))
        ret_code = os.system('git checkout {}'.format(branch_name))
        if ret_code == 0:
            return False
        return True


    def _commit(self, new_branch):
        utils.info("Committing the code.")
        os.system(r'git checkout -b {} {}'.format(new_branch, self.DEFAULT_BRANCH_NAME))   # Create a new branch
        os.system(r'git add -A')   # Add app changes
        os.system(r'git commit -m "{}"'.format(new_branch))   # Commit changes


    def _pr(self, new_branch):
        utils.info("Pushing the code and creating PR.")

        return_value = os.system(r'git push -u origin {}'.format(new_branch))
        if return_value !=0:
            utils.error("Unable to push changes into the branch={}".format(new_branch))
            return

        os.system(r'gh pr create --base {} --head {} --fill'.format(self.DEFAULT_BRANCH_NAME, new_branch))   # Create PR


    def commit_and_pr(self, file_to_generate_hash):
        _hash = get_file_hash(file_to_generate_hash)
        new_branch = 'splunk_app_action_{}'.format(_hash)
        utils.info("Branch Name: {}".format(new_branch))

        if self._check_branch_does_not_exist(new_branch):
            self._commit(new_branch)
            self._pr(new_branch)
        else:
            utils.info("Branch already present.")
