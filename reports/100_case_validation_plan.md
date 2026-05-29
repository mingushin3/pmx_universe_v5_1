# 100-Case Validation Plan (P118)

**Generated:** 2026-05-22T13:55:00+00:00
**Role:** post-release operational stress test (per PATCH-100case-위치, Phase 11)

## Purpose

Final stress test of v1.0 release using 100 realistic synthetic cases
spanning the operational families F01–F29 + the five v4.2 modalities
(F24, F25, F26, F27, F29; F28 represented when scenarios available).

This 100-case run is a **post-release operational stress test**; it is NOT
the basis of the coverage_claim_statement (D9).  D9 rests on the
universe-wide tree-table consistency (P103, 100%) + the golden validation
(D8) + the H4 blinded audit.  The 100-case run is used to **trigger v1.1
candidate register entries** for any case that requires manual override.

## Case selection

- **70 cases** from operational families (F01–F23): roughly proportional
  to expected real-world frequency.
- **30 cases** from v4.2 families (F24–F29): each family ≥3 cases when
  the universe has enough scenarios.  F28 may receive fewer (only 8
  scenarios in the universe).
- Mix targets: ~35 AUTO, ~45 REPAIR, ~20 QUARANTINE — actual mix is
  driven by per-family terminal_state distribution in D2.

## Case construction

- Cases are drawn deterministically (seed=42) from the locked D2
  (`scenario_action_table_locked.csv`).
- For each case we record: `scenario_id`, `family_id`,
  `modality_class`, `endpoint_data_type`, axis state A0..A10,
  `expected_terminal_state`, `expected_q_code` (from D2),
  `policy_variant` (present / absent / n.a.).
- Synthetic raw inputs are NOT regenerated (HANDOVER §2.1); routing
  validation operates against the locked D3/D6 chain.

## Validation procedure

For each case:

1. Look up the scenario's D3 representative class (matching family + terminal_state).
2. Walk the operational decision tree (D6) using its N0..N29 values.
3. Compare predicted terminal_state and q_code to expected.
4. If AUTO / REPAIR predicted: confirm action_sequence executable
   (verify ≥1 repair-class function for REPAIR; verify
   `export_nonmem_ready` present for AUTO).

## Pass criteria

- Overall PASS rate ≥ 95%.
- Per-family PASS rate ≥ 80%.
- v4.2-new family PASS rate ≥ 80%.
- Q-code coverage: each Q-code from D3 (Q01, Q02, Q11, Q12, Q15A, Q15B,
  Q16, Q18, Q19) exercised ≥1 case (where the universe contains examples).
- Forced-node coverage: each forced node (N0..N5, N8) evaluated as both
  Y and N at least once across the 100 cases (where the universe contains
  examples).

## Reporting

- per-case results in `reports/100_case_validation_results.csv`
- summary in `reports/100_case_validation_summary.md`

## Failure handling

- **<95% overall:** register all failures as v1.1 candidates via the
  `SOP_change_control_v1_0.md` flow.
- **<80% any family:** BLOCKER for the operational SOP rollout for that
  family; document in `100_case_failure_triage.md` (P121).

---

*— End of 100_case_validation_plan.md —*
