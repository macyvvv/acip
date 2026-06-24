# Repository Self Test Complete Checklist

## Checklist

| ID | Check | Script |
|---|---|---|
| ST-01 | Repository health | `check_repository_health.py` |
| ST-02 | Boundary validation | `check_boundaries.py` |
| ST-03 | Secret scan | `check_secret_boundary.py` |
| ST-04 | Link integrity | `check_link_integrity.py` |
| ST-05 | Duplicate detection | `check_duplicates.py` |
| ST-06 | Orphan/dead docs | `check_orphans.py` |
| ST-07 | Workflow-script consistency | `check_workflows.py` |
| ST-08 | Current Objective drift | `check_current_objective.py` |
| ST-09 | Full validation | `validate_repository_selftest_complete.py` |

## Definition of Done

Self Test Complete is done when all scripts pass or produce only accepted warnings.
