# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportFunctionMemberAccess=false
# pyright: reportUnannotatedClassAttribute=false

import os
import sys

# path to be added -> src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))


from unittest.mock import patch


# Mock the set_env function during the test
def mock_set_env(name, value):
    print(f"Mocked set_env called with args: name={name}, value={value}")
    os.environ[name] = value


patcher_set_env = patch("github_action_toolkit.set_env", side_effect=mock_set_env)
mock_set_env_patcher = patcher_set_env.start()


mock_set_env.side_effect = mock_set_env


# Mock the App Inspect API related function _api_login
patcher_app_inspect_login = patch("app_inspect.SplunkAppInspect._api_login")
mock_app_inspect_login = patcher_app_inspect_login.start()


def mock_app_inspect_login_fn():
    print("Mocked app_inspect.SplunkAppInspect._app_inspect_login called.")


mock_app_inspect_login.side_effect = mock_app_inspect_login_fn
