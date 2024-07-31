"""Stream schemas for tap-stripe."""

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

charges_schema = PropertiesList(
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


disputes_schema = PropertiesList(
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
    Property("payment_intent", StringType),
    Property("reason", StringType),
    Property("status", StringType),
).to_dict()

payment_intents_schema = PropertiesList(
    Property("id", StringType),
    Property("object", StringType),
    Property("amount", IntegerType),
    Property(
        "automatic_payment_methods",
        ObjectType(
            Property("allow_redirects", StringType),
            Property("enabled", BooleanType)
        ),
    ),
    Property("created", IntegerType),
    Property("client_secret", StringType),
    Property("currency", StringType),
    Property("customer", StringType),
    Property("description", StringType),
    Property(
        "last_payment_error",
        ObjectType(
            Property("charge", StringType),
            Property("code", StringType),
            Property("decline_code", StringType),
            Property("doc_url", StringType),
            Property("message", StringType),
            Property("param", StringType),
            Property("payment_method", ObjectType(Property("id", StringType))),
            Property("payment_method_type", StringType),
            Property("source", ObjectType(Property("source", StringType))),
            Property("type", StringType),
        ),
    ),
    Property("latest_charge", StringType),
    Property("payment_method", StringType),
    Property("receipt_email", StringType),
    Property("setup_future_usage", StringType),
    Property(
        "shipping",
        ObjectType(
            Property("address", ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("line1", StringType),
                Property("line2", StringType),
                Property("postal_code", StringType),
                Property("state", StringType),
            )),
            Property("carrier", StringType),
            Property("name", StringType),
            Property("phone", StringType),
            Property("tracking_number", StringType)
        ),
    ),
    Property("statement_descriptor", StringType),
    Property("statement_descriptor_suffix", StringType),
    Property("status", StringType),
    Property("amount_capturable", IntegerType),
    Property(
        "amount_details",
        ObjectType(
            Property("tip", ObjectType(Property("amount", IntegerType)))
        ),
    ),
    Property("amount_received", IntegerType),
    Property("application", StringType),
    Property("application_fee_amount", IntegerType),
    Property("canceled_at", IntegerType),
    Property("cancellation_reason", StringType),
    Property("capture_method", StringType),
    Property("confirmation_method", StringType),
    Property("created", IntegerType),
    Property("invoice", StringType),
    Property("livemode", BooleanType),
    Property("on_behalf_of", StringType),
    Property(
        "payment_method_configuration_details",
        ObjectType(
            Property("id", StringType),
            Property("parent", StringType),
        ),
    ),
    Property("payment_method_types", ArrayType(Property("id", StringType))),
    Property(
        "processing",
        ObjectType(
            Property(
                "card", 
                ObjectType(
                    Property(
                        "customer_notification", 
                        ObjectType(
                            Property("approval_requested", BooleanType), 
                            Property("completes_at", DateTimeType),
                        )
                    )
                )
            )
        )
    ),
    Property("review", StringType),
    Property(
        "transfer_data",
        ObjectType(
            Property("amount", IntegerType),
            Property("destination", StringType),
        ),
    ),
    Property("transfer_group", StringType)
).to_dict()

