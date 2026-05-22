# Operator Quick Reference (v1.0)

## 5-step workflow

1. **Intake**: collect raw input + AIC YAML + sponsor metadata.
2. **AIC validate**: `python3 scripts/config_validation/validate_aic.py --aic-file <aic>`
3. **Tree route**: walk D6 → get `terminal_state` + recommended `action_sequence`.
4. **Execute**: run `repair_executor` for AUTO/REPAIR; emit notice for QUARANTINE.
5. **QC**: `python3 scripts/validation/nonmem_ready_qc.py --dataset <out> --aic <aic> --audit-log <log> --out <report>`

## Common Q-codes — what to do

| Q | meaning | action |
|---|---|---|
| Q01 | BLQ policy missing | request BLQ policy (M1/M3/M4 + cellular_LLOQ if cellular) |
| Q02 | TIME axis unresolvable | request actual/nominal/elapsed mapping |
| Q11 | AIC missing or endpoint_data_type absent | request complete AIC |
| Q15A | data package incomplete | request bioanalytical-final flag |
| Q15B | legacy flag undocumented | request flag definition |
| Q15C | RWD adherence/admin unresolved | request administration log |
| Q15D | reanalysis selection missing | request final-result adjudication |
| Q16 | analyte_role missing (multi-CMT) | request role tags |
| Q18 | maternal-infant dyad missing | request dyad_linkage_key |
| Q19 | immunogenicity positivity rule absent | request adjudication rule |

## v4.2 gotchas

- **CAR-T (F26)**: cellular_LLOQ must be in AIC; `canonicalize_cellular_blq` runs.
- **Maternal/lactation (F29)**: DYADID column required; postpartum anchor must be set.
- **Immunogenicity**: DV must be binary 0/1; `adjudicate_immunogenicity_positivity` runs.
- **ADC/Bispecific (F24/F25)**: `analyte_role` per CMT required.

## Where to find what

| artifact | path |
|---|---|
| D1 universe | `data/scenario_universe/scenario_universe_v1.0.csv` |
| D2 action labels | `data/action_labels/scenario_action_table_locked.csv` |
| D3 decision table | `data/decision_table/reduced_decision_table_v1.0.csv` |
| D4 pairwise matrix | `data/ilp/pairwise_distinguishability_matrix.npz` |
| D5 minimal nodes | `data/ilp/final_minimal_node_set.csv` |
| D6 decision tree | `config/operational_decision_tree.yaml` |
| D7 executor | `scripts/repair_executor/repair_executor.py` |
| D8 golden report | `reports/golden_validation_report.md` |
| D9 coverage claim | `release/v1.0/coverage_claim_statement.md` |
| SOPs | `release/v1.0/SOP_*` |

## Escalation triggers

- decision_log path `N0=N` repeatedly for one sponsor → AIC training gap (escalate sponsor liaison).
- v1.1 register growth ≥3 per quarter → schedule v1.1 cycle.
- Confirmed false AUTO/REPAIR → CRITICAL → halt, contact PMX lead (H5).

## H5 escalation contact

PMX lead (see `release/v1.0/H5_final_release_approval.md`). For v5.1, placeholder
`(placeholder) PMX_Lead_A`; replace before production rollout.

---

*— v1.0 operator quick reference —*
