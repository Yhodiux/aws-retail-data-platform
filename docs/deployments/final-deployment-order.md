# Final AWS Deployment Order

Status: pending manual execution

This runbook consolidates the local Silver, Gold, quality, and shared-library changes into one controlled AWS deployment. Individual runbooks remain the source of dataset-specific reference totals and rollback details.

## 1. Pre-deployment freeze

1. Commit or tag the exact repository version being deployed.
2. Run `scripts/run_tests.ps1` and require all tests to pass.
3. Rebuild `libs/common.zip` with `scripts/build_common_zip.ps1`.
4. Record the SHA-256 hash of `libs/common.zip`.
5. Preserve the existing S3 object versions for the shared library and every Glue script.
6. Confirm S3 versioning or another recovery mechanism for overwritten Silver and Gold outputs.
7. Do not start the complete Glue workflow during the schema transition.

## 2. Upload shared dependencies and scripts

Upload in this order:

1. `libs/common.zip`
2. `scripts/silver/build_silver_generic.py`
3. `scripts/quality/validate_silver_referential.py`
4. All five scripts under `scripts/gold/`
5. `scripts/quality/validate_gold_quality.py`

Confirm every affected Glue job references the same new `common.zip` S3 object version before running it.

## 3. Rebuild and validate Silver

Run the generic Silver job separately for these core tables:

1. `customers`
2. `orders`
3. `products`
4. `sellers`
5. `order_items`
6. `payments`

Then:

1. Verify each run succeeded and table-level quality did not fail.
2. Refresh the Silver Data Catalog tables.
3. Confirm ZIP-code, decimal, integer, and timestamp types in Athena.
4. Run the Silver referential-integrity job.
5. Require zero orphan records across all five configured relationships.

Optional datasets (`geolocation`, `reviews`, and `product_category_translation`) may be processed after the core workflow is stable.

## 4. Rebuild and catalog Gold

Run each Gold job independently:

1. `sales_by_state`
2. `sales_by_category`
3. `sales_by_payment_type`
4. `top_customers`
5. `top_sellers`

After all five succeed:

1. Refresh the Gold Data Catalog tables.
2. Confirm every new delivered metric appears in Athena.
3. Run `validate_gold_quality.py`.
4. Require every Gold quality result to pass.

## 5. Athena reconciliation

Execute `sql/queries.sql` and compare results with the reference values in the dataset-specific runbooks:

- `phase-1-sales-by-state.md`
- `phase-1-sales-by-category.md`
- `phase-1-sales-by-payment-type.md`
- `phase-1-top-customers.md`
- `phase-1-top-sellers.md`

The invalid-row queries must return zero rows. Any difference in reference totals must be explained before proceeding.

## 6. End-to-end workflow

1. Start one complete Glue Workflow run.
2. Confirm Silver processing succeeds.
3. Confirm all five Gold jobs execute through the expected parallel branch.
4. Confirm quality jobs and conditional triggers behave correctly.
5. Review CloudWatch logs for errors or unexpected warnings.
6. If practical, trigger a controlled development failure and confirm EventBridge/SNS routing still works.

## 7. Downstream validation

1. Refresh the Power BI model.
2. Confirm legacy columns still resolve.
3. Add new delivered metrics only after the existing dashboard refresh succeeds.
4. Compare headline dashboard totals with Athena.

## 8. Record completion

Update `docs/project-status.md` with:

- Deployment date and environment.
- Git commit or tag.
- Shared-library S3 version and SHA-256 hash.
- Silver and Gold Glue run IDs.
- Crawler and quality-job run IDs.
- Complete workflow run ID.
- Athena reconciliation result.
- Power BI refresh result.

## Consolidated rollback

If a blocking validation fails:

1. Stop downstream workflow execution.
2. Restore the previous shared library and Glue script S3 versions as one compatible set.
3. Regenerate affected Silver outputs and refresh the Silver catalog.
4. Regenerate affected Gold outputs and refresh the Gold catalog.
5. Run the previous quality jobs and Athena checks.
6. Record the failed deployment and rollback evidence.

