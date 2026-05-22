# Frozen Universe v4.2 — Structured Summary (v5.1 working basis)

This document is the dense, structured reference for the Frozen Universe v4.2,
organized by axes A0–A10, Q-codes, families, decision nodes, AIC fields,
coverage targets, scope constraints, and v4.1 → v4.2 patches C16–C24.
All downstream artifacts in v5.1 must conform to this summary.

---

## A. Axes A0–A10

### A0 — Analysis Intent Contract (AIC)
**Definition:** The contract declaring model family, analysis objective, modality,
endpoint data type, and all required policies before data routing.

**Auxiliary fields (v4.2):**

| Field | Allowed values | Required when | Missing → q_code |
|---|---|---|---|
| `modality_class` | SMALL_MOLECULE, PEPTIDE, MAB, ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY, MRNA, VACCINE, OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL, OTHER_CUSTOM (12 values) | always (auxiliary, recommended) | informational |
| `endpoint_data_type` | PK_CONCENTRATION, EXPOSURE_METRIC, CONTINUOUS_PD, CATEGORICAL_PD, COUNT_PD, TTE_EVENT, **CELLULAR_KINETICS**, **IMMUNOGENICITY**, **MILK_PK**, **MATERNAL_INFANT_PK** (10 values) | A0 ∈ {AIC-PKPD, AIC-ER, AIC-TTE, AIC-BIOMARKER, AIC-CELL_THERAPY, AIC-IMMUNOGEN, AIC-LACTATION} | Q11 |

**States:**

| state_code | terminal_hint | q_code |
|---|---|---|
| AIC-MISSING | QUARANTINE | Q11 |
| AIC-PK | AUTO | — |
| AIC-PKPD | AUTO | — |
| AIC-ER | AUTO | — |
| AIC-TTE | AUTO | — |
| AIC-BIOMARKER | AUTO | — |
| AIC-CELL_THERAPY (v4.2) | AUTO | — |
| AIC-IMMUNOGEN (v4.2) | AUTO | — |
| AIC-LACTATION (v4.2) | AUTO | — |
| AIC-PRECLINICAL | AUTO | — |
| AIC-UNRECOVERABLE | INVALID | — |

> **NOTE:** When `endpoint_data_type` is required by the AIC type but absent,
> the terminal_hint flips to QUARANTINE (Q11). When `endpoint_data_type` ∈
> {CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK},
> additional policies (HR7/HR8/HR9, HR10) gate the AUTO outcome.

### A1 — Subject Identifier
**Definition:** Subject identifier structure and uniqueness.
**Maternal-infant note (v4.2):** mother and infant may have separate IDs
if `dyad_linkage_key` is declared; otherwise → INVALID. If dyad linkage
policy is absent in the AIC → Q18.

| state_code | terminal_hint | q_code |
|---|---|---|
| ID-DEFINED | AUTO | — |
| ID-DUPLICATE-RESOLVABLE | REPAIR | — |
| ID-AMBIGUOUS | QUARANTINE | Q03 |
| ID-DYAD-LINKABLE (v4.2) | REPAIR | — |
| ID-DYAD-UNLINKED-POLICY-MISSING (v4.2) | QUARANTINE | Q18 |
| ID-UNRECOVERABLE | INVALID | — |

### A2 — Time
**Definition:** Time axis structure (actual/nominal/elapsed/interval).

| state_code | terminal_hint | q_code |
|---|---|---|
| TIME-DEFINED | AUTO | — |
| TIME-ACTUAL-VS-NOMINAL-RESOLVABLE | REPAIR | — |
| TIME-INTERVAL-RESOLVABLE | REPAIR | — |
| TIME-ELAPSED-RESOLVABLE | REPAIR | — |
| TIME-ANCHOR-AMBIGUOUS | QUARANTINE | Q02 |
| TIME-UNRECOVERABLE | INVALID | — |

### A3 — Dose
**Definition:** Dose record completeness and reconstruction feasibility.
**v4.2 note (C20):** delivery / postpartum date treated as an ELAPSED anchor
(`elapsed_anchor_policy = delivery_date | postpartum_day`).

| state_code | terminal_hint | q_code |
|---|---|---|
| DOSE-DEFINED | AUTO | — |
| DOSE-WEIGHT-BASED | REPAIR | — |
| DOSE-BSA-BASED | REPAIR | — |
| DOSE-TITRATION | REPAIR | — |
| DOSE-LOADING-MAINTENANCE | REPAIR | — |
| DOSE-INFUSION-STOP-RESTART | REPAIR | — |
| DOSE-ADDL-ACTUAL-CONFLICT | QUARANTINE/REPAIR | Q14 / (REPAIR if policy) |
| DOSE-AMBIGUOUS | QUARANTINE | Q02 |
| DOSE-UNRECOVERABLE | INVALID | — |

