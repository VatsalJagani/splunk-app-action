import os
import unittest
from unittest.mock import patch
from utilities.base_utility import BaseUtility

# # Mock the git_manager related function get_file_hash
# patcher_get_file_hash = patch("src.helpers.git_manager.get_file_hash")
# mock_get_file_hash = patcher_get_file_hash.start()

# def mock_get_file_hash_fn(file_path):
#     print(f"Mocked helpers.git_manager.get_file_hash called. file_path={file_path}")
#     return "hash"
# mock_get_file_hash.side_effect = mock_get_file_hash_fn


class TestBaseUtility(unittest.TestCase):

    def setUp(self):
        self.app_read_dir = os.path.join(os.path.dirname(__file__), 'test_app_repos')
        self.app_write_dir = os.path.join(os.path.dirname(__file__), 'test_app_repos')
        self.base_utility = BaseUtility(self.app_read_dir, self.app_write_dir)

    @patch('helpers.git_manager.GitHubPR')
    def test_add_no_change(self, mock_github_pr):
        with patch.object(self.base_utility, 'implement_utility', return_value=None):
            self.base_utility.add()
            mock_github_pr.assert_not_called()

    # @patch('os.path.isfile', return_value=True)
    @patch('helpers.git_manager.GitHubPR')
    def test_add_single_file_changed(self, mock_github_pr):
        # print(mock_get_file_hash())
        file_path = os.path.join(os.path.dirname(__file__), "dummy_utility_files", "abc.txt")
        with patch.object(self.base_utility, 'implement_utility', return_value=file_path):
            self.base_utility.add()
            # mock_get_file_hash.assert_called_once_with('/path/to/updated_file.txt')
            mock_github_pr.commit_and_pr.assert_called_once_with(hash='900150983cd24fb0d6963f7d28e17f72')

    # @patch('helpers.git_manager.get_folder_hash', return_value='hash')
    # @patch('helpers.git_manager.GitHubPR')
    # def test_add_folder_changed(self, mock_github_pr, mock_get_folder_hash):
    #     with patch.object(self.base_utility, 'implement_utility', return_value='/path/to/updated_folder'):
    #         self.base_utility.add()
    #         mock_github_pr.commit_and_pr.assert_called_once_with(hash='hash')

    # @patch('helpers.git_manager.get_multi_files_hash', return_value='hash')
    # @patch('helpers.git_manager.GitHubPR')
    # def test_add_multi_files_changed(self, mock_github_pr, mock_get_multi_files_hash):
    #     with patch.object(self.base_utility, 'implement_utility', return_value=['/path/to/updated_file1.txt', '/path/to/updated_file2.txt']):
    #         self.base_utility.add()
    #         mock_github_pr.commit_and_pr.assert_called_once_with(hash='hash')

    # @patch('helpers.git_manager.GitHubPR')
    # def test_add_invalid_file(self, mock_github_pr):
    #     with patch.object(self.base_utility, 'implement_utility', return_value='/path/to/invalid_file'):
    #         with self.assertRaises(Exception):
    #             self.base_utility.add()

    # def test_implement_utility_not_implemented(self):
    #     with self.assertRaises(NotImplementedError):
    #         self.base_utility.implement_utility()
