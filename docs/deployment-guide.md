# Manual AWS Deployment Guide

This project currently uses manual AWS deployments. This guide provides a repeatable checklist and prevents a local change from being confused with a deployed change.

Deployment is intentionally deferred until the planned local code, test, and documentation changes are complete. Individual deployment runbooks are prepared during development and executed together in the final AWS phase.

Use `docs/deployments/final-deployment-order.md` as the controlling runbook for the consolidated release. Dataset-specific runbooks provide reference totals and detailed rollback notes.

## Deployment record

For every deployment, record:

- Date and environment.
- Git commit or release identifier.
- Files uploaded.
- AWS resources changed.
- Job arguments used.
- Validation result.
- Rollback action, if required.

Deployment evidence should be summarized in `docs/project-status.md`. Repository changes belong in `CHANGELOG.md`.

## Prerequisites

- Access to the AWS account and target Region.
- Permission to update the relevant S3 objects and AWS Glue jobs.
- Existing Raw, Silver, Gold, logs, and temporary S3 prefixes.
- Existing Glue Data Catalog databases and tables.
- A previous working script available for rollback.

Do not store AWS access keys, secret keys, account IDs, or temporary credentials in this repository.

## Deploying the shared library

The Glue dependency is stored at `libs/common.zip` and contains the importable `common/` package.

Rebuild it before deployment whenever a file under `scripts/common/` changes:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_common_zip.ps1
```

The builder emits portable `/` archive paths and replaces the previous ZIP only after the new archive is created successfully.

1. Upload `libs/common.zip` to the S3 location used for Glue dependencies.
2. Open each affected Glue job.
3. Confirm the uploaded S3 URI is configured under Python library paths or `--extra-py-files`.
4. Save the job without changing unrelated runtime settings.
5. Run a job that imports `common.config`, `common.logger`, and `common.utils`.
6. Confirm that no `ModuleNotFoundError` appears in CloudWatch logs.

Deploy the library before scripts that depend on a new library change.

## Deploying a Glue script

1. Preserve the current working script or note its S3 version ID.
2. Upload only the changed script from `scripts/` to its configured S3 script location.
3. Confirm that the Glue job still references the correct script and shared library paths.
4. Verify Glue version, worker type, worker count, IAM role, timeout, and job arguments.
5. Run the job manually in the development environment.
6. Review CloudWatch logs and the Glue run status.
7. Validate the generated S3 output and Data Catalog table.
8. Execute the relevant queries from `sql/queries.sql` in Athena.
9. Run the Gold quality job when a Gold dataset changes.
10. Record the deployment result.

## Validation checklist

- [ ] Glue job finished successfully.
- [ ] Output path contains current Parquet files.
- [ ] Output schema matches the documented contract.
- [ ] Row counts are plausible and explained.
- [ ] Key columns do not contain unexpected nulls.
- [ ] Financial totals reconcile with the agreed business definition.
- [ ] Data-quality job passed.
- [ ] Athena query returned the expected result.
- [ ] Downstream Power BI fields remain compatible or were updated.
- [ ] `docs/project-status.md` reflects the deployed state.

## Rollback

If validation fails:

1. Stop dependent workflow runs if necessary.
2. Restore the previous Glue script and shared library version.
3. Restore the previous output only if the failed run replaced valid data and an S3 version or backup exists.
4. Run the previous job version.
5. Repeat the validation checklist.
6. Record the failure and rollback result.

Because current jobs use overwrite mode, production-like environments should enable S3 versioning or write to versioned output prefixes before replacing a known-good dataset.

## Deployment log template

```text
Date:
Environment:
Commit/release:
Files uploaded:
AWS resources changed:
Job arguments:
Validation queries:
Result: SUCCESS | FAILED | ROLLED BACK
Evidence/notes:
```