### A4 — Regimen
**Definition:** Dosing regimen reconstruction.

| state_code | terminal_hint | q_code |
|---|---|---|
| REGIMEN-FIXED | AUTO | — |
| REGIMEN-EXPANDABLE-ADDL | REPAIR | — |
| TITRATION-ADAPTIVE | REPAIR / Q08 | (Q08 if policy missing) |
| LOADING-MAINTENANCE | REPAIR / Q08 | (Q08 if transition point undefined) |
| INFUSION-STOP-RESTART | REPAIR / Q04 | (Q04 if reconstruction policy absent) |
| ADDL-ACTUAL-CONFLICT | REPAIR / Q14 | (Q14 if policy absent) |
| MISSING-NO-POLICY | QUARANTINE | Q08 |
| UNRECOVERABLE | INVALID | — |

### A5 — Observation (Bioanalytical)
**Definition:** Observation/DV value source and adjudication.

| state_code | terminal_hint | q_code |
|---|---|---|
| BIOANALYTICAL-FINAL | AUTO | — |
| BIOANALYTICAL-FINAL-FLAG-MISSING | QUARANTINE | **Q15A** (PATCH m-4) |
| BLQ-DEFINED-POLICY | REPAIR | — |
| BLQ-NO-POLICY | QUARANTINE | Q01 |
| LLOQ-MISSING | QUARANTINE | Q01 |
| CELLULAR-BLQ-DEFINED (v4.2) | REPAIR | — |
| CELLULAR-LLOQ-POLICY-MISSING (v4.2) | QUARANTINE | Q01 (cellular subtype) |
| IMMUNOGEN-POSITIVITY-DEFINED (v4.2) | REPAIR | — |
| IMMUNOGEN-POSITIVITY-MISSING (v4.2) | QUARANTINE | Q19 |
| ABSENT | INVALID | — |

### A6 — Covariate
**Definition:** Baseline and time-varying covariate availability.

| state_code | terminal_hint | q_code |
|---|---|---|
| COVARIATE-COMPLETE | AUTO | — |
| COVARIATE-BASELINE-ONLY | AUTO | — |
| COVARIATE-TIME-VARYING-RESOLVABLE | REPAIR | — |
| COVARIATE-PARTIAL-POLICY | REPAIR | — |
| COVARIATE-IMPUTATION-POLICY-MISSING | QUARANTINE | Q06 |
| COVARIATE-ABSENT | INVALID | — |

### A7 — External / Product Linkage
**Definition:** External covariate or product-level attribute linkage.
**v4.2 NEW (C19):** PRODUCT-LEVEL-COVARIATE state for CAR-T / cell-therapy
lot or batch attributes (lot → subject reverse-key join).

| state_code | terminal_hint | q_code |
|---|---|---|
| SUBJECT-LEVEL-COVARIATE | AUTO | — |
| BASELINE-CLEAN | AUTO | — |
| TIME-VARYING | REPAIR | — |
| EXTERNAL-LINKABLE | REPAIR | — |
| **PRODUCT-LEVEL-COVARIATE (v4.2)** | REPAIR | Q13 if linkage missing; Q15A if attribute absent from data package |
| KEY-MISSING | QUARANTINE | Q13 |
| POLICY-MISSING | QUARANTINE | Q07 |
| UNRECOVERABLE | INVALID | — |

### A8 — Compartment / Analyte
**Definition:** Compartment (CMT) assignment for analytes.

**Auxiliary fields (v4.2):**

| Field | Allowed values | Required when | Missing → q_code |
|---|---|---|---|
| `analyte_role` | PARENT, TOTAL_ANTIBODY, CONJUGATED_ADC, UNCONJUGATED_PAYLOAD, ACTIVE_METABOLITE, SOLUBLE_TARGET, DRUG_TARGET_COMPLEX, ADA, NAB, VECTOR_COPY, TRANSGENE_EXPRESSION, CAR_POSITIVE_CELL, OTHER_CUSTOM (13 values) | A8 ∈ {MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED} AND modality_class ∈ {ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY} | **Q16** |

| state_code | terminal_hint | q_code |
|---|---|---|
| SINGLE-ANALYTE | AUTO | — |
| MULTI-CMT-DEFINED | REPAIR / Q16 | (Q16 if analyte_role missing) |
| DDI-VICTIM-ONLY | REPAIR | — |
| DDI-VICTIM-PERPETRATOR | REPAIR / Q09 / Q16 | (Q09 if dual CMT policy missing; Q16 if analyte_role missing) |
| METABOLITE-DEFINED | REPAIR / Q16 | (Q16 if analyte_role missing) |
| CMT-POLICY-MISSING | QUARANTINE | Q09 |

