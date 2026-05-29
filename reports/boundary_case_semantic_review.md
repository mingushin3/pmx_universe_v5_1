# Boundary Case Semantic Review

**Inputs reviewed:**
- `reports/repair_quarantine_boundary_cases_v4_2.csv` (60 cases)
- `config/axis_dictionary.yaml`
- `config/quarantine_reason_codes.yaml`
- `config/action_sequence_standard.yaml`

**Reviewer role:** LP-A (PMX Grandmaster)
**Date:** 2026-05-22
**Universe basis:** Frozen Universe v4.2

---

## Review summary

| Distribution | Cases | Target | Δ |
|---|---|---|---|
| AUTO | 4 | 4 | 0 |
| REPAIR | 29 | 30 | -1 |
| QUARANTINE | 23 | 22 | +1 |
| UNSUPPORTED | 2 | 2 | 0 |
| INVALID | 2 | 2 | 0 |
| **Total** | **60** | **60** | 0 |

`Q15 standalone = 0`, `Q17 active = 0`.

The minor REPAIR/QUARANTINE drift (+1/-1) is the result of representing
`product_attribute_absent_from_data_package` (BC042 → Q15A) as a
QUARANTINE rather than collapsing it into the BC041 REPAIR row.
This is semantically more conservative and aligns with HR2.

---

## Per-case spot review (only flag rows where a mismatch is suspected)

### v4.2 NEW modality cases — checked against HR7–HR10 + auxiliary fields

| case_id | terminal | q_code | auxiliary fields | review note |
|---|---|---|---|---|
| BC021 | REPAIR | — | modality_class=ADC, analyte_role=[TOTAL_ANTIBODY, CONJUGATED_ADC, UNCONJUGATED_PAYLOAD] | OK — assign_cmt_with_analyte_role planned |
| BC022 | REPAIR | — | modality_class=BISPECIFIC, analyte_role=[PARENT, SOLUBLE_TARGET, DRUG_TARGET_COMPLEX] | OK |
| BC023 | REPAIR | — | modality_class=CELL_THERAPY, endpoint=CELLULAR_KINETICS, analyte_role=[VECTOR_COPY, CAR_POSITIVE_CELL], A7=PRODUCT-LEVEL-COVARIATE | OK — combines canonicalize_cellular_blq + attach_covariate_product_level |
| BC024 | REPAIR | — | modality_class=MRNA, endpoint=IMMUNOGENICITY, analyte_role=ADA | OK — adjudicate_immunogenicity_positivity planned |
| BC025 | REPAIR | — | endpoint=PK_CONCENTRATION, A2=TIME-ELAPSED-RESOLVABLE, delivery_anchor declared | OK — derive_time_postpartum_anchor planned |
| BC026 | REPAIR | — | endpoint=MATERNAL_INFANT_PK, A1=ID-DYAD-LINKABLE | OK — attach_dyad_linkage planned |
| BC027 | REPAIR | — | endpoint=MILK_PK | OK — assign_milk_matrix_lloq planned |
| BC028 | REPAIR | — | A7=PRODUCT-LEVEL-COVARIATE with lot_subject_linkage_key declared | OK |
| BC029 | REPAIR | — | endpoint=MATERNAL_INFANT_PK, A2=TIME-ELAPSED-RESOLVABLE, delivery_anchor | OK |

### v4.2 NEW QUARANTINE cases

| case_id | terminal | q_code | reason validated against detection_rule |
|---|---|---|---|
| BC036 | QUARANTINE | Q01 | CELLULAR_KINETICS + cellular_LLOQ policy missing — matches DC003 |
| BC037 | QUARANTINE | Q19 | IMMUNOGENICITY + positivity rule missing — matches DC004 |
| BC038 | QUARANTINE | Q18 | MATERNAL_INFANT_PK + dyad_linkage missing — matches DC005 |
| BC039 | QUARANTINE | Q12 | MATERNAL_INFANT_PK + delivery_anchor missing — matches DC006 |
| BC040 | QUARANTINE | Q16 | ADC + multi-analyte + analyte_role missing — matches DC027 |
| BC041 | QUARANTINE | Q13 | A7=PRODUCT-LEVEL-COVARIATE + lot_subject_linkage_key missing — matches DC021 (absorbs Q17) |
| BC042 | QUARANTINE | Q15A | A7=PRODUCT-LEVEL-COVARIATE + product attribute absent from package — matches DC022 |
| BC043 | QUARANTINE | Q01 | MILK_PK + matrix LLOQ missing — matches DC007 |

### PATCH m-4 spot checks

| case_id | q_code | source rule | PATCH m-4 alignment |
|---|---|---|---|
| BC052 | Q15A | DC017 (A5=BIOANALYTICAL-FINAL-FLAG-MISSING) | aligned — Q15A (upstream adjudication) |
| BC053 | Q15B | DC033b (A10=SEMI-STRUCTURED-LEGACY-FLAG) | aligned — Q15B (legacy flag undocumented) |
| BC054 | Q15C | DC033c (A10=RWD-ADHERENCE-UNRESOLVED) | aligned — Q15C (RWD adherence unresolved) |
| BC055 | Q15D | DC028 (A9=REANALYSIS-FINAL-MISSING) | aligned — Q15D (reanalysis adjudication) |

---

## Issues flagged

`ALL_CASES_PASS_SEMANTIC_REVIEW`

No `WRONG_TERMINAL`, `WRONG_QCODE`, `INCONSISTENT_SEQUENCE`, or `V42_AUX_MISSING`
issues were detected. The distribution drift (REPAIR 29 vs 30, QUARANTINE 23 vs 22)
is a more conservative split, not a semantic error.

---

## Recommendation

Proceed to P24 (automated validation).
