# Project Overview

The AWS Retail Data Platform is a portfolio implementation of a medallion-style analytics data lake for the public Olist ecommerce dataset.

## Objective

Demonstrate practical AWS data-engineering skills across ingestion design, PySpark ETL, schema management, data quality, workflow orchestration, SQL analytics, monitoring, and business reporting.

## Flow

```text
Olist CSV -> S3 Raw -> Glue Silver -> S3 Silver -> Glue Gold
          -> S3 Gold -> Data Catalog -> Athena -> Power BI
```

Silver applies explicit schemas and table-level quality controls. A separate quality job checks parent-child relationships. Gold produces five backward-compatible analytical datasets with additional delivered-order metrics.

## Operational design

- Glue Workflow coordinates conditional and parallel processing.
- CloudWatch stores Glue logs.
- EventBridge routes Glue failure events to SNS email notifications.
- Athena provides reconciliation and analytical queries.
- Docker runs deterministic PySpark tests locally without AWS credentials.

## Current status

Local implementation and tests are complete. AWS deployment and runtime validation of the new code are deferred to a final controlled phase. Infrastructure as Code and CI/CD remain roadmap items.

## Detailed documentation

- [Current status](project-status.md)
- [Silver contracts](silver-data-contracts.md)
- [Gold contracts](gold-data-contracts.md)
- [Logical data model](data_model/logical_model.md)
- [Testing guide](testing-guide.md)
- [Final AWS deployment order](deployments/final-deployment-order.md)
