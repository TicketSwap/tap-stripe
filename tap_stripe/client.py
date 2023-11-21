"""client handling, including StripeStream base class."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Iterable
import base64
from urllib.parse import urlencode
from datetime import datetime
from urllib.parse import parse_qsl
import requests
import stripe

from singer_sdk.tap_base import Tap
from singer_sdk.streams import Stream


if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]


class StripeStream(Stream):
    """Stripe stream class."""

    def __init__(self, tap: Tap):
        super().__init__(tap)
        stripe.api_key = self.config.get("api_key")

    def get_starting_timestamp(self, context: dict | None) -> int | None:
        starting_timestamp = self.get_starting_replication_key_value(context)
        if type(starting_timestamp) == str:
            gt = int(datetime.timestamp(datetime.strptime(starting_timestamp, "%Y-%m-%dT%H:%M:%SZ")))
        else:
            gt = starting_timestamp
        return gt

