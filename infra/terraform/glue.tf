resource "aws_glue_catalog_database" "raw" {
  name        = local.raw_database
  description = "Raw layer for Olist ecommerce dataset"
}

resource "aws_glue_catalog_database" "silver" {
  name        = local.silver_database
  description = "Silver layer for Olist ecommerce dataset"
}

resource "aws_glue_catalog_database" "gold" {
  name        = local.gold_database
  description = "Gold layer for Olist ecommerce analytics"
}

resource "aws_glue_job" "silver" {
  name              = "olist-silver-generic-job"
  role_arn          = data.aws_iam_role.glue.arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = 30
  execution_class   = "STANDARD"

  command {
    name            = "glueetl"
    python_version  = "3"
    script_location = "s3://${var.data_bucket_name}/${local.artifact_keys.silver_generic}"
  }

  default_arguments = merge(local.common_job_arguments, {
    "--TABLE_NAME"                   = "order_items"
    "--TempDir"                      = "s3://${var.data_bucket_name}/temp/"
    "--spark-event-logs-path"        = "s3://${var.data_bucket_name}/logs/silver/"
    "--enable-glue-datacatalog"      = "true"
    "--enable-job-insights"          = "true"
    "--enable-observability-metrics" = "true"
    "--enable-spark-ui"              = "true"
    "--job-bookmark-option"          = "job-bookmark-disable"
  })

  depends_on = [aws_s3_object.common_zip, aws_s3_object.silver_generic]
}

resource "aws_glue_job" "gold" {
  for_each = local.gold_jobs

  name              = each.value.name
  role_arn          = data.aws_iam_role.glue.arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = 30
  execution_class   = "STANDARD"

  command {
    name            = "glueetl"
    python_version  = "3"
    script_location = "s3://${var.data_bucket_name}/${each.value.key}"
  }

  default_arguments = merge(local.common_job_arguments, {
    "--TempDir"                      = "s3://${var.data_bucket_name}/temp/"
    "--spark-event-logs-path"        = "s3://${var.data_bucket_name}/logs/gold/"
    "--enable-glue-datacatalog"      = "true"
    "--enable-job-insights"          = "true"
    "--enable-observability-metrics" = "true"
    "--enable-spark-ui"              = "true"
    "--job-bookmark-option"          = "job-bookmark-disable"
  })

  depends_on = [aws_s3_object.common_zip, aws_s3_object.gold_scripts]
}

resource "aws_glue_job" "gold_quality" {
  name              = "olist-data-quality-gold-job"
  role_arn          = data.aws_iam_role.glue.arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = 30
  execution_class   = "STANDARD"

  command {
    name            = "glueetl"
    python_version  = "3"
    script_location = "s3://${var.data_bucket_name}/${local.artifact_keys.gold_quality}"
  }

  default_arguments = merge(local.common_job_arguments, {
    "--TempDir"                      = "s3://aws-glue-assets-746552104319-us-east-1/temporary/"
    "--spark-event-logs-path"        = "s3://aws-glue-assets-746552104319-us-east-1/sparkHistoryLogs/"
    "--enable-glue-datacatalog"      = "true"
    "--enable-job-insights"          = "true"
    "--enable-observability-metrics" = "true"
    "--enable-spark-ui"              = "true"
    "--job-bookmark-option"          = "job-bookmark-disable"
  })

  depends_on = [aws_s3_object.common_zip, aws_s3_object.gold_quality]
}

resource "aws_glue_crawler" "raw" {
  database_name = aws_glue_catalog_database.raw.name
  name          = "olist-raw-crawler"
  role          = data.aws_iam_role.glue.arn
  description   = "Discovers Olist raw CSV datasets from S3 and creates Glue Catalog tables"
  configuration = jsonencode({ Version = 1.0, CreatePartitionIndex = true })
  s3_target {
    path       = "s3://${var.data_bucket_name}/raw/"
    exclusions = []
  }
}

resource "aws_glue_crawler" "silver" {
  database_name = aws_glue_catalog_database.silver.name
  name          = "olist-silver-crawler"
  role          = data.aws_iam_role.glue.arn
  configuration = jsonencode({ Version = 1.0, CreatePartitionIndex = true })
  dynamic "s3_target" {
    for_each = ["customers", "orders", "order_items", "payments", "products", "sellers"]
    content {
      path       = "s3://${var.data_bucket_name}/silver/${s3_target.value}/"
      exclusions = []
    }
  }
}

resource "aws_glue_crawler" "gold" {
  database_name = aws_glue_catalog_database.gold.name
  name          = "olist-gold-crawler"
  role          = data.aws_iam_role.glue.arn
  configuration = jsonencode({ Version = 1.0, CreatePartitionIndex = true })
  dynamic "s3_target" {
    for_each = ["sales_by_state", "sales_by_category", "sales_by_payment_type", "top_sellers", "top_customers"]
    content {
      path       = "s3://${var.data_bucket_name}/gold/${s3_target.value}/"
      exclusions = []
    }
  }
}

resource "aws_glue_workflow" "pipeline" {
  name        = "olist-retail-etl-workflow"
  description = "Enterprise ETL Workflow for Olist Retail Data Platform. Orchestrates Silver and Gold layers using AWS Glue Jobs and conditional triggers."
  tags = {
    Project     = "OLIST"
    Environment = "Dev"
    Owner       = "Otto"
    Layer       = "ETL"
  }
}

resource "aws_glue_trigger" "start" {
  name          = "start-silver-trigger"
  type          = "ON_DEMAND"
  workflow_name = aws_glue_workflow.pipeline.name
  enabled       = false
  actions { job_name = aws_glue_job.silver.name }
}

resource "aws_glue_trigger" "silver_success" {
  name          = "silver-success-trigger"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.pipeline.name

  dynamic "actions" {
    for_each = local.gold_action_order
    content { job_name = aws_glue_job.gold[actions.value].name }
  }

  predicate {
    logical = "ANY"
    conditions {
      job_name         = aws_glue_job.silver.name
      logical_operator = "EQUALS"
      state            = "SUCCEEDED"
    }
  }
}

resource "aws_glue_trigger" "gold_success" {
  name          = "gold-success-trigger"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.pipeline.name
  actions { job_name = aws_glue_job.gold_quality.name }

  predicate {
    logical = "AND"
    dynamic "conditions" {
      for_each = local.gold_condition_order
      content {
        job_name         = aws_glue_job.gold[conditions.value].name
        logical_operator = "EQUALS"
        state            = "SUCCEEDED"
      }
    }
  }
}