### A9 — Reanalysis
**Definition:** Repeat / reanalysis result handling.

| state_code | terminal_hint | q_code |
|---|---|---|
| REANALYSIS-NONE | AUTO | — |
| REANALYSIS-FINAL-RESOLVABLE | REPAIR | — |
| REANALYSIS-FINAL-MISSING | QUARANTINE | **Q15D** |
| PROTOCOL-DEVIATION-RESOLVABLE | REPAIR | — |
| PROTOCOL-DEVIATION-NO-POLICY | QUARANTINE | Q06 |
| IRRECONCILABLE | INVALID | — |

### A10 — Data Source Structure
**Definition:** Source file/parser structure.

| state_code | terminal_hint | q_code |
|---|---|---|
| STRUCTURED | AUTO | — |
| SEMI-STRUCTURED | REPAIR / Q15A | (Q15A if `source_parser_subtype=unknown`) |
| NON-TABULAR | UNSUPPORTED | — |
| CORRUPTED | INVALID | — |
| SEMI-STRUCTURED-LEGACY-FLAG | QUARANTINE | **Q15B** |
| RWD-ADHERENCE-UNRESOLVED | QUARANTINE | **Q15C** |

---

## B. Q-Codes (Q01–Q19, Q17 REJECTED) — 21 active + 1 rejected

| Code | Short name | Linked axis | Linked node |
|---|---|---|---|
| Q01 | BLQ_OR_LLOQ_POLICY_MISSING | A5 | N5 |
| Q02 | TIME_ANCHOR_AMBIGUOUS | A2, A3 | N2 |
| Q03 | ID_AMBIGUOUS | A1 | N1 |
| Q04 | INFUSION_RECONSTRUCTION_MISSING | A3, A4 | N3 |
| Q05 | OBSERVATION_UNIT_AMBIGUOUS | A5 | N4 |
| Q06 | COVARIATE_OR_DEVIATION_POLICY_MISSING | A6, A9 | N7 |
| Q07 | EXTERNAL_POLICY_MISSING | A7 | — |
| Q08 | REGIMEN_POLICY_MISSING | A4 | N3 |
| Q09 | CMT_POLICY_MISSING | A8 | N4 |
| Q10 | OCCASION_POLICY_MISSING | A4 | N3 |
| Q11 | AIC_OR_ENDPOINT_TYPE_MISSING | A0 | N0 |
| Q12 | ANCHOR_MISSING (e.g. delivery_anchor) | A3 | N2 |
| Q13 | EXTERNAL_LINKAGE_KEY_MISSING | A7 | — |
| Q14 | ADDL_ACTUAL_CONFLICT_POLICY_MISSING | A4 | N3 |
| **Q15A** | DATA_PACKAGE_INCOMPLETE_UPSTREAM_ADJUDICATION | A5, A7, A10 | — |
| **Q15B** | LEGACY_FLAG_UNDOCUMENTED | A10 | — |
| **Q15C** | REALWORLD_ADHERENCE_HISTORY_UNRESOLVED | A10 | — |
| **Q15D** | ASSAY_REANALYSIS_FINAL_ADJUDICATION_MISSING | A9 | — |
| **Q16 (v4.2)** | ANALYTE_ROLE_POLICY_MISSING | A8 | N4 |
| **Q17** | **REJECTED — absorbed into Q13** | — | — |
| **Q18 (v4.2)** | MATERNAL_INFANT_DYAD_LINKAGE_MISSING | A1 | N1 |
| **Q19 (v4.2)** | IMMUNOGENICITY_POSITIVITY_RULE_MISSING | A5 | N5 |

> **HR1:** Q15 standalone forbidden. Always use Q15A/B/C/D.
> **HR3:** Q17 forbidden. Any reference to Q13 must include log note "absorbed Q17".

### v4.2 NEW codes — full definitions

**Q16 — ANALYTE_ROLE_POLICY_MISSING**
- definition: "Modality-specific analyte role policy missing for ADC / CAR-T / bispecific / gene-therapy multi-analyte data."
- detection_rule: `A8 ∈ {MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED} AND modality_class ∈ {ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY} AND analyte_role NOT declared`
- difference_from_Q09: Q09 = no CMT number; Q16 = CMT exists but role missing.

**Q18 — MATERNAL_INFANT_DYAD_LINKAGE_MISSING**
- detection_rule: `endpoint_data_type = MATERNAL_INFANT_PK AND dyad_linkage_key absent OR dyad_linkage_policy absent`.
- post-clear: link mother and infant IDs via declared key; re-run N1.

