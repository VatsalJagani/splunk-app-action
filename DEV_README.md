# README for Developers

* Fork the project and submit a Pull Request if you would like to contribute to the project.

* Run below command to install all node JS dependencies.
  * `npm install`

* Run below command if you make any changes to JS file before committing the code to repo.
  * `ncc build index.js --license LICENSE`
  * This do not require if there is change in python file or action.yml file.



# Notes for author

* Create a new tag and push the tag from git:
  ```
  git tag -a -m "v2" v2
  git push --follow-tags
  ```

* Update the tag from one commit to other:
  ```
  git tag -f -a -m "v2" v2
  git push -f --follow-tags
  ```
