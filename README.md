# PMX-to-NONMEM Scenario Universe v5.1

Working basis: **Frozen Universe v4.2**.
Total prompts: ~140 across Phases 0–12.
Final deliverables: 9 (D1–D9).

## Overview

This repository implements the v5.1 prompt-driven workflow for
producing a NONMEM-ready dataset transformation decision system from
any practical input data + Analysis Intent Contract (AIC).

The output is a minimal set of decision nodes that, given the
forced safety gates `{N0, N1, N2, N3, N4, N5, N8}`, satisfies the
strengthened distinguishability constraint (HR14) over the v4.2
scenario universe.

## Phases

| Phase | Range | Purpose |
|---|---|---|
| 0 | P1–P6 | Charter, LP Panel template, scaffold, logging utility |
| 1 | P7–P22 | Frozen Universe v4.2 → machine-readable YAML config |
| 2 | P23–P28 | Scenario universe generator → D1 |
| 3 | P29–P40 | Pilot fingerprints + 20-case seed pack |
| 4 | P41–P50 | Repair executor implementation → D7 |
| 5 | P61–P79 | Action labeling + adjudication + lock → D2 |
| 7 | P84–P87 | Decision table construction → D3 |
| 8 | P88–P90 | Pairwise distinguishability matrix → D4 |
| 9 | P91–P95 | ILP solve + minimal node approval → D5 |
| 10 | P96–P100 | Operational decision tree → D6 |
| 11 | P101–P110 | Golden validation + H4 blinded audit → D8 |
| 12 | P111–P118 | Release coverage approval → D9 |

## How to run

1. Read `project_charter_v5_1.md` (HR1–HR14, scope, deliverables).
2. Read `reports/backward_artifact_dag.md` (dependency DAG).
3. Read `reports/success_criteria.md` (17 release acceptance criteria).
4. Execute `v5_1_step1_patched_v3.md` prompts in order (P1 → P28).
   Each prompt's deliverable is saved per the path in this README's
   "Final deliverables" section below.
5. Continue with Step 2 (P29–P79) and Step 3 (P80–P118).
6. Run `python check_phase{N}.py` after each phase. Do NOT advance
   on FAIL — follow the failure_fallback in
   `reports/backward_artifact_dag.md`.

### Windows quick commands

```powershell
.\run.ps1 test       # run pytest
.\run.ps1 validate   # run config validator
.\run.ps1 generate   # generate scenario universe
.\run.ps1 all        # validate + test
```

## Final deliverables

| ID | Path | Locked at |
|---|---|---|
| D1 | `data/scenario_universe/scenario_universe_v1.0.csv` | H2 (universe freeze) |
| D2 | `data/action_labels/scenario_action_table_locked.csv` | H3 (action label lock) |
| D3 | `data/decision_table/reduced_decision_table_v1.0.csv` | — |
| D4 | `data/ilp/pairwise_distinguishability_matrix.npz` | — |
| D5 | `data/ilp/final_minimal_node_set.csv` | CP6 (minimal node approval) |
| D6 | `config/operational_decision_tree.yaml` | H5 |
| D7 | `scripts/repair_executor/repair_executor.py` | H3 |
| D8 | `reports/golden_validation_report.md` | H4 |
| D9 | `release/v1.0/coverage_claim_statement.md` | H5 |
