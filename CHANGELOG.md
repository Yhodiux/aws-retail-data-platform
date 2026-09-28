# Changelog

All notable repository changes will be documented in this file. AWS deployment status is tracked separately in `docs/project-status.md`.

## [Unreleased]

### Added

- Project status and phased roadmap.
- Manual AWS deployment and rollback guide.
- Olist source dataset documentation and Raw S3 mapping.
- Git exclusions for local source data and generated Python files.
- Gold data contract for `sales_by_state`.
- Athena reconciliation queries for delivered state metrics.
- A deployment and rollback runbook for the `sales_by_state` change, including reference totals from the source snapshot.
- Gold data contract, Athena reconciliation queries, and final-phase deployment runbook for `sales_by_category`.
- Gold data contract, Athena reconciliation queries, and final-phase deployment runbook for `sales_by_payment_type`.
- Gold data contract, Athena reconciliation queries, and final-phase deployment runbook for `top_customers`.
- Gold data contract, Athena reconciliation queries, and final-phase deployment runbook for `top_sellers`.
- Centralized explicit PySpark schemas for all nine public Olist datasets.
- Reproducible shared-library packaging script.
- Silver data-contract documentation, full-source validation baseline, and deferred deployment runbook.
- Centralized Silver quality rules and reusable DataFrame validation framework.
- Silver referential-integrity Glue job with persistent date-partitioned audit results.
- Docker-based Apache Spark 3.5.4 test runner and 10 deterministic PySpark tests.
- Reusable Silver and Gold transformation modules shared by Glue jobs and local tests.
- Local testing guide requiring no AWS credentials or global Java installation.
- Consolidated final AWS deployment and rollback order.
- Repository review with verified controls, known gaps, and release options.
- Git attributes for consistent text line endings and binary artifact handling.
- Repeatable repository validator for Python syntax, Markdown links, package contents, and source-data exclusion.
- Terraform infrastructure for S3, IAM, Glue jobs, crawlers, workflow orchestration, Data Catalog, EventBridge, and SNS.
- In-progress Lambda Analytics API documentation covering the Repository -> Service -> Handler pattern, Athena query generation, Athena service integration, pytest coverage, local example execution, and deployment roadmap.
- Terraform-managed IAM role and least-privilege access policy for the Analytics Lambda.
- Terraform-managed deployment of `olist-analytics-api-dev` using the Python 3.13 Lambda runtime.
- Terraform Archive provider packaging for the Analytics API Lambda artifact.
- Successful AWS Lambda invocation validating the Analytics API end to end against Athena and `olist_gold_db`.
- Analytics API query support for all five Gold analytical datasets: `sales_by_state`, `sales_by_category`, `sales_by_payment_type`, `top_customers`, and `top_sellers`.
- Handler routing with configurable analytical operation and validated result limits from 1 to 100.
- Pytest coverage for Analytics API repositories, service delegation, handler routing, input validation, and API Gateway query parameters, reaching 22 passing tests.
- Terraform-managed Amazon API Gateway HTTP API exposing the Analytics API through `GET /analytics`.
- API Gateway Lambda proxy integration, automatic `$default` stage deployment, CORS configuration, and least-privilege Lambda invocation permission.
- Terraform output for the deployed Analytics API HTTP endpoint.
- GitHub Actions CI/CD workflows for Terraform Plan and controlled Terraform Apply deployments.
- GitHub OIDC authentication with a dedicated AWS IAM role, eliminating long-lived AWS access keys from the CI/CD deployment path.
- Post-deployment Analytics API smoke test that resolves the deployed endpoint from Terraform output and requires an HTTP 200 response.
- Terraform-managed Amazon CloudWatch alarms for Analytics API Lambda execution errors and high execution duration.
- Amazon SNS integration for Analytics API CloudWatch alarm email notifications.
- Monitoring evidence for the validated CloudWatch -> SNS -> email alert path in `docs/screenshots/mail.png`.

### Changed

