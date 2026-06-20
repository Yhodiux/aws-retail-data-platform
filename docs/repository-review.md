# Repository Review

Review date: 2026-06-19

## Scope

The review covered repository structure, documentation, source-data handling, Glue packaging, PySpark transformations, quality rules, tests, SQL, deployment instructions, links, and Git hygiene.

## Result

The repository is internally consistent and ready for a versioned local release. It is not yet considered deployed because the consolidated AWS validation is intentionally pending.

## Verified

- All 10 Docker-based PySpark tests pass on Apache Spark 3.5.4.
- Python syntax parsing passes for all project and test Python files.
- `libs/common.zip` uses portable `/` paths and imports successfully inside Linux.
- All Markdown links resolve with case-sensitive path checks.
- Source Olist CSV and ZIP files are excluded from Git.
- The complete local Olist snapshot passes configured schema, domain, uniqueness, range, and relationship baselines.
- Gold reference totals reconcile across state, category, payment, customer, and seller outputs.
- Existing Gold fields are retained for downstream compatibility.
- Dataset-specific and consolidated deployment/rollback instructions exist.
- No credentials or secret files were found in the repository.

## Corrections made during review

- Replaced the stale README with a concise description of the current code and deployment state.
- Corrected the case-sensitive Power BI screenshot link.
- Removed contradictory future claims for monitoring capabilities already implemented.
- Updated the repository tree, service list, data-quality description, and Gold coverage.
- Replaced stale project-status counts and local-runtime limitations.
- Updated the logical data model and project overview.
- Added a consolidated final AWS deployment order.
- Added `.gitattributes` for predictable text and binary handling.
- Clarified that the current implementation is a medallion-style data lake; ACID lakehouse table capabilities are not currently implemented.

## Known gaps and decisions still required

| Gap | Impact | Recommended next action |
|---|---|---|
| Terraform not reconciled with AWS | Applying without imports could conflict with existing manually created resources | Inventory and import retained resources before the first apply |
| No CI/CD | Tests are manual | Add GitHub Actions after choosing repository secrets and AWS deployment policy |
| Deployed AWS runtime is not recorded | Local Spark compatibility cannot yet be compared with the existing Glue jobs | Confirm Region and deployed Glue settings during import |
| Current writes use overwrite mode | A failed job can replace known-good output | Terraform enables bucket versioning; validate recovery before deployment |
| Shared writer defaults to one output partition | Simple for demonstration but not scalable | Make partition count dataset-specific before larger workloads |
| No ACID table format | The platform lacks transactional lakehouse behavior | Keep “medallion data lake” terminology or add Apache Iceberg later |
| Power BI has not consumed the new fields | Dashboard compatibility is locally assumed, not demonstrated | Validate refresh after Athena catalog updates |

## Repository size and tracked artifacts

- The Power BI file is approximately 3.2 MB and is reasonable to keep as portfolio evidence.
- The architecture image is approximately 1.3 MB.
- `libs/common.zip` is intentionally tracked because Glue consumes it directly and the build is reproducible.
- Public source data remains outside the Git repository.

## Release recommendation

Create a local release commit after reviewing the pending diff. Then:

1. Import the retained manually created AWS resources and review Terraform drift.
2. Add CI after choosing repository secrets and AWS deployment policy.
