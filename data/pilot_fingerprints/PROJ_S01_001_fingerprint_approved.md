# Fingerprint Approved: PROJ_S01_001

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F01
- seed_category_id: 1
- raw_input_path: data/raw_examples/F01/PROJ_S01_001/raw_files/dataset_deidentified.csv
- modality_class: MAB
- endpoint_data_type: PK_CONCENTRATION

## Axis States
- A0_state: AIC-PK
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-DEFINED
- A4_state: REGIMEN-FIXED
- A5_state: BIOANALYTICAL-FINAL
- A6_state: COVARIATE-COMPLETE
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: SINGLE-ANALYTE
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: N/A

## Detected Policies
- known_policies: ['time_policy=actual']
- missing_policies: []

## Expected Classification
- expected_terminal_state: AUTO
- expected_q_code: N/A
- expected_action_sequence: parse->assign->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 1. Golden candidate: PREFERRED.
