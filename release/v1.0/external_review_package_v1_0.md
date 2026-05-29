# External Review Package — v1.0 (P138)

## System summary

The PMX-to-NONMEM Scenario Universe v1.0 is a hash-locked pipeline that
takes a sponsor's pharmacometric source dataset plus an Analysis Intent
Contract (AIC) and routes it to one of five terminal states: AUTO (ready
for NONMEM), REPAIR (ready after policy-driven transformations),
QUARANTINE (clear policy required from sponsor), UNSUPPORTED (out of
operational scope), or INVALID (corruption / irrecoverable).

The pipeline is built on three locked artifacts: a 2998-scenario universe
covering the Frozen Universe v4.2 (D1), an operational decision tree with
seven forced safety gates and twelve optional branching nodes (D6), and a
26-function repair executor (D7).  Every output dataset carries an audit
log linking input → tree path → output via SHA256 hashes.

## D1–D9 file list with SHA256

| ID | path | SHA256 |
|---|---|---|
| D1 | `data/scenario_universe/scenario_universe_v1.0.csv` | `afa253fb…` |
| D2 | `data/action_labels/scenario_action_table_locked.csv` | `8795a5d1…` |
| D3 | `data/decision_table/reduced_decision_table_v1.0.csv` | `73422767…` |
| D4 | `data/ilp/pairwise_distinguishability_matrix.npz` | `20bd7f42…` |
| D5 | `data/ilp/final_minimal_node_set.csv` | `ca40f5e8…` |
| D6 | `config/operational_decision_tree.yaml` | `dab2f6f7…` |
| D7 | `scripts/repair_executor/repair_executor.py` | `db3a0793…` |
| D8 | `reports/golden_validation_report.md` | `72c1a4a6…` |
| D9 | `release/v1.0/coverage_claim_statement.md` | `df141e76…` |
| — | COMBINED manifest | `fb52af05…` |

Full hashes in `release/v1.0/release_v1_0_combined.sha256`.

## Coverage statement

> See `release/v1.0/coverage_claim_statement.md` (D9) for verbatim text.

In short: **review-inclusive coverage of scenario classes represented in
v4.2 universe** is 100.00% of the 2962 in-scope scenarios.  Out-of-scope
cases (F31–F34) are explicitly excluded by family classification.

## H1–H5 approval dates (no PHI)

| H | role | signed | date |
|---|---|---|---|
| H1 | deidentification | YES | 2026-05-22 (simulated_human_signer=TRUE) |
| H2 | fingerprint | YES | 2026-05-22 (simulated_human_signer=TRUE) |
| H3 | golden | YES | 2026-05-22 (simulated_human_signer=TRUE) |
| H4 | audit + veto (VETO=NO) | YES | 2026-05-22 (simulated_human_signer=TRUE) |
| H5 | final release | APPROVED | 2026-05-22 (simulated_human_signer=TRUE) |

All five gates carry placeholder signatures pending real-reviewer replay
per V1_1_001.

## LP Panel summary

| CP | name | LP-B simulated | LP-C decision | H4-escalated |
|---|---|---|---|---|
| CP1 | config_semantic_review (backfilled) | TRUE | APPROVE | NO |
| CP2 | universe_attack_freeze | TRUE | APPROVE | NO |
| CP3 | repair_semantic_review | TRUE | APPROVE | NO |
| CP4 | action_label_adjudication | TRUE | APPROVE | NO |
| CP5 | action_label_lock | TRUE | APPROVE | NO |
| CP6 | minimal_node_approval | TRUE | APPROVE | NO |
| CP7 | release_coverage_approval | TRUE | APPROVE_FOR_H5 | YES (H5 final) |

All LP-B runs simulated; real-release run requires fresh non-Claude session.

## Known limitations & v1.1 roadmap

| ID | description |
|---|---|
| V1_1_001 | Real-data H4 audit replay |
| V1_1_002 | F09 / F12 family universe gap |
| V1_1_003 | F25 / F27 golden gap |
| V1_1_004 | D3 / D4 release-hash entries |
| V1_1_005 | CP1 doc nits (N8 Q15A, F30 reservation) |
| V1_1_006 | Q08 / Q12 generator paths (100-case soft gap) |

v1.1 triggered when: ≥10 candidates / ≥1 CRITICAL / 6mo since v1.0 / v4.x upgrade.
See `release/v1.0/SOP_change_control_v1_0.md`.

---

*— External review package v1.0 — 4 pages max recommended. —*
