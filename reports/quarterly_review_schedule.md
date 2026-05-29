# Quarterly Review Schedule — v1.0 Operations (P136)

## Schedule (relative to v1.0 release: 2026-05-22)

| quarter | window | activities |
|---|---|---|
| Q1 (3 months post-release) | 2026-08-22 ± 14 d | v1.1 candidate triage; H4 spot-check 10 random new cases |
| Q2 (6 months) | 2026-11-22 ± 14 d | v1.1 trigger evaluation; 100-case re-run if executor patched |
| Q3 (9 months) | 2027-02-22 ± 14 d | metric dashboard update; new modality pipeline check |
| Q4 (12 months) | 2027-05-22 ± 14 d | annual review; v2.0 planning decision |

## Per-quarter checklist

### Q1
- [ ] Review `change_control/v1_1_candidate_register.csv` and triage open items.
- [ ] Randomly sample 10 new cases processed since release; H4 spot-check each.
- [ ] Update `reports/operational_metrics_v1_0.md` with Q1 numbers.

### Q2
- [ ] Evaluate v1.1 trigger criteria (≥10 candidates / ≥1 CRITICAL / 6mo / v4.x upgrade).
- [ ] If patched: re-run `scripts/validation/run_100_case_validation.py`.
- [ ] Decide whether to start v1.1 cycle.

### Q3
- [ ] Refresh dashboard per `metric_dashboard_specification.md`.
- [ ] Check for new modality data on horizon (sponsor pipeline).

### Q4
- [ ] Annual review of operational metrics.
- [ ] Decide on v2.0 timeline (typically 12–18 months from v1.0 if triggered).

---
