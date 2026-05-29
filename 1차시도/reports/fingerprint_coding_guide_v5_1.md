# Fingerprint Coding Guide v5.1

Use this guide when filling rows of
`data/pilot_fingerprints/fingerprint_template.csv` and producing
`{PROJECT_ID}_fingerprint_draft.md` files.

## Column reference (43 columns)

| Column | What to write | Forbidden |
|---|---|---|
| project_id | unique project ID (e.g., PROJ_S01_001) | spaces |
| family_candidate | F01..F29 or F31..F34 | other |
| source_format | csv / xlsx / sas7bdat / xpt / json / parquet | other |
| source_parser_subtype | when A10=SEMI-STRUCTURED, name the parser (e.g., "legacy_NONMEM_table") | "unknown" → Q15A |
| study_design | one-line summary | hallucinated content |
| aic_summary | 2–4 lines of AIC content | absent fields hidden |
| modality_class | one of 12 from axis_dictionary A0 auxiliary | invented values |
| endpoint_data_type | one of 10 | invented values |
| A0_state .. A10_state | exact `state_code` from axis_dictionary | invented codes |
| analyte_role | one of 13 (only when A8 is multi-CMT/DDI-VP/METABOLITE and modality is ADC/BISPECIFIC/CELL/GENE) | for non-required cases leave blank |
| input_tables | list of source tables | hidden tables |
| key_columns | ID, USUBJID etc | non-existent columns |
| time_columns | actual column names | guessed names |
| dose_columns | actual column names | guessed names |
| observation_columns | DV / PCSTRESN etc | guessed |
| covariate_columns | WT, AGE, etc | guessed |
| known_policies | list AIC fields with values | invented policies |
| missing_policies | list AIC fields absent | hidden absences |
| manual_steps_required | yes/no + short description | vague |
| expected_terminal_state | AUTO / REPAIR / QUARANTINE / UNSUPPORTED / INVALID / UNKNOWN | guesses |
| expected_q_code | Q01..Q19 (no Q15 standalone, no Q17) | Q15 / Q17 |
| expected_action_sequence | function names from action_sequence_standard | invented functions |
| golden_dataset_available | YES / NO / PREFERRED | unclear |
| raw_input_path | path under `data/raw_examples/...` | absolute/external paths |
| reference_output_path | path under `data/golden_datasets/...` | external |
| seed_category_id | 1..20 (or UNCERTAIN_n) | invented |
| v4_2_relevant_axes | comma-separated, e.g., "A0,A8" | irrelevant |
| fingerprint_confidence | HIGH / MEDIUM / LOW | other |
| unknown_field_count | integer | string |
| notes | free text | hallucinated context |

## UNKNOWN coding rule

> If you cannot determine the correct value from the data + AIC,
> write **UNKNOWN**. Never guess. A row with `unknown_field_count > 17`
> (>40% of 43 columns) triggers H2 escalation review.

## Forbidden patterns

- `q_code = "Q15"` standalone → must be Q15A/B/C/D
- `q_code = "Q17"` → forbidden, route to Q13 instead
- expected_terminal_state = AUTO with any REPAIR function in expected_action_sequence → contradictory
- expected_terminal_state = REPAIR with no required_policy declared → would fail HR4

## v5.1-specific guidance

### modality_class (A0 auxiliary)
12 values from `config/axis_dictionary.yaml` axis A0 auxiliary_fields:
SMALL_MOLECULE, PEPTIDE, MAB, ADC, BISPECIFIC, CELL_THERAPY,
GENE_THERAPY, MRNA, VACCINE, OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL,
OTHER_CUSTOM.

### endpoint_data_type
10 values: PK_CONCENTRATION, EXPOSURE_METRIC, CONTINUOUS_PD,
CATEGORICAL_PD, COUNT_PD, TTE_EVENT, CELLULAR_KINETICS,
IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK.

### analyte_role (A8 auxiliary)
Only fill in when A8 ∈ {MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR,
METABOLITE-DEFINED} AND modality_class ∈ {ADC, BISPECIFIC,
CELL_THERAPY, GENE_THERAPY}. Otherwise leave blank.

### seed_category_id
Must match `reports/pilot_edge_case_seed_pack_v5_1.md` 1..20.

## 5 example fingerprints (abbreviated)

### F01 routine (PROJ_S01_001)
- family: F01, modality: MAB, endpoint: PK_CONCENTRATION
- A0=AIC-PK, A1=ID-DEFINED, A2=TIME-DEFINED, A3=DOSE-DEFINED,
  A4=REGIMEN-FIXED, A5=BIOANALYTICAL-FINAL, A6=COVARIATE-COMPLETE,
  A7=SUBJECT-LEVEL-COVARIATE, A8=SINGLE-ANALYTE, A9=REANALYSIS-NONE,
  A10=STRUCTURED
- expected_terminal: AUTO
- seed_category_id: 1

### F09 DDI victim-only (PROJ_DDI_001)
- family: F09, modality: SMALL_MOLECULE, endpoint: PK_CONCENTRATION
- A8=DDI-VICTIM-ONLY, cmt_analyte_policy=ddi_victim_only
- expected_terminal: REPAIR, action_sequence includes assign_cmt_ddi_victim_only
- seed_category_id: 5

### F26 CAR-T cellular (PROJ_CART_002)
- family: F26, modality: CELL_THERAPY, endpoint: CELLULAR_KINETICS,
  analyte_role: [VECTOR_COPY, CAR_POSITIVE_CELL]
- cellular_LLOQ_derivation_policy declared
- expected_terminal: REPAIR (or Q01 if policy missing)
- seed_category_id: 16

### F29 lactation dyad (PROJ_LAC_003)
- family: F29, modality: MAB, endpoint: MATERNAL_INFANT_PK
- A1=ID-DYAD-LINKABLE, dyad_linkage_policy + delivery_anchor_policy declared
- expected_terminal: REPAIR
- seed_category_id: 20

### F22 DDI dual (PROJ_DDI_DUAL_001)
- family: F22, A8=DDI-VICTIM-PERPETRATOR
- cmt_analyte_policy + dual_cmt_policy declared
- expected_terminal: REPAIR
- seed_category_id: 18
