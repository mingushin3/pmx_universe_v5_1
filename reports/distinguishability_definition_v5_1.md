# Pairwise Distinguishability Definition v5.1 (PATCH-2)

## Definition

For two DC-equivalence classes `c_i` and `c_j`:

```
DISTINGUISHABLE_REQUIRED(c_i, c_j) = TRUE iff ANY of:
  - terminal_state(c_i) != terminal_state(c_j)
  - action_sequence_hash(c_i) != action_sequence_hash(c_j)
  - q_code(c_i) != q_code(c_j)             (null vs null → equal)
  - required_policy_set(c_i) != required_policy_set(c_j)
```

For pairs where `DISTINGUISHABLE_REQUIRED` is TRUE, the selected node
subset `S` (the minimal node set) MUST satisfy:

```
∃ n ∈ S such that node_value(c_i, n) ≠ node_value(c_j, n)
where "*" (don't-care) is compatible with any value.
```

For pairs where `DISTINGUISHABLE_REQUIRED` is FALSE (truly equivalent),
the constraint is satisfied vacuously.

## Why strengthened (vs v3.1)

v3.1 only required terminal_state OR action_label difference. This was
insufficient because:

1. Same action_label may carry different parameter_policy (e.g., BLQ-M1 vs BLQ-M3).
2. Same terminal_state may require different policies in AIC.
3. v4.2: CAR-T REPAIR with vs without product-level linkage policy would
   be merged under v3.1.

## "*" (don't-care) semantics

| left | right | match? |
|---|---|---|
| Y | Y | YES (same) |
| N | N | YES (same) |
| Y | N | NO (distinguishable on this node) |
| * | Y or N or * | YES (don't-care is compatible) |

So a node distinguishes a pair only if BOTH have non-* values that differ.

## Mathematical formulation for ILP

Binary `x_n ∈ {0,1}` indicating whether node n is selected.

Constraint per distinguishable pair `(c_i, c_j)`:

```
Σ_{n: node_value(c_i, n) ≠ node_value(c_j, n) AND both non-*}  x_n  ≥  1
```

If the RHS set is empty for some pair → INFEASIBLE → P91 triage.