**Q19 — IMMUNOGENICITY_POSITIVITY_RULE_MISSING**
- detection_rule: `endpoint_data_type = IMMUNOGENICITY AND positivity_adjudication_rule absent`.
- post-clear: adjudication rule supplied; A5 → IMMUNOGEN-POSITIVITY-DEFINED.

---

## C. Families (F01–F29 operational + F31–F34 out-of-scope)

> **NOTE:** F30 is intentionally unassigned — reserved as a buffer between
> operational and out-of-scope ranges. Do NOT create an F30 entry.

### Operational (F01–F29)

| Fxx | Name | Expected terminal | v4.2 new? |
|---|---|---|---|
| F01 | Standard SDTM/ADaM popPK | AUTO | no |
| F02 | Multi-study pooled popPK | REPAIR | no |
| F03 | EDC multi-table clinical PK | REPAIR | no |
| F04 | CRO PK concentration + dosing | AUTO | no |
| F05 | Flat Excel/CSV PMX | REPAIR | no |
| F06 | Legacy NONMEM-like | REPAIR | no |
| F07 | SAD/MAD dose-escalation | AUTO | no |
| F08 | Crossover/BA-BE | REPAIR | no |
| F09 | DDI victim-only | REPAIR | no |
| F10 | Food-effect | AUTO | no |
| F11 | Special population (renal/hepatic) | AUTO | no |
| F12 | Pediatric PK | AUTO | no |
| F13 | PK/PD continuous biomarker | REPAIR | no |
| F14 | Exposure-response | AUTO | no |
| F15 | TTE / count / categorical | REPAIR | no |
| F16 | External covariate linkage | REPAIR | no |
| F17 | FACS-derived endpoint | REPAIR | no |
| F18 | qPCR-derived endpoint | REPAIR | no |
| F19 | Simple preclinical PK | AUTO | no |
| F20 | TDM / RWD | REPAIR | no |
| F21 | Urine / interval collection PK | REPAIR | no |
| F22 | DDI victim+perpetrator | REPAIR | no |
| F23 | Combination / concomitant therapy | REPAIR | no |
| **F24** | **ADC PK/PKPD** | REPAIR | **yes** |
| **F25** | **Bispecific / T-cell engager PKPD** | REPAIR | **yes** |
| **F26** | **CAR-T / cell-therapy cellular kinetics** | REPAIR | **yes** |
| **F27** | **mRNA / vaccine-like** | REPAIR | **yes** |
| **F28** | **Pregnancy PK** | REPAIR | **yes** |
| **F29** | **Lactation / mother-infant PK** | REPAIR | **yes** |

### Out-of-scope (F31–F34, `operational_scope = false`)

| Fxx | Name | Terminal | Renumbered from |
|---|---|---|---|
| F31 | raw FCS / qPCR without derivation | UNSUPPORTED | old F24 |
| F32 | omics / imaging / waveform raw | UNSUPPORTED | old F25 |
| F33 | unstructured notes only | UNSUPPORTED | old F26 |
| F34 | unrecoverable core missing | INVALID | old F27 |

---

## D. Decision Nodes N0–N8

| Node | Question | Default | Forced? | v5.1 new? |
|---|---|---|---|---|
| N0 | Is AIC valid AND endpoint_data_type declared as required? | Y | YES | — |
| N1 | Is the subject identifier resolvable (including maternal-infant dyad linkage path)? | Y | YES | — |
| N2 | Is time axis resolvable (including delivery/postpartum elapsed anchor)? | Y | YES | — |
| N3 | Is dose resolvable (regimen + infusion + ADDL)? | Y | YES | — |
| N4 | Is observation/compartment resolvable (including analyte_role)? | Y | YES | — |
| N5 | Is BLQ/LLOQ handling resolvable (concentration / cellular / immunogenicity)? | Y | YES | — |
| N6 | Is covariate handling resolvable? | Y | optional | — |
| N7 | Is reanalysis / protocol deviation handled? | Y | optional | — |
| **N8** | **Are ALL required_policies for the proposed action_sequence declared in AIC?** | **Y** | **YES** | **YES (v5.1 NEW)** |

> **N8 detail (HR13):**
> - `detection_rule`: "proposed action_sequence가 필요로 하는 모든 required_policy가 AIC에 선언되어 있으면 Y; 하나라도 부재하면 N"
> - `cost_if_excluded = ∞` (ILP must always include N8)
> - When N8 = N → `terminal_state = QUARANTINE` with `q_code` set by the missing policy.

