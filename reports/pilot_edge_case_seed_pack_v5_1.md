# Pilot Edge-Case Seed Pack (v5.1)

**Status:** MANDATORY — universe freeze (Phase 5 in Step 2) cannot proceed
unless `data/pilot_fingerprints/empirical_fingerprints_pilot.csv` covers all
20 categories below with at least one row each.

**Source:** v5.1 patch P5-06 (pilot diversity enforcement).

## Summary table

| # | Category | Group | Expected family | Expected terminal |
|---|---|---|---|---|
| 1 | Standard SDTM/ADaM popPK | Routine | F01 | AUTO |
| 2 | Multi-study pooled popPK | Routine | F02 | REPAIR |
| 3 | SAD/MAD with ADDL/II | Routine | F07 | AUTO or REPAIR |
| 4 | Crossover/BA-BE | Routine | F08 | REPAIR |
| 5 | DDI victim-only | Routine | F09 | REPAIR |
| 6 | Pediatric mg/kg/BSA | Routine | F12 | REPAIR |
| 7 | TDM/RWD irregular dosing | Routine | F20 | REPAIR |
| 8 | Simple preclinical PK | Routine | F19 | AUTO |
| 9 | Titration/adaptive dosing | v4.1 Edge | F07 | REPAIR or Q08 |
| 10 | Loading-maintenance regimen | v4.1 Edge | F01 | REPAIR or Q08 |
| 11 | Infusion stop-restart | v4.1 Edge | F01 | REPAIR or Q04 |
| 12 | ADDL vs actual dose conflict | v4.1 Edge | F01 | REPAIR or Q14 |
| 13 | Reanalysis duplicate (final flag) | v4.1 Edge | F01 | REPAIR or Q15D |
| 14 | ADC multi-analyte (total Ab + conjugated + payload) | v4.2 Modality | F24 | REPAIR or Q16 |
| 15 | Bispecific PK + soluble target | v4.2 Modality | F25 | REPAIR or Q16 |
| 16 | CAR-T cellular kinetics (qPCR or FACS) | v4.2 Modality | F26 | REPAIR or Q01 |
| 17 | mRNA prime/boost with immunogenicity | v4.2 Modality | F27 | REPAIR or Q19 |
| 18 | DDI victim+perpetrator (dual CMT) | v4.2 Modality | F22 | REPAIR or Q09 |
| 19 | Pregnancy PK with delivery-anchored time | v4.2 Special Pop | F28 | REPAIR or Q12 |
| 20 | Lactation/mother-infant dyad PK with milk matrix | v4.2 Special Pop | F29 | REPAIR or Q18 |

---

## Per-category detail

### 1. Standard SDTM/ADaM popPK
- description: CDISC-compliant ADPC + ADaM EX/DM/VS bundle.
- expected family_id: F01
- expected modality_class: SMALL_MOLECULE or MAB
- expected endpoint_data_type: PK_CONCENTRATION
- key axis states: A0=AIC-PK, A1=ID-DEFINED, A2=TIME-DEFINED, A3=DOSE-DEFINED, A4=REGIMEN-FIXED, A5=BIOANALYTICAL-FINAL, A6=COVARIATE-COMPLETE, A7=SUBJECT-LEVEL-COVARIATE, A8=SINGLE-ANALYTE, A9=REANALYSIS-NONE, A10=STRUCTURED
- minimum AIC fields: model_family, analysis_objective, time_policy
- expected terminal: AUTO
- subcases: policy-present (AUTO), no QUARANTINE subcase

### 2. Multi-study pooled popPK
- description: 3+ studies pooled with SUBJID collisions.
- expected family_id: F02
- modality_class: SMALL_MOLECULE / MAB
- endpoint: PK_CONCENTRATION
- key states: A1=ID-DUPLICATE-RESOLVABLE
- required AIC: id_disambiguation_policy
- terminal: REPAIR (policy present) / QUARANTINE Q03 (absent)

### 3. SAD/MAD with ADDL/II
- description: Ascending-dose study using ADDL/II expansion.
- expected family_id: F07
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A4=REGIMEN-EXPANDABLE-ADDL
- required AIC: dose_reconstruction_policy
- terminal: AUTO or REPAIR / Q08 (no policy)

### 4. Crossover/BA-BE
- description: 2×2 crossover.
- expected family_id: F08
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A4=REGIMEN-FIXED with multiple periods
- required AIC: occasion_policy
- terminal: REPAIR / Q10

### 5. DDI victim-only
- description: DDI study measuring victim drug only.
- expected family_id: F09
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A8=DDI-VICTIM-ONLY
- required AIC: cmt_analyte_policy
- terminal: REPAIR / Q09

### 6. Pediatric mg/kg/BSA
- description: Pediatric PK with weight-based dosing.
- expected family_id: F12
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A3=DOSE-WEIGHT-BASED or DOSE-BSA-BASED
- required AIC: dose_reconstruction_policy
- terminal: REPAIR / Q08

### 7. TDM/RWD irregular dosing
- description: Real-world TDM with pharmacy dispensing.
- expected family_id: F20
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A10=SEMI-STRUCTURED or RWD-ADHERENCE-UNRESOLVED
- required AIC: adherence_imputation_policy
- terminal: REPAIR / Q15C

### 8. Simple preclinical PK
- description: Rat/mouse sparse PK.
- expected family_id: F19
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A0=AIC-PRECLINICAL
- terminal: AUTO

