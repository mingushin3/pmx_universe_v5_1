# Fingerprint Draft: PROJ_INF_011

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F01
- seed_category_id: 11
- raw_input_path: data/raw_examples/F01/PROJ_INF_011/raw_files/dataset_deidentified.csv
- modality_class: MAB
- endpoint_data_type: PK_CONCENTRATION

## Axis States
- A0_state: AIC-PK
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-INFUSION-STOP-RESTART
- A4_state: INFUSION-STOP-RESTART
- A5_state: BIOANALYTICAL-FINAL
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: SINGLE-ANALYTE
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: N/A

## Detected Policies
- known_policies: ['infusion_reconstruction_policy=stop_restart_from_events']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->reconstruct_infusion_stop_restart->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 11. Golden candidate: NO.
