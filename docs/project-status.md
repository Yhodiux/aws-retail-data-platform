# Project Status

Last updated: 2026-06-19

## Current state

The project is a working AWS data engineering demonstration based on the public Olist ecommerce dataset. Existing AWS resources were created manually; the repository now contains a Terraform definition for the target infrastructure alongside the Glue/PySpark jobs, shared library, SQL queries, architecture evidence, and Power BI artifact.

The current pipeline implements:

- Raw, Silver, and Gold layers on Amazon S3.
- AWS Glue jobs and workflow orchestration.
- Five Gold analytical datasets.
- A fail-fast Gold data-quality job.
- Athena consumption and a Power BI dashboard.
- EventBridge and SNS failure notifications documented with screenshots.

Terraform now defines S3, IAM, Glue jobs, crawlers, workflow triggers, Data Catalog databases, EventBridge, and SNS. It validates locally but has not been imported or applied, so the deployed AWS state is not yet reconciled with Terraform state.

## Active phase

### Phase 5 — Terraform infrastructure

Status: implemented and validated locally; AWS import/plan pending

Phase 1 Gold status: local implementation complete; runtime and AWS validation deferred.
Phase 2 Silver status: local implementation and full-source validation complete; AWS runtime validation deferred.
Phase 3 testing status: 10/10 Docker-based PySpark tests passing.

Objective: make the AWS platform reproducible while preserving the existing manually deployed environment through explicit imports and reviewed plans.

Planned work:

- [x] Reorganize and validate the repository at its final local path.
- [x] Define S3, IAM, Glue, Data Catalog, workflow, EventBridge, and SNS resources.
- [x] Publish Glue scripts and `common.zip` through Terraform-managed S3 objects.
- [x] Parameterize bucket, databases, and environment through Glue job arguments.
- [x] Validate Terraform formatting and configuration with Terraform 1.12 and AWS Provider 6.51.0.
- [ ] Import existing AWS resources and review the first Terraform plan.
- [ ] Deploy and validate manually in AWS during the final phase.

Phase 1 confirmed business rules:

- Existing columns will not be removed or renamed, preserving compatibility with Athena queries and Power BI.
- Existing `total_sales` fields remain available as legacy compatibility metrics and retain their current calculation during this phase.
- Completed-sale metrics include only orders whose `order_status` is `delivered`.
- `delivered_product_revenue` is the sum of `order_items.price` for delivered orders.
- `delivered_freight_value` is the sum of `order_items.freight_value` for delivered orders.
- `delivered_payment_value` is the sum of recorded payments for delivered orders.
- `delivered_avg_ticket` is the relevant delivered value divided by distinct delivered orders.
- New metric names must identify the underlying business value instead of using another generic sales alias.
- Non-delivered orders remain represented by the legacy metrics for backward compatibility and may receive explicit operational metrics later.

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 0 | Project documentation and change control | Completed |
| 1 | Gold business definitions and metric consistency | Local complete; AWS deferred |
| 2 | Explicit Silver schemas and stronger data quality | Local complete; runtime/AWS deferred |
| 3 | Local PySpark tests | Completed |
| 4 | Documentation consolidation | Completed |
| 5 | Terraform infrastructure | Local complete; AWS import/apply pending |
| 6 | CI/CD | Not started |
| 7 | Optional Apache Iceberg evaluation | Backlog |

## Working agreement

- Code and documentation changes are made in this repository.
- AWS changes require a reviewed Terraform plan or an explicitly documented manual deployment step.
- Local implementation, tests, and documentation will be completed before AWS deployment begins.
- AWS deployment is deferred to a final consolidated phase and must follow `docs/deployment-guide.md`.
- A local code change is not considered deployed until its AWS validation is recorded here.
- Completed repository changes are recorded in `CHANGELOG.md`.

## Current blockers

No local implementation blocker. AWS account access and the actual Region/resource names are required before importing the existing environment and reviewing a real plan.

## Current checkpoint — 2026-06-19

Local implementation and documentation are complete for all five Gold datasets:

- `sales_by_state`
- `sales_by_category`
- `sales_by_payment_type`
- `top_customers`
- `top_sellers`

Completed validation:

- Repository validation passes for Python syntax, Markdown links, package contents, and source-data exclusion.
- Git diff whitespace validation passed.
- Reference totals were reconciled against the local public Olist CSV snapshot.
- Gold contracts, Athena checks, quality rules, changelog entries, and deferred AWS runbooks were prepared.
- Cross-dataset delivered item, revenue, freight, and payment totals were checked for consistency.
- All 10 Docker-based PySpark tests passed on Apache Spark 3.5.4.
- The packaged `common.zip` imported successfully inside Linux.
- All Markdown links passed a case-sensitive path check.
- Repository documentation and the final deployment order were consolidated.
- Terraform configuration validates with Terraform 1.12 and AWS Provider 6.51.0.
- Glue runtime configuration is parameterized while retaining backward-compatible local defaults.

Remaining runtime limitation:

- AWS Glue-specific initialization, S3 writes, crawlers, workflow triggers, Athena catalog refresh, monitoring, and Power BI refresh still require final AWS validation.

Pending work:

1. Confirm the AWS Region, credentials/profile, and final bucket/resource names.
2. Import existing AWS resources into Terraform state where they should be retained.
3. Review a real Terraform plan and resolve any drift before applying changes.
4. Review and commit the resulting local release.
5. Publish the repository and execute the documented AWS deployment when ready.

Resume point: configure `terraform.tfvars`, inspect the existing AWS account, and prepare resource imports before the first apply.
