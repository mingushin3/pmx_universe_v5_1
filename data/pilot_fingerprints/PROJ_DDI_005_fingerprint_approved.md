# Fingerprint Approved: PROJ_DDI_005

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F09
- seed_category_id: 5
- raw_input_path: data/raw_examples/F09/PROJ_DDI_005/raw_files/dataset_deidentified.csv
- modality_class: SMALL_MOLECULE
- endpoint_data_type: PK_CONCENTRATION

## Axis States
- A0_state: AIC-PK
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-DEFINED
- A4_state: REGIMEN-FIXED
- A5_state: BIOANALYTICAL-FINAL
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: DDI-VICTIM-ONLY
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: N/A

## Detected Policies
- known_policies: ['cmt_analyte_policy=ddi_victim_only']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->assign_cmt_ddi_victim_only->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 5. Golden candidate: PREFERRED.
