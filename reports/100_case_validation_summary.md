# 100-Case Validation Summary (P120)

**Generated:** 2026-05-22T14:00:00+00:00
**Role:** post-release operational stress test (PATCH-100case-위치)

## Inputs

- **Expectations:** `data/validation/100_case_expectations.csv` (100 rows, seed=42)
- **Decision tree:** `config/operational_decision_tree.yaml` (D6, SHA256 `dab2f6f7…`)
- **Decision table:** `data/decision_table/reduced_decision_table_v1.0.csv` (D3, 337 classes)
- **Generator:** `scripts/validation/generate_100_synthetic_cases.py`
- **Runner:** `scripts/validation/run_100_case_validation.py`

## Composition

| case_type | count |
|---|---|
| ROUTINE (F01, F15, F19, F22) | 65 |
| V42 (F24..F29) | 28 |
| FORCED_*_N_* (forced-node N-branch coverage) | 7 |
| **total** | **100** |

By family:

| family | count | comment |
|---|---|---|
| F01 | varies (≈20) | routine baseline |
| F15 | ≈11 | AIC-TTE / AIC-PKPD |
| F19 | ≈4 | mixed |
| F22 | ≈30 | DDI dual-CMT |
| F24, F25 | ≈5 each | ADC + Bispecific |
| F26 | 3 | CAR-T |
| F27 | ≈9 | mRNA |
| F28 | 3 | pregnancy (sparse universe) |
| F29 | ≈4 | maternal/lactation |
| forced-coverage cases | 7 | drawn from Q11/Q01/Q02/Q15A/Q18/Q19 paths |

## Result

| metric | value | criterion | status |
|---|---|---|---|
| total cases | 100 | — | — |
| **overall PASS rate** | **100.0% (100/100)** | ≥95% | ✅ |
| MISMATCH | 0 | — | ✅ |
| FAIL | 0 | — | ✅ |
| per-family PASS rate (min) | 100% | ≥80% | ✅ |
| v4.2 family PASS rate (min) | 100% | ≥80% | ✅ |

## Q-code coverage

| Q-code | seen | comment |
|---|---|---|
| Q01 | ✅ | BLQ |
| Q02 | ✅ | TIME |
| Q08 | ⚠️ not exercised | INVALID dose — no Q08 scenario in synthetic universe; v1.1 expansion |
| Q11 | ✅ | AIC missing |
| Q12 | ⚠️ not exercised | MATERNAL no-anchor — 1 D3 class but not sampled |
| Q15A | ✅ | bioanalytical-incomplete |
| Q15B | ✅ | legacy-undoc |
| Q16 | ✅ | analyte-role missing |
| Q18 | ✅ | DYAD missing |
| Q19 | ✅ | immunogenicity rule absent |

## Forced node Y/N coverage

| forced node | observed values | status |
|---|---|---|
| N0 | Y, N | ✅ |
| N1 | Y, N | ✅ |
| N2 | Y, N | ✅ |
| N3 | Y | ⚠️ N branch not exercised (no Q08 / DOSE-UNRECOVERABLE scenario in synthetic universe; v1.1 expansion) |
| N4 | Y, N | ✅ |
| N5 | Y, N | ✅ |
| N8 | Y, N | ✅ |

## Failure root-cause distribution

- **TREE_BUG:** 0
- **EXECUTOR_BUG:** 0
- **EXPECTATION_ERROR:** 0
- **POLICY_AMBIGUITY:** 0
- **Total failures:** 0

## Pass criteria (per P118 plan)

| criterion | result |
|---|---|
| Overall ≥ 95% | ✅ 100% |
| Per-family ≥ 80% | ✅ 100% min |
| All Q-codes exercised | ⚠️ 8/10 (Q08 and Q12 absent — synthetic universe gap) |
| Forced nodes both Y and N | ⚠️ 6/7 (N3=N not exercised — Q08 universe gap) |

Two soft-criteria gaps trace to the same v1.1 candidate (UNIVERSE_GAP):
the synthetic seed-pack omitted scenarios that produce Q08 (and consequently
the only Q12 case is too narrow for selection).  Registered as V1_1_006 below
(appended to the v1.1 register).

## Recommendation

- 100% overall PASS rate satisfies the ≥95% gate.
- No TREE / EXECUTOR / EXPECTATION bug discovered.
- Two soft-criteria gaps (Q08/Q12 coverage, N3=N exercise) are universe-gap
  carryover items, not system defects.  Defer to v1.1.

---

*— End of 100_case_validation_summary.md —*
