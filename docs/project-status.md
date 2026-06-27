# Project Status

Last updated: 2026-06-26

## Current state

The project is a working AWS data engineering demonstration based on the public Olist ecommerce dataset. Existing AWS resources were created manually; the repository now contains a Terraform definition for the target infrastructure alongside the Glue/PySpark jobs, shared library, SQL queries, architecture evidence, and Power BI artifact.

The current pipeline implements:

- Raw, Silver, and Gold layers on Amazon S3.
- AWS Glue jobs and workflow orchestration.
- Five Gold analytical datasets.
- A fail-fast Gold data-quality job.
- Athena consumption and a Power BI dashboard.
- EventBridge and SNS failure notifications documented with screenshots.

The repository also contains an in-progress Analytics API under `functions/analytics_api/`. This API layer is not deployed yet. It currently provides the foundation for generating Athena SQL, executing Athena queries through `boto3`, and retrieving results from the configured Athena output location.

Terraform now defines S3, IAM, Glue jobs, crawlers, workflow triggers, Data Catalog databases, EventBridge, and SNS. It validates locally but has not been imported or applied, so the deployed AWS state is not yet reconciled with Terraform state.

## Active phase

### Phase 5 — Terraform infrastructure

Status: implemented and validated locally; AWS import/plan pending

Phase 1 Gold status: local implementation complete; runtime and AWS validation deferred.
Phase 2 Silver status: local implementation and full-source validation complete; AWS runtime validation deferred.
Phase 3 testing status: 10/10 Docker-based PySpark tests passing.
Analytics API status: local foundation started; Lambda deployment pending.

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

### Phase 6 - Analytics API foundation

Status: local foundation started; Lambda deployment pending

During this phase, a new Analytics API structure was created under `functions/analytics_api/`.

Implemented structure:

- `repositories/`
- `services/`
- `tests/`
- `utils/`
- `examples/`
- `handler.py`
- `config.py`
- `requirements.txt`

The API follows a `Repository -> Service -> Handler` pattern:

- Repository classes generate SQL only.
- Service classes communicate with AWS services.
- The Lambda handler remains a thin entry point and is still in construction.

Current components:

- `AthenaQueries.sales_by_state()` builds the SQL for `sales_by_state`.
- `AthenaService.execute_query()` starts Athena query execution.
- `AthenaService.wait_for_completion()` waits for terminal Athena states.
- `AthenaService.get_results()` retrieves Athena result rows.
- `AthenaService.run_query()` orchestrates execution, waiting, and result retrieval.

Testing added:

- Unit test: `functions/analytics_api/tests/repositories/test_athena_queries.py`.
- Integration test: `functions/analytics_api/tests/services/test_athena_service.py`.

The integration test validates the path from Python to `boto3`, Amazon Athena, the AWS Glue Data Catalog, S3 Gold data, and query results. It has been executed successfully in the current development environment.

Local example:

- `functions/analytics_api/examples/run_sales_by_state.py`.

Architecture decisions:

- Separate Repository and Service responsibilities.
- Keep SQL isolated from consumers.
- Use `pytest` for Analytics API tests.
- Separate unit tests from integration tests.
- Build the API architecture before deployment.
- Keep the Lambda handler thin and free of business logic.

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 0 | Project documentation and change control | Completed |
| 1 | Gold business definitions and metric consistency | Local complete; AWS deferred |
| 2 | Explicit Silver schemas and stronger data quality | Local complete; runtime/AWS deferred |
| 3 | Local PySpark tests | Completed |
| 4 | Documentation consolidation | Completed |
| 5 | Terraform infrastructure | Local complete; AWS import/apply pending |
| 6 | Analytics API foundation | Local foundation started; deployment pending |
| 7 | CI/CD | Not started |
| 8 | Optional Apache Iceberg evaluation | Backlog |

## Working agreement

- Code and documentation changes are made in this repository.
- AWS changes require a reviewed Terraform plan or an explicitly documented manual deployment step.
- Local implementation, tests, and documentation will be completed before AWS deployment begins.
- AWS deployment is deferred to a final consolidated phase and must follow `docs/deployment-guide.md`.
- A local code change is not considered deployed until its AWS validation is recorded here.
- Completed repository changes are recorded in `CHANGELOG.md`.
- The Analytics API remains part of this repository only at this stage; it is not documented as an ALCAZ component.

## Current blockers

No local implementation blocker. AWS account access and the actual Region/resource names are required before importing the existing environment and reviewing a real plan.

For the Analytics API, deployment is intentionally pending until the service-level business methods, Lambda handler, API Gateway integration, and Terraform automation are completed.

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

Analytics API roadmap:

1. Complete `AthenaService` with business methods such as `sales_by_state`, `top_customers`, `top_sellers`, `sales_by_category`, and `sales_by_payment_type`.
2. Implement the Lambda handler.
3. Integrate API Gateway.
4. Automate deployment through Terraform.
5. Incorporate final technical documentation and diagrams.

Resume point: complete Athena reconciliation, deploy/run Silver referential validation, validate Power BI refresh, and retire the legacy bucket only after downstream sign-off.

## AWS deployment record — 2026-06-20

- Commit: `14dcc0d`.
- Region: `us-east-1`.
- Terraform apply: 18 resources updated in place; none created or destroyed.
- Data bucket: `olist-retail-data-dev-us-east-1-793a6f`.
- Terraform state: remote, encrypted, locked, and versioned in S3.
- Glue IAM access: least-privilege inline policy for the new data bucket.
- Core Silver isolated validation: `customers`, `orders`, `products`, `sellers`, `order_items`, and `payments` succeeded.
- Silver crawler: succeeded against the new bucket.
- Five isolated Gold jobs: succeeded.
- Gold crawler: succeeded; canonical tables were rebuilt against the new locations and schemas.
- Gold quality retry: succeeded (`jr_6fcc9c46c4d1b5bc9a2c24fd55af70449091bda282ab8b458512e85879e3fb7f`).
- Complete workflow: succeeded (`wr_b458d74ded2ad229d99690a887f659776f48ea065fa9f5849f5c866ff67d4593`).
- Terraform post-deployment plan: no drift.

Remaining validation:

- Deploy and run the Silver referential-integrity job.
- Execute Athena reconciliation queries.
- Refresh and validate Power BI.
- Keep the legacy bucket unchanged until all downstream checks pass.

## Restart checkpoint — 2026-06-20

Safe shutdown state:

- AWS deployment and end-to-end workflow validation are complete.
- Terraform reports no drift and uses remote state in the new versioned bucket.
- No AWS resource deletion is pending.
- The legacy bucket `olist-data-engineering-otto` remains intact as rollback evidence.
- The active data bucket is `olist-retail-data-dev-us-east-1-793a6f`.
- Local branch `main` contains deployment commits `14dcc0d` and `ff595b8` ahead of `origin/main`.
- Saved `.tfplan` files are local/ignored and must not be reused after future state changes; generate a fresh plan.

After restarting:

1. Recreate the temporary MFA session with `aws configure mfa-login --profile default --update-profile terraform-mfa --serial-number arn:aws:iam::746552104319:mfa/UserYhodiux --duration-seconds 43200`.
2. Run `terraform plan` and require no drift before further AWS work.
3. Deploy and run the Silver referential-integrity job.
4. Execute Athena reconciliation queries.
5. Validate the Power BI refresh.
6. Retire the legacy bucket only after all downstream checks pass.
