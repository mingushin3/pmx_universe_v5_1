# SOP: Change Control (v1.0)

**Version:** v1.0 (locked at 2026-05-22T13:50:00+00:00)
**Next review:** at v1.1 release (planned: 6 months from v1.0)

## When to register a v1.1 candidate

A change is required when:

1. New dataset cannot be classified by the current universe (UNIVERSE_GAP).
2. New family-class encountered (FAMILY_PATCH_NEEDED).
3. AIC field insufficient (AIC_INSUFFICIENT).
4. Confirmed false classification post-release (CLASSIFICATION_FIX).
5. Repair executor bug discovered (EXECUTOR_FIX).
6. Decision tree routing error (TREE_FIX).
7. Documentation nit carried over from LP review (DOC_NIT, low priority).

## Registration procedure

1. **Document the issue:**
   - `case_id` (real project that triggered)
   - `issue_type` (one of the seven above)
   - `affected_axis` / `affected_family` / `affected_function`
   - `severity` (CRITICAL / MAJOR / MINOR)
   - `workaround_used` (how was it handled in v1.0?)

2. **Append to** `change_control/v1_1_candidate_register.csv`.
   Columns: `candidate_id, source_p_number, issue_type, affected_axis,
   affected_label, affected_executor, required_patch, required_rerun_prompts,
   status, registered_date`.

3. **Set `required_rerun_steps`** — which prompts / phases need re-execution.

## v1.1 release trigger

v1.1 is triggered when ANY of:

- ≥10 candidates in register (volume threshold).
- ≥1 CRITICAL severity (urgency).
- 6 months since v1.0 (calendar).
- Major v4.x universe upgrade (e.g., v4.3).

## v1.1 release procedure

1. Group candidates by phase impact.
2. Re-execute affected phase(s) (start from earliest impacted).
3. Re-run all subsequent CHECKs (CHECK-N onwards).
4. Re-run LP Panels for impacted checkpoints (with real non-Claude LP-B).
5. Re-do golden validation (subset, with NEW goldens for new families).
6. H4 sample audit (PATCH-5 still applies, sample size 26).
7. H5 final approval.
8. Tag git as `v1.1.0`.

## Forbidden changes (require v2.0 not v1.1)

- Removing existing F-codes.
- Changing Q-code numbering (e.g., re-using Q17).
- Renaming `action_function` names (breaks backward compat).
- Changing decision tree node order (breaks audit-trail compatibility).

For these → v2.0 with full rebuild.

## Current v1.1 candidate register snapshot (as of 2026-05-22)

| candidate_id | issue_type | severity | description |
|---|---|---|---|
| V1_1_001 | AUDIT_REPLAY_NEEDED | MAJOR | Re-run H4 with real PMX reviewer (simulated_human_signer=TRUE in v5.1) |
| V1_1_002 | UNIVERSE_GAP | MINOR | Add F09 + F12 to synthetic seed-pack and regenerate |
| V1_1_003 | GOLDEN_GAP | MINOR | Register golden datasets for F25 + F27 |
| V1_1_004 | RELEASE_HASH | MINOR | Add D3 + D4 hash files under `release/v1.0/` |
| V1_1_005 | DOC_NIT | MINOR | Document N8 Q15A normalization and F30 reservation |

Source-of-truth: `change_control/v1_1_candidate_register.csv`.

---

*— End of SOP_change_control_v1_0.md —*
