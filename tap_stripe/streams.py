"""Stream type classes for tap-stripe."""

from __future__ import annotations

import typing as t
import requests
from datetime import datetime

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath
from tap_stripe.client import StripeStream, StripeReportStream

from .schemas import *


class ChargesStream(StripeStream):
    name = "charges"
    path = "/charges"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "created"
    is_sorted = False

    schema = charges_schema


class DisputesStream(StripeStream):
    name = "disputes"
    path = "/disputes"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    is_sorted = False
    replication_key = "created"

    schema = disputes_schema


class ExchangeRateStream(StripeStream):
    name = "exchange_rates"
    path = "/exchange_rates"
    primary_keys: t.ClassVar[list[str]] = ["send_currency", "receive_currency", "date"]
    schema = exchange_rates_schema

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: A raw `requests.Response`_ object.

        Yields:
            One item for every item found in the response.

        .. _requests.Response:
            https://requests.readthedocs.io/en/latest/api/#requests.Response
        """
        data = response.json()["data"]
        for row in data:
            for receive_currency, rate in row["rates"].items():
                yield {
                    "send_currency": row["id"],
                    "receive_currency": receive_currency,
                    "rate": rate,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }


class ReportRunsStream(StripeStream):
    name = "report_runs"
    path = "/reporting/report_runs"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "created"
    is_sorted = False
    schema = report_runs_schema


class ActivityItemized2Stream(StripeReportStream):
    name = "activity_itemized_2"
    original_name = "activity.itemized.2"
    id_keys: t.ClassVar[list[str]] = [
        "balance_transaction_id",
        "balance_transaction_component",
        "fee_id",
        "activity_at",
    ]
    schema = activity_itemized_2_schema


class ActivitySummary1Stream(StripeReportStream):
    name = "activity_summary_1"
    original_name = "activity.summary.1"
    id_keys: t.ClassVar[list[str]] = ["reporting_category", "currency", "report_start_at"]
    schema = activity_summary_1_schema


class BalanceChangeFromActivityItemized2Stream(StripeReportStream):
    name = "balance_change_from_activity_itemized_2"
    original_name = "balance_change_from_activity.itemized.2"
    id_keys: t.ClassVar[list[str]] = ["balance_transaction_id", "created_utc"]
    schema = balance_change_from_activity_itemized_2_schema


class BalanceChangeFromActivitySummary1Stream(StripeReportStream):
    name = "balance_change_from_activity_summary_1"
    original_name = "balance_change_from_activity.summary.1"
    id_keys: t.ClassVar[list[str]] = ["reporting_category", "currency", "report_start_at"]
    schema = balance_change_from_activity_summary_1_schema
