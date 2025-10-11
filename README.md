# splunk-app-action - Python Package

This is python library for utility functions and class helpful for custom GitHub actions.


## Documentation

Installation & Usage Documentation is hosted at - [https://splunk-app-action.readthedocs.io/](https://splunk-app-action.readthedocs.io/)


### Note from actions/upload-artifact - Zipped Artifact Downloads
During a workflow run, files are uploaded and downloaded individually using the upload-artifact and download-artifact actions. However, when a workflow run finishes and an artifact is downloaded from either the UI or through the download api, a zip is dynamically created with all the file contents that were uploaded. There is currently no way to download artifacts after a workflow run finishes in a format other than a zip or to download artifact contents individually. One of the consequences of this limitation is that if a zip is uploaded during a workflow run and then downloaded from the UI, there will be a double zip created.



## Project Docs

For development workflows, see [development.md](devtools/development.md).

For instructions on release process, see [release.md](devtools/release.md).
