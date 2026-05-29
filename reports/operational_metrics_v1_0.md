# Operational Metrics — Baseline at v1.0 Release (P135)

**Generated:** 2026-05-22T14:10:00+00:00

## Terminal-state distribution (from D2)

| terminal_state | count | % of total |
|---|---|---|
| AUTO | 116 | 3.87% |
| REPAIR | 638 | 21.28% |
| QUARANTINE | 2208 | 73.65% |
| INVALID (all F34) | 36 | 1.20% |
| **total** | **2998** | **100.00%** |

## Coverage (from `release/v1.0/coverage_claim_statement.md`)

- review_inclusive: **100.00%** (2962 / 2962 in-scope scenarios)
- operational (AUTO+REPAIR): 25.46%
- auto_only: 3.92%
- unsupported_invalid_rate: 1.20%

## Validation snapshots

- Tree ↔ Table consistency (P103): 100.000%
- Golden Validation (D8, v1.0 scope): 4/4 PASS (100%)
- H4 Blinded Sampling Audit: 0/26 mismatches
- 100-case post-release stress test: 100/100 PASS

## v1.1 register count at release

- Open: 6 (V1_1_001 .. V1_1_006)

---
