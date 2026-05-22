"""DC reduction (P87) — group scenarios by (terminal, q_code, action_seq_hash,
parameter_policy_hash, required_policy_set) AND by node pattern.

Uses exact_pattern grouping (PATCH DC-wildcard option 1)."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NODE_COLS = [f"N{i}" for i in range(30)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-csv", default=ROOT / "data" / "decision_table" / "raw_decision_table.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "data" / "decision_table" / "reduced_decision_table_v1.0.csv", type=Path)
    parser.add_argument("--report", default=ROOT / "reports" / "dc_reduction_report.md", type=Path)
    args = parser.parse_args(argv)

    with args.in_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    # Replace NA with *
    for r in rows:
        for c in NODE_COLS:
            if r[c] == "NA":
                r[c] = "*"

    # exact_pattern grouping — by N0..N8 + the operational distinguishers
    # (action_sequence_hash, parameter_policy_hash, q_code).
    # This is PATCH DC-wildcard option 1 extended to ensure within-class
    # consistency on the operational invariants that ILP needs to distinguish.
    groups: dict[tuple, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        key = tuple(r[c] for c in NODE_COLS) + (
            r["action_sequence_hash"], r["parameter_policy_hash"], r["q_code"],
        )
        groups[key].append(r)

    fatal: list[str] = []
    out_rows: list[dict[str, str]] = []
    for key, members in groups.items():
        # Check consistency within DC class
        ts = {m["terminal_state"] for m in members}
        qs = {m["q_code"] for m in members}
        seqs = {m["action_sequence_hash"] for m in members}
        ps = {m["parameter_policy_hash"] for m in members}
        rps = {m["required_policy_set"] for m in members}
        if len(ts) > 1 or len(qs) > 1 or len(seqs) > 1 or len(ps) > 1 or len(rps) > 1:
            fatal.append(f"DC class {''.join(key)}: terminals={ts} qs={qs}")
            continue
        head = members[0]
        out_rows.append({
            "dc_class_id": "DC" + str(len(out_rows) + 1).zfill(5),
            "terminal_state": head["terminal_state"],
            "q_code": head["q_code"],
            "action_label": head["action_label"],
            "action_sequence_hash": head["action_sequence_hash"],
            "parameter_policy_hash": head["parameter_policy_hash"],
            "required_policy_set": head["required_policy_set"],
            "member_count": str(len(members)),
            "member_scenario_ids": ";".join(m["scenario_id"] for m in members),
            **{c: head[c] for c in NODE_COLS},
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        f"# DC Reduction Report\n\n"
        f"total_input_scenarios: {len(rows)}\n"
        f"total_dc_classes: {len(out_rows)}\n"
        f"reduction_ratio: {len(out_rows)/len(rows):.4f}\n"
        f"fatal_inconsistencies: {len(fatal)}\n\n"
        + ("## Fatal inconsistencies\n" + "\n".join(f"- {x}" for x in fatal) if fatal else
           "All DC classes are consistent.\n"),
        encoding="utf-8"
    )
    print(f"DC classes: {len(out_rows)} / {len(rows)} (ratio {len(out_rows)/len(rows):.3f}), fatal: {len(fatal)}")
    return 0 if not fatal else 1


if __name__ == "__main__":
    raise SystemExit(main())