sources_schema = PropertiesList(
    Property("id", StringType),
    Property("object", StringType),
    Property("amount", IntegerType),
    Property("client_secret", StringType),
    Property("code_verification", ObjectType(
        Property("attempts_remaining", IntegerType),
        Property("status", StringType)
    )),
    Property("created", IntegerType),
    Property("currency", StringType),
    Property("customer", StringType),
    Property("flow", StringType),
    Property("livemode", BooleanType),
    Property("mandate", ObjectType(
        Property("acceptance", ObjectType(
            Property("date", IntegerType),
            Property("ip", StringType),
            Property("offline", ObjectType(
                Property("contact_email", StringType)
            )),
            Property("online", ObjectType(
                Property("user_agent", StringType)
            )),
            Property("status", StringType),
            Property("type", StringType),
            Property("user", StringType)
        )),
        Property("amount", IntegerType),
        Property("currency", StringType),
        Property("interval", StringType),
        Property("notification_method", StringType)
    )),
    Property("owner", ObjectType(
        Property("address", ObjectType(
            Property("city", StringType),
            Property("country", StringType),
            Property("line1", StringType),
            Property("line2", StringType),
            Property("postal_code", StringType),
            Property("state", StringType)
        )),
        Property("email", StringType),
        Property("name", StringType),
        Property("phone", StringType),
        Property("verified_address", ObjectType(
            Property("city", StringType),
            Property("country", StringType),
            Property("line1", StringType),
            Property("line2", StringType),
            Property("postal_code", StringType),
            Property("state", StringType)
        )),
        Property("verified_email", StringType),
        Property("verified_name", StringType),
        Property("verified_phone", StringType)
    )),
    Property("receiver", ObjectType(
        Property("address", StringType),
        Property("amount_charged", IntegerType),
        Property("amount_received", IntegerType),
        Property("amount_returned", IntegerType)
    )),
    Property("redirect", ObjectType(
        Property("failure_reason", StringType),
        Property("return_url", StringType),
        Property("status", StringType),
        Property("url", StringType)
    )),
    Property("statement_descriptor", StringType),
    Property("status", StringType),
    Property("type", StringType),
    Property("usage", StringType),
    Property("ach_credit_transfer", ObjectType(
        Property("account_number", StringType),
        Property("bank_name", StringType),
        Property("routing_number", StringType),
        Property("swift_code", StringType)
    )),
    Property("ach_debit", ObjectType(
        Property("bank_name", StringType),
        Property("country", StringType),
        Property("fingerprint", StringType),
        Property("last4", StringType),
        Property("routing_number", StringType),
        Property("swift_code", StringType)
    )),
    Property("au_becs_debit", ObjectType(
        Property("bsb_number", StringType),
        Property("fingerprint", StringType),
        Property("last4", StringType)
    )),
    Property("bancontact", ObjectType(
        Property("bank_code", StringType),
        Property("bank_name", StringType),
        Property("bic", StringType),
        Property("iban_last4", StringType),
        Property("preferred_language", StringType),
        Property("verified_name", StringType)
    )),
    Property("card", ObjectType(
        Property("address_line1_check", StringType),
        Property("address_zip_check", StringType),
        Property("brand", StringType),
        Property("country", StringType),
        Property("cvc_check", StringType),
        Property("dynamic_last4", StringType),
        Property("exp_month", IntegerType),
        Property("exp_year", IntegerType),
        Property("fingerprint", StringType),
        Property("funding", StringType),
        Property("last4", StringType),
        Property("name", StringType),
        Property("three_d_secure", StringType),
        Property("tokenization_method", StringType)
    )),
    Property("card_present", ObjectType(
        Property("brand", StringType),
        Property("cardholder_name", StringType),
        Property("country", StringType),
        Property("emv_auth_data", StringType),
        Property("exp_month", IntegerType),
        Property("exp_year", IntegerType),
        Property("fingerprint", StringType),
        Property("funding", StringType),
        Property("last4", StringType),
        Property("read_method", StringType),
        Property("receipt", ObjectType(
            Property("account_type", StringType),
            Property("application_cryptogram", StringType),
            Property("authorization_code", StringType),
            Property("authorization_response_code", StringType),
            Property("card_expiration_date", StringType),
            Property("dedicated_file_name", StringType),
            Property("terminal_verification_results", StringType),
            Property("transaction_status_information", StringType)
        ))
    )),
    Property("eps", ObjectType(
        Property("reference", StringType),
        Property("verified_name", StringType)
    )),
    Property("giropay", ObjectType(
        Property("bank_code", StringType),
        Property("bank_name", StringType),
        Property("bic", StringType),
        Property("verified_name", StringType)
    )),
    Property("ideal", ObjectType(
        Property("bank", StringType),
        Property("bic", StringType),
        Property("iban_last4", StringType),
        Property("verified_name", StringType)
    )),
    Property("klarna", ObjectType(
        Property("background_color", StringType),
        Property("client_token", StringType),
        Property("first_name", StringType),
        Property("last_name", StringType),
        Property("locale", StringType),
        Property("logo_url", StringType),
        Property("page_title", StringType),
        Property("pay_later_asset_urls_descriptive", ObjectType(
            Property("long", StringType),
            Property("medium", StringType),
            Property("short", StringType)
        )),
        Property("pay_now_asset_urls_descriptive", ObjectType(
            Property("long", StringType),
            Property("medium", StringType),
            Property("short", StringType)
        )),
        Property("pay_over_time_asset_urls_descriptive", ObjectType(
            Property("long", StringType),
            Property("medium", StringType),
            Property("short", StringType)
        )),
        Property("pay_later_asset_urls_standard", ObjectType(
            Property("long", StringType),
            Property("medium", StringType),
            Property("short", StringType)
        )),
        Property("pay_now_asset_urls_standard", ObjectType(
            Property("long", StringType),
            Property("medium", StringType),
            Property("short", StringType)
        )),
        Property("pay_over_time_asset_urls_standard", ObjectType(
            Property("long", StringType),
            Property("medium", StringType),
            Property("short", StringType)
        )),
        Property("payment_method_categories", ObjectType(
            Property("descriptive", ObjectType(
                Property("description", StringType),
                Property("logo", StringType),
                Property("subheader", StringType)
            )),
            Property("standard", ObjectType(
                Property("description", StringType),
                Property("logo", StringType),
                Property("subheader", StringType)
            ))
        )),
        Property("payment_method_category_order", ObjectType(
            Property("descriptive", ObjectType(
                Property("category", StringType),
                Property("display_name", StringType),
                Property("priority", IntegerType)
            )),
            Property("standard", ObjectType(
                Property("category", StringType),
                Property("display_name", StringType),
                Property("priority", IntegerType)
            ))
        )),
        Property("payment_method_order", ObjectType(
            Property("category", StringType),
            Property("display_name", StringType),
            Property("priority", IntegerType)
        )),
        Property("phone", StringType),
        Property("purchased_at", IntegerType),
        Property("quantity", IntegerType),
        Property("shipping_address", ObjectType(
            Property("city", StringType),
            Property("country", StringType),
            Property("line1", StringType),
            Property("line2", StringType),
            Property("postal_code", StringType),
            Property("state", StringType)
        )),
        Property("title", StringType),
        Property("total_amount", IntegerType),
        Property("total_tax_amount", IntegerType)
    )),
    Property("multibanco", ObjectType(
        Property("entity", StringType),
        Property("reference", StringType)
    )),
    Property("p24", ObjectType(
        Property("reference", StringType),
        Property("verified_name", StringType)
    )),
    Property("sepa_debit", ObjectType(
        Property("bank_code", StringType),
        Property("branch_code", StringType),
        Property("country", StringType),
        Property("fingerprint", StringType),
        Property("last4", StringType)
    )),
    Property("sofort", ObjectType(
        Property("country", StringType),
        Property("preferred_language", StringType),
        Property("reference", StringType),
        Property("verified_name", StringType)
    )),
    Property("three_d_secure", ObjectType(
        Property("authenticated", BooleanType),
        Property("authentication_flow", StringType),
        Property("result", StringType),
        Property("result_reason", StringType)
    )),
    Property("wechat", ObjectType(
        Property("prepay_id", StringType),
        Property("qr_code_url", StringType),
        Property("qr_code_url_expires_at", IntegerType)
    ))
).to_dict()

