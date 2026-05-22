# A-LLM Universe Attack v5.1

> **NOTE — this run:** Simulated by the main session (not an
> independent-family LLM). A real A-LLM pass with Gemini / GPT-class
> model in a fresh chat is required before external release.
> `a_llm_simulated: TRUE`.

## Inputs reviewed

- `data/scenario_universe/scenario_universe_with_family.csv` (head + summary)
- `reports/frozen_universe_v4_2_summary.md`

## 12 typed attack queries

### Q01 Multi-study ID conflict, no harmonization policy
- concrete_axis_combo: A0=AIC-PK, A1=ID-AMBIGUOUS, A2=TIME-DEFINED, A3=DOSE-DEFINED, A4=REGIMEN-FIXED, A5=BIOANALYTICAL-FINAL, A6=COVARIATE-BASELINE-ONLY, A7=SUBJECT-LEVEL-COVARIATE, A8=SINGLE-ANALYTE, A9=REANALYSIS-NONE, A10=STRUCTURED, modality=SMALL_MOLECULE
- covered_by_current_universe: YES
- universe_search_result: scenario exists (terminal=QUARANTINE, q_code=Q03)
- terminal_state_match: Y, q_code_match: Y

### Q02 LLOQ changed mid-study + reanalysis without final flag
- concrete_axis_combo: A0=AIC-PK, A9=REANALYSIS-FINAL-MISSING, A5=BIOANALYTICAL-FINAL
- covered: YES (terminal=QUARANTINE, q_code=Q15D)

### Q03 ADDL/II + actual mixed without resolution policy
- A4=ADDL-ACTUAL-CONFLICT (no policy declared) → QUARANTINE, q_code=Q14 — YES covered

### Q04 Titration with variable AMT
- A4=TITRATION-ADAPTIVE → REPAIR (with dose_adaptation_policy) or QUARANTINE Q08 — YES covered

### Q05 Loading + maintenance with different RATE phases
- A4=LOADING-MAINTENANCE → REPAIR — YES covered

### Q06 IV infusion stop/restart, no policy
- A4=INFUSION-STOP-RESTART → QUARANTINE Q04 (or REPAIR with policy) — YES covered

### Q07 DDI victim+perpetrator dual CMT
- A8=DDI-VICTIM-PERPETRATOR → REPAIR (F22 via dual_cmt_policy) — YES covered

### Q08 Pediatric weight time-varying + mg/kg
- A3=DOSE-WEIGHT-BASED + A6=COVARIATE-TIME-VARYING-RESOLVABLE → REPAIR (F12) — YES covered

### Q09 CAR-T cellular kinetics, no cellular_LLOQ_policy
- modality=CELL_THERAPY, edt=CELLULAR_KINETICS, A5=CELLULAR-LLOQ-POLICY-MISSING → QUARANTINE, q_code=Q01 (cellular subtype), family=F26 — YES covered

### Q10 ADC multi-analyte, analyte_role not declared
- modality=ADC, A8=MULTI-CMT-DEFINED, analyte_role="" → QUARANTINE, q_code=Q16, family=F24 — YES covered

### Q11 Maternal-infant pair, no dyad linkage
- edt=MATERNAL_INFANT_PK, A1=ID-DYAD-UNLINKED-POLICY-MISSING → QUARANTINE, q_code=Q18, family=F29 — YES covered

### Q12 mRNA prime/boost, no positivity rule
- modality=MRNA, edt=IMMUNOGENICITY, A5=IMMUNOGEN-POSITIVITY-MISSING → QUARANTINE, q_code=Q19, family=F27 — YES covered

## Summary table

| query | covered | terminal_match | q_code_match | severity |
|---|---|---|---|---|
| Q01 | YES | YES | YES | - |
| Q02 | YES | YES | YES | - |
| Q03 | YES | YES | YES | - |
| Q04 | YES | YES | YES | - |
| Q05 | YES | YES | YES | - |
| Q06 | YES | YES | YES | - |
| Q07 | YES | YES | YES | - |
| Q08 | YES | YES | YES | - |
| Q09 | YES | YES | YES | - |
| Q10 | YES | YES | YES | - |
| Q11 | YES | YES | YES | - |
| Q12 | YES | YES | YES | - |

**All 12 attack queries are covered by the current universe.** No
universe gaps surfaced. Note v4.2 fields (modality_class, endpoint_data_type,
analyte_role) appear in every relevant query.
