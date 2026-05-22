# minimal_node_approval_judge.md (LP-C, Checkpoint: CP6)

> Simulated.

## Hard rules check

- HR13: forced set {N0,N1,N2,N3,N4,N5,N8} ⊆ selected — **YES**.
- confidence LOW → escalate — not triggered.
- unresolved_fatal_count ≥ 1 → escalate — not triggered.
- dangerous merge — none.

## Decision

- final_decision: **accept** (auto-apply)
- confidence: HIGH
- fatal_resolved: YES
- escalate_to_human: NO

Mark `data/ilp/final_minimal_node_set.csv` as APPROVED. Proceed to P99.
