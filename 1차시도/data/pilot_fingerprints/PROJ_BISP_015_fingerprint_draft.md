# Fingerprint Draft: PROJ_BISP_015

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F25
- seed_category_id: 15
- raw_input_path: data/raw_examples/F25/PROJ_BISP_015/raw_files/dataset_deidentified.csv
- modality_class: BISPECIFIC
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
- analyte_role: PARENT|SOLUBLE_TARGET|DRUG_TARGET_COMPLEX

## Detected Policies
- known_policies: ['cmt_analyte_policy=multi_analyte_role_tagged', 'analyte_role=PARENT|SOLUBLE_TARGET|DRUG_TARGET_COMPLEX']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->assign_cmt_with_analyte_role->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 15. Golden candidate: NO.
