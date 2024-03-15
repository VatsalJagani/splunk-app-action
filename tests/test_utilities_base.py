import os
import unittest
from unittest.mock import patch
from .helper import stdout_capture

from utilities.base_utility import BaseUtility



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

    @patch('helpers.git_manager.GitHubPR')
    def test_add_single_file_changed(self, mock_github_pr):
        file_path = os.path.join(os.path.dirname(__file__), "dummy_utility_files", "abc.txt")
        with patch.object(self.base_utility, 'implement_utility', return_value=file_path):
            with stdout_capture() as stdout:
                self.base_utility.add()
                output = stdout.getvalue()
                assert "Committing and creating PR for the code change." in output

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
