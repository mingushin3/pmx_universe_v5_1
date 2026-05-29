# Operational Metrics Dashboard Specification (v1.0)

## Cadence: quarterly

## Metrics

| metric | source | target / interpretation |
|---|---|---|
| new cases processed (total, by terminal_state, by family) | `reports/execution_log.csv` | trend chart; sponsor diversity |
| QUARANTINE rate | execution log | should be stable ~70%; spike → AIC training gap |
| v1.1 register growth | `change_control/v1_1_candidate_register.csv` | trend; ≥10 → trigger v1.1 cycle |
| H4 blinded sample audit pass rate | quarterly H4 spot-check (P136) | ≥95% target |
| Confirmed false-classification incidents | incident log | target 0 |
| 100-case re-run pass rate (after patches) | re-run summary md | ≥95% |
| Hash chain re-verification | `release_v1_0_combined.sha256` | 100% match expected |

## Reporting cadence

- Q1 post-release: spot-check 10 random new cases.
- Q2: trigger v1.1 evaluation; re-run 100-case if executor patched.
- Q3: dashboard refresh; new modality pipeline check.
- Q4: annual review; v2.0 planning decision.

---
