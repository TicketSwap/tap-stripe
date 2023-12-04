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
import logging
import json
import typing

from singer_sdk.tap_base import Tap
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.pagination import BaseOffsetPaginator

if typing.TYPE_CHECKING:
    from requests import Response

T = typing.TypeVar("T")
TPageToken = typing.TypeVar("TPageToken")

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]


class StripePaginator(BaseOffsetPaginator):
    def has_more(self, response: Response) -> bool:  # noqa: ARG002
        """Override this method to check if the endpoint has any pages left.

        Args:
            response: API response object.

        Returns:
            Boolean flag used to indicate if the endpoint has more pages.
        """
        return response.json()["has_more"]

    def get_next(self, response: Response) -> TPageToken | None:
        """Get the next pagination token or index from the API response.

        Args:
            response: API response object.

        Returns:
            The next page token or index. Return `None` from this method to indicate
                the end of pagination.
        """
        return response.json()["data"][-1]["id"]


class StripeStream(RESTStream):
    """Stripe stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://api.stripe.com/v1"

    records_jsonpath = "$.data[*]"  # Or override `parse_response`.

    @property
    def authenticator(self):
        """Return the authenticator."""
        return BasicAuthenticator.create_for_stream(self, username=self.config.get("api_key"), password="")

    def get_url_params(self, context, next_page_token):
        params = {"limit": 100}
        start_date = self.get_starting_replication_key_value(context)

        if start_date:
            if type(start_date) == str:
                start_date = int(datetime.timestamp(datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")))
            params["created[gt]"] = start_date

        if next_page_token:
            params["starting_after"] = next_page_token

        self.logger.info(f"params = {params}")

        return params

    def get_new_paginator(self) -> BaseOffsetPaginator:
        """Create a new pagination helper instance.

        If the source API can make use of the `next_page_token_jsonpath`
        attribute, or it contains a `X-Next-Page` header in the response
        then you can remove this method.

        If you need custom pagination that uses page numbers, "next" links, or
        other approaches, please read the guide: https://sdk.meltano.com/en/v0.25.0/guides/pagination-classes.html.

        Returns:
            A pagination helper instance.
        """
        return StripePaginator(page_size=100, start_value=0)
