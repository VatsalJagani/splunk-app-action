import os
import zipfile

import requests
from github import Github as PyGithub
from github.Artifact import Artifact
from github.PaginatedList import PaginatedList
from github.Repository import Repository


class GitHubArtifacts:
    token: str
    action_run_id: str

    def __init__(
        self,
        github_token: str | None = None,
        github_repo: str | None = None,
    ) -> None:
        """
        GitHubArtifacts
        :param github_token: GitHub token with repo access (optional, defaults to env variable)
        """

        _token = github_token or os.environ.get("GITHUB_TOKEN")
        if not _token:
            raise ValueError("GitHub token not provided and GITHUB_TOKEN not set in environment.")
        self.token = _token

        if github_repo:
            if "/" not in github_repo:
                raise ValueError("github_repo must be in 'owner/repo' format")
        elif os.environ.get("GITHUB_REPOSITORY"):
            github_repo = os.environ.get("GITHUB_REPOSITORY")
        if not github_repo:
            raise ValueError(
                "GitHub repository not provided and GITHUB_REPOSITORY not set in environment."
            )

        _a_run_id: str | None = os.environ.get("GITHUB_RUN_ID")
        if _a_run_id:
            self.action_run_id = _a_run_id
        else:
            raise RuntimeError("GITHUB_RUN_ID not set")

        gh = PyGithub(login_or_token=self.token)
        self.repo: Repository = gh.get_repo(full_name_or_id=github_repo)

    def get_artifacts(
        self, current_run_only: bool = False
    ) -> PaginatedList[Artifact] | list[Artifact]:
        all_artifacts = self.repo.get_artifacts()
        if current_run_only:
            return [a for a in all_artifacts if a.workflow_run.id == int(self.action_run_id)]
        return all_artifacts

    def get_artifact(self, artifact_id: int) -> Artifact:
        return self.repo.get_artifact(artifact_id=artifact_id)

    def download_artifact(
        self, artifact: Artifact, is_extract: bool = False, extract_dir: str | None = None
    ):
        response = requests.get(
            artifact.archive_download_url, headers={"Authorization": f"token {self.token}"}
        )
        file_name = f"{artifact.name}.zip"
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(response.content)
            print(f"Artifact '{artifact.name}' downloaded successfully.")
        else:
            print(f"Failed to download artifact: {response.status_code}")

        if is_extract:
            dir_path: str = extract_dir or f"artifact_{artifact.name}"
            with zipfile.ZipFile(file_name, "r") as z:
                z.extractall(dir_path)
            os.remove(file_name)
            return dir_path
        return file_name

    def delete_artifact(self, artifact: Artifact) -> bool:
        headers: dict[str, str] = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }
        url = f"https://api.github.com/repos/{self.repo.full_name}/actions/artifacts/{artifact.id}"
        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print(f"Artifact {artifact.id} ({artifact.name}) deleted successfully.")
            return True
        else:
            print(
                f"Failed to delete artifact {artifact.id} ({artifact.name}): {response.status_code}"
            )
            return False
