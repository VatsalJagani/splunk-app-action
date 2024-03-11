
import os
import re
import hashlib
import helpers.github_action_utils as utils
from helpers.global_variables import GlobalVariables


def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_folder_hash(folder_path):
    hash_md5 = hashlib.md5()
    if not os.path.isdir(folder_path):
        raise Exception("Incorrect folder_path provided.")
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
    CURRENT_BRANCH_NAME = None
    IS_GIT_CONFIGURED = False

    def __init__(self, repo_dir, is_test=False) -> None:
        self.is_test = is_test

        os.chdir(repo_dir)

        GitHubPR.configure_git(is_test)
        GitHubPR.set_current_branch(is_test)


    def _reset_the_git_repo(self):
        utils.execute_system_command("git fetch")
        utils.execute_system_command(
            f"git checkout {self.CURRENT_BRANCH_NAME}")
        utils.execute_system_command(
            f"git reset --hard origin/{self.CURRENT_BRANCH_NAME}")
        utils.execute_system_command("git clean -df")
        utils.execute_system_command("git pull")


    def __enter__(self):
        if self.is_test:
            return self

        self._reset_the_git_repo()
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_test:
            return

        os.chdir(GlobalVariables.ROOT_DIR_PATH)


    @staticmethod
    def set_current_branch(is_test):
        if is_test:
            return

        if GitHubPR.CURRENT_BRANCH_NAME:
            return

        utils.info("Finding current branch for the repo on which GitHub action is being executed.")

        _current_branch_name_input = utils.get_input('current_branch_name')
        if _current_branch_name_input and _current_branch_name_input != "NONE":
            GitHubPR.CURRENT_BRANCH_NAME = _current_branch_name_input
        else:
            ret_code, output = utils.execute_system_command(
                "git remote show origin")
            match = re.search(
                r"HEAD branch:\s*([^\n]+)", output)
            utils.info(f"branch found: {match.group(1)}")
            GitHubPR.CURRENT_BRANCH_NAME = match.group(1)

        utils.info("current_branch_name: {}".format(
            GitHubPR.CURRENT_BRANCH_NAME))


    @staticmethod
    def configure_git(is_test):
        if is_test:
            return

        if GitHubPR.IS_GIT_CONFIGURED:
            return

        utils.info("Configuring git username & credentials.")
        if not os.environ.get("GITHUB_TOKEN"):
            raise ValueError(
                "Please configure the GitHub Token in MY_GITHUB_TOKEN environment secret for actions in the Repo Settings.")

        utils.execute_system_command(r'gh auth setup-git')
        utils.execute_system_command(r'git config user.name SplunkAppAction')
        utils.execute_system_command(
            r'git config user.email splunkappaction@gmail.com')

        GitHubPR.IS_GIT_CONFIGURED = True


    def _check_branch_exist(self, branch_name):
        utils.info("Checking whether git branch already present or not.")
        utils.execute_system_command('git fetch')
        ret_code, output = utils.execute_system_command(
            f"git show-ref --verify refs/remotes/origin/{branch_name}")   # Use --quiet to avoid output
        return ret_code == 0


    def _commit(self, new_branch):
        utils.info("Committing the code.")
        utils.execute_system_command(r'git checkout -b {} {}'.format(
            new_branch, self.CURRENT_BRANCH_NAME))   # Create a new branch
        utils.execute_system_command(r'git add -A')   # Add app changes
        utils.execute_system_command(
            r'git commit -m "{}"'.format(new_branch))   # Commit changes


    def _pr(self, new_branch):
        utils.info("Pushing the code and creating PR.")

        return_value, output = utils.execute_system_command(
            r'git push -u origin {}'.format(new_branch))
        if return_value != 0:
            utils.error(
                "Unable to push changes into the branch={}".format(new_branch))
            return

        utils.execute_system_command(r'gh pr create --base {} --head {} --fill'.format(
            self.CURRENT_BRANCH_NAME, new_branch))   # Create PR


    def commit_and_pr(self, hash):
        if self.is_test:
            return

        new_branch = 'splunk_app_action_{}'.format(hash)
        utils.info("Branch Name: {}".format(new_branch))

        if not self._check_branch_exist(new_branch):
            try:
                self._commit(new_branch)
                self._pr(new_branch)
            except Exception as e:
                utils.warning(
                    f"Fail to push the code for utility, this could be due to that the PR is already open for it. {e}")
        else:
            utils.info("Branch already present.")
