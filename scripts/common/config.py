# Centralized project configuration

BUCKET_NAME = "olist-data-engineering-otto"

RAW_BASE_PATH = f"s3://{BUCKET_NAME}/raw"
SILVER_BASE_PATH = f"s3://{BUCKET_NAME}/silver"
GOLD_BASE_PATH = f"s3://{BUCKET_NAME}/gold"

RAW_DATABASE = "olist_raw_db"
SILVER_DATABASE = "olist_silver_db"
GOLD_DATABASE = "olist_gold_db"

DEFAULT_WRITE_MODE = "overwrite"
DEFAULT_FILE_FORMAT = "parquet"