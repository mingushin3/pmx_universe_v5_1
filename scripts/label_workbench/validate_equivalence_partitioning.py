"""Verify that all scenarios sharing an action_label have identical
function_name sequence + parameter_policy + terminal_state + q_code."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(in_csv: Path, after_ep_csv: Path, residual_csv: Path, report_md: Path) -> int:
    with in_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        groups[r["candidate_action_label"]].append(r)

    inconsistent: list[tuple[str, str]] = []
    for label, members in groups.items():
        if len(members) == 1:
            continue
        seqs = {m["action_sequence"] for m in members}
        ps = {m["parameter_policy"] for m in members}
        ts = {m["terminal_state"] for m in members}
        qs = {m["q_code"] for m in members}
        if len(seqs) > 1 or len(ps) > 1 or len(ts) > 1 or len(qs) > 1:
            inconsistent.append((label, f"seqs={len(seqs)} ps={len(ps)} ts={len(ts)} qs={len(qs)}"))

    after_ep_csv.parent.mkdir(parents=True, exist_ok=True)
    with in_csv.open("r", encoding="utf-8") as fi, after_ep_csv.open("w", encoding="utf-8") as fo:
        fo.write(fi.read())

    residual_csv.parent.mkdir(parents=True, exist_ok=True)
    with residual_csv.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["label", "issue"])
        wr.writerows(inconsistent)

    report_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Equivalence Partition Report",
        "",
        f"total_groups: {len(groups)}",
        f"inconsistent_groups: {len(inconsistent)}",
        "",
    ]
    if inconsistent:
        lines.append("## Inconsistent labels (need split)")
        for label, detail in inconsistent:
            lines.append(f"- {label}: {detail}")
    else:
        lines.append("All groups are EP-equivalent. No splits required.")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"groups: {len(groups)}, inconsistent: {len(inconsistent)}")
    return 0 if not inconsistent else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-csv", default=ROOT / "data" / "action_labels" / "scenario_action_table_adjudicated.csv", type=Path)
    parser.add_argument("--after-ep", default=ROOT / "data" / "action_labels" / "scenario_action_table_after_ep.csv", type=Path)
    parser.add_argument("--residual", default=ROOT / "reports" / "ep_split_residual.csv", type=Path)
    parser.add_argument("--report", default=ROOT / "reports" / "equivalence_partition_report.md", type=Path)
    args = parser.parse_args(argv)
    return run(args.in_csv, args.after_ep, args.residual, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
