"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_stripe.client import StripeReportStream
from tap_stripe.tap import TapStripe

SAMPLE_CONFIG = {
    "start_date": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "api_key": os.getenv("TAP_STRIPE_API_KEY"),
}


class TapStripeReadOnly(TapStripe):
    """TapStripe without the report streams, which create report runs in Stripe."""

    def discover_streams(self) -> list:
        """Return the streams that only read from Stripe."""
        streams = super().discover_streams()
        return [s for s in streams if not isinstance(s, StripeReportStream)]


TestTapStripe = get_tap_test_class(
    tap_class=TapStripeReadOnly,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(ignore_no_records_for_streams=["report_runs"]),
)
