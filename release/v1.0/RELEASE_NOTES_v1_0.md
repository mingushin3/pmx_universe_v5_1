# Release v1.0 Notes — PMX-to-NONMEM Scenario Universe

**Released:** 2026-05-22
**Universe basis:** Frozen Universe v4.2
**Combined release hash:** `fb52af05bb5cb3e56fbe9164742dcd9bfaabeaf8ca1f85d83afd49e5ad82397c`
**Companion:** `release/v1.0/release_v1_0_combined.sha256`

> **Note on simulated audit trail.** v5.1 was built without real PMX raw data
> and without real human reviewer sessions.  All `H*` sign-offs in this release
> carry `simulated_human_signer: TRUE` and `lp_b_simulated: TRUE`.  Before any
> sponsor-facing or regulatory submission, the H1–H5 logs and LP-B panels must
> be re-issued in real sessions (v1.1 register V1_1_001).

---

## Approved by H5

- **Approver:** `(placeholder) PMX_Lead_A`
- **Date:** 2026-05-22
- **Sign-off file:** `release/v1.0/H5_final_release_approval.md`
- **Decision:** APPROVED FOR RELEASE v1.0 (simulated_human_signer=TRUE)

## Deliverables (9 final artifacts with SHA256)

| ID | Path | SHA256 |
|---|---|---|
| D1 | `data/scenario_universe/scenario_universe_v1.0.csv` | `afa253fb26c832c1c98a9c3e636b26b0c5092f3316d2f646ac22f6db42f3f0e0` |
| D2 | `data/action_labels/scenario_action_table_locked.csv` | `8795a5d1944ae4d97db4685cfb5236e310c7fe12dd344a4e6fcacf9825eafd28` |
| D3 | `data/decision_table/reduced_decision_table_v1.0.csv` | `734227679af3337fa925ce63588a65efbfbae43559d77c1c2c52e2e7fa78474c` |
| D4 | `data/ilp/pairwise_distinguishability_matrix.npz` | `20bd7f426ed66edc86a1630e387e3726bff0c3a47dedcde867bf34d7a607498b` |
| D5 | `data/ilp/final_minimal_node_set.csv` | `ca40f5e8f6e092b2031e7438c4b07b423a4a69906b6f09bdf71ba00cc92afa5b` |
| D6 | `config/operational_decision_tree.yaml` | `dab2f6f7f44a42fa7db03e9ea83cbe8494b79580b458d31ec655be277bde4288` |
| D7 | `scripts/repair_executor/repair_executor.py` | `db3a0793cec04e605735dc5cec0a7d47bd3eece50df5b1358c59f410839b94f0` |
| D8 | `reports/golden_validation_report.md` | `72c1a4a66959cd340c1b483e842680c149676bcef5be0123f7901cf19a86c202` |
| D9 | `release/v1.0/coverage_claim_statement.md` | `0da3a388ad8acfe505895bfae8ff435b36848971531af9bc174226e1e496e402` |
| — | COMBINED (SHA256 of concatenated individual hashes) | `fb52af05bb5cb3e56fbe9164742dcd9bfaabeaf8ca1f85d83afd49e5ad82397c` |

## Coverage (review-inclusive; PATCH-7 compliant wording)

PMX-to-NONMEM Scenario Universe v1.0 provides **review-inclusive coverage of
scenario classes represented in the Frozen Universe v4.2 of ≥95%** (this
release: **100%** of the 2962 in-scope scenarios route through the locked
operational decision tree D6 to a terminal_state).  Out-of-scope cases
(F31–F34) are explicitly excluded by family classification.  "Review-inclusive"
counts AUTO, REPAIR, and QUARANTINE as valid outcomes; QUARANTINE is a
deliberate signal to the operator to clear the gated condition, not a
failure mode.  This release does NOT claim coverage of all possible
scenarios; new modalities or sponsor data shapes outside Frozen Universe v4.2
require a v1.1 cycle (see `release/v1.0/SOP_change_control_v1_0.md`,
issued at Phase 11 P117).

| metric | value |
|---|---|
| review_inclusive | 100.00% (2962 / 2962) |
| operational (AUTO + REPAIR) | 25.46% (754 / 2962) |
| auto_only | 3.92% (116 / 2962) |
| unsupported_invalid_rate | 1.20% (36 / 2998) |

## Known limitations (v1.1 deferred)

| ID | item | reason |
|---|---|---|
| V1_1_001 | real-data H4 audit replay | v5.1 built with simulated_human_signer=TRUE (HANDOVER §2.2) |
| V1_1_002 | F09 (DDI) + F12 (Pediatric) golden families absent | Not in 20-seed-pack used in Phase 3 (HANDOVER §2.1); deferred to `golden_dataset_registry_v1_1_deferred.csv` |
| V1_1_003 | F25 (Bispecific) + F27 (mRNA) lack registered goldens | Routed by tree, no golden-validation evidence in v1.0 |
| V1_1_004 | D3 / D4 release-hash entries absent | Hashed via combined manifest; standalone hash files deferred |
| V1_1_005 | CP1 LP-B documentation nits | N8 Q15A normalization + F30 reservation comment |

## Universe basis

Frozen Universe v4.2 (PATCH-1 applied; F24–F29 v4.2 families).

## LP Panel results (CP1–CP7)

| CP | name | LP-A | LP-B simulated | LP-C decision |
|---|---|---|---|---|
| CP1 | config_semantic_review | APPROVE | TRUE (Phase 10 backfill) | APPROVE |
| CP2 | universe_attack_freeze | APPROVE | TRUE | APPROVE |
| CP3 | repair_semantic_review | APPROVE (cond.) | TRUE | APPROVE |
| CP4 | action_label_adjudication | APPROVE | TRUE | APPROVE |
| CP5 | action_label_lock | APPROVE | TRUE | APPROVE |
| CP6 | minimal_node_approval | APPROVE | TRUE | APPROVE |
| CP7 | release_coverage_approval | APPROVE | TRUE | APPROVE_FOR_H5 |

All LP-B panels were simulated in this build; the canonical run requires a
fresh non-Claude session per HANDOVER §2.2.

## Human checkpoints (H1–H5)

| H | name | status |
|---|---|---|
| H1 | deidentification | SIGNED (simulated_human_signer=TRUE) |
| H2 | fingerprint | SIGNED (simulated_human_signer=TRUE) |
| H3 | golden | SIGNED (simulated_human_signer=TRUE) |
| H4 | audit + veto (PATCH-5) | SIGNED, VETO=NO (simulated_human_signer=TRUE) |
| H5 | final release | APPROVED (simulated_human_signer=TRUE) |

All five gates are filled with placeholder signatures pending real-reviewer
replay per V1_1_001.

## Validation evidence summary

- Decision Tree ↔ Decision Table consistency (P103): **100.000%** (337/337 D3 classes).
- NONMEM-Ready QC (P104): **21 checks**, **12/12 pytest PASS**.
- Golden Validation (post-H3, v1.0 scope): **4/4 PASS = 100%** (G001 F24, G002 F26, G004 F29, G006 F01).
- H4 Blinded Sampling Audit (PATCH-5): **0/26 mismatches**; 0 LP-flagged candidates.
- v5.1 PATCH-1 … PATCH-9: all applied.

## Wording compliance (PATCH-7)

This file's coverage claim uses only the prescribed phrasing
"review-inclusive coverage of scenario classes represented in v4.2 universe".
The four phrasings disallowed by PATCH-7 (see
`release/v1.0/coverage_claim_statement.md` §"Compliance check") do not
appear in any body content of this file.

---

*— End of RELEASE_NOTES_v1_0.md —*
