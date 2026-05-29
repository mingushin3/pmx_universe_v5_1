# Regulatory Submission Evidence Pack Skeleton (v1.0)

> Fill in `[FILL-IN]` placeholders for each submission.

## 1. System description

The PMX-to-NONMEM Scenario Universe v1.0 is a deterministic, hash-locked
pipeline that classifies pharmacometric source datasets into NONMEM-ready
outputs.  It rests on:

- **D6 Decision Tree** (`config/operational_decision_tree.yaml`, SHA256
  `dab2f6f7…`) — 19 internal-node binary tree with seven forced gates.
- **D7 Repair Executor** (`scripts/repair_executor/repair_executor.py`,
  SHA256 `db3a0793…`) — 26 v4.2 repair functions implementing the
  operational pipeline.

Each output dataset carries an audit_log JSON with decision_path,
action_sequence_executed, parameter_policies, and a SHA256 hash chain
linking input → tree → output.

## 2. Validation evidence

- **Tree ↔ Table consistency (P103):** 100.000% (337/337 D3 classes).
- **NONMEM-Ready QC (P104):** 21 checks; 12/12 pytest PASS.
- **Golden Validation (D8):** 4/4 PASS in v1.0 scope (G001 F24, G002 F26,
  G004 F29, G006 F01).  2 deferred to v1.1 (F09, F12 — not in synthetic
  universe).
- **H4 Blinded Sampling Audit (PATCH-5):** 26 samples, 0 mismatches,
  VETO=NO.
- **100-case post-release stress test:** 100/100 PASS (100.0%).

## 3. Coverage claim statement

> [Insert verbatim from `release/v1.0/coverage_claim_statement.md`.]

## 4. Human oversight evidence

- H1 deidentification — SIGNED [FILL-IN signer].
- H2 fingerprint approval — SIGNED [FILL-IN signer].
- H3 golden reference approval — SIGNED [FILL-IN signer].
- H4 audit + veto — SIGNED, VETO=NO [FILL-IN signer].
- H5 final release approval — APPROVED [FILL-IN signer], 2026-05-22.

> **NOTE:** v5.1 build was completed with `simulated_human_signer=TRUE` for
> all five H gates (HANDOVER §2.2).  For any regulatory submission, the
> H1–H5 logs MUST be re-issued with real reviewer identification per
> V1_1_001.

## 5. Audit trail

- `reports/execution_log.csv` — per-prompt CHECK pass log.
- `release/v1.0/release_v1_0_combined.sha256` — combined manifest.
- Per-case audit_log JSON (one per AUTO/REPAIR invocation, alongside the
  NONMEM-ready CSV).

## 6. Known limitations

| ID | description |
|---|---|
| V1_1_001 | Real-data H4 audit replay pending |
| V1_1_002 | F09 / F12 family universe gap |
| V1_1_003 | F25 / F27 golden gap |
| V1_1_004 | D3 / D4 release-hash entries deferred |
| V1_1_005 | CP1 documentation nits |
| V1_1_006 | Q08 / Q12 generator paths (100-case soft gap) |

## 7. Compliance attestations

- HR12 / PATCH-7: coverage claim uses only "review-inclusive coverage of
  scenario classes represented in v4.2 universe".  No prohibited phrasings.
- HR1: no Q15 standalone leaves.
- HR2: no Q17 leaves.
- HR3: 100% of D3 classes routed.
- HR4: all 7 forced nodes present in D6.

## 8. Submission cover sheet

- Project: [FILL-IN]
- Indication: [FILL-IN]
- Modality: [FILL-IN]
- Sponsor: [FILL-IN]
- Submission type: [FILL-IN]
- Submission date: [FILL-IN]

---
