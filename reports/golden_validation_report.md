# Golden Validation Report v1.0 (D8, post-H3)

**generated_at:** 2026-05-22T13:35:00+00:00
**universe_basis:** v4.2
**executor_version:** `db3a0793cec04e605735dc5cec0a7d47bd3eece50df5b1358c59f410839b94f0` (repair_executor.py)
**tree_version:** `dab2f6f7f44a42fa7db03e9ea83cbe8494b79580b458d31ec655be277bde4288` (operational_decision_tree.yaml)
**simulated_data_basis:** TRUE — HANDOVER §2.1 (synthetic seed-pack substitution; real PMX raw inputs unavailable in v5.1).

---

## Summary (v1.0 scope, post-H3)

- **total_golden_datasets (v1.0 scope):** 4
- **overall_pass_rate:** 4 / 4 = **100.0%**
- **deferred to v1.1:** 2 (G003 F09 DDI, G005 F12 Pediatric) — see
  `data/golden_datasets/golden_dataset_registry_v1_1_deferred.csv`
- **per_family_pass_rate (v1.0 scope):**
  - F01 routine: 100% (1/1)
  - F24 ADC: 100% (1/1)
  - F26 CAR-T: 100% (1/1)
  - F29 Maternal/Lactation: 100% (1/1)
- **v4.2_family_pass_rate:** F24/F26/F29 → 100% (3/3 in scope)
  - F25 (Bispecific), F27 (mRNA): routed by tree, no registered golden in v1.0
    (V1_1_003 candidate).
  - F28 (pregnancy): low scenario count (8); v1.1 expansion target.

## H3 Corrections Applied

- **registry_corrections:** 1 (registry split into `_v1_0.csv` + `_v1_1_deferred.csv`)
- **executor_bugs_confirmed:** 0
- **tree_bugs_confirmed:** 0
- **v1.1 deferrals (registry vs universe drift):** 2 (G003 F09, G005 F12)

H3 reviewer (placeholder): `(placeholder) PMX_Reviewer_A`, 2026-05-22.
Detailed approval log: `reports/human_review/h3_golden_approval_log.md`.
H3 sign-off: `APPROVED` with v1.1 caveats on G003 + G005.

## Per-Dataset Index (v1.0 scope)

| golden_id | project_id | family_id | terminal_match | dv_match | overall_status | h3_action |
|---|---|---|---|---|---|---|
| G001 | PROJ_ADC_014 | F24 | Y | Y (header check only) | PASS | none |
| G002 | PROJ_CART_016 | F26 | Y | Y (header check only) | PASS | none |
| G004 | PROJ_LAC_020 | F29 | Y | Y (header check only) | PASS | none |
| G006 | PROJ_S01_001 | F01 | Y | Y (header check only) | PASS | none |

(Full path traces in `reports/golden_validation_per_dataset/{golden_id}_detail.md`.)

## Known Limitations (v1.1 deferred)

| limitation | scope | reason | v1.1 plan |
|---|---|---|---|
| F09 DDI golden | G003 PROJ_DDI_005 | Not in 20 seed-pack categories used in Phase 3 synthetic generation; HANDOVER §2.1 | V1_1_002 — Add F09 to seed-pack and re-run P107 |
| F12 Pediatric golden | G005 PROJ_PED_006 | Same | V1_1_002 — Add F12 to seed-pack and re-run P107 |
| Deep DV-tolerance comparison | all goldens | No real raw inputs available; reference outputs are placeholders | Re-run pipeline with real data and DV tolerance 1e-6 |
| F25 / F27 golden coverage | absent | No goldens registered for these v4.2 families (routed by tree but no validation evidence) | V1_1_003 — Add ≥1 golden per family in v1.1 |
| F28 (pregnancy) low count | 8 scenarios | Acceptable for v1.0 | v1.1 expansion target |
| H4 simulated reviewer | all 26 samples | simulated_human_signer=TRUE (HANDOVER §2.2) | V1_1_001 — Re-run H4 with real PMX reviewer |

## Coverage Claim Contribution

This D8 report contributes to D9 (`release/v1.0/coverage_claim_statement.md`) as evidence of:

- **AUTO/REPAIR correctness:** 100% tree-routing match within the 4 evaluable v1.0-scope goldens (G001, G002, G004, G006), including representatives of v4.2 families F24, F26, F29.
- **QUARANTINE detection:** Indirectly via tree-table consistency (P103, 100%) — all 9 Q-code paths reachable; not exercised in this batch since no QUARANTINE expectation is registered.
- **v4.2 modality handling:** F24/F26/F29 pass rate 100% supports the v4.2 review-inclusive coverage claim.

The two v1.1-deferred goldens (F09, F12) are explicitly noted as **review-inclusive
coverage of scenario classes represented in v4.2 universe** — they are out
of the represented set, not out of the operational scope.

## Constraints honored

- No PHI in this report (all project_ids are internal synthetic codes).
- No deferred golden was silently removed; both are listed in
  `data/golden_datasets/golden_dataset_registry_v1_1_deferred.csv`.

---

*— End of golden_validation_report.md (D8, post-H3) —*
