# Local Testing Guide

The project runs automated PySpark tests in Docker so Java, Python, and Spark do not need to be installed globally.

## Prerequisite

- Docker Desktop or another active Docker Engine.

The test runner uses the pinned image `apache/spark:3.5.4`.

## Run the tests

From the repository root in PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1
```

Before the Spark suite, validate repository structure, Markdown links, Python syntax, source-data exclusions, and the shared ZIP:

```powershell
python .\scripts\validate_repository.py
```

The runner:

1. Verifies or downloads the pinned Spark image.
2. Mounts the repository read-only from the perspective of test logic.
3. Adds `scripts/` and the Spark Python libraries to `PYTHONPATH`.
4. Executes the standard-library `unittest` suite.
5. Removes the test container after completion.

No AWS credentials are required or passed to the container.

## Current coverage

The suite in `tests/test_pyspark_pipeline.py` verifies:

- Explicit schema types and rejection of unsupported tables.
- Silver trimming and customer normalization.
- Successful table-level quality validation.
- Fail-fast required-field, domain, and uniqueness violations.
- Referential orphan-row counting.
- Backward-compatible legacy and delivered metrics for all five Gold datasets.
- Unknown product-category behavior.
- Payment-record versus distinct-order semantics.
- Delivered customer and seller activity timestamps.

## Architecture for testability

Glue scripts retain environment-specific responsibilities such as job arguments, S3 reads and writes, logging, and commits. Reusable DataFrame logic lives in the shared package:

- `common.silver_transformations`
- `common.gold_transformations`
- `common.data_quality`
- `common.schemas`

The local tests call these same functions directly with small deterministic DataFrames.

## Baseline

On 2026-06-19, all 10 tests passed with Apache Spark 3.5.4. The final verification run completed in approximately 16 seconds after Spark startup.
