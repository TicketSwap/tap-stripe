"""client handling, including StripeStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable
from datetime import datetime
import ast
import requests
import typing
import time
import backoff
import csv
from io import StringIO

from singer_sdk._singerlib import Schema
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


class AttributeError(Exception):
    """Raised when an attribute throws an error"""


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


class StripeReportStream(StripeStream):
    """Stripe report stream class"""

    def __init__(
        self, tap: Tap, name: str | None = None, schema: dict[str, Any] | Schema | None = None, path: str | None = None
    ) -> None:
        super().__init__(tap, name, schema, path)
        self.path = ""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://api.stripe.com/v1/reporting"

    def retrieve_report_data_availability(self) -> (int, int):
        prepared_request = self.build_prepared_request(
            method="GET",
            url=f"{self.url_base}/report_types/{self.original_name}",
            headers=self.http_headers,
        )
        response = self._request(prepared_request=prepared_request, context=None).json()
        return response["data_available_start"], response["data_available_end"]

    def issue_run(self, interval_start, interval_end) -> str:
        params = {
            "report_type": self.original_name,
            "parameters[interval_start]": interval_start,
            "parameters[interval_end]": interval_end,
        }
        prepared_request = self.build_prepared_request(
            method="POST", url=f"{self.url_base}/report_runs", params=params, headers=self.http_headers, json={}
        )
        response = self._request(prepared_request=prepared_request, context=None).json()
        return response["id"]

    def get_download_url(self, run_id) -> str | None:
        prepared_request = self.build_prepared_request(
            method="GET",
            url=f"{self.url_base}/report_runs/{run_id}",
            headers=self.http_headers,
        )
        retry = 1
        while retry <= 20:
            try:
                url = self._request(prepared_request, None).json().get("result").get("url")
                return url
            except:
                retry += 1
                sleep = 2**retry
                self.logger.info(f"backing off for {sleep} seconds.")
                time.sleep(sleep)

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        start_date = self.get_starting_replication_key_value(context)
        data_available_start, data_available_end = self.retrieve_report_data_availability()

        if start_date:
            if type(start_date) == str:
                start_date = int(datetime.timestamp(datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")))
            start_date += 1

        interval_start = max(data_available_start, start_date)
        interval_end = data_available_end

        if interval_start < interval_end:
            self.interval_end_at = interval_end
            run_id = self.issue_run(interval_start, interval_end)
            url = self.get_download_url(run_id)

            prepared_request = self.build_prepared_request(
                method="GET",
                url=url,
                headers=self.http_headers,
            )
            response = self._request(prepared_request=prepared_request, context=None)
            csv_file = StringIO(response.text)
            dict_reader = csv.DictReader(csv_file)
            for record in dict_reader:
                transformed_record = self.post_process(record, context)
                if transformed_record is None:
                    # Record filtered out during post_process()
                    continue
                yield transformed_record

    def safe_eval(self, value):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        row = {key: self.safe_eval(value) for key, value in row.items()}
        row["interval_end_at"] = self.interval_end_at
        row["loaded_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        return row
