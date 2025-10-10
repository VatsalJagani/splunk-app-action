## Releasing a new Version / Publishing new Package

1. Update the version in `github_action_toolkit/version.py`.

2. Update dependencies, run checks and tests and create build.
    * `make`
    * `make build`

3. Run the release script:

    ```bash
    make create-release
    ```

    This will commit the changes to the CHANGELOG and `version.py` files and then create a new tag in git
    which will trigger a workflow on GitHub Actions that handles the rest.


### What does `release.yml` GitHub Workflow Do Automatically:

* It generates Release Notes from Change Log.
* It publishes a GitHub release on the Repo.
* It publishes a release on Pypi.


### Fixing a failed release

If for some reason the GitHub Actions release workflow failed with an error that needs to be fixed, you'll have to delete both the tag and corresponding release from GitHub. After you've pushed a fix, delete the tag from your local clone with

```bash
git tag -l | xargs git tag -d && git fetch -t
```

Then repeat the steps above.


### Pypi Authentication (**Authorize** your repository to publish to PyPI)

* Go to [the publishing settings page](https://pypi.org/manage/account/publishing/).

* Find "Trusted Publisher Management" and register your GitHub repo as a new
     "pending" trusted publisher

* Enter the project name, repo owner, repo name, and `release.yml` as the workflow
     name. (You can leave the "environment name" field blank.)


## readthedocs Doc Publish Setup (First Time Only)

(Optional) If you want to deploy your API docs to [readthedocs.org](https://readthedocs.org), go to the [readthedocs dashboard](https://readthedocs.org/dashboard/import/?) and import your new project.

    Then click on the "Admin" button, navigate to "Automation Rules" in the sidebar, click "Add Rule", and then enter the following fields:

    - **Description:** Publish new versions from tags
    - **Match:** Custom Match
    - **Custom match:** v[vV]
    - **Version:** Tag
    - **Action:** Activate version

    Then hit "Save".

    *After your first release, the docs will automatically be published to [your-project-name.readthedocs.io](https://your-project-name.readthedocs.io/).*
