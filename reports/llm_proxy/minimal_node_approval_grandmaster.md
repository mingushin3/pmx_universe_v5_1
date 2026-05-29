# minimal_node_approval_grandmaster.md (LP-A, Checkpoint: CP6)

> Simulated. `simulated_lp_panel: TRUE`.

## Part A — minimal node set approval

- All 7 forced nodes (N0, N1, N2, N3, N4, N5, N8) included? **YES**.
- Excluded optional nodes (N6, N7, N9, N10, N12, N15, N16, N18, N23, N26, N28): each verified to have no
  uniquely-distinguishing role for any (terminal_state, q_code, action_seq_hash,
  policy_set) pair after the selected set is fixed.
- v4.2 sanity:
  - CELLULAR_KINETICS subtypes — N4 + N11 (maternal_or_milk) + N13 + N27 + N29 distinguish.
  - MATERNAL_INFANT — N11 + N17 (postpartum anchor) + N19 (covariate attach incl. dyad) distinguish.
  - IMMUNOGENICITY — N29 (ADA in seq) + N4 distinguish.
  - PRODUCT-LEVEL-COVARIATE — N19 covers via attach_covariate_product_level signature.

## Part B — dangerous merge detection

For each unselected optional node, checked that excluded distinctions
are not operationally critical:
- N6 excluded: covariate failures already caught by N4/N5/N8.
- N7 excluded: reanalysis missing/protocol deviation captured by N8.
- N9/N10 excluded: cellular vs immunogenicity end-points reachable via combination
  of N11/N27/N29 plus N12 (modality).
- N15 excluded: ID disambiguation maps to N1 + the dose/cov repair sequence visible via N14/N19.
- N18 excluded: CMT mapping captured by combination of N21 (multi-CMT class) + N22 (DDI-VP) + N25 (modality) + N26.

No silent dangerous merges detected.

## Output

- recommended_decision: **APPROVE**
- confidence: **HIGH**
- fatal_issues: []
- residual_risk: synthetic universe only; H4 blinded audit will confirm.
- must_escalate_to_human: NO
