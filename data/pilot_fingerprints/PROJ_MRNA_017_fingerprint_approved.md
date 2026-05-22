# Fingerprint Approved: PROJ_MRNA_017

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F27
- seed_category_id: 17
- raw_input_path: data/raw_examples/F27/PROJ_MRNA_017/raw_files/dataset_deidentified.csv
- modality_class: MRNA
- endpoint_data_type: IMMUNOGENICITY

## Axis States
- A0_state: AIC-IMMUNOGEN
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-LOADING-MAINTENANCE
- A4_state: LOADING-MAINTENANCE
- A5_state: IMMUNOGEN-POSITIVITY-DEFINED
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: SUBJECT-LEVEL-COVARIATE
- A8_state: SINGLE-ANALYTE
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: ADA

## Detected Policies
- known_policies: ['positivity_adjudication_rule=screening_plus_confirmation', 'dose_reconstruction_policy=loading_maintenance']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->adjudicate_immunogenicity_positivity->reconstruct_loading_maintenance->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 17. Golden candidate: NO.
