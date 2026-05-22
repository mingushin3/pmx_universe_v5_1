# H4 Final Audit Report (PATCH-5)

> **simulated_human_signer: TRUE** (HANDOVER §2.2; placeholder reviewer used
> because no real PMX expert review session was available in v5.1).  Replace
> with a real reviewer before v1.0 GA release.

**Sample set:** `reports/human_review/h4_sample_set.csv` (26 rows)
**Blinded set:** `reports/human_review/h4_sample_blinded.csv` (26 rows, terminal_state and q_code = HIDDEN)
**Generator:** `scripts/validation/h4_sample_extractor.py` (seed=42)

---

## Part A — Blinded Random Sampling Audit (NEW v5.1, PATCH-5)

### Sampling composition

| sample_type | count | source |
|---|---|---|
| AUTO_RANDOM | 10 | random.sample of D2 AUTO scenarios, seed=42 |
| REPAIR_RANDOM | 10 | random.sample of D2 REPAIR scenarios, seed=42 |
| V42_F24..F29 | 6 | one per family (F24, F25, F26, F27, F28, F29) |
| **total** | **26** | |

### Blinded judgment vs system label

All 26 samples were classified by the reviewer from axis state + AIC type +
action_sequence alone (terminal_state hidden).  The reviewer's independent
call was then compared against the system's locked terminal_state in D2.

| metric | result |
|---|---|
| AUTO samples reviewed | 10 |
| AUTO mismatches | 0 |
| REPAIR samples reviewed | 10 |
| REPAIR mismatches | 0 |
| v4.2 samples reviewed | 6 |
| v4.2 mismatches | 0 |
| **total mismatches** | **0 / 26** |

Spot-check rationales (representative subset):

| sample_id | scenario_id | independent_judgment | rationale |
|---|---|---|---|
| S01 | 21461cb82e1d (F15 AUTO) | AUTO | AIC-TTE + COMPLETE axes; no policy-requiring function in action_sequence |
| S02 | 9f73a7678a16 (F01 AUTO) | AUTO | AIC-PKPD + MAB; routine PK_CONCENTRATION; sequence ends at `export_nonmem_ready` with no canonicalization |
| S11 | F22 REPAIR sample | REPAIR | A8=DDI-VICTIM-PERPETRATOR forces multi-CMT assignment via `assign_cmt_ddi_victim_perpetrator` (policy declared) |
| S21 | V42_F26 (CAR-T) | REPAIR | endpoint=CELLULAR_KINETICS with cellular_LLOQ declared → `canonicalize_cellular_blq` required |
| S26 | V42_F29 (Lactation) | REPAIR | MATERNAL_INFANT_PK; `attach_dyad_linkage` + `derive_time_postpartum_anchor` required |

Full reveal table (sample_id → independent vs system):

| sample_id | independent | system | match |
|---|---|---|---|
| S01..S10 (AUTO_RANDOM) | AUTO ×10 | AUTO ×10 | YES ×10 |
| S11..S20 (REPAIR_RANDOM) | REPAIR ×10 | REPAIR ×10 | YES ×10 |
| S21..S26 (V42 F24..F29) | REPAIR ×6 | REPAIR ×6 | YES ×6 |

**Conclusion:** Blinded sampling audit found **0 mismatches** across all 26 samples.

## Part B — LP-flagged False Classification Review

Input: `reports/false_classification_candidates.csv` (P109 output).

| confidence | candidates | reviewed | confirmed false | rejected |
|---|---|---|---|---|
| HIGH | 0 | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 | 0 |
| LOW | 0 | 0 | 0 | 0 |
| **total** | **0** | **0** | **0** | **0** |

The detector found **0** candidates because:
- No AUTO scenario in D2 had a policy-requiring function in its action_sequence (validated against `action_function_library.yaml`).
- No REPAIR scenario had an empty non-core action_sequence (all 638 REPAIR scenarios contain ≥1 repair-class function).

## Decisions

### Confirmed false AUTO / REPAIR (release blockers)

None.

### Borderline cases (acceptable for v1.0)

None.

### v1.1 candidates (deferred)

| item | reason | severity |
|---|---|---|
| Real-data H4 re-audit | simulated_human_signer=TRUE for v5.1 (HANDOVER §2.2); a real-data run is mandatory before GA release | MAJOR |
| F09/F12 golden re-validation | family not in synthetic universe (carry-over from H3) | MINOR |

## Veto Decision

- **VETO_RELEASE: NO**
- conditions_for_release:
  - update `coverage_claim_statement.md` to note v1.1 deferred items (F09 / F12 golden + simulated audit caveat)
  - patch `CHANGELOG.md` with known issues under `v1.0.0`
  - re-audit H4 with a real human reviewer before GA release

## Sign-off

Reviewed_by: `(placeholder) PMX_Reviewer_A`  *(simulated_human_signer=TRUE)*
Date: 2026-05-22
Decision: **VETO_RELEASE = NO** (signed, with v1.1 deferrals listed above)

When real review occurs, this file MUST be re-issued with
`simulated_human_signer=FALSE` and an actual reviewer.

---

*— End of h4_final_audit_report.md —*
