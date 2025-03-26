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

from requests.auth import HTTPBasicAuth
from singer_sdk.streams import RESTStream

if typing.TYPE_CHECKING:
    from singer_sdk._singerlib import Schema
    from singer_sdk.tap_base import Tap

T = typing.TypeVar("T")
TPageToken = typing.TypeVar("TPageToken")


class StripeStream(RESTStream):
    """Stripe stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://api.stripe.com/v1"

    records_jsonpath = "$.data[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.data[-1].id"  # noqa: S105

    @property
    def authenticator(self) -> HTTPBasicAuth:
        """Return the authenticator."""
        return HTTPBasicAuth(username=self.config.get("api_key"), password="")

    def get_url_params(self, context:dict, next_page_token:str) -> dict:
        """Get URL parameters."""
        params = {"limit": 100}
        start_date = self.get_starting_replication_key_value(context)

        if start_date:
            if type(start_date) is str:
                start_date = int(datetime.timestamp(datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")))  # noqa: DTZ007
            params["created[gt]"] = start_date

        if next_page_token:
            params["starting_after"] = next_page_token

        return params


class StripeReportStream(StripeStream):
    """Stripe report stream class."""

    path = ""
    replication_key = "report_end_at"

    def __init__(  # noqa: D107
        self, tap: Tap, name: str | None = None, schema: dict[str, Any] | Schema | None = None, path: str | None = None,
    ) -> None:
        super().__init__(tap, name, schema, path)
        self.primary_keys = [f"{self.name}_id"]

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://api.stripe.com/v1/reporting"

    def retrieve_report_data_availability(self) -> tuple[int, int]:
        """Get the data availability for the report."""
        prepared_request = self.build_prepared_request(
            method="GET",
            url=f"{self.url_base}/report_types/{self.original_name}",
            headers=self.http_headers,
        )
        response = self._request(prepared_request=prepared_request, context=None).json()
        return response["data_available_start"], response["data_available_end"]

    def check_pending_reports(self, report_start_at:int) -> str | None:
        """Check if there are any pending reports."""
        prepared_request = self.build_prepared_request(
            method="GET", url=f"{self.url_base}/report_runs", headers=self.http_headers, params={"limit": 100},
        )
        self.logger.info("checking pending reports for report %s", self.original_name)
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
        return None

    def issue_run(self, interval_start:int, interval_end:int) -> str:
        """Issue a report run."""
        params = {
            "report_type": self.original_name,
            "parameters[interval_start]": interval_start,
            "parameters[interval_end]": interval_end,
        }
        prepared_request = self.build_prepared_request(
            method="POST", url=f"{self.url_base}/report_runs", params=params, headers=self.http_headers, json={},
        )
        self.logger.info(
            "issuing report %s with interval_start=%s and interval_end=%s",
            self.original_name,
            interval_start,
            interval_end,
        )
        response = self._request(prepared_request=prepared_request, context=None).json()
        return response["id"]

    def get_download_url(self, run_id:str) -> str | None:
        """Retrieve the download URL for the report."""
        prepared_request = self.build_prepared_request(
            method="GET",
            url=f"{self.url_base}/report_runs/{run_id}",
            headers=self.http_headers,
        )
        retry = 1
        self.logger.info("retrieving download url for report %s", self.original_name)
        while retry <= 6:  # noqa: PLR2004
            try:
                return self._request(prepared_request, None).json().get("result").get("url")
            except:  # noqa: E722, PERF203
                retry += 1
                sleep = 2**retry
                self.logger.info("backing off for %s seconds.", sleep)
                time.sleep(sleep)
        return None

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Get records."""
        start_date = self.get_starting_replication_key_value(context)
        data_available_start, data_available_end = self.retrieve_report_data_availability()

        if start_date and type(start_date) is str:
            start_date = int(datetime.timestamp(datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")))  # noqa: DTZ007

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
                return self.download_report(context=context, url=url)
        return []

    def download_report(self, context: dict | None, url: str) -> Iterable[dict[str, Any]]:
        """Download the report."""
        prepared_request = self.build_prepared_request(
            method="GET",
            url=url,
            headers=self.http_headers,
        )
        self.logger.info("downloading report %s", self.original_name)
        response = self._request(prepared_request=prepared_request, context=None)
        csv_file = StringIO(response.text)
        dict_reader = csv.DictReader(csv_file)
        return [self.post_process(record, context) for record in dict_reader]

    def safe_eval(self, value):  # noqa: ANN001, ANN201
        """Safely evaluate a value."""
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:  # noqa: ARG002
        """Post process a row."""
        row = {key: self.safe_eval(value) for key, value in row.items()}
        row["report_start_at"] = self.report_start_at
        row["report_end_at"] = self.report_end_at
        row["loaded_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: DTZ005
        row[self.primary_keys[0]] = md5(  # noqa: S324
            "".join([str(row[key]) for key in row if key in self.id_keys and row[key] is not None]).encode(),
        ).hexdigest()
        return row
