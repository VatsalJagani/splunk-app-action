# splunk-app-action
Github Action to automatically generate Splunk App and Add-on builds, run app-inspect checks (with the App-Inspect/Splunkbase API) on commit/push etc on GitHub repo. It also performs Splunk cloud checks.


## Capabilities
* Generate Splunk App/Add-on Build artifact
  * The action automatically generates build artifact from github repo.
  * Change file and directory permissions to avoid app-inspect failures.

* Run command before building the App build.
  * This could be useful if you wish to remove some files that you don't want in the build, change permission of some files before running the rest of the app build or app-inspect check.
  * See `Running Commands Before Generating App Build` section for more information.

* Run App-Inspect (with API)
  * Run app-inspect with Splunkbase API
  * I've tried to use CLI version of the App-inspect check, I've also tried to use github action with CLI version from Splunk, but all fails as they are always way behind the Splunkbase API. Hence you end up failing the checks when you try to upload a new version of Splunkbase.
  * This is the automation of Splunkbase API or postman version of App-inspect checks.
  * Fails the GitHub workflow if there is failure or error in App-inspect check or Cloud checks.

* Performs Splunk Cloud checks and SSAI checks for Splunk Cloud

* Supports multiple Apps/Add-ons in single repository.



## Usage
You can easily use this action as part of your Splunk App repo GitHub workflow. Below example shows how to use it.
```
name: "pre-release"

on:
  push:
    branches:
      - 'master'

jobs:
  pre-release:
    name: "Pre Release"
    runs-on: "ubuntu-latest"
    
    steps:
      - uses: VatsalJagani/splunk-app-action@v1
        with:
          app_dir: "my_splunk_app"
          app_build_name: "app"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```

* This workflow action would runs on only `master` branch with below code, if you wish to change that you can change with below part of workflow file.
  ```
  push:
    branches:
      - 'master'
  ```

* In case if you wish to run the Github workflow action manually instead of automatically, use below code instead of `push` under `on` section.
  ```
  workflow_dispatch:
    inputs:
      comment:
        description: 'Add comment for manual workflow execution.'
        required: false
        default: 'Manual execution of Github workflow.'
  ```
  * You can also combine both manually and automatically in the GitHub workflow.

* Above is just the example of the Workflow action, you can change any-part as you like and you can also add steps before or after running the GitHub action splunk-app-action.
  * If you wish to access the app-build right in the workflow you can access it under the current working directory of workflow action. App build file name depends on your input's `app_build_name` value.

* Find more information on GitHub workflow [here](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions).


* Below code from the Workflow file executes the GitHub action to generate the build and run the app-inspect checks, and generates the app build artifacts and app-inspect reports.
  ```
      - uses: VatsalJagani/splunk-app-action@v1
        with:
          app_dir: "my_splunk_app"
          app_build_name: "app"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
  ```
  * The values under `with` are inputs to the GitHub action, please find the details about all the inputs below.

* How to use if I've multiple App in the same repository or App and Add-on in the same repository.
  * You can use the GitHub action multiple times in the same workflow file.
  ```
      - uses: VatsalJagani/splunk-app-action@v1
        with:
          app_dir: "my_splunk_app"
          app_build_name: "app"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}

      - uses: VatsalJagani/splunk-app-action@v1
        with:
          app_dir: "my_splunk_add-on"
          app_build_name: "ta"
          splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
          splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
  ```


### Inputs
1. **`app_dir`**
   - The directory to be used as root directory for the App or the Add-on.
   - Is Required: `false`
   - Default: `. (current directory)` -> Root directory of the GitHub repository itself as root of your App or Add-on.
     * If you are using default value `.` then our action automatically removes the `.github` and `.git` folder as that you don't want in the app build.
     * But if you wish to remove any other files check `Running Commands Before Generating App Build` section.