- Added project governance documentation links to the README.
- Confirmed a backward-compatible Gold metric strategy: existing fields remain available while explicit delivered-order metrics will be added.
- Extended `sales_by_state` with delivered-order counts, item counts, product revenue, freight value, and average ticket while preserving every existing column.
- Extended Gold quality rules for the new `sales_by_state` metrics.
- Deferred AWS deployment until local implementation, tests, and documentation are complete; deployment runbooks remain prepared for the final phase.
- Extended `sales_by_category` with delivered-order, item, product-revenue, freight, average-item-price, and average-ticket metrics while preserving all existing columns.
- Extended Gold quality rules for the new `sales_by_category` metrics.
- Extended `sales_by_payment_type` with explicit payment-record and delivered-order metrics while preserving all existing columns.
- Extended Gold quality rules for the new `sales_by_payment_type` metrics.
- Removed an unused `order_items` read from `sales_by_payment_type` to reduce Glue I/O without changing results.
- Extended `top_customers` with explicit payment-record, delivered-order, value, and purchase-date metrics while preserving all existing columns.
- Extended Gold quality rules for the new `top_customers` metrics.
- Extended `top_sellers` with delivered-order, item, revenue, freight, average, and activity-period metrics while preserving all existing columns.
- Extended Gold quality rules for the new `top_sellers` metrics.
- Completed the backward-compatible local implementation and static review for all five Gold datasets; AWS runtime validation remains deferred.
- Replaced Silver CSV schema inference with explicit schemas, strict header enforcement, fail-fast parsing, fixed timestamp formats, and multiline review support.
- Centralized Silver S3 paths and logging through the shared common library.
- Rebuilt `libs/common.zip` with the schema registry and explicit package initialization.
- Added fail-fast Silver checks for empty datasets, required fields, unique keys, allowed domains, ranges, and non-negative values.
- Added five core cross-table relationship checks for Silver datasets.
- Rebuilt `libs/common.zip` with schemas, table-level validation logic, and centralized quality rules for the final deployment phase.
- Refactored Glue jobs to delegate DataFrame logic to testable shared transformation functions without changing their S3 inputs or outputs.
- Replaced Windows-native ZIP creation with a portable builder that emits Linux-compatible package paths for AWS Glue.
- Consolidated the README, project overview, logical data model, project status, and deployment documentation against the current repository implementation.
- Reframed the implementation as a medallion-style data lake; Apache Iceberg remains an optional future enhancement for ACID lakehouse capabilities.
- Recorded the release sequence decision: manual repository reorganization, Terraform implementation, repository publication, and final AWS deployment.
- Changed repository validation to reject tracked CSV files while allowing ignored local source snapshots.
- Parameterized Glue bucket, database, and environment configuration through job arguments with backward-compatible defaults.
- Migrated the AWS pipeline to a non-personal, versioned S3 bucket and reconciled existing resources into Terraform state.
- Added least-privilege Glue access to the new bucket and completed isolated Silver/Gold, crawler, Gold-quality, and end-to-end workflow validation in AWS.
- Promoted the Analytics API from a local-only foundation to a deployed AWS Lambda implementation.
- Validated the deployed `sales_by_state` path end to end: Lambda -> Athena -> `olist_gold_db` -> S3 query results -> JSON response.
- Renamed the serverless source directory from `lambda` to `functions` to avoid naming ambiguity and aligned the implementation and documentation with the new structure.
- Expanded `AthenaQueries` and `AthenaService` from `sales_by_state` only to all five Gold analytical datasets.
- Evolved the Lambda handler from a single fixed query to backward-compatible operation routing supporting both direct Lambda events and API Gateway HTTP query parameters.
- Redeployed `olist-analytics-api-dev` with multi-operation routing while preserving the default `sales_by_state` behavior.
- Validated all five analytical operations end to end through the deployed Lambda against Athena and `olist_gold_db`.
- Exposed and validated the Analytics API over HTTP through API Gateway, including default `sales_by_state` requests and parameterized `top_sellers` requests.
- Extended the GitHub Actions deployment workflow with an automated post-deployment Analytics API smoke test.
- Extended platform observability from Glue job monitoring to Analytics API Lambda error and duration monitoring.
- Extended the existing SNS alerting path to include Analytics API CloudWatch alarms.
- Validated the complete Terraform deployment workflow through GitHub Actions, including infrastructure deployment and a successful live API smoke test.
- Updated the README and architecture documentation to reflect the deployed Analytics API, CI/CD workflow, observability, alerting, and post-deployment validation.
