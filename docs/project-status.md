# Project Status

Last updated: 2026-09-27

## Current state

The project is a working AWS data engineering demonstration based on the public Olist ecommerce dataset. Existing AWS resources were created manually; the repository now contains a Terraform definition for the target infrastructure alongside the Glue/PySpark jobs, shared library, SQL queries, architecture evidence, and Power BI artifact.

The current pipeline implements:

- Raw, Silver, and Gold layers on Amazon S3.
- AWS Glue jobs and workflow orchestration.
- Five Gold analytical datasets.
- A fail-fast Gold data-quality job.
- Athena consumption and a Power BI dashboard.
- EventBridge and SNS failure notifications documented with screenshots.

The repository also contains a deployed Analytics API under `functions/analytics_api/`. The implementation provides SQL generation and Athena integration for all five Gold analytical datasets, multi-operation Lambda routing, validated result limits, automated pytest coverage, Terraform-managed AWS Lambda deployment, and an Amazon API Gateway HTTP API. All five analytical operations have been validated through the deployed Lambda, and the HTTP path has been validated end to end through API Gateway.

Terraform manages the active AWS platform, including S3, IAM, Glue jobs, crawlers, workflow triggers, Data Catalog databases, EventBridge, SNS, and the Analytics Lambda infrastructure. The core data platform was reconciled and validated in AWS during the June deployment, and the Analytics Lambda IAM and runtime resources were added in September.

## Active phase

### Phase 5 — Analytics API

Status: Analytics API deployed and validated end to end through Lambda, Athena, and API Gateway

Phase 1 Gold status: local implementation complete; runtime and AWS validation deferred.
Phase 2 Silver status: local implementation and full-source validation complete; AWS runtime validation deferred.
Phase 3 testing status: 10/10 Docker-based PySpark tests passing.
Analytics API status: all five Gold analytical operations are implemented, tested, deployed, and validated through AWS Lambda; API Gateway HTTP access is deployed and validated.

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

### Phase 6 - Analytics API

Status: Completed for the current project scope

The Analytics API is implemented under `functions/analytics_api/` and follows a `Repository -> Service -> Handler` pattern exposed through Amazon API Gateway.

Implemented structure:

- `repositories/`
- `services/`
- `tests/`
- `utils/`
- `examples/`
- `handler.py`
- `config.py`
- `requirements.txt`

Architecture responsibilities:

- Repository classes generate SQL only.
- Service classes encapsulate communication with Amazon Athena.
- The Lambda handler validates and routes requests while remaining free of SQL and Athena implementation details.
- Amazon API Gateway exposes the Lambda through `GET /analytics`.

Supported analytical operations:

- `sales_by_state`
- `sales_by_category`
- `sales_by_payment_type`
- `top_customers`
- `top_sellers`

The handler supports both direct Lambda invocation and API Gateway HTTP query parameters. Requests may specify an analytical `operation` and a `limit` between 1 and 100. The default operation remains `sales_by_state` with a default limit of 10.

Current components:

- `AthenaQueries` generates SQL for all five Gold analytical datasets.
- `AthenaService.execute_query()` starts Athena query execution.
- `AthenaService.wait_for_completion()` waits for terminal Athena states.
- `AthenaService.get_results()` retrieves Athena result rows.
- `AthenaService.run_query()` orchestrates execution, waiting, and result retrieval.
- `AthenaService` exposes business methods for all five analytical operations.
- `handler.lambda_handler()` validates input, routes operations, delegates to the service layer, and returns HTTP-style JSON responses.
- `utils/response.py` centralizes successful response formatting.

Testing:

- Repository query tests cover all five Gold analytical operations.
- Service tests cover business-method delegation and retain real Athena integration coverage.
- Handler tests cover routing, defaults, limits, invalid input, unsupported operations, and API Gateway query parameters.
- Current Analytics API test suite: 22/22 tests passing.

AWS deployment:

- AWS Lambda `olist-analytics-api-dev` is deployed using Python 3.13.
- Terraform manages Lambda packaging, deployment, IAM permissions, and environment configuration.
- Terraform manages the Amazon API Gateway HTTP API, Lambda proxy integration, `GET /analytics` route, `$default` stage, CORS configuration, and Lambda invocation permission.
- All five analytical operations have been validated through real Lambda invocations against Athena and `olist_gold_db`.
- HTTP requests through API Gateway have been validated for the default `sales_by_state` operation and a parameterized `top_sellers` request.

Architecture decisions:

- Separate Repository, Service, and Handler responsibilities.
- Keep SQL isolated from API consumers.
- Keep the Lambda handler thin and free of Athena implementation logic.
- Preserve backward compatibility for direct Lambda invocation.
- Validate API inputs before invoking Athena.
- Manage serverless infrastructure through Terraform.
- Use `pytest` for automated API testing.

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 0 | Project documentation and change control | Completed |
| 1 | Gold business definitions and metric consistency | Local complete; AWS deferred |
| 2 | Explicit Silver schemas and stronger data quality | Local complete; runtime/AWS deferred |
| 3 | Local PySpark tests | Completed |
| 4 | Documentation consolidation | Completed |
| 5 | Terraform infrastructure | Deployed and validated in AWS |
| 6 | Analytics API | Completed for current scope; Lambda and API Gateway deployed and validated |
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

No current infrastructure blocker. AWS access, Terraform remote state, and the active `us-east-1` environment have been validated.

The Analytics API has no current implementation blocker for the defined scope. Future API work is considered enhancement work rather than completion work.

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

Analytics API roadmap status:

The original Analytics API roadmap has been completed for the current scope: all five Gold operations, Lambda routing, Terraform deployment, API Gateway integration, automated testing, and end-to-end HTTP validation are implemented. Future work is tracked as optional enhancement work.

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

## Analytics API deployment checkpoint — 2026-09-27

Current state:

- Analytics API source lives under `functions/analytics_api/`.
- Repository -> Service -> Handler architecture is implemented for all five Gold analytical datasets.
- Supported operations are `sales_by_state`, `sales_by_category`, `sales_by_payment_type`, `top_customers`, and `top_sellers`.
- Handler routing supports both direct Lambda events and API Gateway HTTP query parameters.
- Result limits are validated between 1 and 100, with a default of 10.
- Complete Analytics API pytest suite passes: 22/22.
- Terraform manages the Analytics Lambda IAM role and least-privilege access policy.
- Terraform uses the HashiCorp Archive provider to package the Lambda artifact.
- AWS Lambda `olist-analytics-api-dev` is deployed using Python 3.13.
- Lambda configuration points to `olist_gold_db` and the Terraform-managed Athena result location.
- All five analytical operations have been successfully invoked through the deployed Lambda against Athena and the Gold layer.
- Amazon API Gateway HTTP API is deployed through Terraform.
- API Gateway exposes `GET /analytics` through a Lambda proxy integration and `$default` stage.
- The default HTTP request successfully returns `sales_by_state` analytical results.
- A parameterized HTTP request using `operation=top_sellers&limit=5` successfully returns Gold analytical results.
- The deployed HTTP execution path API Gateway -> Lambda -> Athena -> Glue Data Catalog -> S3 Gold -> JSON has been validated.
- Terraform deployment completed without destroying existing platform resources.

Current Analytics API scope: completed.

Potential next enhancements:

1. Add authentication and authorization if the API is exposed beyond controlled development use.
2. Add API-specific CloudWatch metrics, structured logging, and alarms.
3. Add throttling and usage controls.
4. Add richer filtering or pagination where useful.
5. Add automated CI/CD and post-deployment HTTP smoke tests.
