"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_stripe.tap import TapStripe

SAMPLE_CONFIG = {
    "start_date": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "api_key": os.getenv('TAP_STRIPE_API_KEY'),
}

# Run standard built-in tap tests from the SDK:
TestTapStripe = get_tap_test_class(
    tap_class=TapStripe,
    config=SAMPLE_CONFIG,
)