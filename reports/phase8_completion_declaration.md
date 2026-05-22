# Phase 8 Completion Declaration

**Phase:** 8 (P86–P100) — Decision Table + ILP + LP Panel CP6
**Date:** 2026-05-22

## Checklist

- [x] **D3 `reduced_decision_table_v1.0.csv` generated** — 337 DC classes (PATCH DC-wildcard exact_pattern grouping with operational distinguishers).
- [x] **D4 `pairwise_distinguishability_matrix.npz` generated** — 50,867 distinguishable-required pairs; 0 infeasible.
- [x] **D5 `final_minimal_node_set.csv` generated and LOCKED with hash** — 19 nodes selected; SHA256 in `release/v1.0/minimal_node_set_v1_0.sha256`.
- [x] **No infeasible pairs** — resolved via P92 node expansion (N9–N29 added; node dictionary now 30 nodes total).
- [x] **forced nodes (N0,N1,N2,N3,N4,N5,N8) ⊆ minimal set** — all 7 present.
- [x] **LP Panel CP6 (minimal_node_approval) resolved** — `accept`, HIGH confidence, no escalation (`lp_b_simulated: TRUE`).
- [x] **PATCH-2 distinguishability strengthening applied (P89)** — `reports/distinguishability_definition_v5_1.md`.
- [x] **PATCH-3 forced node constraint applied (P93)** — `config/ilp_problem_definition.yaml` `forced_inclusion` constraint group.
- [x] **dangerous merge check passed** — `reports/llm_proxy/minimal_node_approval_grandmaster.md` Part B.
- [x] **CHANGELOG updated to v0.9.0** — entry added.

## P92 patch summary

Started with 9 nodes (N0–N8); 779 infeasible pairs. Iteratively added
21 more nodes (N9–N29) covering:
- v4.2 endpoint / modality discriminators (N9–N12).
- Action-sequence content discriminators (N13–N19, N26, N28, N29).
- Axis-state discriminators (N20–N25, N27).

Final dictionary: 30 nodes (7 forced + 23 optional). ILP selected 19
(forced 7 + optional 12), achieving 100% distinguishability coverage at
cost 43.30.

## Phase 8 artifacts

| Path | Source |
|---|---|
| `scripts/decision_table/generate_decision_table.py` | P86 |
| `scripts/decision_table/dc_reduction.py` | P87 |
| `data/decision_table/raw_decision_table.csv` | P86 |
| `data/decision_table/reduced_decision_table_v1.0.csv` (D3) | P87 |
| `reports/dc_reduction_report.md` | P87 |
| `scripts/decision_table/validate_hashes.py` | P88 |
| `reports/decision_table_hash_validation.md` | P88 |
| `reports/distinguishability_definition_v5_1.md` | P89 |
| `scripts/decision_table/build_pairwise_matrix.py` | P90 |
| `data/ilp/pairwise_distinguishability_matrix.npz` (D4) | P90 |
| `reports/pairwise_matrix_report.md` | P90 |
| `reports/infeasible_pair_triage.md` | P91 |
| `config/candidate_node_dictionary_with_costs.csv` (30 nodes after P92) | P92 |
| `config/ilp_problem_definition.yaml` | P93 |
| `scripts/ilp/solve_minimal_node_set.py` | P94 |
| `data/ilp/solver_output.json` | P95 |
| `data/ilp/final_minimal_node_set.csv` (D5) | P95 |
| `reports/ilp_solution_report.md` | P95 |
| `reports/llm_proxy/minimal_node_approval_*.{md,csv}` | P96–P98 |
| `release/v1.0/minimal_node_set_v1_0.sha256` | P99 |
| `release/v1.0/minimal_node_set_lock_declaration.md` | P99 |
| `reports/phase8_completion_declaration.md` | P100 |

Ready for CHECK-8.
