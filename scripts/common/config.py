"""Centralized project configuration with Glue-argument overrides."""

import sys


def _argument_or_default(name, default):
    option = f"--{name}"
    try:
        index = sys.argv.index(option)
        return sys.argv[index + 1]
    except (ValueError, IndexError):
        return default

BUCKET_NAME = _argument_or_default(
    "PROJECT_BUCKET", "olist-retail-data-dev-us-east-1-793a6f"
)

RAW_BASE_PATH = f"s3://{BUCKET_NAME}/raw"
SILVER_BASE_PATH = f"s3://{BUCKET_NAME}/silver"
GOLD_BASE_PATH = f"s3://{BUCKET_NAME}/gold"

LOGS_BASE_PATH = f"s3://{BUCKET_NAME}/logs"
TEMP_BASE_PATH = f"s3://{BUCKET_NAME}/temp"

RAW_DATABASE = _argument_or_default("RAW_DATABASE", "olist_raw_db")
SILVER_DATABASE = _argument_or_default("SILVER_DATABASE", "olist_silver_db")
GOLD_DATABASE = _argument_or_default("GOLD_DATABASE", "olist_gold_db")

DEFAULT_WRITE_MODE = "overwrite"
DEFAULT_FILE_FORMAT = "parquet"

PROJECT_NAME = "Olist Retail Data Platform"
ENVIRONMENT = _argument_or_default("ENVIRONMENT", "dev")
