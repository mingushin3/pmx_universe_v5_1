# Fingerprint Approved: PROJ_ADC_014

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F24
- seed_category_id: 14
- raw_input_path: data/raw_examples/F24/PROJ_ADC_014/raw_files/dataset_deidentified.csv
- modality_class: ADC
- endpoint_data_type: PK_CONCENTRATION

## Axis States
- A0_state: AIC-PKPD
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-DEFINED
- A4_state: REGIMEN-FIXED
- A5_state: BIOANALYTICAL-FINAL
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: MULTI-CMT-DEFINED
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: TOTAL_ANTIBODY|CONJUGATED_ADC|UNCONJUGATED_PAYLOAD

## Detected Policies
- known_policies: ['cmt_analyte_policy=multi_analyte_role_tagged', 'analyte_role=TOTAL_ANTIBODY|CONJUGATED_ADC|UNCONJUGATED_PAYLOAD']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->assign_cmt_with_analyte_role->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 14. Golden candidate: YES.
