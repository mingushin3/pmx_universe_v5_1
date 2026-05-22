"""Verify / re-assign family_id on the scenario universe.

The generator already assigns family_id, but per the playbook this is
a separate step. This script:
  1. Reads `scenario_universe_valid_candidate.csv`.
  2. Verifies family assignment against `family_assignment_rules.yaml`.
  3. Writes `scenario_universe_with_family.csv` (identical content,
     plus a `family_assigned_at` timestamp).
  4. Emits `reports/family_coverage_summary.md`.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def run(in_csv: Path, out_csv: Path, fam_yaml: Path, report_md: Path) -> int:
    fam_doc = yaml.safe_load(fam_yaml.read_text(encoding="utf-8")) or {}
    fam_ids = {f["family_id"] for f in fam_doc["family_assignment_rules"]["families"]}

    with in_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    iso = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    for r in rows:
        if r.get("family_id", "") not in fam_ids:
            r["family_id"] = "FAMILY_UNASSIGNED"
        r["family_assigned_at"] = iso

    fields = list(rows[0].keys()) if rows else []
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    counts = Counter(r["family_id"] for r in rows)
    op_total = sum(v for k, v in counts.items()
                   if k in {f"F{i:02d}" for i in range(1, 30)})
    unassigned = counts.get("FAMILY_UNASSIGNED", 0)
    unassigned_rate = unassigned / len(rows) if rows else 0

    lines = ["# Family Coverage Summary", ""]
    lines.append(f"total_scenarios: {len(rows)}")
    lines.append(f"operational_total (F01-F29): {op_total}")
    lines.append(f"unassigned_count: {unassigned}")
    lines.append(f"unassigned_rate: {unassigned_rate:.1%}")
    lines.append("")
    lines.append("## Per-family count")
    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")
    lines.append("")
    lines.append("## v4.2 NEW families (must each be > 0)")
    for f in ("F24", "F25", "F26", "F27", "F28", "F29"):
        lines.append(f"- {f}: {counts.get(f, 0)}")
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # gate
    rc = 0
    for f in ("F24", "F25", "F26", "F27", "F28", "F29"):
        if counts.get(f, 0) == 0:
            print(f"WARN: v4.2 family {f} has 0 scenarios")
            rc = 1
    if unassigned_rate > 0.05:
        print(f"WARN: unassigned rate {unassigned_rate:.1%} > 5%")
        rc = 1
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-csv", default=ROOT / "data" / "scenario_universe" / "scenario_universe_valid_candidate.csv", type=Path)
    parser.add_argument("--fam-yaml", default=ROOT / "config" / "family_assignment_rules.yaml", type=Path)
    parser.add_argument("--out-csv", default=ROOT / "data" / "scenario_universe" / "scenario_universe_with_family.csv", type=Path)
    parser.add_argument("--report", default=ROOT / "reports" / "family_coverage_summary.md", type=Path)
    args = parser.parse_args(argv)
    return run(args.in_csv, args.out_csv, args.fam_yaml, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
