# Repair Executor Function Inventory (v1.0)

26 repair functions from `config/repair_rule_dictionary.yaml`
(executor: `scripts/repair_executor/repair_executor.py`, SHA256 `db3a0793…`).

| rule_id | function_name | v4.2_new | input_columns | required_policy | output_columns | fallback_q_code |
|---|---|---|---|---|---|---|
| RR001 | `standardize_column_names` | — | none | none | ID, TIME, AMT, DV, EVID, CMT, MDV | Q15A |
| RR002 | `convert_units` | — | DV | none | DV | Q05 |
| RR003 | `map_subject_id` | — | SUBJID | id_disambiguation_policy | ID | Q03 |
| RR004 | `derive_time_actual` | — | none | none | TIME | Q02 |
| RR005 | `derive_time_nominal` | — | none | time_policy | TIME | Q02 |
| RR006 | `derive_time_elapsed` | — | none | elapsed_anchor_policy | TIME | Q02 |
| RR007 | `derive_time_interval` | — | INTERVAL_START, INTERVAL_END | none | TIME, INTERVAL | Q02 |
| RR008 | `reconstruct_dose_weight` | — | WT | dose_reconstruction_policy | AMT | Q08 |
| RR009 | `reconstruct_dose_bsa` | — | BSA | dose_reconstruction_policy | AMT | Q08 |
| RR010 | `reconstruct_dose_titration` | — | none | dose_adaptation_policy | AMT | Q08 |
| RR011 | `reconstruct_loading_maintenance` | — | none | dose_reconstruction_policy | AMT, RATE | Q08 |
| RR012 | `reconstruct_infusion_stop_restart` | — | none | infusion_reconstruction_policy | AMT, RATE, DUR | Q04 |
| RR013 | `expand_addl_ii` | — | ADDL, II | dose_reconstruction_policy | TIME, AMT | Q08 |
| RR014 | `resolve_addl_actual_conflict` | — | AMT | addl_actual_conflict_policy | AMT | Q14 |
| RR015 | `canonicalize_blq` | — | DV | blq_handling_policy | DV, BLQ_FLAG, MDV | Q01 |
| RR016 | `resolve_reanalysis_final` | — | DV | reanalysis_final_selection_policy | DV | Q15D |
| RR017 | `assign_cmt_ddi_victim_only` | — | none | cmt_analyte_policy | CMT | Q09 |
| RR018 | `assign_cmt_ddi_victim_perpetrator` | — | ANALYTE_NAME | dual_cmt_policy | CMT | Q09 |
| RR019 | `attach_covariate_external` | — | ID | external_linkage_policy | <external_cov_names> | Q07 |
| RR020 | `canonicalize_cellular_blq` | ✅ | ID, TIME, DV, MDV, CMT | cellular_LLOQ_derivation_policy | DV, MDV, CELLULAR_BLQ_FLAG | Q01 |
| RR021 | `adjudicate_immunogenicity_positivity` | ✅ | DV, SCREENING_RESULT | positivity_adjudication_rule | DV, ADA_POSITIVE_FLAG | Q19 |
| RR022 | `attach_dyad_linkage` | ✅ | SUBJID | dyad_linkage_policy | MOTHER_SUBJID, INFANT_SUBJID, DYAD_ID | Q18 |
| RR023 | `derive_time_postpartum_anchor` | ✅ | none | delivery_anchor_policy | TIME, POSTPARTUM_DAY | Q12 |
| RR024 | `assign_milk_matrix_lloq` | ✅ | DV, MATRIX | milk_matrix_lloq_policy | DV, MATRIX_BLQ_FLAG | Q01 |
| RR025 | `assign_cmt_with_analyte_role` | ✅ | ANALYTE_NAME | analyte_role_declaration | CMT, ANALYTE_ROLE | Q16 |
| RR026 | `attach_covariate_product_level` | ✅ | LOT_ID | product_level_covariate_linkage_policy | <product_cov_names> | Q13 |

v4.2-new (✅): RR020 – RR026.

---
