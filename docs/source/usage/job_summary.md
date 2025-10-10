Job Summary Functions
=============

### **`append_job_summary(markdown_text)`**

Sets some custom Markdown for each job so that it will be displayed on the summary page of a workflow run.
GitHub Actions Docs: [append_job_summary](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary)

**example:**

```python
>> from github_action_utils import append_job_summary

>> append_job_summary("# test summary")
```


### **`overwrite_job_summary(markdown_text)`**

Clears all content for the current step, and adds new job summary.
GitHub Actions Docs: [overwrite_job_summary](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#overwriting-job-summaries)

**example:**

```python
>> from github_action_utils import overwrite_job_summary

>> overwrite_job_summary("# test summary")
```

### **`remove_job_summary()`**

completely removes job summary for the current step.
GitHub Actions Docs: [remove_job_summary](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#removing-job-summaries)

**example:**

```python
>> from github_action_utils import remove_job_summary

>> remove_job_summary()
```
