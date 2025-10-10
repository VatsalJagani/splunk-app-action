GitHub Action Event Payload
=============

### **`event_payload()`**

Get GitHub Event payload that triggered the workflow.

More details: [GitHub Actions Event Payload](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)

**example:**

```python
>> from github_action_utils import event_payload

>> event_payload()

# Output:
# {"action": "opened", "number": 1, "pull_request": {"url": "https://api.github.com/repos/octocat/Hello-World/pulls/1"}, "repository": {"url": "https://api.github.com/repos/octocat/Hello-World"}, "sender": {"login": "octocat"}...}
```
