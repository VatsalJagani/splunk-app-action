
# Contributing to splunk-app-action (Python GitHub Action)

Thank you for considering contributing! This repository is for a Python-based custom GitHub Action. Please read below for guidelines specific to GitHub Actions.


## Bug reports and feature requests

### Did you find a bug?

First, search [issues](https://github.com/VatsalJagani/splunk-app-action/issues) to see if your bug is already reported.
If not, open a new issue and include:
- The workflow YAML that uses this action
- The expected and actual behavior
- Logs from the GitHub Actions run (from the Actions tab)
- Any relevant code snippets or configuration


### Suggesting a feature

Open a feature request issue and describe:
- The new action feature or workflow integration you want
- Why it’s useful for GitHub Actions users
- Example workflow YAML or usage


## Making a pull request

When contributing code:
- Fork and clone the repository
- Create a new branch for your changes
- Make sure your code follows best practices for GitHub Actions (inputs, outputs, secrets, error handling)
- Add or update tests (unit tests and workflow examples)
- Document any new inputs/outputs or usage changes
- Test your action in a workflow run (see `.github/workflows/test.yml`)

    git remote add upstream https://github.com/VatsalJagani/splunk-app-action.git

    Now if you do `git remote -v` again, you'll see

    origin https://github.com/USERNAME/splunk-app-action.git (fetch)
    origin https://github.com/USERNAME/splunk-app-action.git (push)
    upstream https://github.com/VatsalJagani/splunk-app-action.git (fetch)
    upstream https://github.com/VatsalJagani/splunk-app-action.git (push)



**See `development.md` for more details on local development and testing for GitHub Actions.**

2. **Ensure your fork is up-to-date**

    <details><summary>Expand details 👇</summary><br/>

    Once you've added an "upstream" remote pointing to [https://github.com/VatsalJagani/splunk-app-action.git](https://github.com/VatsalJagani/splunk-app-action), keeping your fork up-to-date is easy:

        git checkout main  # if not already on main
        git pull --rebase upstream main
        git push

    </details>

3. **Create a new branch to work on your fix or enhancement**

    <details><summary>Expand details 👇</summary><br/>

    Committing directly to the main branch of your fork is not recommended. It will be easier to keep your fork clean if you work on a separate branch for each contribution you intend to make.

    You can create a new branch with

        # replace BRANCH with whatever name you want to give it
        git checkout -b BRANCH
        git push -u origin BRANCH

    </details>

4. **Test your changes**

**Then Read the `development.md` file on GitHub for this project for development guidelines.**


### Writing docstrings

We use [Sphinx](https://www.sphinx-doc.org/en/master/index.html) to build our API docs, which automatically parses all docstrings
of public classes and methods using the [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) extension.
Please refer to autoc's documentation to learn about the docstring syntax.
