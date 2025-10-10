Input, Output, Environment Variables & States
=============

### **`get_workflow_environment_variables()`**

Gets all environment variables from the `GITHUB_ENV` environment file which is available to the workflow.
GitHub Actions Docs: [set_env](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable)

**example:**

```python
>> from github_action_utils import get_workflow_environment_variables

>> get_workflow_environment_variables()

# Output:
# {"my_env": "test value"}
```

### **`get_env(name)`**

Gets all environment variables from `os.environ` or the `GITHUB_ENV` environment file which is available to the workflow.
This can also be used to get [environment variables set by GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables).
GitHub Actions Docs: [set_env](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable)

**example:**

```python
>> from github_action_utils import get_env

>> get_env("my_env")
>> get_env("GITHUB_API_URL")

# Output:
# test value
# https://api.github.com
```

### **`set_env(name, value)`**

Creates an environment variable by writing this to the `GITHUB_ENV` environment file which is available to any subsequent steps in a workflow job.
GitHub Actions Docs: [set_env](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable)

**example:**

```python
>> from github_action_utils import set_env

>> set_env("my_env", "test value")
```

### **`get_all_user_inputs()`**

Gets all user inputs from environment variables prefixed with INPUT_, and returns them as a dictionary.

The input names are normalized to lowercase (e.g., INPUT_USERNAME becomes "username").

**example:**

```python
>> from github_action_toolkit import get_all_user_inputs

>> # Assuming these environment variables:
>> # INPUT_USERNAME="alice"
>> # INPUT_DEBUG="true"

>> get_all_user_inputs()

# Output:
# {'username': 'alice', 'debug': 'true'}

```

### **`print_all_user_inputs()`**

Prints all user inputs (from environment variables prefixed with INPUT_) in a readable format.

If no user inputs are found, it prints a fallback message.

**example:**

```python
>> from github_action_toolkit import print_all_user_inputs

>> # Assuming these environment variables:
>> # INPUT_API_KEY="abc123"
>> # INPUT_VERBOSE="yes"

>> print_all_user_inputs()

# Output:
# User Inputs:
#   api_key: abc123
#   verbose: yes

# Output - If no inputs are found:
# No user inputs found.
```

### **`get_user_input(name)`**

Gets user input from running workflow.

**example:**

```python
>> from github_action_toolkit import get_user_input

>> get_user_input("my_input")

# Output:
# my value
```

### **`get_user_input_as(name, input_type, default_value)`**

Gets user input from running workflow with type-casting into choice.

**example:**

```python
>> from github_action_toolkit import get_user_input_as

>> get_user_input_as("my_bool_input", bool, False)

# Output:
# False
```

### **`set_output(name, value)`**

Sets a step's output parameter by writing to `GITHUB_OUTPUT` environment file. Note that the step will need an `id` to be defined to later retrieve the output value.
GitHub Actions Docs: [set_output](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter)

**example:**

```python
>> from github_action_toolkit import set_output

>> set_output("my_output", "test value")
```

### **`get_state(name)`**

Gets state environment variable from running workflow.

**example:**

```python
>> from github_action_toolkit import get_state

>> get_state("test_name")

# Output:
# test_value
```

### **`save_state(name, value)`**

Creates an environment variable by writing this to the `GITHUB_STATE` environment file which is available to workflow's pre: or post: actions.
GitHub Actions Docs: [save_state](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#sending-values-to-the-pre-and-post-actions)

**example:**

```python
>> from github_action_toolkit import save_state

>> save_state("my_state", "test value")
```
