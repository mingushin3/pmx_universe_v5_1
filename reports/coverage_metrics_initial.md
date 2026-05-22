# Coverage Metrics — Initial

total_scenarios: 2992

## Distribution
- AUTO: 116
- REPAIR: 638
- QUARANTINE: 2202
- UNSUPPORTED: 0
- INVALID: 36

## Coverage targets
- capture_coverage: 1.0000  (target ≥ 0.99)
- review_inclusive: 1.0000  (target ≥ 0.95)
- operational: 0.2551  (target ≥ 0.75)
- auto_only: 0.0392  (target ≥ 0.35 — initial; will rise after action label lock)
- unsupported_invalid_rate: 0.0120  (target ≤ 0.05)

## Hard-rule compliance
- Q15 standalone count: 0 (target 0)
- Q17 count: 0 (target 0)
- q_code missing in QUARANTINE: 0 (target 0)

## Notes
- false_auto_count and false_repair_count are 0 by construction at this
  initial stage. Final values come after golden validation in Phase 10.