### 9. Titration / adaptive dosing
- description: Per-subject titration regimen.
- expected family_id: F07
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A4=TITRATION-ADAPTIVE
- required AIC: dose_adaptation_policy
- terminal: REPAIR / Q08

### 10. Loading-maintenance regimen
- description: Loading dose then maintenance.
- expected family_id: F01
- modality_class: MAB
- endpoint: PK_CONCENTRATION
- key states: A4=LOADING-MAINTENANCE
- required AIC: dose_reconstruction_policy, transition_point
- terminal: REPAIR / Q08

### 11. Infusion stop-restart
- description: Continuous infusion with multiple interruptions.
- expected family_id: F01
- modality_class: MAB
- endpoint: PK_CONCENTRATION
- key states: A4=INFUSION-STOP-RESTART
- required AIC: infusion_reconstruction_policy
- terminal: REPAIR / Q04

### 12. ADDL vs actual dose conflict
- description: ADDL-expanded and actual conflict for a subset of doses.
- expected family_id: F01
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A4=ADDL-ACTUAL-CONFLICT
- required AIC: addl_actual_conflict_policy
- terminal: REPAIR / Q14

### 13. Reanalysis duplicate (with/without final flag)
- description: Original + reanalysis values for same sample.
- expected family_id: F01
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A9=REANALYSIS-FINAL-RESOLVABLE (policy) or REANALYSIS-FINAL-MISSING (no policy)
- required AIC: reanalysis_final_selection_policy
- terminal: REPAIR / Q15D

### 14. ADC multi-analyte
- description: ADC trial measuring total Ab + conjugated ADC + free payload.
- expected family_id: F24
- modality_class: ADC
- endpoint: PK_CONCENTRATION (multiple analytes)
- key states: A8=MULTI-CMT-DEFINED, analyte_role=[TOTAL_ANTIBODY, CONJUGATED_ADC, UNCONJUGATED_PAYLOAD]
- required AIC: cmt_analyte_policy, analyte_role
- terminal: REPAIR / Q16

### 15. Bispecific PK + soluble target
- description: Bispecific T-cell engager with parent + soluble target + complex.
- expected family_id: F25
- modality_class: BISPECIFIC
- endpoint: PK_CONCENTRATION
- key states: A8=MULTI-CMT-DEFINED, analyte_role=[PARENT, SOLUBLE_TARGET, DRUG_TARGET_COMPLEX]
- required AIC: cmt_analyte_policy, analyte_role
- terminal: REPAIR / Q16

### 16. CAR-T cellular kinetics (qPCR or FACS)
- description: Vector copy + CAR+ cell count over time, with lot-level covariate.
- expected family_id: F26
- modality_class: CELL_THERAPY
- endpoint: CELLULAR_KINETICS
- key states: A0=AIC-CELL_THERAPY, A5=CELLULAR-BLQ-DEFINED or CELLULAR-LLOQ-POLICY-MISSING, A7=PRODUCT-LEVEL-COVARIATE
- required AIC: cellular_LLOQ_derivation_policy, product_level_covariate_linkage_policy
- terminal: REPAIR / Q01 (cellular) or Q13 (lot mapping absent)

### 17. mRNA prime/boost with immunogenicity
- description: mRNA vaccine prime/boost; ADA + neutralizing endpoint.
- expected family_id: F27
- modality_class: MRNA
- endpoint: IMMUNOGENICITY
- key states: A0=AIC-IMMUNOGEN, A5=IMMUNOGEN-POSITIVITY-DEFINED or IMMUNOGEN-POSITIVITY-MISSING
- required AIC: positivity_adjudication_rule, dose_reconstruction_policy
- terminal: REPAIR / Q19

### 18. DDI victim+perpetrator (dual CMT)
- description: DDI study measuring both victim and perpetrator concentrations.
- expected family_id: F22
- modality_class: SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A8=DDI-VICTIM-PERPETRATOR
- required AIC: cmt_analyte_policy, dual_cmt_policy
- terminal: REPAIR / Q09

### 19. Pregnancy PK with delivery-anchored time
- description: Pregnant subjects; delivery date used as elapsed anchor.
- expected family_id: F28
- modality_class: MAB or SMALL_MOLECULE
- endpoint: PK_CONCENTRATION
- key states: A0=AIC-LACTATION (or AIC-PKPD with pregnancy context), A2=TIME-ELAPSED-RESOLVABLE
- required AIC: delivery_anchor_policy, elapsed_anchor_policy
- terminal: REPAIR / Q12

### 20. Lactation / mother-infant dyad PK with milk matrix
- description: Mother + infant PK joined by dyad key; milk LLOQ declared.
- expected family_id: F29
- modality_class: MAB
- endpoint: MATERNAL_INFANT_PK + MILK_PK
- key states: A0=AIC-LACTATION, A1=ID-DYAD-LINKABLE (policy present) or ID-DYAD-UNLINKED-POLICY-MISSING, A5 includes MILK matrix
- required AIC: dyad_linkage_policy, delivery_anchor_policy, milk_matrix_lloq_policy
- terminal: REPAIR / Q18 / Q12 / Q01

---

## Validation rule (referenced by Step 2 CHECK-3 / CHECK-5)

> Universe freeze (Phase 5 in Step 2) cannot proceed unless ALL 20 categories
> appear in `data/pilot_fingerprints/empirical_fingerprints_pilot.csv` with at
> least one row each. The pilot fingerprint check (CHECK-3) must enumerate
> coverage by category and refuse to PASS if any category is missing.

---

*— End of pilot_edge_case_seed_pack_v5_1.md —*
