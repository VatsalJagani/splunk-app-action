import os
import pytest
import subprocess

from .helper import get_temp_git_repo, stdout_capture

from helpers.git_manager import get_file_hash, get_folder_hash, get_multi_files_hash, GitHubPR


# Use a fixture to create temporary files with known content for testing
@pytest.fixture
def sample_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("This is a test file")
    return file_path


def test_get_file_hash_nonexistent_file():
    file_path = "path/to/nonexistent_file"
    with pytest.raises(FileNotFoundError):
        get_file_hash(file_path)

def test_get_file_hash_with_tmp_file(sample_file):
    expected_hash = "0b26e313ed4a7ca6904b0e9369e5b957"  # MD5 hash of "This is a test file"
    assert get_file_hash(sample_file) == expected_hash

def test_get_folder_hash_empty_folder():
    folder_path = "empty_folder"
    os.makedirs(folder_path)
    expected_hash = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 hash of an empty string
    assert get_folder_hash(folder_path) == expected_hash
    os.rmdir(folder_path)

def test_get_folder_hash_with_files(sample_file):
    folder_path = sample_file.parent
    expected_hash = "894c0cee919eb49f7a36060c7a607fb7"  # Hash of the single file in the folder
    assert get_folder_hash(folder_path) == expected_hash

def test_get_folder_hash_nonexistent_folder():
    folder_path = "path/to/nonexistent_folder"
    with pytest.raises(Exception, match="Incorrect folder_path provided."):
        abc = get_folder_hash(folder_path)
        print(f"abc={abc}")

def test_get_multi_files_hash_empty_list():
    file_paths = []
    expected_hash = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 hash of an empty string
    assert get_multi_files_hash(file_paths) == expected_hash

def test_get_multi_files_hash_multiple_files(sample_file):
    file_paths = [sample_file, sample_file]  # Use the same file twice for simplicity
    expected_hash = "91405dbee0a9c47e7bc657bda7cb29a9"  # Hypothetical hash of the combined hashes
    assert get_multi_files_hash(file_paths) == expected_hash


def test_commit_and_pr_new_branch():
    with get_temp_git_repo() as repo_path:
        with GitHubPR(repo_dir=repo_path) as github_pr:

            # write test-file
            with open('test_file.txt', 'w') as f:
                f.write('This is test file')

            # Call the commit_and_pr method
            github_pr.commit_and_pr('my_hash')

            # Check that a new branch was created but no pull request was created
            output = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True)
            assert 'splunk_app_action_my_hash' in output.stdout.strip()

            output = subprocess.run(['git', 'log', '--oneline', '--grep', 'splunk_app_action_my_hash'], 
                                    capture_output=True, text=True)
            assert 'splunk_app_action_my_hash' in output.stdout.strip()


def test_commit_and_pr_new_branch_no_change():
    with get_temp_git_repo() as repo_path:
        with GitHubPR(repo_dir=repo_path) as github_pr:

            with stdout_capture() as captured_stdout:
                # calling without any file change
                github_pr.commit_and_pr('my_hash')

                # Get the captured output
                output = captured_stdout.getvalue()
                assert 'CMD=git commit -m "splunk_app_action_my_hash", ReturnCode=1' in output.strip()

            # Check that a new branch was created but no pull request was created
            output = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True)
            assert 'splunk_app_action_my_hash' in output.stdout.strip()

            output = subprocess.run(['git', 'log', '--oneline', '--grep', 'splunk_app_action_my_hash'], 
                                    capture_output=True, text=True)
            assert output.stdout.strip() == ""


def test_commit_and_pr_existing_branch():
    with get_temp_git_repo() as repo_path:
        with GitHubPR(repo_dir=repo_path) as github_pr:
            # Create a branch with the same name as the one we will try to create
            subprocess.run(['git', 'checkout', '-b', 'splunk_app_action_my_hash'], check=True)

            with stdout_capture() as captured_stdout:
                # calling without any file change
                github_pr.commit_and_pr('my_hash')

                # Get the captured output
                output = captured_stdout.getvalue()
                assert "Branch already present." in output.strip() or \
                    "a branch named 'splunk_app_action_my_hash' already exists" in output.strip()
