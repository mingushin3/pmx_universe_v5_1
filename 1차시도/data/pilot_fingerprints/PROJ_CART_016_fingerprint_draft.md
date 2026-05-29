# Fingerprint Draft: PROJ_CART_016

> **NOTE — this run:** synthetic dataset, no PHI.
> Reviewer simulated (placeholder signature in approval log).

## Inventory
- family_candidate: F26
- seed_category_id: 16
- raw_input_path: data/raw_examples/F26/PROJ_CART_016/raw_files/dataset_deidentified.csv
- modality_class: CELL_THERAPY
- endpoint_data_type: CELLULAR_KINETICS

## Axis States
- A0_state: AIC-CELL_THERAPY
- A1_state: ID-DEFINED
- A2_state: TIME-DEFINED
- A3_state: DOSE-DEFINED
- A4_state: REGIMEN-FIXED
- A5_state: CELLULAR-BLQ-DEFINED
- A6_state: COVARIATE-BASELINE-ONLY
- A7_state: PRODUCT-LEVEL-COVARIATE
- A8_state: MULTI-CMT-DEFINED
- A9_state: REANALYSIS-NONE
- A10_state: STRUCTURED

## v4.2 Auxiliary
- analyte_role: VECTOR_COPY|CAR_POSITIVE_CELL

## Detected Policies
- known_policies: ['cellular_LLOQ_derivation_policy=poisson_derived', 'product_level_covariate_linkage_policy=lot_to_subject_via_manufacturing_record', 'lot_subject_linkage_key=LOT_ID']
- missing_policies: []

## Expected Classification
- expected_terminal_state: REPAIR
- expected_q_code: N/A
- expected_action_sequence: parse->canonicalize_cellular_blq->attach_covariate_product_level->assign_cmt_with_analyte_role->export
- fingerprint_confidence: HIGH
- unknown_field_count: 0

## Notes
Synthetic dataset for seed category 16. Golden candidate: YES.
