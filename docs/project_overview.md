# Project Overview

The AWS Retail Data Platform is a portfolio implementation of a medallion-style analytics data lake for the public Olist ecommerce dataset.

## Objective

Demonstrate practical AWS data-engineering skills across ingestion design, PySpark ETL, schema management, data quality, workflow orchestration, SQL analytics, monitoring, and business reporting.

## Flow

```text
Olist CSV -> S3 Raw -> Glue Silver -> S3 Silver -> Glue Gold
          -> S3 Gold -> Data Catalog -> Athena -> Power BI
                                           ^
                                           |
                                      AWS Lambda
                                           ^
                                           |
                                      API Gateway
                                           ^
                                           |
                                      HTTP Client
```

Silver applies explicit schemas and table-level quality controls. A separate quality job checks parent-child relationships. Gold produces five backward-compatible analytical datasets with additional delivered-order metrics.

## Operational design

- The Analytics API encapsulates Athena access behind a Python Repository -> Service -> Handler structure.
- The API supports all five Gold analytical operations: `sales_by_state`, `sales_by_category`, `sales_by_payment_type`, `top_customers`, and `top_sellers`.
- The Lambda handler provides operation routing and validated result limits while keeping SQL and Athena integration outside the handler layer.
- Terraform manages the Analytics Lambda, IAM permissions, Amazon API Gateway HTTP API, Lambda proxy integration, routing, and invocation permissions.
- All five analytical operations have been validated through the deployed Lambda against Athena and `olist_gold_db`.
- The HTTP path has been validated end to end through API Gateway -> Lambda -> Athena -> Glue Data Catalog / S3 Gold -> JSON response.

## Current status

The data platform implementation, Terraform-managed AWS deployment, and core Glue workflow validation are complete for the current phase.

The Analytics API under `functions/analytics_api/` is deployed as the `olist-analytics-api-dev` AWS Lambda using Python 3.13 and exposed through an Amazon API Gateway HTTP API. All five Gold analytical operations are implemented, covered by automated tests, and validated through the deployed Lambda against Athena and `olist_gold_db`.

The HTTP API exposes `GET /analytics`, supports operation selection and validated result limits, and has been validated end to end through API Gateway, Lambda, Athena, the Glue Data Catalog, S3 Gold data, and JSON response delivery.

The current Analytics API scope is complete. Further work such as authentication, enhanced observability, throttling, richer filtering, and CI/CD is considered enhancement work.

## Detailed documentation

- [Current status](project-status.md)
- [Silver contracts](silver-data-contracts.md)
- [Gold contracts](gold-data-contracts.md)
- [Logical data model](data_model/logical_model.md)
- [Analytics API](analytics-api.md)
- [Testing guide](testing-guide.md)
- [Final AWS deployment order](deployments/final-deployment-order.md)
