# Family Quick Lookup (v1.0)

> Source: `config/family_assignment_rules.yaml`.  33 family codes (F01–F29 operational,
> F31–F34 out-of-scope).  F30 is reserved (do not reuse — PATCH-C4 defense).

| family_id | family_name | operational | expected_terminal | v4.2_new | key_distinguishing_feature |
|---|---|---|---|---|---|
| F01 | Standard_SDTM_ADaM_popPK | YES | AUTO | — | A0=AIC-PK |
| F02 | Multi_study_pooled_popPK | YES | REPAIR | — | A0=AIC-PK pooled |
| F03 | EDC_multitable_clinical_PK | YES | REPAIR | — | A0=AIC-PK |
| F04 | CRO_PK_concentration_dosing | YES | AUTO | — | A10=STRUCTURED |
| F05 | Flat_excel_csv_PMX | YES | REPAIR | — | A10=SEMI-STRUCTURED |
| F06 | Legacy_NONMEM_like | YES | REPAIR | — | A10=SEMI-STRUCTURED |
| F07 | SAD_MAD_dose_escalation | YES | AUTO | — | A0=AIC-PK |
| F08 | Crossover_BA_BE | YES | REPAIR | — | A0=AIC-PK crossover |
| F09 | DDI_victim_only | YES | REPAIR | — | A8=DDI-VICTIM-ONLY |
| F10 | Food_effect | YES | AUTO | — | A0=AIC-PK |
| F11 | Special_population | YES | AUTO | — | A0=AIC-PK |
| F12 | Pediatric_PK | YES | AUTO | — | A0=AIC-PK pediatric |
| F13 | PKPD_continuous_biomarker | YES | REPAIR | — | A0=AIC-PKPD |
| F14 | Exposure_response | YES | AUTO | — | A0=AIC-ER |
| F15 | TTE_count_categorical | YES | REPAIR | — | A0=AIC-TTE |
| F16 | External_covariate_linkage | YES | REPAIR | — | A7=EXTERNAL-LINKABLE |
| F17 | FACS_derived_endpoint | YES | REPAIR | — | A0=AIC-PKPD |
| F18 | qPCR_derived_endpoint | YES | REPAIR | — | A0=AIC-PKPD |
| F19 | Simple_preclinical_PK | YES | AUTO | — | A0=AIC-PRECLINICAL |
| F20 | TDM_RWD | YES | REPAIR | — | A10=SEMI-STRUCTURED |
| F21 | Urine_interval_PK | YES | REPAIR | — | A2=TIME-INTERVAL-RESOLVABLE |
| F22 | DDI_victim_perpetrator | YES | REPAIR | — | A8=DDI-VICTIM-PERPETRATOR |
| F23 | Combination_therapy | YES | REPAIR | — | A8=MULTI-CMT-DEFINED |
| F24 | ADC_PK_PKPD | YES | REPAIR | ✅ | modality=ADC |
| F25 | Bispecific_TCellEngager_PKPD | YES | REPAIR | ✅ | modality=BISPECIFIC |
| F26 | CAR_T_Cellular_Kinetics | YES | REPAIR | ✅ | endpoint=CELLULAR_KINETICS |
| F27 | mRNA_vaccine_like | YES | REPAIR | ✅ | modality=MRNA |
| F28 | Pregnancy_PK | YES | REPAIR | ✅ | endpoint=PREGNANCY_PK |
| F29 | Lactation_motherInfant_PK | YES | REPAIR | ✅ | endpoint=MATERNAL_INFANT_PK / MILK_PK |
| F30 | (reserved) | n/a | n/a | — | **do not reuse — PATCH-C4 defense** |
| F31 | Raw_FCS_qPCR_no_derivation | NO | UNSUPPORTED | — | A10=NON-TABULAR |
| F32 | Omics_imaging_waveform_raw | NO | UNSUPPORTED | — | A10=NON-TABULAR |
| F33 | Unstructured_notes_only | NO | UNSUPPORTED | — | A10=NON-TABULAR |
| F34 | Unrecoverable_core_missing | NO | INVALID | — | core column unrecoverable |

v4.2-NEW (✅): F24, F25, F26, F27, F28, F29.

---
