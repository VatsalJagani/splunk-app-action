import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)


from unittest.mock import patch


# Mock the set_env function during the test
patcher_set_env = patch("helpers.github_action_utils.set_env")
mock_set_env = patcher_set_env.start()

def mock_set_env(name, value):
    print(f"Mocked set_env called with args: name={name}, value={value}")
    os.environ[name] = value
mock_set_env.side_effect = mock_set_env


# Mock the _pr function from git_manager.GitHubPR during the test
patcher_github_pr = patch("helpers.git_manager.GitHubPR._pr")
mock_github_pr = patcher_github_pr.start()

def mock_github_pr_fn(new_branch):
    print(f"Mocked git_manager.GitHubPR._pr called with args: new_branch={new_branch}")
mock_github_pr.side_effect = mock_github_pr_fn


# Mock the _check_branch_exist function from git_manager.GitHubPR during the test
patcher_github_check_branch_exist = patch("helpers.git_manager.GitHubPR._check_branch_exist")
mock_github_check_branch_exist = patcher_github_check_branch_exist.start()

def mock_github_check_branch_exist_fn(branch_name):
    print(f"Mocked git_manager.GitHubPR._check_branch_exist called with args: new_branch={branch_name}")
    if str(branch_name).endswith("_exists"):
        return True
    return False
mock_github_check_branch_exist.side_effect = mock_github_check_branch_exist_fn


# Mock the _reset_the_git_repo function from git_manager.GitHubPR during the test
patcher_github_reset_the_git_repo = patch("helpers.git_manager.GitHubPR._reset_the_git_repo")
mock_github_reset_the_git_repo = patcher_github_reset_the_git_repo.start()

def mock_github_reset_the_git_repo_fn():
    print("Mocked git_manager.GitHubPR._reset_the_git_repo called.")
mock_github_reset_the_git_repo.side_effect = mock_github_reset_the_git_repo_fn



# Mock the App Inspect API related function _api_login
patcher_app_inspect_login = patch("app_inspect.SplunkAppInspect._api_login")
mock_app_inspect_login = patcher_app_inspect_login.start()

def mock_app_inspect_login_fn():
    print("Mocked app_inspect.SplunkAppInspect._app_inspect_login called.")
mock_app_inspect_login.side_effect = mock_app_inspect_login_fn
