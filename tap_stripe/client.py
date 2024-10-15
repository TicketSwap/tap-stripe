"""client handling, including StripeStream base class."""

from __future__ import annotations

import ast
import csv
import time
import typing
from datetime import datetime
from hashlib import md5
from io import StringIO
from typing import Any, Iterable

from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.pagination import BaseOffsetPaginator
from singer_sdk.streams import RESTStream

if typing.TYPE_CHECKING:
    from requests import Response
    from singer_sdk._singerlib import Schema
    from singer_sdk.tap_base import Tap

T = typing.TypeVar("T")
TPageToken = typing.TypeVar("TPageToken")


class AttributeError(Exception):  # noqa: A001
    """Raised when an attribute throws an error."""


class StripePaginator(BaseOffsetPaginator):
    """Paginator for Stripe streams."""

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
        """Return the authenticator.

        Returns:
            BasicAuthenticator
        """
        return BasicAuthenticator.create_for_stream(
            self,
            username=self.config.get("api_key"),
            password="",
        )

    def get_url_params(self, context, next_page_token):
        params = {"limit": 100}
        start_date = self.get_starting_replication_key_value(context)

        if start_date:
            if type(start_date) == str:
                start_date = int(
                    datetime.timestamp(
                        datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
                    )
                )
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

    path = ""
    replication_key = "report_end_at"

    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: dict[str, Any] | Schema | None = None,
        path: str | None = None,
    ) -> None:
        super().__init__(tap, name, schema, path)
        self.primary_keys = [f"{self.name}_id"]

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

    def check_pending_reports(self, report_start_at) -> str | None:
        prepared_request = self.build_prepared_request(
            method="GET",
            url=f"{self.url_base}/report_runs",
            headers=self.http_headers,
            params={"limit": 100},
        )
        self.logger.info(f"checking pending reports for report {self.original_name}")
        response = self._request(prepared_request=prepared_request, context=None).json()
        reports = [
            report
            for report in response["data"]
            if report.get("report_type") == self.original_name
            and report.get("status") == "succeeded"
            and report.get("parameters")["interval_start"] == report_start_at
        ]
        latest_report = next(iter(reports), None)
        if latest_report:
            self.report_end_at = latest_report["parameters"]["interval_end"]
            return latest_report["result"]["url"]

    def issue_run(self, interval_start, interval_end) -> str:
        params = {
            "report_type": self.original_name,
            "parameters[interval_start]": interval_start,
            "parameters[interval_end]": interval_end,
        }
        prepared_request = self.build_prepared_request(
            method="POST",
            url=f"{self.url_base}/report_runs",
            params=params,
            headers=self.http_headers,
            json={},
        )
        self.logger.info(
            f"issuing report {self.original_name} with interval_start={interval_start} and interval_end={interval_end}"
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
        self.logger.info(f"retrieving download url for report {self.original_name}")
        while retry <= 6:
            try:
                url = (
                    self._request(prepared_request, None)
                    .json()
                    .get("result")
                    .get("url")
                )
                return url
            except:
                retry += 1
                sleep = 2**retry
                self.logger.info(f"backing off for {sleep} seconds.")
                time.sleep(sleep)

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        start_date = self.get_starting_replication_key_value(context)
        data_available_start, data_available_end = (
            self.retrieve_report_data_availability()
        )

        if start_date:
            if type(start_date) == str:
                start_date = int(
                    datetime.timestamp(
                        datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
                    )
                )

        report_start_at = max(data_available_start, start_date)
        report_end_at = data_available_end

        if report_start_at < report_end_at:
            self.report_start_at = report_start_at
            url = self.check_pending_reports(report_start_at=report_start_at)
            if not url:
                self.report_end_at = report_end_at
                run_id = self.issue_run(report_start_at, report_end_at)
                url = self.get_download_url(run_id)
            if url is not None:
                records = self.download_report(context=context, url=url)
                return records
        return []

    def download_report(
        self, context: dict | None, url: str
    ) -> Iterable[dict[str, Any]]:
        prepared_request = self.build_prepared_request(
            method="GET",
            url=url,
            headers=self.http_headers,
        )
        self.logger.info(f"downloading report {self.original_name}")
        response = self._request(prepared_request=prepared_request, context=None)
        csv_file = StringIO(response.text)
        dict_reader = csv.DictReader(csv_file)
        transformed_records = [
            self.post_process(record, context) for record in dict_reader
        ]
        return transformed_records

    def safe_eval(self, value):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        row = {key: self.safe_eval(value) for key, value in row.items()}
        row["report_start_at"] = self.report_start_at
        row["report_end_at"] = self.report_end_at
        row["loaded_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        row[self.primary_keys[0]] = md5(
            "".join(
                [
                    str(row[key])
                    for key in row.keys()
                    if key in self.id_keys and row[key] is not None
                ]
            ).encode(),
        ).hexdigest()
        return row