exchange_rates_schema = PropertiesList(
    Property("send_currency", StringType),
    Property("receive_currency", StringType),
    Property("rate", NumberType),
    Property("date", DateTimeType),
).to_dict()


report_runs_schema = PropertiesList(
    Property("id", StringType),
    Property("object", StringType),
    Property("created", IntegerType),
    Property("error", StringType),
    Property("livemode", BooleanType),
    Property("parameters", ObjectType(Property("interval_end", IntegerType), Property("interval_start", IntegerType))),
    Property("report_type", StringType),
    Property(
        "result",
        ObjectType(
            Property("id", StringType),
            Property("object", StringType),
            Property("created", IntegerType),
            Property("expires_at", IntegerType),
            Property("filename", StringType),
            Property(
                "links",
                ObjectType(
                    Property("object", StringType),
                    Property("data", ArrayType(ObjectType(Property("id", StringType)))),
                    Property("has_more", BooleanType),
                    Property("url", StringType),
                ),
            ),
            Property("purpose", StringType),
            Property("size", IntegerType),
            Property("title", StringType),
            Property("type", StringType),
            Property("url", StringType),
        ),
    ),
    Property("status", StringType),
    Property("succeeded_at", IntegerType),
).to_dict()


activity_itemized_2_schema = PropertiesList(
    Property("balance_transaction_id", StringType),
    Property("balance_transaction_created_at", DateTimeType),
    Property("balance_transaction_reporting_category", StringType),
    Property("balance_transaction_component", StringType),
    Property("balance_transaction_regulatory_tag", StringType),
    Property("activity_at", DateTimeType),
    Property("currency", StringType),
    Property("amount", NumberType),
    Property("charge_id", StringType),
    Property("payment_intent_id", StringType),
    Property("refund_id", StringType),
    Property("dispute_id", StringType),
    Property("invoice_id", StringType),
    Property("invoice_number", StringType),
    Property("subscription_id", StringType),
    Property("fee_id", StringType),
    Property("transfer_id", StringType),
    Property("destination_id", StringType),
    Property("customer_id", StringType),
    Property("customer_email", StringType),
    Property("customer_description", StringType),
    Property("customer_shipping_address_line1", StringType),
    Property("customer_shipping_address_line2", StringType),
    Property("customer_shipping_address_city", StringType),
    Property("customer_shipping_address_state", StringType),
    Property("customer_shipping_address_postal_code", StringType),
    Property("customer_shipping_address_country", StringType),
    Property("customer_address_line1", StringType),
    Property("customer_address_line2", StringType),
    Property("customer_address_city", StringType),
    Property("customer_address_state", StringType),
    Property("customer_address_postal_code", StringType),
    Property("customer_address_country", StringType),
    Property("shipping_address_line1", StringType),
    Property("shipping_address_line2", StringType),
    Property("shipping_address_city", StringType),
    Property("shipping_address_state", StringType),
    Property("shipping_address_postal_code", StringType),
    Property("shipping_address_country", StringType),
    Property("card_address_line1", StringType),
    Property("card_address_line2", StringType),
    Property("card_address_city", StringType),
    Property("card_address_state", StringType),
    Property("card_address_postal_code", StringType),
    Property("card_address_country", StringType),
    Property("automatic_payout_id", StringType),
    Property("automatic_payout_effective_at", DateTimeType),
    Property("event_type", StringType),
    Property("payment_method_type", StringType),
    Property("is_link", BooleanType),
    Property("card_brand", StringType),
    Property("card_funding", StringType),
    Property("card_country", IntegerType),
    Property("statement_descriptor", StringType),
    Property("customer_facing_currency", StringType),
    Property("customer_facing_amount", NumberType),
    Property("activity_interval_type", StringType),
    Property("activity_start_date", DateTimeType),
    Property("activity_end_date", DateTimeType),
    Property("balance_transaction_description", StringType),
    Property("connected_account_id", StringType),
    Property("connected_account_name", StringType),
    Property("connected_account_country", StringType),
    Property("connected_account_direct_charge_id", StringType),
    Property("activity_itemized_2_id", StringType),
    Property("report_start_at", IntegerType),
    Property("report_end_at", IntegerType),
    Property("loaded_at", DateTimeType),
).to_dict()


