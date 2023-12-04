"""Stream type classes for tap-stripe."""

from __future__ import annotations

import typing as t
import requests
from pathlib import Path
from typing import Iterable, Optional
from datetime import datetime

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.typing import (
    IntegerType,
    StringType,
    DateTimeType,
    ObjectType,
    Property,
    PropertiesList,
    ArrayType,
    BooleanType,
    NumberType,
)

from tap_stripe.client import StripeStream


class ChargesStream(StripeStream):
    name = "charges"
    path = "/charges"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "created"
    is_sorted = False

    schema = PropertiesList(
        Property("id", StringType),
        Property("amount", IntegerType),
        Property("balance_transaction", StringType),
        Property("created", IntegerType),
        Property("currency", StringType),
        Property("customer", StringType),
        Property("description", StringType),
        Property("disputed", BooleanType),
        Property("invoice", StringType),
        Property(
            "metadata",
            ObjectType(
                Property("customerId", StringType),
                Property("paymentFlowId", StringType),
                Property("fingerprint", StringType),
            ),
        ),
        Property("refunded", BooleanType),
        Property("status", StringType),
    ).to_dict()


class DisputesStream(StripeStream):
    name = "disputes"
    path = "/disputes"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    is_sorted = False
    replication_key = "created"

    schema = PropertiesList(
        Property("id", StringType),
        Property("amount", IntegerType),
        Property("charge", StringType),
        Property("created", IntegerType),
        Property("currency", StringType),
        Property(
            "evidence_details",
            ObjectType(
                Property("due_by", IntegerType),
                Property("has_evidence", BooleanType),
                Property("past_due", BooleanType),
                Property("submission_count", IntegerType),
            ),
        ),
        Property("is_charge_refundable", BooleanType),
        Property("livemode", BooleanType),
        Property("payment_intent", StringType),
        Property("reason", StringType),
        Property("status", StringType),
    ).to_dict()


class ExchangeRateStream(StripeStream):
    name = "exchange_rates"
    path = "/exchange_rates"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    schema = PropertiesList(
        Property("send_currency", StringType),
        Property("receive_currency", StringType),
        Property("rate", NumberType),
        Property("date", DateTimeType),
    ).to_dict()

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
