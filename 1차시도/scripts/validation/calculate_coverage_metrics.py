"""Compute capture / review-inclusive / operational / auto coverage
metrics on the frozen scenario universe."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(universe_csv: Path, out_md: Path) -> int:
    with universe_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    total = len(rows)
    terms = Counter(r["terminal_state"] for r in rows)
    auto = terms.get("AUTO", 0)
    repair = terms.get("REPAIR", 0)
    quar = terms.get("QUARANTINE", 0)
    unsup = terms.get("UNSUPPORTED", 0)
    inv = terms.get("INVALID", 0)

    capture_coverage = (auto + repair + quar + unsup + inv) / total if total else 0
    in_scope = total - unsup - inv
    review_inclusive = (auto + repair + quar) / in_scope if in_scope else 0
    operational = (auto + repair) / in_scope if in_scope else 0
    auto_only = auto / in_scope if in_scope else 0
    unsup_inv_rate = (unsup + inv) / total if total else 0

    q15_solo = sum(1 for r in rows if r["q_code"] == "Q15")
    q17 = sum(1 for r in rows if r["q_code"] == "Q17")
    q_missing = sum(1 for r in rows if r["terminal_state"] == "QUARANTINE" and not r["q_code"])

    lines = [
        "# Coverage Metrics — Initial",
        "",
        f"total_scenarios: {total}",
        "",
        "## Distribution",
        f"- AUTO: {auto}",
        f"- REPAIR: {repair}",
        f"- QUARANTINE: {quar}",
        f"- UNSUPPORTED: {unsup}",
        f"- INVALID: {inv}",
        "",
        "## Coverage targets",
        f"- capture_coverage: {capture_coverage:.4f}  (target ≥ 0.99)",
        f"- review_inclusive: {review_inclusive:.4f}  (target ≥ 0.95)",
        f"- operational: {operational:.4f}  (target ≥ 0.75)",
        f"- auto_only: {auto_only:.4f}  (target ≥ 0.35 — initial; will rise after action label lock)",
        f"- unsupported_invalid_rate: {unsup_inv_rate:.4f}  (target ≤ 0.05)",
        "",
        "## Hard-rule compliance",
        f"- Q15 standalone count: {q15_solo} (target 0)",
        f"- Q17 count: {q17} (target 0)",
        f"- q_code missing in QUARANTINE: {q_missing} (target 0)",
        "",
        "## Notes",
        "- false_auto_count and false_repair_count are 0 by construction at this",
        "  initial stage. Final values come after golden validation in Phase 10.",
    ]
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"capture={capture_coverage:.4f} review_inclusive={review_inclusive:.4f} operational={operational:.4f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default=ROOT / "data" / "scenario_universe" / "scenario_universe_v1.0.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "reports" / "coverage_metrics_initial.md", type=Path)
    args = parser.parse_args(argv)
    return run(args.universe, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
