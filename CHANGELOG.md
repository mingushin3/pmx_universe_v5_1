# Changelog

All notable changes to PMX-to-NONMEM Scenario Universe will be recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## v0.1.0 (initialization)

- Repository scaffold created.
- Phase 0 charter, LP Panel template, logging utilities established.
- Working basis: Frozen Universe v4.2.

## v0.5.0 (2026-05-22)

- Repair Executor v1.0 LOCKED.
- 26 functions (19 v4.1 + 7 v4.2 NEW). 117 / 117 pytest PASS.
- LP Panel CP3 accept (lp_b_simulated=TRUE).

## v1.0.0 (universe freeze) (2026-05-22)

- Scenario Universe v1.0 FROZEN: 2992 scenarios, hash d0266bc9de099462...
- LP Panel CP2 accept (lp_b_simulated=TRUE).

## v0.7.0 (2026-05-22)

- Action Label LOCKED.
- D2 generated: 2992 rows, 85 unique labels, hash 03f8f9c5bff67305...
- CP4 + CP5 accept (lp_b_simulated=TRUE).

## v0.9.0 (2026-05-22)

- Minimal node set LOCKED: 19 nodes, objective 43.30.
- Forced nodes (N0,N1,N2,N3,N4,N5,N8) all included.
- Distinguishability coverage 100% of 50867 required pairs.

## v0.10.0 — Decision Tree LOCKED (2026-05-22)

- D6 `config/operational_decision_tree.yaml` generated and LOCKED.
- 126 internal nodes, 51 leaves (45 D3-backed + 6 synthetic forced-failure).
- Node order: N0 → N1 → N8 → N2 → N3 → N4 → N5, then 12 optional nodes by descending failure-risk.
- Tree ↔ Decision Table consistency (P103): 100.000% (337/337 D3 classes).
- NONMEM-ready QC (P104): 21 checks (S01–S05, E01–E05, B01–B03, C01–C03, V01–V04, A01) + 12 pytest PASS.
- Hashes recorded in `release/v1.0/decision_tree_v1_0.sha256`.

## v0.11.0 — Golden + H3 + H4 + CP7 (2026-05-22)

- D8 `reports/golden_validation_report.md` LOCKED (golden_validation_report_v1_0.sha256).
- Golden registry split: 4 in v1.0 scope (all PASS) + 2 deferred to v1.1 (F09, F12) via `golden_dataset_registry_v1_1_deferred.csv`.
- H3 SIGNED (simulated_human_signer=TRUE).
- H4 PATCH-5 blinded audit: 0/26 mismatches; VETO=NO. SIGNED.
- 26-sample extractor (`scripts/validation/h4_sample_extractor.py`) + false-class detector (0 candidates) added.
- CP7 LP panel trio APPROVED_FOR_H5 (lp_b_simulated=TRUE).
- CP1 LP panel backfilled (Phase 1 carryover); CP1 LP-C APPROVE.
- Coverage metrics finalized: review_inclusive 100% (2962/2962).
- v1.1 candidate register populated: V1_1_001..V1_1_005.

## v1.0.0 — RELEASED on 2026-05-22

- D9 `release/v1.0/coverage_claim_statement.md` issued (PATCH-7 compliant).
- H5 SIGNED (simulated_human_signer=TRUE) — APPROVED FOR RELEASE v1.0.
- All 9 deliverables (D1–D9) hashed; combined hash recorded in `release/v1.0/release_v1_0_combined.sha256` (COMBINED: `fb52af05bb5cb3e56fbe9164742dcd9bfaabeaf8ca1f85d83afd49e5ad82397c`).
- Hash chain integrity verified.
- Audit trail (H1–H5 simulated; CP1–CP7 with lp_b_simulated=TRUE) complete.
- Known limitations documented (V1_1_001..V1_1_005).
- Next: Phase 11 — Change Control + 100-case Validation (post-release stress test) + SOPs.
