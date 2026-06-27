# Project Overview

The AWS Retail Data Platform is a portfolio implementation of a medallion-style analytics data lake for the public Olist ecommerce dataset.

## Objective

Demonstrate practical AWS data-engineering skills across ingestion design, PySpark ETL, schema management, data quality, workflow orchestration, SQL analytics, monitoring, and business reporting.

## Flow

```text
Olist CSV -> S3 Raw -> Glue Silver -> S3 Silver -> Glue Gold
          -> S3 Gold -> Data Catalog -> Athena -> Power BI
                                           `-> Analytics API (in progress)
```

Silver applies explicit schemas and table-level quality controls. A separate quality job checks parent-child relationships. Gold produces five backward-compatible analytical datasets with additional delivered-order metrics.

## Operational design

- Glue Workflow coordinates conditional and parallel processing.
- CloudWatch stores Glue logs.
- EventBridge routes Glue failure events to SNS email notifications.
- Athena provides reconciliation and analytical queries.
- The in-progress Analytics API encapsulates Athena access behind a Python Repository -> Service -> Handler structure.
- Docker runs deterministic PySpark tests locally without AWS credentials.

## Current status

The data platform implementation, Terraform-managed AWS deployment, and core Glue workflow validation are complete for the current phase. The Analytics API has been started under `functions/analytics_api/`; it can generate SQL, execute Athena queries, and retrieve results locally, but the Lambda handler, API Gateway integration, and Terraform deployment are still pending.

## Detailed documentation

- [Current status](project-status.md)
- [Silver contracts](silver-data-contracts.md)
- [Gold contracts](gold-data-contracts.md)
- [Logical data model](data_model/logical_model.md)
- [Analytics API](analytics-api.md)
- [Testing guide](testing-guide.md)
- [Final AWS deployment order](deployments/final-deployment-order.md)
