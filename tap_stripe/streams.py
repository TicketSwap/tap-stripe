"""Stream type classes for tap-stripe."""

from __future__ import annotations

import typing as t
import requests
from pathlib import Path
from typing import Iterable, Optional
from datetime import datetime
import stripe

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.typing import IntegerType, StringType, DateTimeType, ObjectType, Property, PropertiesList, ArrayType, BooleanType, NumberType

from tap_stripe.client import StripeStream


class ChargesStream(StripeStream):
    name = "charges"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = 'created'
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
        Property("metadata", ObjectType(
            Property("customerId", StringType),
            Property("paymentFlowId", StringType),
            Property("fingerprint", StringType)
        )),
        Property("refunded", BooleanType),
        Property("status", StringType)
    ).to_dict()
    
    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.
        """
        charges = stripe.Charge.list(limit=100, created={'gt':self.get_starting_timestamp(context)})
        return charges.auto_paging_iter()

class DisputesStream(StripeStream):
    name = "disputes"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = 'created'
    schema = PropertiesList(
        Property("id", StringType),
        Property("amount", IntegerType),
        Property("charge", StringType),
        Property("created", IntegerType),
        Property("currency", StringType),
        Property("evidence_details", ObjectType(
            Property("due_by", IntegerType),
            Property("has_evidence", BooleanType),
            Property("past_due", BooleanType),
            Property("submission_count", IntegerType)
        )),
        Property("is_charge_refundable", BooleanType),
        Property("livemode", BooleanType),
        Property("payment_intent", StringType),
        Property("reason", StringType),
        Property("status", StringType),
    ).to_dict()
    
    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.
        """
        disputes = stripe.Dispute.list(limit=100, created={'gt':self.get_starting_timestamp(context)})
        return disputes.auto_paging_iter()
    
class ExxchangeRateStream(StripeStream):
    name = "exchangerates"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    schema = PropertiesList(
        Property("receive_currency", StringType),
        Property("send_currency", StringType),
        Property("rate", NumberType),
        Property("date", DateTimeType)
    ).to_dict()
    
    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.
        """
        exchangerates = stripe.ExchangeRate.list(limit=100)
        for exchange_rate in exchangerates.auto_paging_iter():
            for recieve_currency, rate in exchange_rate['rates'].items():
                yield {'send_currency': exchange_rate['id'],
                       'receive_currency': recieve_currency,
                       'rate': rate,
                       'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                       }