activity_summary_1_schema = PropertiesList(
    Property("reporting_category", StringType),
    Property("currency", StringType),
    Property("count", IntegerType),
    Property("gross", NumberType),
    Property("fee", NumberType),
    Property("net", NumberType),
    Property("activity_summary_1_id", StringType),
    Property("report_start_at", IntegerType),
    Property("report_end_at", IntegerType),
    Property("loaded_at", DateTimeType),
).to_dict()


balance_change_from_activity_itemized_2_schema = PropertiesList(
    Property("balance_transaction_id", StringType),
    Property("created_utc", DateTimeType),
    Property("available_on_utc", DateTimeType),
    Property("currency", StringType),
    Property("gross", NumberType),
    Property("fee", NumberType),
    Property("net", NumberType),
    Property("reporting_category", StringType),
    Property("source_id", StringType),
    Property("description", StringType),
    Property("customer_facing_amount", StringType),
    Property("customer_facing_currency", StringType),
    Property("regulatory_tag", StringType),
    Property("automatic_payout_id", StringType),
    Property("automatic_payout_effective_at", DateTimeType),
    Property("customer_id", StringType),
    Property("customer_email", StringType),
    Property("customer_description", StringType),
    Property("customer_shipping_address_line1", StringType),
    Property("customer_shipping_address_line2", StringType),
    Property("customer_shipping_address_city", StringType),
    Property("customer_shipping_address_state", StringType),
    Property("customer_shipping_address_postal_code", StringType),
    Property("customer_shipping_address_country", StringType),
    Property("customer_address_line1", StringType),
    Property("customer_address_line2", StringType),
    Property("customer_address_city", StringType),
    Property("customer_address_state", StringType),
    Property("customer_address_postal_code", StringType),
    Property("customer_address_country", StringType),
    Property("shipping_address_line1", StringType),
    Property("shipping_address_line2", StringType),
    Property("shipping_address_city", StringType),
    Property("shipping_address_state", StringType),
    Property("shipping_address_postal_code", StringType),
    Property("shipping_address_country", StringType),
    Property("card_address_line1", StringType),
    Property("card_address_line2", StringType),
    Property("card_address_city", StringType),
    Property("card_address_state", StringType),
    Property("card_address_postal_code", StringType),
    Property("card_address_country", StringType),
    Property("charge_id", StringType),
    Property("payment_intent_id", StringType),
    Property("charge_created_utc", DateTimeType),
    Property("invoice_id", StringType),
    Property("invoice_number", StringType),
    Property("subscription_id", StringType),
    Property("payment_method_type", StringType),
    Property("is_link", BooleanType),
    Property("card_brand", StringType),
    Property("card_funding", StringType),
    Property("card_country", IntegerType),
    Property("statement_descriptor", StringType),
    Property("dispute_reason", StringType),
    Property("connected_account_id", StringType),
    Property("connected_account_name", StringType),
    Property("connected_account_country", StringType),
    Property("connected_account_direct_charge_id", StringType),
    Property("balance_change_from_activity_itemized_2_id", StringType),
    Property("report_start_at", IntegerType),
    Property("report_end_at", IntegerType),
    Property("loaded_at", DateTimeType),
).to_dict()


balance_change_from_activity_summary_1_schema = PropertiesList(
    Property("reporting_category", StringType),
    Property("currency", StringType),
    Property("count", IntegerType),
    Property("gross", NumberType),
    Property("fee", NumberType),
    Property("net", NumberType),
    Property("balance_change_from_activity_summary_1_id", StringType),
    Property("report_start_at", IntegerType),
    Property("report_end_at", IntegerType),
    Property("loaded_at", DateTimeType),
).to_dict()


curl -G https://api.stripe.com/v1/payment_methods \
  -u "sk_test_Gx4mWEgHtCMr4DYMUIqfIrsz:" \
  -d type=source \
  -d limit=3 \
