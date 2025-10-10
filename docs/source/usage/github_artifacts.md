Github Artifact related Functions
================

### **`GitHubArtifacts(github_token=None, github_repo=None)` Class**

Initializes the necessary functions and pre-requisites for artifacts related operations.

Both parameters are optional but environment variables for it needs to be present GITHUB_TOKEN and GITHUB_REPOSITORY respectively.

**example:**

```python
>> from github_action_toolkit import GitHubArtifacts
>> artifacts = GitHubArtifacts()
```

### **`GitHubArtifacts.get_artifacts(current_run_only=False)`**

Returns a list of GitHub Actions artifacts for the current repository.

`current_run_only` (optional): If True, only returns artifacts from the current workflow run (GITHUB_RUN_ID must be set in env).

**example:**

```python
>> artifacts = artifacts.get_artifacts(current_run_only=True)
>> for artifact in artifacts:
>>     print(artifact.name)

# Output:
# running-tests
# publish-release
```

### **`GitHubArtifacts.get_artifact(artifact_id)`**

Fetches a specific artifact by its ID.

**example:**

```python
>> artifact = artifacts.get_artifact(artifact_id=123456)
>> print(artifact.name)

# Output
# running-tests
```

### **`GitHubArtifacts.download_artifact(artifact, is_extract=False, extract_dir=None)`**

Downloads a given artifact as a zip file. Optionally extracts it and returns the folder path.

* `artifact`: The artifact object (from get_artifacts() or get_artifact()).
* `is_extract` (optional): If True, extracts the contents of the zip.
* `extract_dir` (optional): Directory to extract to. Defaults to artifact_<artifact.name>.

**example:**

```python
>> file_path = artifacts.download_artifact(artifact)

# Output:
# Artifact 'running-tests' downloaded successfully.
```

Extracting it:

```python
>> folder = artifacts.download_artifact(artifact, is_extract=True)

# Output:
# Artifact 'running-tests' downloaded successfully.
# Folder 'artifact_running-tests' created with extracted contents.
```

### **`GitHubArtifacts.delete_artifact(artifact)`**

Deletes the given artifact from the repository.

* `artifact`: The artifact object to delete.

Returns True if deleted successfully, otherwise False.

**example:**

```python
>> result = artifacts.delete_artifact(artifact)

# Output:
# Artifact 123456 (test-logs) deleted successfully.
```
