# H3 — Golden Reference Approval Log

> **simulated_human_signer: TRUE** (HANDOVER §2.2; real data unavailable in v5.1)
> Replace placeholder reviewer with real PMX expert identification before v1.0 GA release.

| golden_id | project_id | family_id | reviewed_by | date | reference_correct | validation_result_correct | action |
|---|---|---|---|---|---|---|---|
| G001 | PROJ_ADC_014 | F24 | (placeholder) PMX_Reviewer_A | 2026-05-22 | YES | PASS | none |
| G002 | PROJ_CART_016 | F26 | (placeholder) PMX_Reviewer_A | 2026-05-22 | YES | PASS | none |
| G003 | PROJ_DDI_005 | F09 | (placeholder) PMX_Reviewer_A | 2026-05-22 | n/a | MISMATCH | **registry corrected**: moved to `golden_dataset_registry_v1_1_deferred.csv` (F09 not in 20-seed pack); v1.1 register V1_1_002 |
| G004 | PROJ_LAC_020 | F29 | (placeholder) PMX_Reviewer_A | 2026-05-22 | YES | PASS | none |
| G005 | PROJ_PED_006 | F12 | (placeholder) PMX_Reviewer_A | 2026-05-22 | n/a | MISMATCH | **registry corrected**: moved to `golden_dataset_registry_v1_1_deferred.csv` (F12 not in 20-seed pack); v1.1 register V1_1_002 |
| G006 | PROJ_S01_001 | F01 | (placeholder) PMX_Reviewer_A | 2026-05-22 | YES | PASS | none |

## Summary

- Total reviewed: 6 (original draft registry)
- References confirmed correct: 4 (G001, G002, G004, G006) → v1.0 release scope
- Registry corrections: 2 (G003 F09, G005 F12) → split into `golden_dataset_registry_v1_1_deferred.csv`
- Executor/tree bugs confirmed: 0
- Post-H3 v1.0 scope (`golden_dataset_registry_v1_0.csv`): 4 goldens, all PASS

## PASS sample spot-check

Beyond the 6 register entries above, 3 PASS samples were spot-checked
(decision-path traceability + leaf attribute match against the simulated AIC):

- G001 path: `N0=Y → N1=Y → N8=Y → N2=Y → N3=Y → N4=Y → N5=Y → N14=N → N13=N → N19=N → N21=Y → N22=N → N24=N → N25=Y` → `leaf_REPAIR_NA_067eec0a` — confirmed consistent with REPAIR_F24_CMTROLE plan.
- G002 path leads to `leaf_REPAIR_NA_8291e7f5` (F26 PRODUCT-level covariate REPAIR) — confirmed consistent.
- G006 path leads to `leaf_AUTO_NA_375dc3d8` (AUTO_F01_SMALL_MOLECULE) — confirmed `export_nonmem_ready` present.

## Decision

APPROVED for release with caveats:
- `G003 PROJ_DDI_005` (F09) marked as **v1.1 deferred** (F09 not in synthetic universe).
- `G005 PROJ_PED_006` (F12) marked as **v1.1 deferred** (F12 not in synthetic universe).
- Coverage claim (D9) must explicitly note F09/F12 partial coverage and the
  HANDOVER §2.1 synthetic-data substitution.

## Sign-off

Reviewed_by: `(placeholder) PMX_Reviewer_A`  *(simulated_human_signer=TRUE)*
Date: 2026-05-22
Decision: **APPROVED** (signed)

When real data and reviewer become available, the LP-A/B/C trio at
`reports/llm_proxy/release_coverage_approval_*.md` and this log must be
re-issued with `simulated_human_signer=FALSE` and the real reviewer name.

---

*— End of h3_golden_approval_log.md —*
