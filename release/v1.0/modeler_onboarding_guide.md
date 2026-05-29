# PMX Modeler Onboarding Guide (v1.0)

## Receiving a NONMEM-ready dataset

Every dataset delivered from the v1.0 pipeline arrives with three companions:

1. The CSV itself.
2. An `audit_log.json` next to it.
3. A `qc_report.md` (from `nonmem_ready_qc.py`).

## audit_log fields to read first

| field | meaning |
|---|---|
| `decision_path` | list of (node_id, answer) pairs from D6 walk |
| `terminal_state` | AUTO / REPAIR (QUARANTINE/INVALID should never reach you) |
| `q_code` | always null for AUTO/REPAIR |
| `action_sequence_executed` | actual function order executed by repair_executor |
| `parameter_policies` | resolved policy values from AIC |
| `timestamp_iso` | UTC ISO-8601 |
| `input_data_summary` | row_count, columns_used, fingerprint_sha256 |
| `row_counts_before_after` | per repair function (sanity check on filtering) |
| `operator` | SHA256(user@host), anonymised |
| `aic_hash` | SHA256 of attached AIC YAML |

## Verifying executor / tree version (hash match)

Open `release/v1.0/release_v1_0_combined.sha256` and confirm:

- `D6 operational_decision_tree.yaml` hash matches `audit_log.tree_version`.
- `D7 repair_executor.py` hash matches `audit_log.executor_version`.

If either differs, the dataset was produced by a non-locked build; reject it and
escalate to PMX lead.

## When to question the terminal_state

Raise an H5 escalation if any of:

- An AUTO dataset has obvious modeling issues (e.g., negative DV under
  PK_CONCENTRATION endpoint).
- A REPAIR dataset's parameter_policy is internally inconsistent.
- An audit_log references a `repair_function` whose `output_columns_added`
  set is missing in the CSV.

## Coverage interpretation

The v1.0 release covers ≥95% review-inclusive of scenario classes represented
in Frozen Universe v4.2.  This is **not** the same as "≥95% of all real-world
datasets" — datasets outside v4.2 (e.g., new modalities) will be flagged as
UNSUPPORTED and routed via the change_control SOP.

## v1.1 candidate register

Path: `change_control/v1_1_candidate_register.csv`.  Append entries whenever
a dataset requires manual override or you suspect a system defect.

---

*— v1.0 modeler onboarding guide —*
