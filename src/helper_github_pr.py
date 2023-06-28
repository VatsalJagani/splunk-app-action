
import os
import subprocess
import hashlib
import helper_github_action as utils


def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class GitHubPR:
    def __init__(self, repo_dir) -> None:
        self.REPO_DIR = repo_dir
        self.default_branch_name = self._get_default_branch()
        utils.info("default_branch_name: {}".format(self.default_branch_name))


    def _get_default_branch(self):
        _default_branch_name_input = utils.get_input('default_branch_name')
        if _default_branch_name_input and _default_branch_name_input!="NONE":
            return _default_branch_name_input

        output = subprocess.check_output(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'])
        branch_name = output.decode('utf-8').strip().split('/')[-1]
        return branch_name


    def check_branch_does_not_exist(self, branch_name):
        # https://stackoverflow.com/questions/5167957/is-there-a-better-way-to-find-out-if-a-local-git-branch-exists
        os.system('git fetch')
        utils.info("Checking whether git branch already present or not.")
        # ret_code = os.system('git rev-parse --verify {}'.format(branch_name))
        ret_code = os.system('git checkout {}'.format(branch_name))
        if ret_code == 0:
            return False
        return True


    def _configure_git(self):
        if not os.environ.get("GITHUB_TOKEN"):
            raise ValueError("Please configure the GitHub Token in MY_GITHUB_TOKEN environment secret for actions in the Repo Settings.")

        os.system(r'gh auth setup-git')
        os.system(r'git config user.name splunk_app_action')
        os.system(r'git config user.email splunkappaction@gmail.com')
        # TODO - Create this GitHub account


    def _commit(self, new_branch):
        utils.info("Committing the code.")
        # checkout default branch
        os.system(r'git checkout {}'.format(self.default_branch_name))

        # Create a new branch
        os.system(r'git checkout -b {} {}'.format(new_branch, self.default_branch_name))

        # Add app changes
        os.system(r'git add -A')

        # Commit changes
        os.system(r'git commit -m "{}"'.format(new_branch))


    def _pr(self, new_branch):
        utils.info("Pushing the code and creating PR.")
        # Push branch on github
        return_value = os.system(r'git push -u origin {}'.format(new_branch))
        if return_value !=0:
            utils.error("Unable to push changes into the branch={}".format(new_branch))
            return

        # Create PR
        os.system(r'gh pr create --base {} --head {} --fill'.format(self.default_branch_name, new_branch))


    def commit_and_pr(self, file_to_generate_hash, local_test=False):
        _hash = get_file_hash(file_to_generate_hash)
        new_branch = 'splunk_app_action_{}'.format(_hash)
        utils.info("Branch Name: {}".format(new_branch))
        os.chdir(self.REPO_DIR)
        if local_test or self.check_branch_does_not_exist(new_branch):
            is_any_update = self.add_utility()
            if not local_test:
                if is_any_update:
                    self._configure_git()
                    self._commit(new_branch)
                    self._pr(new_branch)
                else:
                    utils.info("No changes.")
            else:
                utils.info("Local test, ignoring git commit and PR.")
        else:
            utils.info("Branch already present.")
