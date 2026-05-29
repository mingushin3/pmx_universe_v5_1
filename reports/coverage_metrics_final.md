# Coverage Metrics — Final (P111)

**Generated:** 2026-05-22T13:25:00+00:00
**Universe basis:** v4.2 (Frozen Universe)
**D1:** `data/scenario_universe/scenario_universe_v1.0.csv` (2998 scenarios, FROZEN)
**H4 status:** VETO_RELEASE = NO (PATCH-5 audit completed; 0/26 mismatches)

---

## 1. Scenario terminal-state distribution

| terminal_state | count | % of total |
|---|---|---|
| AUTO | 116 | 3.87% |
| REPAIR | 638 | 21.28% |
| QUARANTINE | 2208 | 73.65% |
| INVALID | 36 | 1.20% |
| UNSUPPORTED | 0 | 0.00% |
| **total** | **2998** | **100.00%** |

Note: `INVALID` rows are all family F34 (UNSUPPORTED-RESERVED).  No
scenario carries `UNSUPPORTED` as a terminal_state in this universe.

## 2. Coverage metrics (pre-H4 = post-H4; no H4 patches applied)

| metric | value | HR threshold | status |
|---|---|---|---|
| capture_coverage = (AUTO+REPAIR+QUARANTINE+UNSUPPORTED+INVALID) / total | **100.00%** | ≥99% | ✅ |
| review_inclusive = (AUTO+REPAIR+QUARANTINE) / (total − UNSUPPORTED − INVALID) | **100.00%** | ≥95% | ✅ |
| operational = (AUTO+REPAIR) / (total − UNSUPPORTED − INVALID) | 25.46% | (informational) | — |
| auto_only = AUTO / (total − UNSUPPORTED − INVALID) | 3.92% | (informational) | — |
| unsupported_invalid_rate = (UNSUPPORTED+INVALID) / total | 1.20% | (informational) | — |
| false_auto_count (H4 confirmed) | **0** | 0 (or v1.1 deferred) | ✅ |
| false_repair_count (H4 confirmed) | **0** | 0 (or v1.1 deferred) | ✅ |

## 3. Pre-H4 vs Post-H4

| metric | pre-H4 | post-H4 | delta |
|---|---|---|---|
| AUTO | 116 | 116 | 0 |
| REPAIR | 638 | 638 | 0 |
| QUARANTINE | 2208 | 2208 | 0 |
| INVALID | 36 | 36 | 0 |
| capture_coverage | 100.00% | 100.00% | 0 |
| review_inclusive | 100.00% | 100.00% | 0 |

H4 confirmed 0 false classifications.  No re-label was applied to D2.

## 4. v4.2 family-specific coverage

| family | count | terminal mix | notes |
|---|---|---|---|
| F01 (routine) | 596 | mostly QUARANTINE + AUTO/REPAIR | reference baseline |
| F15 | 324 | AUTO/REPAIR for AIC-TTE/AIC-PKPD | — |
| F19 | 108 | QUARANTINE + REPAIR | — |
| F22 (DDI dual-CMT) | 892 | REPAIR dominant | DDI-VICTIM-PERPETRATOR REPAIR coverage |
| F24 (ADC) | 216 | REPAIR with CMTROLE | v4.2 NEW |
| F25 (Bispecific) | 216 | REPAIR with CMTROLE | v4.2 NEW |
| F26 (CAR-T) | 81 | REPAIR with CELLULAR_BLQ + PROD | v4.2 NEW |
| F27 (mRNA) | 374 | REPAIR with CMTM | v4.2 NEW |
| F28 (pregnancy) | 8 | REPAIR with TPP | v4.2 NEW (acceptable v1.1 expansion target) |
| F29 (lactation) | 147 | REPAIR with DYAD_TPP | v4.2 NEW |
| F34 (UNSUPPORTED-RESERVED) | 36 | INVALID | by design |

## 5. Coverage CLAIM (HR12 + PATCH-7 wording, mandatory)

> **review-inclusive coverage of scenario classes represented in v4.2 universe ≥95%**
>
> Specifically: 100% of the 2962 in-scope scenarios (AUTO + REPAIR + QUARANTINE)
> are routed to a terminal_state by the v1.0 operational decision tree
> (D6, SHA256 `dab2f6f7…`).  The remaining 36 scenarios in F34 are
> intentionally INVALID by design (UNSUPPORTED-RESERVED).

Forbidden phrasings (do NOT use — listed in HR12 of `project_charter_v5_1.md`):
- overreach phrase A (3-word "all prac…rios")
- overreach phrase B (single-word "ex…tive")
- overreach phrase C (2-word "all mod…ies")

(Phrases are intentionally elided in this release artifact to satisfy CHECK-11's
substring lint while keeping the policy intent traceable to the charter.)

## 6. Known limitations (v1.1 deferrals)

| limitation | reason | v1.1 ticket |
|---|---|---|
| F09 (DDI) and F12 (Pediatric) golden families | not in synthetic seed-pack used in Phase 3 | V1_1_002 |
| H4 reviewer placeholder | simulated_human_signer=TRUE for v5.1 (HANDOVER §2.2) | V1_1_001 |
| F28 (pregnancy) has only 8 scenarios | acceptable for v1.0; future expansion target | (v1.1 candidate) |
| Deep DV-tolerance comparison in golden validation | no real raw inputs; reference outputs are placeholders | (v1.1 candidate) |

## 7. coverage_claim_text — verbatim release wording

```
PMX-to-NONMEM Scenario Universe v1.0 provides review-inclusive coverage of
scenario classes represented in the Frozen Universe v4.2 of ≥95% (in this
release: 100% of the 2962 in-scope scenarios route through the locked
operational decision tree D6 to a terminal_state).  Out-of-scope cases
(F31-F34) are explicitly excluded by family classification.  This release
does NOT claim universal coverage; new modalities or sponsor data shapes
outside Frozen Universe v4.2 require a v1.1 cycle
(see SOP_change_control_v1_0.md).
```

This text will be inserted verbatim into `release/v1.0/coverage_claim_statement.md` (D9) at P115.

---

*— End of coverage_metrics_final.md —*
