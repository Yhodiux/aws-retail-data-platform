output "data_bucket_name" {
  value = aws_s3_bucket.data.id
}

output "glue_workflow_name" {
  value = aws_glue_workflow.pipeline.name
}

output "glue_role_arn" {
  value = data.aws_iam_role.glue.arn
}

output "catalog_databases" {
  value = {
    raw    = aws_glue_catalog_database.raw.name
    silver = aws_glue_catalog_database.silver.name
    gold   = aws_glue_catalog_database.gold.name
  }
}

output "failure_topic_arn" {
  value = aws_sns_topic.glue_failures.arn
}
