# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false

import json
import os
from typing import Any
from unittest import mock

import github_action_toolkit as gat


def test_event_payload(tmpdir: Any) -> None:
    file = tmpdir.join("summary")
    payload = {"test": "test"}
    file.write(json.dumps(payload))

    with mock.patch.dict(os.environ, {"GITHUB_EVENT_PATH": file.strpath}):
        data = gat.event_payload()

    assert data == payload
