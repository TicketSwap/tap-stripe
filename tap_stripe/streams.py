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
        Property("amount_captured", IntegerType),
        Property("amount_refunded", IntegerType),
        Property("application", StringType),
        Property("application_fee", StringType),
        Property("application_fee_amount", IntegerType),
        Property("balance_transaction", StringType),
        Property(
            "billing_details",
            ObjectType(
                Property(
                    "address",
                    ObjectType(
                        Property("city", StringType),
                        Property("country", StringType),
                        Property("line1", StringType),
                        Property("line2", StringType),
                        Property("postal_code", StringType),
                        Property("state", StringType),
                    ),
                ),
                Property("email", StringType),
                Property("name", StringType),
                Property("phone", StringType),
            ),
        ),
        Property("calculated_statement_descriptor", StringType),
        Property("captured", BooleanType),
        Property("created", IntegerType),
        Property("currency", StringType),
        Property("customer", StringType),
        Property("description", StringType),
        Property("disputed", BooleanType),
        Property("failure_balance_transaction", StringType),
        Property("failure_code", StringType),
        Property("failure_message", StringType),
        Property(
            "fraud_details",
            ObjectType(
                Property("stripe_report", StringType),
                Property("user_report", StringType),
            ),
        ),
        Property("invoice", StringType),
        Property("livemode", BooleanType),
        Property(
            "metadata",
            ObjectType(
                Property("customerId", StringType),
                Property("fingerprint", StringType),
                Property("paymentFlowId", StringType),
                Property("isForPayoutReversal", StringType),
                Property("manuallyFixedByTeamDelta", StringType),
                Property("paymentId", StringType),
            ),
        ),
        Property("on_behalf_of", StringType),
        Property(
            "outcome",
            ObjectType(
                Property("network_status", StringType),
                Property("reason", StringType),
                Property("risk_level", StringType),
                Property("risk_score", IntegerType),
                Property("rule", StringType),
                Property("seller_message", StringType),
                Property("type", StringType),
            ),
        ),
        Property("paid", BooleanType),
        Property("payment_intent", StringType),
        Property("payment_method", StringType),
        Property("payment_method_details", ObjectType()),
        Property("receipt_email", StringType),
        Property("receipt_number", StringType),
        Property("receipt_url", StringType),
        Property("refunded", BooleanType),
        Property("review", StringType),
        Property("source_transfer", StringType),
        Property("statement_descriptor", StringType),
        Property("statement_descriptor_suffix", StringType),
        Property("status", StringType),
        Property(
            "transfer_data",
            ObjectType(
                Property("amount", StringType),
                Property("destination", StringType),
            ),
        ),
        Property("transfer_group", StringType),
    ).to_dict()


class DisputesStream(StripeStream):
    name = "disputes"
    path = "/disputes"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    is_sorted = False
    replication_key = "created"

    schema = PropertiesList(
        Property("id", StringType),
        Property("object", StringType),
        Property("amount", IntegerType),
        Property(
            "balance_transactions",
            ArrayType(
                Property("id", StringType),
            ),
        ),
        Property("charge", StringType),
        Property("created", IntegerType),
        Property("currency", StringType),
        Property(
            "evidence",
            ObjectType(
                Property("access_activity_log", StringType),
                Property("billing_address", StringType),
                Property("cancellation_policy", StringType),
                Property("cancellation_policy_disclosure", StringType),
                Property("cancellation_rebuttal", StringType),
                Property("customer_communication", StringType),
                Property("customer_email_address", StringType),
                Property("customer_name", StringType),
                Property("customer_purchase_ip", StringType),
                Property("customer_signature", StringType),
                Property("duplicate_charge_documentation", StringType),
                Property("duplicate_charge_explanation", StringType),
                Property("duplicate_charge_id", StringType),
                Property("receipt", StringType),
                Property("refund_policy", StringType),
                Property("refund_policy_disclosure", StringType),
                Property("refund_refusal_explanation", StringType),
                Property("service_date", StringType),
                Property("service_documentation", StringType),
                Property("shipping_address", StringType),
                Property("shipping_carrier", StringType),
                Property("shipping_date", StringType),
                Property("shipping_documentation", StringType),
                Property("shipping_tracking_number", StringType),
                Property("uncategorized_file", StringType),
                Property("uncategorized_text", StringType),
            ),
        ),
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
        Property("metadata", ObjectType()),
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