---

## E. AIC Field Schema (Auxiliary structure for A0)

### Core fields
`model_family`, `analysis_objective`, `modality_class` (11 + OTHER_CUSTOM),
`endpoint_data_type` (10), `analyte_role` (12 + OTHER_CUSTOM, conditional).

### Policy fields
`blq_handling_policy`, `cellular_LLOQ_derivation_policy` (v4.2),
`positivity_adjudication_rule` (v4.2), `time_policy`,
`elapsed_anchor_policy` (v4.2: includes `delivery_date`, `postpartum_day`),
`occasion_policy`, `dose_reconstruction_policy`, `addl_actual_conflict_policy`,
`infusion_reconstruction_policy`, `covariate_policy`, `cmt_analyte_policy`,
`external_linkage_policy`, `product_level_covariate_linkage_policy` (v4.2),
`bioanalytical_final_selection_policy`, `reanalysis_final_selection_policy`,
`dyad_linkage_policy` (v4.2), `delivery_anchor_policy` (v4.2),
`milk_matrix_lloq_policy` (v4.2).

### Output requirements
`nonmem_required_columns`, `exclusion_policy`,
`audit_trail_requirement ∈ {full, minimal}`.

---

## F. Coverage Targets

| Target | Threshold |
|---|---|
| capture_coverage | ≥ 99% |
| review_inclusive (AUTO + REPAIR + QUARANTINE) | ≥ 95% |
| operational (AUTO + REPAIR) | ≥ 75% |
| auto_only (AUTO) | ≥ 35% |
| unsupported + invalid | ≤ 5% |

---

## G. 8 Scope Constraints (Frozen Universe v4.2)

1. **C1.** Decision system covers PMX → NONMEM-ready dataset transformation only.
   Model fitting, simulation, and clinical decision are out of scope.

2. **C2.** Every QUARANTINE row must carry a q_code from {Q01..Q14, Q15A–D, Q16, Q18, Q19}.

3. **C3.** Q15 standalone is forbidden. Q17 is forbidden (absorbed into Q13).

4. **C4.** AUTO terminal_state may not invoke any repair function.

5. **C5.** REPAIR terminal_state requires (a) declared policy in AIC and
   (b) a single deterministic algorithm; both must be present in
   `repair_rule_dictionary.yaml`.

6. **C6.** AIC of type {AIC-PKPD, AIC-ER, AIC-TTE, AIC-BIOMARKER,
   AIC-CELL_THERAPY, AIC-IMMUNOGEN, AIC-LACTATION} must declare
   `endpoint_data_type`; otherwise Q11.

7. **C7 (v4.2 NEW).** When `endpoint_data_type = CELLULAR_KINETICS`,
   `cellular_LLOQ_derivation_policy` must be declared and applied via
   the Poisson-LLOQ algorithm in `canonicalize_cellular_blq`. Concentration
   BLQ rules are not applicable to cell-count data.

8. **C8 (v4.2 NEW).** When `endpoint_data_type = MATERNAL_INFANT_PK`,
   both `dyad_linkage_key` and `delivery_anchor_policy` must be declared;
   absence routes to Q18 (linkage) or Q12 (anchor) respectively, never
   to INVALID.

---

## H. v4.1 → v4.2 Patches C16–C24

| Patch | Title | Affected component | Effect |
|---|---|---|---|
| C16 | modality_class auxiliary on A0 | axis_dictionary | Adds 11-value (+OTHER) modality taxonomy under A0 |
| C17 | endpoint_data_type expansion | axis_dictionary | Adds CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK |
| C18 | analyte_role auxiliary on A8 | axis_dictionary | Adds 12 (+OTHER) analyte-role taxonomy under A8 |
| C19 | A7 PRODUCT-LEVEL-COVARIATE | axis_dictionary | New A7 state for CAR-T / cell-therapy lot attributes |
| C20 | A3 delivery/postpartum anchor | axis_dictionary | Treats delivery date as ELAPSED anchor |
| C21 | N1 dyad linkage path | candidate_node_dictionary | N1 supports separate mother/infant IDs if dyad key present |
| C22 | Q16, Q18, Q19 added; Q17 rejected | quarantine_reason_codes | New v4.2 codes; Q17 absorbed into Q13 |
| C23 | Cellular kinetics Poisson LLOQ | repair_rule_dictionary | New `canonicalize_cellular_blq` function (Poisson-derived) |
| C24 | Operational families F24–F29; F31–F34 renumber | family_assignment_rules | 6 new operational families; old F24–F27 → F31–F34 (F30 reserved buffer) |

---

*— End of frozen_universe_v4_2_summary.md —*
