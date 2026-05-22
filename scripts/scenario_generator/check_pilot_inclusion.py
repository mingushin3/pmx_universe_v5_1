"""Verify each pilot fingerprint is representable in the generated universe.

Also emits seed-pack coverage report for the universe (v5.1 NEW).
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


AXIS_COLS = [f"A{i}_state" for i in range(11)]


def _key(row: dict[str, str]) -> tuple:
    return tuple(row[c] for c in AXIS_COLS + ["modality_class", "endpoint_data_type"])


def run(universe_csv: Path, pilot_csv: Path, out_md: Path,
        failures_csv: Path, seed_md: Path) -> int:
    with universe_csv.open("r", encoding="utf-8", newline="") as f:
        universe = list(csv.DictReader(f))
    with pilot_csv.open("r", encoding="utf-8", newline="") as f:
        pilots = list(csv.DictReader(f))

    universe_index: dict[tuple, dict[str, str]] = {}
    for r in universe:
        universe_index[_key(r)] = r

    failures: list[dict[str, str]] = []
    seed_status: dict[str, tuple[bool, str]] = {}
    for fp in pilots:
        if not any(fp[c] for c in AXIS_COLS):
            continue
        key = _key(fp)
        sid = fp.get("seed_category_id", "")
        found = universe_index.get(key)
        if found is None:
            failures.append({
                "project_id": fp["project_id"],
                "seed_category_id": sid,
                "axes": "|".join(fp[c] for c in AXIS_COLS),
                "cause": "universe_gap",
                "expected_terminal": fp.get("expected_terminal_state", ""),
                "expected_q_code": fp.get("expected_q_code", ""),
            })
            seed_status[sid] = (False, "MISSING")
        else:
            term_ok = found["terminal_state"] == fp.get("expected_terminal_state", "")
            q_ok = (found["q_code"] or "") == (fp.get("expected_q_code", "") if fp.get("expected_q_code") not in {"N/A", ""} else "")
            if not term_ok:
                failures.append({
                    "project_id": fp["project_id"],
                    "seed_category_id": sid,
                    "axes": "|".join(fp[c] for c in AXIS_COLS),
                    "cause": "terminal_mismatch",
                    "expected_terminal": fp.get("expected_terminal_state", ""),
                    "actual_terminal": found["terminal_state"],
                })
                seed_status[sid] = (True, "TERMINAL_MISMATCH")
            else:
                seed_status[sid] = (True, "COVERED")

    # operational failures (excluding F31-F34 intentional)
    operational_failures = [f for f in failures
                            if f["cause"] != "f24_f27_intentional"]

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(_render_md(pilots, failures), encoding="utf-8")
    failures_csv.parent.mkdir(parents=True, exist_ok=True)
    with failures_csv.open("w", encoding="utf-8", newline="") as f:
        if failures:
            w = csv.DictWriter(f, fieldnames=list(failures[0].keys()))
            w.writeheader()
            w.writerows(failures)
        else:
            w = csv.writer(f)
            w.writerow(["project_id", "seed_category_id", "cause"])

    # seed-pack universe coverage
    seed_md.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Seed Pack Universe Coverage v5.1", "",
             "| seed_category_id | universe_representation | match_status |", "|---|---|---|"]
    for sid_int in range(1, 21):
        sid = str(sid_int)
        if sid in seed_status:
            present, status = seed_status[sid]
            lines.append(f"| {sid} | YES | {status} |")
        else:
            lines.append(f"| {sid} | NO | MISSING |")
    lines.append("")
    op_count = sum(1 for s, (p, _) in seed_status.items() if p)
    lines.append(f"covered_in_universe: {op_count}/20")
    seed_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return 0 if not operational_failures else 1


def _render_md(pilots: list[dict[str, str]], failures: list[dict]) -> str:
    lines = [
        "# Pilot Inclusion Check",
        "",
        f"total_pilots: {len(pilots)}",
        f"failures: {len(failures)}",
        "",
    ]
    if failures:
        lines.append("## Failures")
        for f in failures:
            lines.append(f"- {f['project_id']} (seed {f['seed_category_id']}): {f['cause']}")
    else:
        lines.append("All pilot fingerprints representable in current universe.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default=ROOT / "data" / "scenario_universe" / "scenario_universe_with_family.csv", type=Path)
    parser.add_argument("--pilot", default=ROOT / "data" / "pilot_fingerprints" / "empirical_fingerprints_pilot.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "reports" / "pilot_inclusion_check.md", type=Path)
    parser.add_argument("--failures", default=ROOT / "reports" / "pilot_inclusion_failures.csv", type=Path)
    parser.add_argument("--seed-out", default=ROOT / "reports" / "seed_pack_universe_coverage.md", type=Path)
    args = parser.parse_args(argv)
    return run(args.universe, args.pilot, args.out, args.failures, args.seed_out)


if __name__ == "__main__":
    raise SystemExit(main())
