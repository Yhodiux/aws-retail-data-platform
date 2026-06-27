import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "olist_gold_db")
ATHENA_OUTPUT_LOCATION = os.getenv(
    "ATHENA_OUTPUT_LOCATION",
    "s3://olist-retail-data-dev-us-east-1-793a6f/athena/query-results/"
)