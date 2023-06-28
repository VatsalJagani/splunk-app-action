# README for Developers

* Fork the project and submit a Pull Request if you would like to contribute to the project.

* Automated tests for the GitHub action present in the separate repo here [splunk-app-action-test-app](https://github.com/VatsalJagani/splunk-app-action-test-app)


## How to Run Locally
```
python3 src/main.py local_test
```


# Notes for author

* Create a new tag and push the tag from git:
  ```
  git tag -a -m "v2" v2
  git push --follow-tags
  ```

* Update the tag from one commit to other:
  ```
  git tag -f -a -m "v1.12" v1.12
  git push -f --tags
  git push -f --follow-tags
  ```

* To delete tag
  ```
  git tag -d v1.12
  git push --delete origin v1.12
  ```


* Run below command to install all node JS dependencies.
  * `npm install`

* Run below command if you make any changes to JS file before committing the code to repo.
  * `ncc build index.js --license LICENSE`
  * This do not require if there is change in python file or action.yml file.



## Note from actions/upload-artifact - Zipped Artifact Downloads
During a workflow run, files are uploaded and downloaded individually using the upload-artifact and download-artifact actions. However, when a workflow run finishes and an artifact is downloaded from either the UI or through the download api, a zip is dynamically created with all the file contents that were uploaded. There is currently no way to download artifacts after a workflow run finishes in a format other than a zip or to download artifact contents individually. One of the consequences of this limitation is that if a zip is uploaded during a workflow run and then downloaded from the UI, there will be a double zip created.