2. **`app_build_name`**
   - The build name which will be generated by the action.
   - For example if you provide value as `my_app` below files will be generated.
     * App build - `my_app.tgz` within `App-Build-my_app` GitHub artifact. (Which you can download your repository's action page on GitHub UI.)
     * App Inspect Report - Following app-inspect report files will be created under the GitHub artifact `App-Inspect-Reports-my_app.`
       * `my_app_app_inspect_check.html`
       * `my_app_cloud_inspect_check.html`
       * `my_app_ssai_inspect_check.html`
   - Is Required: `false`
   - Default: `app`

3. **`app_package_id`**
   - Splunk app folder name when installed in Splunk or the app package being extracted.
   - It is recommended to provide as part of app.conf's `[package]` stanza's `id` attribute.
   - Is Required: `false`
   - Default:
     * If you do not provide the parameter the one found in the app.conf will be used.
     * Do not provide the parameter is the id is present in the app.conf file as mismatching value will result in app-inspect failure on Splunkbase.
     * If the parameter is not provided and app.conf also does not have the id attribute then `app_build_name` will be used.

4. **`app_build_path`**
   - The previously generated App build file path.
   - If this parameter is provided then App building will be disabled, instead the action will take this file as input to run the app-inspect checks.
   - If this input parameter is provided then `app_dir`, and `app_package_id` will be ignore. The `app_build_name` will only be use to name the app_inspect report files.
   - Is Required: `false`
   - Default: None

5. **`is_app_inspect_check`**
   - Whether to perform App inspect checks, cloud checks and SSAI checks or not?
   - Is Required: `false`
   - Default: `true`
     * By default app-inspect checks will be performed, if you wish to disable it provide `false`.

6. **`splunkbase_username`**
    - Provide your Splunkbase account username to run the App-inspect API. (Do not use full email, use just the username.)
    - Best way to provide is to create GitHub secret and assign the secret here.
      * Example: create a GitHub repository secret `SPLUNKBASE_USERNAME` and use it like:
        * `splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}`
    - Is Required: `false`
      * Required if you want to perform app-inspect checks (Depending on the value of `is_app_inspect_check` input which is true by default.)
    - Default: `N/A`

7. **`splunkbase_password`**
    - Provide your Splunkbase account password to run the App-inspect API.
    - Do not use the hard-coded password on your GitHub workflow file unless your are the only one accessing the repository. Use GitHub secrets instead.
      * GitHub secrets are secure as that cannot be logged in the action anywhere.
      * Example: create a GitHub repository secret `SPLUNKBASE_PASSWORD` and use it like:
        * `splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}`
    - Is Required: `false`
      * Required if you want to perform app-inspect checks (Depending on the value of `is_app_inspect_check` input which is true by default.)
    - Default: `N/A`


### Outputs
* GitHub action pass or fail the GitHub workflow:
  * Fail:
    * if there is any error executing the workflow
    * if app-inspect check or any cloud checks for App/Add-on fails (Any error or failures)
  * Pass:
    * otherwise

* GitHub action generates artifacts:
  * App build
  * App inspect reports JSON files


### Running Commands Before Generating App Build
* If you wish to run the commands before generating the App build, set the environment variables `SPLUNK_APP_ACTION_<n>`.
```
  - uses: VatsalJagani/splunk-app-action@v1
    env:
      SPLUNK_APP_ACTION_1: "find my_app -type f -name *.sh -exec chmod +x '{}' \\;"
    with:
      app_dir: "my_app"
      app_build_name: "app"
      splunkbase_username: ${{ secrets.SPLUNKBASE_USERNAME }}
      splunkbase_password: ${{ secrets.SPLUNKBASE_PASSWORD }}
```
* Above use-case is very common as if your App/Add-on has shell scripts in bin directory and you want to make sure it has executable permission.
* Run the command in the context of your repo's root directory. (Assume current working directory is your repo's root directory.)
* Maximum 100 commands can be executed. So from `SPLUNK_APP_ACTION_1` to `SPLUNK_APP_ACTION_99`.
* The command will be executed in incremented order from `SPLUNK_APP_ACTION_1` to `SPLUNK_APP_ACTION_99`.



## Examples
* **Cyences App for Splunk**
  * Has App and Add-on in the same repo.
  * Uses user defined command execution before generating the Add-on build. (To give executable permissions to bash (`.sh`) files in the Add-on automatically.)
  ![](images/cyences_workflow_3.png)
  * Executes workflow action whenever a new pull request is created. It also runs on any changes to `master` branch.
  ![](images/cyences_workflow_1.png)
  * [Splunkbase App](https://splunkbase.splunk.com/app/5351/)
  * [Splunkbase Add-on](https://splunkbase.splunk.com/app/5659/)
  * [Workflow file](https://github.com/VatsalJagani/Splunk-Cyences-App-for-Splunk/blob/master/.github/workflows/main.yml)
[](images/cyences_workflow.png)


* **3CX PhoneSystem App**
  * Has github repo's root directory as the App's root directory.
  * Executes on all changes in all branches. Also, option to manually execute the workflow from GitHub UI.
  ![](images/3cx_app_workflow.png)
  * [Workflow file](https://github.com/VatsalJagani/Splunk-3CX-App/blob/master/.github/workflows/main.yml)


* **Sample run app-inspect checks directly on previously generated build**
  * ![](images/sample_to_use_on_already_generated_build.png)


* **MaxMind Database Auto Update App**
  * Removing unnecessary files from build.
    ![](images/max_mind_database_update_app_workflow.png)
  * [Workflow file](https://github.com/VatsalJagani/Splunk-App-Auto-Update-MaxMind-Database/blob/master/.github/workflows/main.yml)


* **Lansweeper App and Add-on**
  * [Workflow file](https://github.com/VatsalJagani/Splunk-Integration-for-Lansweeper/blob/master/.github/workflows/main.yml)



## Contribute
* If you are developer and want to contribute to this project, please submit a Pull Request.
* If you find a bug or have a request for enhancement, create a Github Issue in this project.
* If you wish to share Feedback or success story, please add comment in [this issue](https://github.com/VatsalJagani/splunk-app-action/issues/19).
