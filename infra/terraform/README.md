# Terraform infrastructure

This module provisions the reproducible AWS foundation for the Olist pipeline:

- Versioned, encrypted, private S3 storage.
- Glue IAM role, Data Catalog databases, jobs, crawlers, and workflow triggers.
- Script and shared-library publication to S3.
- EventBridge routing of Glue failures to SNS.

Terraform intentionally does not manage the downloaded Olist CSV files. Upload Raw data separately using the mapping in [Data Source](../../docs/data-source.md).

## Prerequisites

- Terraform 1.6 or later.
- AWS credentials supplied through the standard AWS credential chain.
- A globally unique S3 bucket name.
- `libs/common.zip` rebuilt before planning when shared Python code changes.

## Configure and validate

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out deployment.tfplan
```

The state backend uses the existing versioned project bucket at
`s3://olist-retail-data-dev-us-east-1-793a6f/terraform/dev/terraform.tfstate`. Initialize
it with the temporary MFA profile without storing that profile in Git:

```powershell
terraform init -reconfigure -backend-config="profile=terraform-mfa"
```

Review the plan before applying it. If resources already exist in AWS, import them into this state instead of attempting to create duplicates. In particular, import the existing bucket before the first plan:

```powershell
terraform import aws_s3_bucket.data <bucket-name>
```

Other existing resources require their corresponding Terraform resource addresses, including `for_each` keys for Silver and Gold jobs.

## Runtime flow

The on-demand workflow trigger starts the six core Silver jobs in parallel. Successful Silver jobs start the Silver crawler and referential-quality job. After both pass, five Gold jobs run in parallel, followed by the Gold crawler and Gold quality job.

The Raw crawler is provisioned but remains manually invoked after source-data uploads.

## Environment configuration

Glue jobs receive bucket, database, and environment values as job arguments. The Python configuration retains local defaults so unit tests and existing manual jobs remain backward compatible.

The default Glue runtime is 5.0 because the local suite targets Apache Spark 3.5.4. Confirm availability in the selected Region before applying.
