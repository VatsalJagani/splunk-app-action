## Creating a new minor Tag

1. Update the version in `src/version.py`.

2. Update dependencies, run checks and tests.
    * `make`

3. Prepare changelog.

    ```bash
    python devtools/prepare_changelog.py
    ```

4. Run the release script:

    ```bash
    make create-tag
    ```

    This will commit the changes and then create a new tag in git.

5. Move the floating major tag (e.g. `v6`) to point to the new patch release.

    ```bash
    git tag -f "vX" -m "vX"
    git push origin -f "vX"
    # Example - git tag -f "v6" -m "v6" && git push origin -f "v6"
    ```


## Publishing new Release or Updating the Release (to patch issues)

1. Update the version in `src/version.py`.

2. Update dependencies, run checks and tests.
    * `make`

3. Prepare changelog.

    ```bash
    python devtools/prepare_changelog.py
    ```

    * Change tag number in CHANGELOG.md from v6.0.0 to v6

4. Commit the changes.

5. Creating the new vX tag.

    ```bash
    git tag "<tag-here>" -m "<tag-here>"
    # Example - git tag "v6" -m "v6"
    ```

6. Push the Changes.

    ```bash
    git push
    git push --tags
    ```

7. Workflow Run (This will be executed automatically given that the tag is in vX format.)
    * It generates Release Notes from Change Log.
    * It publishes a GitHub release on the Repo.


### Fixing a failed release

If for some reason the GitHub Actions release workflow failed with an error that needs to be fixed, you'll have to delete both the tag and corresponding release from GitHub. After you've pushed a fix, delete the tag from your local clone with

```bash
git tag -l | xargs git tag -d && git fetch -t
```

Then repeat the steps above.


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
