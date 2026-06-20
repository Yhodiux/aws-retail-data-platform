locals {
  resource_prefix = "${var.project_name}-${var.environment}"

  raw_database    = "olist_raw_db"
  silver_database = "olist_silver_db"
  gold_database   = "olist_gold_db"

  gold_jobs = {
    sales_by_state        = { name = "olist-gold-sales-by-state-job", source = "scripts/gold/build_gold_sales_by_state.py", key = "scripts/gold/olist-gold-sales-by-state-job.py" }
    sales_by_category     = { name = "olist-gold-sales-by-category-job", source = "scripts/gold/build_gold_sales_by_category.py", key = "scripts/gold/olist-gold-sales-by-category-job.py" }
    sales_by_payment_type = { name = "olist-gold-sales-by-payment-type-job", source = "scripts/gold/build_gold_sales_by_payment_type.py", key = "scripts/gold/olist-gold-sales-by-payment-type-job.py" }
    top_customers         = { name = "olist-gold-top-customers-job", source = "scripts/gold/build_gold_top_customers.py", key = "scripts/gold/olist-gold-top-customers-job.py" }
    top_sellers           = { name = "olist-gold-top-sellers-job", source = "scripts/gold/build_gold_top_sellers.py", key = "scripts/gold/olist-gold-top-sellers-job.py" }
  }

  gold_action_order = [
    "sales_by_state",
    "sales_by_category",
    "sales_by_payment_type",
    "top_customers",
    "top_sellers",
  ]

  gold_condition_order = [
    "top_customers",
    "sales_by_state",
    "sales_by_category",
    "sales_by_payment_type",
    "top_sellers",
  ]

  artifact_keys = {
    common_zip     = "libs/common.zip"
    silver_generic = "scripts/silver/olist-silver-generic-job.py"
    gold_quality   = "scripts/quality/olist-data-quality-gold-job.py"
  }

  common_job_arguments = {
    "--PROJECT_BUCKET"                   = var.data_bucket_name
    "--RAW_DATABASE"                     = local.raw_database
    "--SILVER_DATABASE"                  = local.silver_database
    "--GOLD_DATABASE"                    = local.gold_database
    "--ENVIRONMENT"                      = var.environment
    "--extra-py-files"                   = "s3://${var.data_bucket_name}/${local.artifact_keys.common_zip}"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--job-language"                     = "python"
    "--conf"                             = "spark.eventLog.rolling.enabled=true --conf spark.sql.catalog.glue_catalog.glue.skip-name-validation=true"
  }

}
