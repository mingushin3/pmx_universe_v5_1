# Pilot Sampling Plan v5.1

**Mandatory:** all 20 edge-case seed categories must be covered before universe freeze (Phase 5).
Source: `reports/pilot_edge_case_seed_pack_v5_1.md`, `config/family_assignment_rules.yaml`.

> **NOTE — this run:** Real deidentified data is not available in this session.
> The plan below documents the *intended* sampling strategy. Phase 3 in this
> session uses **synthetic** datasets (one per seed category) as a stand-in
> so the downstream gates can run. When real data becomes available, swap the
> synthetic CSVs in `data/raw_examples/` for deidentified real ones and re-run
> P31–P33 + H2.

## Overall sampling table

| category_id | family_id | min_n | golden_candidate | privacy | source_type (this run) |
|---|---|---|---|---|---|
| 1 | F01 | 1 | PREFERRED | LOW | synthetic SDTM-like |
| 2 | F02 | 1 | NO | LOW | synthetic pooled |
| 3 | F07 | 1 | NO | LOW | synthetic SAD |
| 4 | F08 | 1 | NO | LOW | synthetic crossover |
| 5 | F09 | 1 | PREFERRED | LOW | synthetic DDI victim |
| 6 | F12 | 1 | YES | LOW | synthetic pediatric |
| 7 | F20 | 1 | NO | LOW | synthetic TDM |
| 8 | F19 | 1 | NO | LOW | synthetic preclinical |
| 9 | F07 | 1 | NO | LOW | synthetic titration |
| 10 | F01 | 1 | NO | LOW | synthetic loading-maint |
| 11 | F01 | 1 | NO | LOW | synthetic infusion |
| 12 | F01 | 1 | NO | LOW | synthetic ADDL conflict |
| 13 | F01 | 1 | NO | LOW | synthetic reanalysis |
| 14 | F24 | 1 | YES | LOW | synthetic ADC multi-analyte |
| 15 | F25 | 1 | NO | LOW | synthetic bispecific |
| 16 | F26 | 1 | YES | LOW | synthetic CAR-T cellular |
| 17 | F27 | 1 | NO | LOW | synthetic mRNA ADA |
| 18 | F22 | 1 | NO | LOW | synthetic DDI dual |
| 19 | F28 | 1 | NO | LOW | synthetic pregnancy |
| 20 | F29 | 1 | YES | LOW | synthetic lactation dyad |

## Per-category detail (concise — full spec in seed pack doc)

For each of the 20 categories (1..20) the same generic detail
template applies; this run uses synthetic minimal CSVs (5–20 rows)
constructed per the category's `key_axis_states` and `required_AIC`
declarations in `reports/pilot_edge_case_seed_pack_v5_1.md`.

## Public alternatives (when real data unavailable)

| Family | Public dataset suggestion |
|---|---|
| F01 | `nlmixr2::warfarin`, `nlmixr2::theo_sd` |
| F02 | pooled popPK examples from `pmxcode` |
| F07 | synthetic SAD/MAD generated from AIC template |
| F09 | Simcyp-style public DDI examples |
| F12 | published pediatric PK (Vassal et al.) |
| F19 | Tox21 preclinical (NIH) |
| F26 | CAR-T public CK examples (Wang et al. CTOS supplementary) |
| F28/F29 | maternal-fetal PK literature examples (Anderson 2020) |

## Validation rule

```
Pilot completeness = 20 / 20 categories covered.
If < 20, list missing in change_control/v1_1_candidate_register.csv
with justification and defer to v1.1 before freeze.
```

This run targets 20/20 via synthetic substitution.
