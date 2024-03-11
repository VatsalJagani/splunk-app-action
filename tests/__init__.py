import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)


from unittest.mock import patch


# Mock the set_env function during the test
patcher = patch("helpers.github_action_utils.set_env")
mock_set_env = patcher.start()

def mock_set_env(name, value):
    print(f"Mocked set_env called with args: name={name}, value={value}")
    os.environ[name] = value
mock_set_env.side_effect = mock_set_env