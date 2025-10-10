# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false

import os
import tempfile
import zipfile
from unittest import mock

import pytest

from github_action_toolkit.github_artifacts import GitHubArtifacts


@pytest.fixture
def mock_repo():
    """Mocks github.Repository.Repository object and Github instance."""
    with mock.patch("github_action_toolkit.github_artifacts.PyGithub") as mock_github:
        mock_repo = mock.Mock()
        mock_github.return_value.get_repo.return_value = mock_repo
        yield mock_repo


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_RUN_ID", "123456")


def test_init_with_env(mock_repo, mock_env):
    gh_artifact = GitHubArtifacts()
    assert gh_artifact.token == "fake-token"
    assert gh_artifact.repo == mock_repo
    assert gh_artifact.action_run_id == "123456"


def test_get_artifacts_all(mock_repo, mock_env):
    mock_artifact_1 = mock.Mock()
    mock_artifact_1.workflow_run.id = 123456
    mock_artifact_2 = mock.Mock()
    mock_artifact_2.workflow_run.id = 654321

    mock_repo.get_artifacts.return_value = [mock_artifact_1, mock_artifact_2]

    gh_artifact = GitHubArtifacts()
    artifacts = list(gh_artifact.get_artifacts())
    assert len(artifacts) == 2


def test_get_artifacts_filtered(mock_repo, mock_env):
    mock_artifact = mock.Mock()
    mock_artifact.workflow_run.id = 123456
    mock_repo.get_artifacts.return_value = [mock_artifact]

    gh_artifact = GitHubArtifacts()
    artifacts = list(gh_artifact.get_artifacts(current_run_only=True))
    assert len(artifacts) == 1
    assert artifacts[0].workflow_run.id == 123456


def test_get_artifact(mock_repo, mock_env):
    mock_artifact = mock.Mock()
    mock_repo.get_artifact.return_value = mock_artifact

    gh_artifact = GitHubArtifacts()
    artifact = gh_artifact.get_artifact(artifact_id=1)
    assert artifact == mock_artifact
    mock_repo.get_artifact.assert_called_once_with(artifact_id=1)


@mock.patch("github_action_toolkit.github_artifacts.requests.get")
def test_download_artifact(mock_get, mock_repo, mock_env):
    mock_artifact = mock.Mock()
    mock_artifact.name = "myartifact"
    mock_artifact.archive_download_url = "https://fake-url.com/download"

    # Create fake zip content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as f:
        with zipfile.ZipFile(f, mode="w") as z:
            z.writestr("dummy.txt", "dummy content")
        f.seek(0)
        content = f.read()

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.content = content
    mock_get.return_value = mock_response

    gh_artifact = GitHubArtifacts()
    file_path = gh_artifact.download_artifact(artifact=mock_artifact)

    assert os.path.exists(file_path)
    assert file_path.endswith(".zip")
    os.remove(file_path)  # clean up


@mock.patch("github_action_toolkit.github_artifacts.requests.get")
def test_download_and_extract_artifact(mock_get, mock_repo, mock_env):
    mock_artifact = mock.Mock()
    mock_artifact.name = "extractable"
    mock_artifact.archive_download_url = "https://fake-url.com/download"

    # Create zip with a test file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        with zipfile.ZipFile(tmp_zip, mode="w") as zf:
            zf.writestr("hello.txt", "Hello World")
        tmp_zip_path = tmp_zip.name

    with open(tmp_zip_path, "rb") as f:
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = f.read()
    mock_get.return_value = mock_response

    gh_artifact = GitHubArtifacts()
    extract_dir = tempfile.mkdtemp()

    extracted_path = gh_artifact.download_artifact(
        artifact=mock_artifact,
        is_extract=True,
        extract_dir=extract_dir,
    )

    assert os.path.isdir(extracted_path)
    assert "hello.txt" in os.listdir(extracted_path)

    os.remove(tmp_zip_path)


@mock.patch("github_action_toolkit.github_artifacts.requests.delete")
def test_delete_artifact_success(mock_delete, mock_repo, mock_env):
    mock_response = mock.Mock()
    mock_response.status_code = 204
    mock_delete.return_value = mock_response

    mock_artifact = mock.Mock()
    mock_artifact.id = 123
    mock_artifact.name = "artifact"

    gh_artifact = GitHubArtifacts()
    result = gh_artifact.delete_artifact(mock_artifact)

    assert result is True
    mock_delete.assert_called_once()


@mock.patch("github_action_toolkit.github_artifacts.requests.delete")
def test_delete_artifact_failure(mock_delete, mock_repo, mock_env):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_delete.return_value = mock_response

    mock_artifact = mock.Mock()
    mock_artifact.id = 456
    mock_artifact.name = "bad_artifact"

    gh_artifact = GitHubArtifacts()
    result = gh_artifact.delete_artifact(mock_artifact)

    assert result is False
    mock_delete.assert_called_once()
