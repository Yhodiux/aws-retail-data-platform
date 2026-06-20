# Phase 1 Deployment — sales_by_state

Status: deferred to final manual AWS deployment phase

This deployment extends `sales_by_state` without removing or renaming existing fields.

## Files to deploy

| Local file | AWS purpose |
|---|---|
| `libs/common.zip` | Shared Gold transformation functions |
| `scripts/gold/build_gold_sales_by_state.py` | Glue Gold job script |
| `scripts/quality/validate_gold_quality.py` | Glue Gold quality job script |
| `sql/queries.sql` | Manual Athena validation; this file does not need to be uploaded unless SQL is stored in S3 |

The final deployment must upload `libs/common.zip` before this job because the DataFrame transformation now lives in the shared library.

## New columns

- `delivered_orders`
- `delivered_items`
- `delivered_product_revenue`
- `delivered_freight_value`
- `delivered_avg_ticket`

## Deployment order

Do not run the complete workflow until the new schema is visible in the Glue Data Catalog.

1. Preserve the current S3 versions of the shared library and both Glue scripts.
2. Upload `libs/common.zip` to the configured Glue dependency location.
3. Upload `scripts/gold/build_gold_sales_by_state.py` to the script location of the existing `sales_by_state` Glue job.
4. Run only the `sales_by_state` job.
5. Confirm that the Gold Parquet output was replaced successfully.
6. Run the relevant Gold crawler, or update the Data Catalog table through the existing project procedure.
7. In Athena, run `DESCRIBE olist_gold_db.sales_by_state` and confirm that all five new columns are present.
8. Upload `scripts/quality/validate_gold_quality.py` to the Gold quality job script location.
9. Run the Gold quality job.
10. Execute the new `sales_by_state` checks from `sql/queries.sql`.
11. After all checks pass, run the complete workflow once to verify orchestration.
12. Report the run IDs and validation results so `docs/project-status.md` can be updated.

## Reference values

For the local Olist source snapshot used during development, the delivered metrics across all states are:

| Metric | Expected value |
|---|---:|
| `SUM(delivered_orders)` | 96,478 |
| `SUM(delivered_items)` | 110,197 |
| `SUM(delivered_product_revenue)` | 13,221,498.11 |
| `SUM(delivered_freight_value)` | 2,198,275.64 |

These values assume the standard public Olist files and no Raw records added, removed, or modified. Differences must be explained before considering the deployment successful.

## Success criteria

- The Gold job succeeds.
- Existing columns remain available.
- The five new columns appear in the Data Catalog and Athena.
- The Gold quality job succeeds.
- The invalid-row Athena query returns zero rows.
- Aggregated delivered metrics match the source snapshot or have a documented reason for differing.
- The complete Glue workflow succeeds after the isolated validation.

## Rollback

1. Restore the previous `sales_by_state` Glue script.
2. Run the previous job to restore the former output schema.
3. Run the Gold crawler so the Data Catalog reflects the restored schema.
4. Restore the previous quality script.
5. Run the previous quality job and confirm success.

## Deployment result

```text
Date:
Environment:
Git commit/release:
sales_by_state Glue run ID:
Gold crawler run:
Quality Glue run ID:
Complete workflow run ID:
Athena validation result:
Result: PENDING
Notes:
```
