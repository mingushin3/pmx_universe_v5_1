# minimal_node_approval_adversarial.md (LP-B, Checkpoint: CP6)

> `lp_b_simulated: TRUE`.

## Attack

| issue | severity | evidence | correction |
|---|---|---|---|
| 19/30 selected feels high; could ILP cost weights bias selection? | minor | per ilp_problem_definition.yaml — costs derived from PMX-Grandmaster judgment (Step 2 P68) | Acceptable; costs are LOCKED before solve. |
| Could excluding N6 hide PRODUCT-LEVEL-COVARIATE silently? | minor | N19 selected covers attach_covariate_product_level in the sequence | OK. |
| Q-code coverage check | minor | every Q01..Q19 (except Q17) reaches a unique combination of (N4/N5/N8/N20/N23/N27/N29 + N11/N12) | OK. |
| F24-F29 operational coverage | minor | all 6 families have ≥ 1 DC class in the selected-set partition | OK. |

- unresolved_fatal_count: **0**
- escalate_to_human_override: **NO**
- lp_b_simulated: TRUE
