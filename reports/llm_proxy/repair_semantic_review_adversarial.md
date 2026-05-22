# repair_semantic_review_adversarial.md (LP-B, Checkpoint: CP3)

> **NOTE — this run:** LP-B simulated in the main session (NOT a
> different-family model). A real LP-B pass with a Gemini/GPT-class
> model in a fresh chat is REQUIRED before external release.
> `lp_b_simulated: TRUE`.

## Attack list (best-effort under simulated constraint)

| issue | severity | evidence | correction |
|---|---|---|---|
| ADC partial analyte_role: some analytes labeled, others not | minor | `assign_cmt_with_analyte_role` accepts any subset of analytes in `role_cmt_map`; unknowns map to UNKNOWN/CMT=1. | Acceptable for v1.0 — H4 audit confirms downstream model still parses; otherwise tighten map validation in v1.1. |
| Dyad linkage edge: single mother → multiple infants over time | minor | `attach_dyad_linkage` uses `MOTHER_SUBJID` as DYAD_ID; multi-birth pairs share DYAD_ID. | Acceptable — twin/longitudinal-infant studies are out of scope of v1.0 pilot seed pack. Register as v1.1 candidate if encountered in real data. |
| `repair_blq_canonicalization` LLOQ source ambiguous | minor | LLOQ taken from `LLOQ` column if present; defaults to 0.1 if absent. | Document in operator quick reference; require LLOQ column in NONMEM-ready dataset. |
| `derive_time_postpartum_anchor` POSTPARTUM_DAY uses ceil() | minor | Day-of-life convention; rounding direction not stated in policy. | Acceptable; document in audit_log (already done — `anchor_col` recorded). |
| Q-code mismatch potential: milk subtype Q01 vs new code | minor | MILK_PK uses Q01 (concentration BLQ subtype) for missing matrix LLOQ. | Verified against DC007 in Phase 1. No mismatch. |
| Hidden state drift in `attach_covariate_product_level` | minor | Function inserts new columns (`<product_cov_names>`); could collide with existing names. | Acceptable for synthetic fixtures; real data should pre-check column collisions. |

## Output fields

- unresolved_fatal_count: **0**
- escalate_to_human_override: **NO**
- lp_b_simulated: **TRUE**

## Notes

A real LP-B pass should pay particular attention to:
- Multi-birth dyad cases (twins/triplets).
- M4 (likelihood-based) BLQ method — not implemented in this v1.0; declare as v1.1 candidate if a real study demands it.
- ADC with > 3 analytes (the synthetic fixture uses exactly 3).
