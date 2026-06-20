# Phase 2 Deployment — Explicit Silver Schemas

Status: deferred to final manual AWS deployment phase

This deployment replaces CSV schema inference with centralized explicit PySpark schemas.

## Files to deploy

| Local file | AWS purpose |
|---|---|
| `libs/common.zip` | Updated shared library containing `common.schemas` |
| `scripts/silver/build_silver_generic.py` | Updated generic Silver Glue job |
| `scripts/quality/validate_silver_referential.py` | Silver cross-table quality job |

## Deployment order

1. Preserve the existing shared library ZIP and Silver script S3 versions.
2. Upload `libs/common.zip` to the configured Glue dependency location.
3. Confirm that the Silver Glue job references the uploaded ZIP through its Python library path or `--extra-py-files`.
4. Upload `scripts/silver/build_silver_generic.py` to the existing Silver job script location.
5. Create or update the Silver referential-quality Glue job with `scripts/quality/validate_silver_referential.py`.
6. Run the Silver job separately for each currently deployed `TABLE_NAME`.
7. Verify the resulting Parquet schemas and row counts before running Gold.
8. Refresh the Silver Data Catalog tables.
9. Run the Silver referential-quality job after all six core Silver datasets succeed.
10. Run the full Gold workflow only after every required Silver dataset and relationship passes.

## Supported TABLE_NAME values

- `customers`
- `orders`
- `order_items`
- `payments`
- `products`
- `sellers`
- `geolocation`
- `reviews`
- `product_category_translation`

## Success criteria

- Unsupported table names fail before reading an arbitrary S3 prefix.
- Headers or malformed typed values fail the Silver job.
- ZIP-code prefixes retain leading zeroes.
- Financial columns are stored as `decimal(12,2)`.
- Timestamp columns are stored as timestamps.
- Existing six Silver datasets retain their expected row-level meaning.
- Required-field, domain, uniqueness, range, and non-negative checks pass.
- All five core referential-integrity checks report zero orphan records.
- Referential results are preserved under the Silver quality-log prefix.
- Gold jobs and the complete workflow succeed after catalog refresh.

## Rollback

1. Restore the previous Silver script and shared library ZIP.
2. Regenerate the affected Silver outputs with the previous job version.
3. Refresh the Silver Data Catalog tables.
4. Validate Gold using the previous workflow version.

## Deployment result

```text
Date:
Environment:
Git commit/release:
Shared library S3 version:
Silver Glue run IDs:
Silver quality Glue run ID:
Silver crawler run:
Result: PENDING
Notes:
```
