# action_label_lock_adversarial.md (LP-B, Checkpoint: CP5)

> `lp_b_simulated: TRUE`.

## Final attack

| issue | severity | evidence | correction |
|---|---|---|---|
| Some labels carry truncated descriptors (e.g., `REPAIR_F01_BLQ_CMTM_REAN`) — readability cost | minor | label naming | Acceptable; the unique-label dictionary in `action_label_dictionary_v1_0.yaml` provides full context. |
| Label name doesn't include modality_class for some F-codes | minor | e.g., `REPAIR_F01_BLQ` covers SMALL_MOLECULE/MAB indistinguishably | Acceptable: family already implies modality range; modality is in the CSV row. |
| F28 only 8 scenarios = thin coverage | minor | family_coverage_summary | Already noted in CP2. |

unresolved_fatal_count: 0, escalate_to_human_override: NO.
