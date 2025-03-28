"""Stripe tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_stripe import streams


class TapStripe(Tap):
    """Stripe tap class."""

    name = "tap-stripe"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The key to authenticate against the API service",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.StripeStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ChargesStream(self),
            streams.DisputesStream(self),
            streams.PaymentIntentsStream(self),
            streams.ExchangeRateStream(self),
            streams.ReportRunsStream(self),
            streams.ActivitySummary1Stream(self),
            streams.ActivityItemized2Stream(self),
            streams.BalanceChangeFromActivityItemized2Stream(self),
            streams.BalanceChangeFromActivitySummary1Stream(self),
        ]


if __name__ == "__main__":
    TapStripe.cli()
