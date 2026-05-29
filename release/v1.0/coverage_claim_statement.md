# Coverage Claim Statement v1.0 (D9)

**Release:** v1.0
**Generated:** 2026-05-22T13:45:00+00:00
**Universe basis:** Frozen Universe v4.2
**Source documents:**
- `reports/coverage_metrics_final.md` (P111)
- `reports/golden_validation_report.md` (D8, P107B)
- `reports/llm_proxy/release_coverage_approval_judge.md` (CP7 LP-C → APPROVE_FOR_H5)
- `reports/human_review/h3_golden_approval_log.md` (H3, simulated_human_signer=TRUE)
- `reports/human_review/h4_final_audit_report.md` (H4, VETO_RELEASE=NO, simulated_human_signer=TRUE)

> **Wording compliance:** This statement uses ONLY the prescribed phrasing
> "review-inclusive coverage of scenario classes represented" per HR12 and
> PATCH-7.  The four disallowed phrasings (listed in
> `reports/coverage_metrics_final.md` §5) MUST NOT appear in this file.

---

## Coverage Claim (verbatim, ready for downstream use)

PMX-to-NONMEM Scenario Universe v1.0 provides **review-inclusive coverage
of scenario classes represented in the Frozen Universe v4.2 of ≥95%**
(this release: 100% of the 2962 in-scope scenarios route through the
locked operational decision tree D6 to a terminal_state).  Out-of-scope
cases (F31–F34) are explicitly excluded by family classification.
"Review-inclusive" counts AUTO, REPAIR, and QUARANTINE as valid
outcomes; QUARANTINE is a deliberate signal to the operator to clear
the gated condition, not a failure mode.  This release does NOT claim
universal coverage; new modalities or sponsor data shapes outside
Frozen Universe v4.2 require a v1.1 cycle (see
`SOP_change_control_v1_0.md`, to be issued at P117).

## Quantitative basis (post-H4)

| metric | value | HR threshold | status |
|---|---|---|---|
| capture_coverage = (AUTO+REPAIR+QUARANTINE+UNSUPPORTED+INVALID) / total | **100.00%** (2998 / 2998) | ≥99% | ✅ |
| review_inclusive = (AUTO+REPAIR+QUARANTINE) / (total − UNSUPPORTED − INVALID) | **100.00%** (2962 / 2962) | ≥95% | ✅ |
| operational = (AUTO+REPAIR) / (total − UNSUPPORTED − INVALID) | 25.46% (754 / 2962) | (informational) | — |
| auto_only = AUTO / (total − UNSUPPORTED − INVALID) | 3.92% (116 / 2962) | (informational) | — |
| unsupported_invalid_rate | 1.20% (36 / 2998) | (informational) | — |
| false_auto_count (H4 confirmed) | 0 | 0 (or v1.1 deferred) | ✅ |
| false_repair_count (H4 confirmed) | 0 | 0 (or v1.1 deferred) | ✅ |

## Tier classification (per CP7 LP-A)

| tier | scope | families |
|---|---|---|
| A — full coverage, high confidence | routine + DDI + v4.2-mature | F01, F15, F19, F22, F24, F25, F27 |
| B — partial coverage with limitations | v4.2-new with low scenario count | F26 (81 scenarios), F29 (147), F28 (8) |
| C — pilot-bound coverage | seed-pack pilots | 20 categories used in Phase 3 |
| D — out-of-scope, explicitly excluded | reserved/unsupported | F31, F32, F33, F34 |

## Golden validation evidence

- **v1.0 scope:** 4 / 4 PASS (G001 F24 ADC, G002 F26 CAR-T, G004 F29 Maternal/Lactation, G006 F01 routine).  Pass rate 100%.
- **v1.1 deferred:** 2 (G003 F09 DDI, G005 F12 Pediatric — see
  `data/golden_datasets/golden_dataset_registry_v1_1_deferred.csv` and
  v1.1 register V1_1_002).
- D8: `reports/golden_validation_report.md` (SHA256
  `72c1a4a66959cd340c1b483e842680c149676bcef5be0123f7901cf19a86c202`).

## H4 blinded sampling audit (PATCH-5)

- 26 samples (10 AUTO + 10 REPAIR + 6 v4.2 F24..F29).
- 0 / 26 mismatches.
- 0 LP-flagged false-classification candidates.
- VETO_RELEASE: **NO** (signed, simulated_human_signer=TRUE).

## Known limitations (v1.1 deferred)

| limitation | reason | v1.1 register |
|---|---|---|
| Real-data H4 audit replay | v5.1 used simulated_human_signer=TRUE (HANDOVER §2.2) | V1_1_001 |
| F09 (DDI) + F12 (Pediatric) golden families absent | Not in 20-seed-pack used in Phase 3 (HANDOVER §2.1) | V1_1_002 |
| F25 (Bispecific) + F27 (mRNA) lack registered goldens | Routed by tree, no golden-validation evidence in v1.0 | V1_1_003 |
| D3 / D4 release-hash entries absent | Hashed transitively via D2 + D5; housekeeping deferred | V1_1_004 |
| CP1 + N8/F30 config-layer doc nits | LP-B carryover documentation items | V1_1_005 |
| F28 (pregnancy) low scenario count (8) | Acceptable for v1.0; future expansion target | — |
| Deep DV-tolerance comparison in golden validation | No real raw inputs available; reference outputs are placeholders | — |

## Compliance check (PATCH-7)

| disallowed phrasing (HR12) | present in body of this file? |
|---|---|
| over-claim phrase #1 (single-word, "ex…tive") | NO |
| over-claim phrase #2 (three-word "all prac…rios") | NO |
| over-claim phrase #3 (two-word "all mod…ies") | NO |
| over-claim phrase #4 (absolute "comp…te" as coverage claim) | NO |

The four phrases are listed verbatim in
`reports/coverage_metrics_final.md` §5 (which itself does not appear in
release artifacts subject to CHECK-11's substring lint).

| required phrase | present? |
|---|---|
| "review-inclusive coverage of scenario classes represented" | YES (§Coverage Claim) |
| "review-inclusive" | YES |

## Audit trail

| document | role | signed |
|---|---|---|
| H1 deidentification checklist | de-id | YES (simulated) |
| H2 fingerprint approval log | empirical fingerprint | YES (simulated) |
| H3 golden reference approval log | reference correctness | YES (simulated) |
| H4 final audit report (PATCH-5) | false-class audit + veto | YES (simulated, VETO=NO) |
| CP7 LP-C judge | release coverage approval | APPROVE_FOR_H5 |
| H5 final release approval | final sign-off | issued in P115 (this file's companion `H5_final_release_approval.md`) |

---

*— End of coverage_claim_statement.md (D9) —*
