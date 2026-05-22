# Golden Validation Summary — v1.0 (P107, post-H3)

**Generated:** 2026-05-22T13:35:00+00:00
**Pipeline:** `scripts/validation/run_golden_validation.py`
**Inputs:**
- registry (v1.0 scope, post-H3): `data/golden_datasets/golden_dataset_registry_v1_0.csv`
- registry (v1.1 deferred): `data/golden_datasets/golden_dataset_registry_v1_1_deferred.csv`
- tree: `config/operational_decision_tree.yaml`
- decision table: `data/decision_table/reduced_decision_table_v1.0.csv`
**Results CSV:** `reports/golden_validation_results.csv` (4 entries, all PASS)
**Per-dataset details:** `reports/golden_validation_per_dataset/*.md`

---

## H3 scope correction applied

The original draft registry (`golden_dataset_registry_draft.csv`) contained
6 entries.  H3 review (2026-05-22) deferred 2 of them to v1.1 because
the underlying families are not present in the synthetic v5.1 universe
(HANDOVER §2.1):

| golden_id | family | reason | new status |
|---|---|---|---|
| G003 | F09 (DDI) | family not in 20-seed-pack | deferred → `golden_dataset_registry_v1_1_deferred.csv`; v1.1 register entry V1_1_002 |
| G005 | F12 (Pediatric) | family not in 20-seed-pack | deferred → `golden_dataset_registry_v1_1_deferred.csv`; v1.1 register entry V1_1_002 |

The v1.0 release scope is therefore 4 goldens (G001, G002, G004, G006),
covering F24 (ADC), F26 (CAR-T), F29 (Maternal/Lactation), and F01 (routine).

## Overall (v1.0 scope, 4 goldens)

| metric | value |
|---|---|
| total goldens | 4 |
| PASS | 4 |
| MISMATCH | 0 |
| FAIL | 0 |
| **overall PASS rate** | **100.0 %** (4/4) |

## Per-golden outcomes

| golden_id | project_id | family | expected | actual | result | leaf |
|---|---|---|---|---|---|---|
| G001 | PROJ_ADC_014 | F24 | REPAIR | REPAIR | PASS | `leaf_REPAIR_NA_067eec0a` |
| G002 | PROJ_CART_016 | F26 | REPAIR | REPAIR | PASS | `leaf_REPAIR_NA_8291e7f5` |
| G004 | PROJ_LAC_020 | F29 | REPAIR | REPAIR | PASS | `leaf_REPAIR_NA_97865932` |
| G006 | PROJ_S01_001 | F01 | AUTO | AUTO | PASS | `leaf_AUTO_NA_375dc3d8` |

## Per-family PASS rate (within v1.0 scope)

| family | goldens | PASS | rate | target |
|---|---|---|---|---|
| F01 (routine) | 1 | 1 | 100% | 100% |
| F24 (ADC) | 1 | 1 | 100% | ≥80% |
| F26 (CAR-T) | 1 | 1 | 100% | ≥80% |
| F29 (Maternal/Lactation) | 1 | 1 | 100% | ≥80% |

## v4.2 family-specific PASS rate

F24, F26, F29 (all v4.2): 3/3 (100%) — exceeds the ≥80% threshold.
F25 (Bispecific), F27 (mRNA), F28 (pregnancy): not represented in this
golden batch; future v1.1 candidate (CP7 LP-B noted, → V1_1_003).

## Mismatch root-cause categories (v1.0 scope)

| category | count |
|---|---|
| `tree_routing_error` | 0 |
| `executor_logic_error` | 0 |
| `reference_output_error` | 0 |
| `aic_under_specification` | 0 |

## Recommendation

- Overall PASS rate **100% (4/4)** within v1.0 scope, well above the ≥95%
  threshold for direct release-prep flow.
- Skip P108 (mismatch deep-dive) — no mismatches in v1.0 scope.
- Proceed directly to **H3 + P107B + P109** (H3 already signed; D8 already
  emitted at `reports/golden_validation_report.md`).

---

*— End of golden_validation_summary_v1.md (post-H3) —*
