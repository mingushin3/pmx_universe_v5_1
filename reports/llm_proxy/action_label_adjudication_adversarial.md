# action_label_adjudication_adversarial.md (LP-B, Checkpoint: CP4)

> `lp_b_simulated: TRUE`.

## Attack

| issue | severity | evidence | correction |
|---|---|---|---|
| Label naming collapses (M1/M3/M4) BLQ variants to same label | minor | `REPAIR_F01_BLQ` covers all BLQ-DEFINED-POLICY rows regardless of method | Acceptable for v1.0: method is in parameter_policy (`blq_handling_policy: M3`). EP split (P77) verifies parameter_policy is part of label equivalence. |
| ADC analyte_role values "TOTAL_ANTIBODY|CONJUGATED_ADC|UNCONJUGATED_PAYLOAD" treated as single bundle | minor | label `REPAIR_F24_CMTROLE` regardless of role list ordering | Acceptable: analyte_role list is sorted (pipe-separated). EP split would catch ordering issues. |
| Pregnancy F28 has only 8 scenarios | minor | family_coverage_summary | Already noted in CP2 acceptance. |

- unresolved_fatal_count: 0
- escalate_to_human_override: NO
- lp_b_simulated: TRUE
