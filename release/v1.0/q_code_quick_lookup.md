# Q-code Quick Lookup (v1.0)

> Source: `config/quarantine_reason_codes.yaml`.  21 active Q-codes.  Q17 is REJECTED
> in v5.1 (HR2).

| code | short_name | definition | how_to_clear | v4.2_new |
|---|---|---|---|---|
| Q01 | BLQ_OR_LLOQ_POLICY_MISSING | BLQ handling rule or LLOQ value absent for the observation domain | blq_handling_policy + LLOQ (or cellular_LLOQ / milk_matrix_lloq) | — |
| Q02 | TIME_ANCHOR_AMBIGUOUS | Time or dose anchor for elapsed/interval/dose timing is ambiguous | elapsed_anchor_policy or dose_time anchor | — |
| Q03 | ID_AMBIGUOUS | Subject identifier ambiguous or duplicated; no resolution rule | id_disambiguation_policy | — |
| Q04 | INFUSION_RECONSTRUCTION_MISSING | Infusion stop/restart events present but no reconstruction policy | infusion_reconstruction_policy | — |
| Q05 | OBSERVATION_UNIT_AMBIGUOUS | Observation unit ambiguous (conc / copy number) | observation_unit declaration | — |
| Q06 | COVARIATE_OR_DEVIATION_POLICY_MISSING | Covariate imputation or protocol deviation policy absent | covariate_policy or protocol_deviation_policy | — |
| Q07 | EXTERNAL_POLICY_MISSING | External linkage policy absent | external_linkage_policy | — |
| Q08 | REGIMEN_POLICY_MISSING | Regimen incompletely declared; no fallback | dose_reconstruction_policy / transition_point | — |
| Q09 | CMT_POLICY_MISSING | Multi-analyte data but CMT assignment policy absent | cmt_analyte_policy | — |
| Q10 | OCCASION_POLICY_MISSING | Occasion undeclared for IOV/within-subject random effects | occasion_policy | — |
| Q11 | AIC_OR_ENDPOINT_TYPE_MISSING | AIC missing OR endpoint_data_type absent | Analysis Intent Contract + endpoint_data_type | — |
| Q12 | ANCHOR_MISSING | Required anchor (e.g. delivery) missing | delivery_anchor_policy or elapsed_anchor_policy | ✅ |
| Q13 | EXTERNAL_LINKAGE_KEY_MISSING | External / product-level linkage key absent | lot_subject_linkage_key or external join key | — |
| Q14 | ADDL_ACTUAL_CONFLICT_POLICY_MISSING | ADDL-expanded and actual dosing records conflict; no policy | addl_actual_conflict_policy | — |
| Q15A | DATA_PACKAGE_INCOMPLETE_UPSTREAM_ADJUDICATION | Upstream adjudication decision not submitted | Adjudicated values / attribute table | — |
| Q15B | LEGACY_FLAG_UNDOCUMENTED | Legacy data flag / field definition absent | Legacy flag dictionary | — |
| Q15C | REALWORLD_ADHERENCE_HISTORY_UNRESOLVED | RWD/TDM administration history unclear | SAP-level adherence imputation policy | ✅ |
| Q15D | ASSAY_REANALYSIS_FINAL_ADJUDICATION_MISSING | No rule for choosing among reanalysis results | reanalysis_final_selection_policy | ✅ |
| Q16 | ANALYTE_ROLE_POLICY_MISSING | Modality-specific analyte role missing (ADC / CAR-T / bispecific / gene-therapy) | analyte_role declaration in AIC per analyte | ✅ |
| Q17 | (REJECTED) | retired in v5.1 (HR2) | n/a | — |
| Q18 | MATERNAL_INFANT_DYAD_LINKAGE_MISSING | Mother + infant data but no dyad_linkage_key | dyad_linkage_key + dyad_linkage_policy | ✅ |
| Q19 | IMMUNOGENICITY_POSITIVITY_RULE_MISSING | Immunogenicity data but positivity adjudication rule absent | positivity_adjudication_rule | ✅ |

v4.2-NEW (✅): Q12, Q15C, Q15D, Q16, Q18, Q19.

---
