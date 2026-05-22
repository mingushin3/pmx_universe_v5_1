# Operational Decision Tree Construction Plan

**Document ID:** decision_tree_construction_plan
**Version:** v1.0
**Phase:** 9 (P101)
**Inputs:**
- `data/decision_table/reduced_decision_table_v1.0.csv` (D3, 337 DC classes)
- `data/ilp/final_minimal_node_set.csv` (D5, 19 selected nodes)
- `config/candidate_node_dictionary_with_costs.csv` (30 candidate nodes with cost + rationale)

---

## 1. Tree structure

The operational decision tree is a **binary tree** in which:

- **Internal nodes** correspond to the 19 nodes that the ILP solver selected
  in Phase 8 (`final_minimal_node_set.csv`). Each internal node carries the
  exact yes/no `question` text from `candidate_node_dictionary_with_costs.csv`
  and the `detection_rule` that operationalizes that question against the
  AIC + raw fingerprint.
- **Leaf nodes** correspond to unique outcome tuples
  `(terminal_state, q_code, action_sequence_label, family_id_examples)` drawn
  from D3 and cross-checked against `config/action_label_dictionary_v1_0.yaml`.
- **Edges** are the two answers `Y` and `N`. `*` (don't-care) values in D3 are
  treated as "this node need not distinguish" at construction time: the class
  is duplicated into both `Y` and `N` subtrees so that any walker reaches the
  same leaf regardless of the answer.

Selected node set (in tree order, see §2):

```
forced     : N0, N1, N8, N2, N3, N4, N5
optional   : N11, N13, N14, N17, N19, N20, N21, N22, N24, N25, N27, N29
total      : 19 (7 forced + 12 optional)
```

D3 outcome inventory (counts):

| terminal_state | q_code | classes |
|---|---|---|
| QUARANTINE | Q11 | 24 |
| QUARANTINE | Q01 | 2 |
| QUARANTINE | Q02 | 1 |
| QUARANTINE | Q12 | 1 |
| QUARANTINE | Q15A | 84 |
| QUARANTINE | Q15B | 48 |
| QUARANTINE | Q16 | 24 |
| QUARANTINE | Q18 | 1 |
| QUARANTINE | Q19 | 2 |
| INVALID    | —   | 24 |
| REPAIR     | —   | 114 |
| AUTO       | —   | 12 |
| **total**  |     | **337** |

Unique `(terminal_state, q_code, action_label)` triples in D3 = **67**, which
is the upper bound on distinct leaves.

---

## 2. Node ordering rationale

The order is fixed for two reasons: (a) HR1–HR14 axis dependency
(`A0 → A1 → A2 → A3 → A4/A5 → A8 → A6/A7 → A9 → AIC-policy`) determines
which node can even be asked once an earlier axis has failed; and (b) within
a tier we order by **descending `failure_risk` cost** so that high-risk
disqualifiers terminate the walk early and minimize downstream wasted work.

### 2.1 Forced tier (always evaluated, before any optional node)

| Rank | Node | Axis | Cost | Reason |
|---|---|---|---|---|
| 1 | N0 | A0 (AIC + endpoint_data_type) | 4.20 | Root. Without AIC nothing is decidable; `N0=N → Q11`. |
| 2 | N1 | A1 (ID, dyad linkage) | 3.90 | Identifier resolvable; `N1=N → Q03/Q18` (INVALID or dyad-missing). |
| 3 | N8 | AIC-policy completeness | 4.40 | v5.1 NEW gate (PATCH-3). Catches partial policy declarations before any sequence is attempted; placed immediately after N1 so we don't waste later nodes on a half-specified AIC. |
| 4 | N2 | A2 (time anchor) | 4.10 | Time axis incl. postpartum/elapsed; `N2=N → Q02`. |
| 5 | N3 | A3 (dose path) | 4.50 | Highest dose-axis risk; `N3=N → Q08` (INVALID). |
| 6 | N4 | A5+A8 (observation/CMT/analyte_role) | 4.10 | Catches cellular/immunogen/milk silent errors; `N4=N → Q09/Q15A`. |
| 7 | N5 | A5 (BLQ/MDV policy) | 3.10 | `N5=N → Q01`. |

The seven forced nodes are evaluated **in this order on every walk**.
Failure at any forced node short-circuits the walk to a QUARANTINE or
INVALID leaf (q_code per the `q_code_if_fail` column of the dictionary).
This satisfies HR-2 ("INVALID/QUARANTINE must be detected as early as
possible") and the P101 spec's "high-risk early to terminate fast on failure".

### 2.2 Optional tier (descending failure_risk within each group)

Optional nodes are evaluated only when all forced nodes return `Y`
(meaning the scenario is at least a REPAIR or AUTO candidate). Within the
optional tier the order is:

```
N14 (dose-reconstruction)            cost 1.5   action_sequence axis A3+A4
N13 (BLQ canonicalization)           cost 1.5   action_sequence axis A5
N19 (covariate attachment)           cost 1.3   action_sequence axis A7
N21 (multi-CMT class state)          cost 1.1   axis A8
N22 (DDI VICTIM/PERPETRATOR)         cost 1.1   axis A8
N24 (ADDL-actual conflict)           cost 1.1   axis A4
N25 (modality supports analyte_role) cost 1.1   axis A0 modality
N11 (endpoint MATERNAL_INFANT/MILK)  cost 2.0   axis A0
N17 (postpartum / elapsed anchor)    cost 1.2   action_sequence axis A2
N20 (A5=BIOANALYTICAL-FINAL-FLAG-MISSING) cost 1.1   axis A5
N27 (A5=CELLULAR-BLQ-DEFINED)        cost 1.0   axis A5
N29 (adjudicate_immunogenicity_positivity) cost 1.0   action_sequence
```

Justification for the within-tier order:

1. **Dose / BLQ first (N14, N13).** These two carry the highest optional
   cost (1.5 each) and they discriminate REPAIR sub-classes that depend on
   the action_sequence executing `reconstruct_dose_*` / `canonicalize_blq*`.
   Resolving them early collapses 162 REPAIR classes most quickly.
2. **Covariate / CMT-class / DDI (N19, N21, N22).** Together these split
   the multi-CMT and DDI REPAIR branches (24 Q16 + dual-CMT REPAIR classes).
3. **Regimen + modality (N24, N25).** ADDL conflict and modality tagging are
   close cost (1.1) and split parameter_policy hashes.
4. **Endpoint family discriminators (N11, N17).** Maternal/Milk and
   postpartum/elapsed time anchors discriminate F26–F30 v4.2 families.
5. **Bioanalytical-incomplete + cellular BLQ + ADA (N20, N27, N29).** These
   discriminate Q15A vs Q15B QUARANTINE sub-classes and CELLULAR vs ADA leaves
   among the v4.2 modalities.

The order is recorded in `node_order` field of `operational_decision_tree.yaml`
exactly as listed above and used unchanged by the recursive builder.

### 2.3 Excluded candidate nodes (documented for traceability)

`N6, N7, N9, N10, N12, N15, N16, N18, N23, N26, N28` were available but were
NOT selected by the ILP solver (cost `INFINITY` was not invoked; they would
have raised total cost without distinguishing any infeasible pair, see
`reports/ilp_solution_report.md`). They MUST NOT appear in the tree.

---

## 3. Branching logic

```
At each internal node n:
    answer = detection_rule(n, scenario)
    if remaining_classes (after split on n) contain Y_classes:
        Y_branch -> (next internal node if remaining_nodes non-empty,
                    else leaf(majority_outcome(Y_classes)))
    if remaining_classes (after split on n) contain N_classes:
        N_branch -> leaf(failure_outcome(n))  for forced nodes
                    or next internal node     for optional nodes

Y_classes for node n  = { c in remaining_classes : c[n] in {'Y','*'} }
N_classes for node n  = { c in remaining_classes : c[n] in {'N','*'} }
```

A `*` value in D3 means the class is indifferent to the answer at this node;
it joins both subtrees, so any path leads to the correct leaf.

For forced nodes the `N` branch always points to a **QUARANTINE or INVALID
leaf** keyed on `q_code_if_fail`:

```
N0=N → leaf_Q11  (terminal_state=QUARANTINE)
N1=N → leaf_Q03 (INVALID) OR leaf_Q18 (QUARANTINE if dyad-key missing) — discriminated by N11
N8=N → leaf_Q15A_policy_incomplete  (QUARANTINE)
N2=N → leaf_Q02  (QUARANTINE)
N3=N → leaf_Q08  (INVALID; not in D3 because Phase 5 filter removed Q08-only seeds)
N4=N → leaf_Q09 / leaf_Q15A   (QUARANTINE; sub-discriminated by N20)
N5=N → leaf_Q01  (QUARANTINE)
```

For optional nodes both branches point either to the next optional internal
node OR — when the remaining_classes collapse to a single outcome tuple — to
a leaf.

### 3.1 Terminal-collapse rule

Recursion stops when **all remaining classes share the same
`(terminal_state, q_code, action_label)` tuple**, regardless of how many
remaining internal nodes are still available. The leaf is the unique outcome
tuple and its `action_sequence` is looked up in
`config/action_label_dictionary_v1_0.yaml`.

---

## 4. Leaf assignment rules

Each leaf is constructed deterministically:

1. The leaf's `terminal_state`, `q_code`, and `action_label` come from the
   converged class outcome.
2. The leaf's `action_sequence` is the canonical sequence in
   `config/action_label_dictionary_v1_0.yaml[<action_label>].action_sequence`.
3. The leaf's `parameter_policy` is the dictionary entry's
   `parameter_policy` mapping.
4. The leaf's `family_id_examples` is the de-duplicated list of family ids
   appearing in `member_scenario_ids` for that converged group (resolved via
   `data/action_labels/scenario_action_table_locked.csv`).

### 4.1 Validation invariants

Enforced at tree-build time and re-checked in P103:

- Every D3 class reaches **exactly one** leaf.
- Every leaf is reached by **≥1 D3 class** (no orphan leaves).
- All forced nodes (N0,N1,N2,N3,N4,N5,N8) appear in **every** walk that
  exits at a leaf, OR a forced node short-circuits earlier with a known
  failure leaf.
- `q_code != "Q17"` for every leaf (HR-6: Q17 was retired in v5.1).
- No leaf has `q_code == "Q15"` standalone (only `Q15A` or `Q15B`).
- Every `terminal_state == "AUTO"` leaf's `action_sequence` contains
  `export_nonmem_ready` (HR-7).
- Every `terminal_state == "REPAIR"` leaf's `action_sequence` contains
  ≥1 function from `repair_rule_dictionary.yaml`.
- v4.2 leaf-pattern coverage: leaf set MUST contain action_labels matching
  the regexes `CELLULAR`, `IMMUNOGEN`, `MATERNAL` (or `DYAD`), and `MILK`.

---

## 5. Audit log requirement

The YAML carries a top-level `audit_log_template` (one template, used per
leaf hit at runtime). Required fields:

```yaml
audit_log_template:
  fields:
    - decision_path             # list of (node_id, answer) tuples
    - terminal_state            # final outcome
    - q_code                    # if QUARANTINE; null otherwise
    - action_sequence_executed  # function names invoked, in order
    - parameter_policies        # mapping function -> resolved parameter values
    - timestamp_iso             # UTC ISO-8601, microsecond precision
    - input_data_summary        # {row_count, columns_used, fingerprint_sha256}
    - row_counts_before_after   # before/after per repair function
    - operator                  # SHA256(user@host) — anonymised
    - aic_hash                  # SHA256 of attached AIC YAML
```

The audit log is **emitted per dataset** (one JSON per AUTO/REPAIR
invocation), filed alongside the NONMEM-ready CSV. The downstream NONMEM-
ready QC script (P104) refuses to PASS check A01 unless the audit log file
exists with all required fields populated.

---

## 6. Construction algorithm (pseudo)

```python
def build_tree(remaining_classes: list[DC], remaining_nodes: list[NodeId]) -> TreeNode:
    if len(remaining_classes) == 0:
        raise BuildError("empty subtree — unreachable region")
    outcomes = { (c.terminal_state, c.q_code, c.action_label) for c in remaining_classes }
    if len(outcomes) == 1:
        return leaf(*outcomes.pop())
    if not remaining_nodes:
        raise BuildError(f"node set under-distinguishes: {outcomes}")
    n = remaining_nodes[0]
    Y = [c for c in remaining_classes if c.values[n] in ('Y','*')]
    N = [c for c in remaining_classes if c.values[n] in ('N','*')]
    rest = remaining_nodes[1:]
    return internal_node(
        node_id=n,
        yes=build_tree(Y, rest) if Y else None,
        no=build_tree(N, rest) if N else None,
    )
```

Termination is guaranteed because `remaining_nodes` strictly shrinks every
recursion step.

---

## 7. Estimated tree statistics (pre-build, sanity check)

- internal nodes (selected): 19
- maximum depth: 19
- realistic depth: ≤14 (most paths collapse at the forced tier when
  N0/N1/N8 short-circuit, or at the first 2–3 optional nodes for the
  AUTO/REPAIR collapse)
- expected leaves: 67 (= number of unique outcome triples)
- expected leaves by terminal_state: 1 AUTO archetype × 5 family blocks,
  46 REPAIR labels, ~15 QUARANTINE q_code/label variants, 1 INVALID
  catch-all (or split by N1 sub-reason)

These numbers are estimates only and are reconciled with the actual build
output in `reports/tree_table_consistency.md` (P103).

---

*— End of construction plan —*
