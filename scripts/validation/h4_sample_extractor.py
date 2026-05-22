#!/usr/bin/env python3
"""H4 sample extractor (P109 Task 2, PATCH-C2).

Samples 26 scenarios from the D2 locked action table:
  - 10 random AUTO
  - 10 random REPAIR
  - 1 per F24..F29 v4.2 family (skip empty families with warning)

Emits both a full set (terminal_state visible) and a blinded set
(terminal_state = "HIDDEN", q_code = "HIDDEN") for the H4 blinded
sampling audit (PATCH-5).

CLI:
  python3 scripts/validation/h4_sample_extractor.py \\
      --action-table data/action_labels/scenario_action_table_locked.csv \\
      --universe data/scenario_universe/scenario_universe_v1.0.csv \\
      --out-full reports/human_review/h4_sample_set.csv \\
      --out-blinded reports/human_review/h4_sample_blinded.csv \\
      --seed 42
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path
from typing import Any


V42_FAMILIES = ["F24", "F25", "F26", "F27", "F28", "F29"]

OUT_COLUMNS = [
    "sample_id", "scenario_id", "family_id", "terminal_state", "q_code",
    "A0_state", "A1_state", "A2_state", "A3_state", "A4_state", "A5_state",
    "A6_state", "A7_state", "A8_state", "A9_state", "A10_state",
    "modality_class", "endpoint_data_type", "analyte_role",
    "action_label", "action_sequence", "parameter_policy", "sample_type",
]


def load_d2(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_d1(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return {r["scenario_id"]: r for r in csv.DictReader(fh)}


def merge(scenario: dict[str, Any], d1: dict[str, dict[str, Any]],
          sample_id: str, sample_type: str) -> dict[str, Any]:
    """Build one output row by joining D2 row with D1 axis state."""
    sid = scenario["scenario_id"]
    d1row = d1.get(sid, {})
    return {
        "sample_id": sample_id,
        "scenario_id": sid,
        "family_id": scenario.get("family_id", ""),
        "terminal_state": scenario.get("terminal_state", ""),
        "q_code": scenario.get("q_code", ""),
        "A0_state": d1row.get("A0_state", ""),
        "A1_state": d1row.get("A1_state", ""),
        "A2_state": d1row.get("A2_state", ""),
        "A3_state": d1row.get("A3_state", ""),
        "A4_state": d1row.get("A4_state", ""),
        "A5_state": d1row.get("A5_state", ""),
        "A6_state": d1row.get("A6_state", ""),
        "A7_state": d1row.get("A7_state", ""),
        "A8_state": d1row.get("A8_state", ""),
        "A9_state": d1row.get("A9_state", ""),
        "A10_state": d1row.get("A10_state", ""),
        "modality_class": d1row.get("modality_class", ""),
        "endpoint_data_type": d1row.get("endpoint_data_type", ""),
        "analyte_role": d1row.get("analyte_role", ""),
        "action_label": scenario.get("candidate_action_label", ""),
        "action_sequence": scenario.get("action_sequence", ""),
        "parameter_policy": scenario.get("parameter_policy", ""),
        "sample_type": sample_type,
    }


def extract_samples(d2: list[dict[str, Any]], seed: int = 42) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    autos = [r for r in d2 if r["terminal_state"] == "AUTO"]
    repairs = [r for r in d2 if r["terminal_state"] == "REPAIR"]
    auto_n = min(10, len(autos))
    repair_n = min(10, len(repairs))
    auto_pick = rng.sample(autos, auto_n) if auto_n else []
    repair_pick = rng.sample(repairs, repair_n) if repair_n else []
    v42_pick: list[tuple[str, dict[str, Any]]] = []
    for f in V42_FAMILIES:
        pool = [r for r in d2 if r["family_id"] == f]
        if not pool:
            print(f"[h4_sample_extractor] WARNING: family {f} has 0 scenarios; skipped")
            continue
        v42_pick.append((f, rng.choice(pool)))
    return [
        ("AUTO_RANDOM", r) for r in auto_pick
    ] + [
        ("REPAIR_RANDOM", r) for r in repair_pick
    ] + [
        (f"V42_{f}", r) for (f, r) in v42_pick
    ]


def emit(rows: list[dict[str, Any]], out_path: Path, blinded: bool, seed: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# h4 sample (seed={seed}, blinded={blinded})\n")
        w = csv.DictWriter(fh, fieldnames=OUT_COLUMNS)
        w.writeheader()
        for r in rows:
            row = dict(r)
            if blinded:
                row["terminal_state"] = "HIDDEN"
                row["q_code"] = "HIDDEN"
            w.writerow(row)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--action-table", required=True, type=Path)
    p.add_argument("--universe",
                   default=Path("data/scenario_universe/scenario_universe_v1.0.csv"),
                   type=Path)
    p.add_argument("--out-full", required=True, type=Path)
    p.add_argument("--out-blinded", required=True, type=Path)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)

    d2 = load_d2(args.action_table)
    d1 = load_d1(args.universe)
    picks = extract_samples(d2, seed=args.seed)
    out_rows: list[dict[str, Any]] = []
    for idx, (sample_type, scenario) in enumerate(picks, start=1):
        sid = f"S{idx:02d}"
        out_rows.append(merge(scenario, d1, sid, sample_type))
    emit(out_rows, args.out_full, blinded=False, seed=args.seed)
    emit(out_rows, args.out_blinded, blinded=True, seed=args.seed)
    print(f"[h4_sample_extractor] full={args.out_full}  blinded={args.out_blinded}")
    print(f"[h4_sample_extractor] rows={len(out_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
