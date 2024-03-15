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

    @patch('helpers.git_manager.GitHubPR')
    def test_add_folder_changed(self, mock_github_pr):
        folder_path = os.path.join(os.path.dirname(__file__), "dummy_utility_files")
        with patch.object(self.base_utility, 'implement_utility', return_value=folder_path):
            with stdout_capture() as stdout:
                self.base_utility.add()
                output = stdout.getvalue()
                assert "Committing and creating PR for the code change." in output


    @patch('helpers.git_manager.GitHubPR')
    def test_add_multi_files_changed(self, mock_github_pr):
        file1 = os.path.join(os.path.dirname(__file__), "dummy_utility_files", "abc.txt")
        file2 = os.path.join(os.path.dirname(__file__), "dummy_utility_files", "xyz.txt")
        with patch.object(self.base_utility, 'implement_utility', return_value=[file1, file2]):
            with stdout_capture() as stdout:
                self.base_utility.add()
                output = stdout.getvalue()
                assert "Committing and creating PR for the code change." in output


    # @patch('helpers.git_manager.GitHubPR')
    # def test_add_invalid_file(self, mock_github_pr):
    #     with patch.object(self.base_utility, 'implement_utility', return_value='/path/to/invalid_file'):
    #         with self.assertRaises(Exception):
    #             self.base_utility.add()

    # def test_implement_utility_not_implemented(self):
    #     with self.assertRaises(NotImplementedError):
    #         self.base_utility.implement_utility()
