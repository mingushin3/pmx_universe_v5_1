# Action Sequence + AIC Template Lock Decision (v1.0 candidate)

**Reviewer role:** LP-A (PMX Grandmaster) — single R-LLM review (LP Panel CP for action_sequence was compressed out per P5-04).
**Inputs:** `reports/boundary_case_semantic_review.md`, `reports/boundary_case_qcode_validation.md`.
**Date:** 2026-05-22

## Checklist

- [x] **All 60 boundary cases semantic-review PASS** — `ALL_CASES_PASS_SEMANTIC_REVIEW` declared in `reports/boundary_case_semantic_review.md`.
- [x] **All 9 BC automated checks PASS** — BC1..BC9 PASS in `reports/boundary_case_qcode_validation.md` (failed_checks=0).
- [x] **action_sequence_standard contains v4.2 NEW functions** — verified in `config/action_sequence_standard.yaml`:
    - `canonicalize_cellular_blq`
    - `adjudicate_immunogenicity_positivity`
    - `attach_dyad_linkage`
    - `derive_time_postpartum_anchor`
    - `assign_milk_matrix_lloq`
    - `assign_cmt_with_analyte_role`
    - `attach_covariate_product_level`
- [x] **AIC template covers all v4.2 conditional fields** — `analysis_intent_contract_template.yaml` declares the following fields with explicit `required_when`:
    - `cellular_LLOQ_derivation_policy` (CELLULAR_KINETICS → Q01)
    - `positivity_adjudication_rule` (IMMUNOGENICITY → Q19)
    - `dyad_linkage_policy` (MATERNAL_INFANT_PK → Q18)
    - `delivery_anchor_policy` (MATERNAL_INFANT_PK / pregnancy / lactation → Q12)
    - `milk_matrix_lloq_policy` (MILK_PK → Q01)
    - `product_level_covariate_linkage_policy` (PRODUCT-LEVEL-COVARIATE → Q13; absorbs former Q17)
    - `analyte_role` (multi-analyte ADC/BISPECIFIC/CELL/GENE → Q16)

## Decision

**LOCKED v1.0 (action_sequence + AIC).**

SHA256 hashes for the three artifacts below to be computed by P26 and recorded in
`release/v1.0/action_sequence_v1_0.sha256`:

- `config/action_sequence_standard.yaml` — `<SHA256>`
- `config/action_function_library.yaml` — `<SHA256>`
- `config/analysis_intent_contract_template.yaml` — `<SHA256>`
- combined — `<SHA256>`

> Action sequence vocabulary and AIC template are now frozen for v1.0.
> Any addition or removal of a function or AIC field requires a `change_control/`
> RFC and H3 re-signature.
