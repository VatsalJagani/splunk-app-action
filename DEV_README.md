# README for Developers

* Fork the project and submit a Pull Request if you would like to contribute to the project.

* Automated tests for the GitHub action present in the separate repo here [splunk-app-action-tests](https://github.com/VatsalJagani/splunk-app-action-tests)


# Notes for author

* Create a new tag and push the tag from git:
  ```
  git tag -a -m "v2" v2
  git push --follow-tags
  ```

* Update the tag from one commit to other:
  ```
  git tag -f -a -m "v1" v1
  git push -f --tags
  git push -f --follow-tags
  ```

* To delete tag
  ```
  git tag -d v0
  git push --delete origin v0
  ```


* Run below command to install all node JS dependencies.
  * `npm install`

* Run below command if you make any changes to JS file before committing the code to repo.
  * `ncc build index.js --license LICENSE`
  * This do not require if there is change in python file or action.yml file.
