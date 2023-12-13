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

activity_summary_1 = PropertiesList(
    Property("reporting_category", StringType),
    Property("currency", StringType),
    Property("count", IntegerType),
    Property("gross", NumberType),
    Property("fee", NumberType),
    Property("net", NumberType),
).to_dict()
