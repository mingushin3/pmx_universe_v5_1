# Fingerprint Draft: PROJ_PREG_019

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F28
- seed_category_id: 19
- raw_input_path: data/raw_examples/F28/PROJ_PREG_019/raw_files/dataset_deidentified.csv
- modality_class: MAB
- endpoint_data_type: PK_CONCENTRATION

## Axis States
- A0_state: AIC-PKPD
- A1_state: ID-DEFINED
- A2_state: TIME-ELAPSED-RESOLVABLE
- A3_state: DOSE-DEFINED
- A4_state: REGIMEN-FIXED
- A5_state: BIOANALYTICAL-FINAL
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: SINGLE-ANALYTE
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: N/A

## Detected Policies
- known_policies: ['delivery_anchor_policy=delivery_date', 'elapsed_anchor_policy=delivery_date']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->derive_time_postpartum_anchor->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 19. Golden candidate: NO.
