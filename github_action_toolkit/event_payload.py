import json
import os
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def event_payload() -> dict[str, Any]:
    """
    gets GitHub event payload data.

    :returns: dictionary of event payload
    """
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        data: dict[str, Any] = json.load(f)
    return data
