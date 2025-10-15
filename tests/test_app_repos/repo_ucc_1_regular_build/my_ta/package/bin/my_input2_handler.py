
import json
from datetime import datetime, timedelta
from splunklib import modularinput as smi

from addon_helper import AddonInput
from api import API
from checkpoint import MyInput2Checkpoint


class MyInput1Input(AddonInput):
    def collect(self, account_details, last_checkpoint):
        api = API(self.logger, self, account_details, self.proxy_settings)

        _start_date = self.input_item.get("start_date") if self.input_item.get("start_date") else "1999/01/01"

        ckpt = MyInput2Checkpoint(self.logger, account_details.url, _start_date)
        ckpt.read(last_checkpoint)

        if ckpt.contents.get(account_details.url,{}).get("start_date") != _start_date:
            ckpt.delete()
            ckpt = MyInput2Checkpoint(self.logger, account_details.url, _start_date)
            ckpt.read()

        updated_ckpt = api.collect_data1(ckpt)

        return updated_ckpt.write()



def validate_input(input_script: smi.Script, definition: smi.ValidationDefinition):
    return


def stream_events(input_script: smi.Script, inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    session_key = input_script._input_definition.metadata["session_key"]

    for input_name, input_item in inputs.inputs.items():
        MyInput1Input(session_key, input_name, input_item, event_writer)

