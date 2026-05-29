# Fingerprint Draft: PROJ_LM_010

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F01
- seed_category_id: 10
- raw_input_path: data/raw_examples/F01/PROJ_LM_010/raw_files/dataset_deidentified.csv
- modality_class: MAB
- endpoint_data_type: PK_CONCENTRATION

## Axis States
- A0_state: AIC-PK
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-LOADING-MAINTENANCE
- A4_state: LOADING-MAINTENANCE
- A5_state: BIOANALYTICAL-FINAL
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: SINGLE-ANALYTE
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: N/A

## Detected Policies
- known_policies: ['dose_reconstruction_policy=loading_maintenance']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->reconstruct_loading_maintenance->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 10. Golden candidate: NO.
