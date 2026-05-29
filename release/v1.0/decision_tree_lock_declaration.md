# Decision Tree v1.0 — Lock Declaration

**Artifact:** `config/operational_decision_tree.yaml` (D6)
**Companion:** `scripts/validation/nonmem_ready_qc.py`
**Locked at (UTC):** 2026-05-22T12:55:00+00:00
**Locked by:** automated pipeline (Phase 9 / P105)
**Source inputs:**
- `data/decision_table/reduced_decision_table_v1.0.csv` (D3, 337 DC classes)
- `data/ilp/final_minimal_node_set.csv` (D5, 19 selected nodes)
- `config/candidate_node_dictionary_with_costs.csv` (30 candidate nodes)
- `config/action_label_dictionary_v1_0.yaml` (90 labels)

---

## 1. Tree statistics

| metric | value |
|---|---|
| internal nodes | 126 |
| leaves | 51 |
| — real leaves (D3-backed) | 45 |
| — synthetic forced-failure leaves | 6 |
| D3 classes covered | 337 / 337 (100%) |
| tree depth (max) | 19 |
| forced-node count | 7 |
| optional node count | 12 |

## 2. Forced node evaluation order

```
N0 → N1 → N8 → N2 → N3 → N4 → N5
```

Every operational walk evaluates these seven nodes in this order before any
optional node is consulted.  When the forced tier short-circuits (any forced
node answers `N`), the walk terminates at a QUARANTINE/INVALID leaf
(real-leaf if D3 contains an example; synthetic forced-fail leaf otherwise).

## 3. Optional node evaluation order

```
N14 → N13 → N19 → N21 → N22 → N24 → N25 → N11 → N17 → N20 → N27 → N29
```

Ordered by descending failure-risk cost within tier
(see `reports/decision_tree_construction_plan.md` §2.2).

## 4. v4.2 leaf coverage

| pattern | present? |
|---|---|
| `CELLULAR` | ✅ |
| `IMMUNOGEN` | ✅ |
| `MATERNAL` | ✅ |
| `DYAD` | ✅ |
| `MILK` | ✅ |

## 5. Tree ↔ Decision Table consistency (P103)

- match_rate: **100.000%** (337 / 337)
- T01 failures: 0
- T02 failures: 0
- T03 failures: 0
- T04 failures: 0
- T05 informational notes: 0
- T06 failures: 0

Report: `reports/tree_table_consistency.md`.

## 6. NONMEM-Ready QC (P104)

| metric | value |
|---|---|
| total checks | 21 (S01–S05, E01–E05, B01–B03, C01–C03, V01–V04, A01) |
| pytest cases | 12 |
| pytest result | **12 PASS / 0 FAIL** |

Tests: `tests/test_nonmem_ready_qc.py` covering clean AUTO, clean REPAIR,
EVID violation, MDV/DV inconsistency, multi-analyte CMT missing role-map,
CELLULAR negative DV, MATERNAL_INFANT missing DYADID, audit-log missing,
EVID=1 dose missing AMT, malformed column name, UTF-8 BOM present,
ID non-monotonic.

## 7. Hashes

```
dab2f6f7f44a42fa7db03e9ea83cbe8494b79580b458d31ec655be277bde4288  config/operational_decision_tree.yaml
07576ed54b487f48d073fe1ed0c7ead77226497eed3ec79dc61201cb80816db8  scripts/validation/nonmem_ready_qc.py
```

(Companion file: `release/v1.0/decision_tree_v1_0.sha256`.)

## 8. Invariants enforced at build time

1. All 7 forced nodes (N0, N1, N2, N3, N4, N5, N8) present in node_order.
2. Optional nodes appear only after the forced tier.
3. Excluded candidate nodes (N6, N7, N9, N10, N12, N15, N16, N18, N23, N26, N28)
   do not appear as internal nodes.
4. Every leaf with `terminal_state == AUTO` carries `export_nonmem_ready` in
   its `action_sequence`.
5. Every leaf with `terminal_state == REPAIR` carries ≥1 repair-class function.
6. No leaf with `q_code == "Q17"` (retired in v5.1).
7. No leaf with `q_code == "Q15"` (only `Q15A` or `Q15B`).
8. All four `terminal_state` values (AUTO, REPAIR, QUARANTINE, INVALID) are reachable.
9. v4.2 leaf labels include CELLULAR, IMMUNOGEN, MATERNAL, DYAD, MILK.
10. Every D3 class routes to exactly one leaf, and the leaf's action_label_set
    contains the class's action_label.

## 9. Notes on synthetic leaves

Six forced-failure leaves (`leaf_QUARANTINE_*_forced_fail_N{1..8}`) were
emitted by the build for forced nodes that did not split the remaining D3
classes at construction time.  They are reached only by **new** scenarios in
which the corresponding forced gate fails after earlier gates have passed.
None of the 337 D3 classes route to a synthetic leaf, so they do not
contribute to the 100% T01–T06 consistency above.

## 10. Change-control trigger

Any modification to `config/operational_decision_tree.yaml` or
`scripts/validation/nonmem_ready_qc.py` invalidates this lock and requires:
- a `change_control/v1_1_candidate_register.csv` entry,
- regeneration of D6 via P102 → P103 (100% match),
- pytest of P104 (≥12 PASS),
- re-issue of this declaration with a new ISO timestamp.

---

*— End of decision_tree_lock_declaration.md —*
