# UCC Additional Packaging Utility

This utility adds `additional_packaging.py` for UCC-built Add-ons, helping generate input handler files for Splunk modular inputs.

## Example Usage

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "."
    use_ucc_gen: true
    app_utilities: "ucc_additional_packaging"
    my_github_token: ${{ secrets.MY_GITHUB_TOKEN }}
```

The input handler file `<Input_Name>_handler.py` will start with:

```python
from splunklib import modularinput as smi

def validate_input(input_script: smi.Script, definition: smi.ValidationDefinition):
    return

def stream_events(input_script: smi.Script, inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    return
```

- Update `validate_input` and `stream_events` as needed.
- `validate_input` is optional; `stream_events` is required for event ingestion.
