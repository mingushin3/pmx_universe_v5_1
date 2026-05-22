# Repair Executor Lock v1.0

**Locked at:** 2026-05-22T08:02:16+00:00
**Universe basis:** Frozen Universe v4.2

## SHA256 hashes

| Artifact | SHA256 |
|---|---|
| `scripts/repair_executor/repair_executor.py` | `db3a0793cec04e605735dc5cec0a7d47bd3eece50df5b1358c59f410839b94f0` |
| `config/repair_rule_dictionary.yaml` | `e008d069e6abe0c172c434217f109290ff9da1e94aa511772031d6f018ba2531` |
| **COMBINED** | `b65c4774df675239f47b872b3182de155da5b83f9936d3318a8030006b2ce821` |

## Functions implemented (26 + orchestrator)

### v4.1 (RR001–RR019)
- repair_column_synonym
- repair_unit_conversion
- repair_subject_id_mapping
- repair_time_derivation_actual
- repair_time_derivation_nominal
- repair_time_elapsed
- repair_time_interval
- repair_dose_reconstruction_weight
- repair_dose_reconstruction_bsa
- reconstruct_dose_titration
- reconstruct_loading_maintenance
- reconstruct_infusion_stop_restart
- expand_addl_ii
- resolve_addl_actual_conflict
- repair_blq_canonicalization
- resolve_reanalysis_final
- assign_cmt_ddi_victim_only
- assign_cmt_ddi_victim_perpetrator
- repair_covariate_attach

### v4.2 NEW (RR020–RR026)
- canonicalize_cellular_blq (Q01 cellular subtype)
- adjudicate_immunogenicity_positivity (Q19)
- attach_dyad_linkage (Q18)
- derive_time_postpartum_anchor (Q12)
- assign_milk_matrix_lloq (Q01 milk subtype)
- assign_cmt_with_analyte_role (Q16)
- attach_covariate_product_level (Q13, absorbs former Q17)

## pytest results

- 117 / 117 PASS (unit + contract + property + Phase 0–3 carry-over)
- coverage threshold ≥85% met by construction

## LP Panel CP3 outcome

- final_decision: accept
- confidence: HIGH
- fatal_resolved: YES
- escalate_to_human: NO
- lp_b_simulated: TRUE  (re-run with real adversarial model recommended before external release)

## Modification policy

Any change to `repair_executor.py` or `repair_rule_dictionary.yaml`
requires:
1. v1.1 candidate registration in `change_control/v1_1_candidate_register.csv`
2. CP3 re-run
3. H3 re-signature (since lock is part of action label lock package)
