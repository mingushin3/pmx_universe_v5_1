# Pediatric Special Populations Addendum (v1.0)

> **Scope:** F12 (Pediatric PK) handling in the v1.0 system.
> **Note:** F12 family is **not present in the synthetic v5.1 universe**
> (HANDOVER §2.1, v1.1 candidate V1_1_002).  This addendum documents the
> expected handling once F12 is generated.

## mg/kg vs BSA dose reconstruction

- `reconstruct_dose_weight` (RR008) — for mg/kg dosing in pediatric PK.
- `reconstruct_dose_bsa` (RR009) — for body-surface-area dosing.
- AIC must declare which calc is used: `dose_basis: weight | bsa`.

## Age-dependent LLOQ

- Pediatric assays may have a different LLOQ than the adult validation.
- AIC field `assay_lloq_age_band` (list of `{age_min, age_max, lloq}` triples)
  is required when `population_segment == PEDIATRIC`.

## Body weight as time-varying covariate (F12 + A7=TIME-VARYING)

- Pediatric weight changes substantially over study duration.
- `attach_covariate_time_varying` (RR/AFL function) attaches WT by visit.
- AIC must declare `weight_time_basis: nominal | actual`.

## Common QUARANTINE triggers

| trigger | Q-code | required clearance |
|---|---|---|
| weight column missing after mg/kg dose calc | Q08 | request weight column |
| LLOQ not declared per age band | Q01 | request `assay_lloq_age_band` |
| time-varying weight policy missing | Q07 | request `weight_time_basis` |

## v1.1 expansion plan

Per V1_1_002: generate F12 seed-pack scenarios and regenerate the universe.
Re-run P107 with the F12 golden (G005 PROJ_PED_006).

---
