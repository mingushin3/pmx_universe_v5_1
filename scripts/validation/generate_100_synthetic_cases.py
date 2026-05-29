#!/usr/bin/env python3
"""Generate 100 synthetic cases for post-release stress test (P119).

Cases are drawn deterministically (seed=42) from the locked D2 + D1.
Each case carries the axis state, family, expected terminal_state,
expected q_code, and a policy_variant tag.

Because no real raw inputs exist in v5.1 (HANDOVER §2.1), this generator
emits *case expectations* — not raw input CSVs.  The 100-case runner
(P120) walks D6 directly from each case's axis state and compares to
expectations.

CLI:
  python3 scripts/validation/generate_100_synthetic_cases.py \\
      --universe data/scenario_universe/scenario_universe_v1.0.csv \\
      --action-table data/action_labels/scenario_action_table_locked.csv \\
      --out data/validation/100_case_expectations.csv \\
      --seed 42
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


# Allocation per playbook P118 (illustrative; subject to per-family availability)
ROUTINE_FAMILIES = ["F01", "F15", "F19", "F22"]
V42_FAMILIES = ["F24", "F25", "F26", "F27", "F28", "F29"]
UNSUPPORTED_FAMILIES = ["F34"]

TARGET_ROUTINE = 65   # combined across routine families
TARGET_V42 = 28       # combined across v4.2 families
TARGET_FORCED_COVERAGE = 7  # one per forced node = N path where universe contains it
TOTAL_TARGET = TARGET_ROUTINE + TARGET_V42 + TARGET_FORCED_COVERAGE  # = 100


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def assign_policy_variant(family: str, terminal_state: str, q_code: str, rng: random.Random) -> str:
    if family in V42_FAMILIES:
        # half present, half absent
        return rng.choice(["present", "absent"])
    if terminal_state == "QUARANTINE":
        return "absent"
    return "n.a."


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--universe", required=True, type=Path)
    p.add_argument("--action-table", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)

    rng = random.Random(args.seed)
    universe = load(args.universe)
    action_table = {r["scenario_id"]: r for r in load(args.action_table)}

    # Group by family
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in universe:
        by_family[r["family_id"]].append(r)

    def allocate(avail: dict[str, int], target: int, floor: int = 0) -> dict[str, int]:
        """Largest-remainder proportional allocation, with optional per-family floor."""
        total = sum(avail.values()) or 1
        raw = {f: target * n / total for f, n in avail.items()}
        floors = {f: max(min(int(raw[f]), avail[f]), min(floor, avail[f])) for f in avail}
        remaining = target - sum(floors.values())
        # distribute remaining by largest fractional remainder, capped by availability
        remainders = sorted(avail.keys(), key=lambda f: (raw[f] - int(raw[f])), reverse=True)
        idx = 0
        guard = 0
        while remaining > 0 and guard < 10000:
            guard += 1
            f = remainders[idx % len(remainders)]
            if floors[f] < avail[f]:
                floors[f] += 1
                remaining -= 1
            idx += 1
        # if oversubscribed, trim from lowest fractional first
        if remaining < 0:
            for f in reversed(remainders):
                while remaining < 0 and floors[f] > min(floor, avail[f]):
                    floors[f] -= 1
                    remaining += 1
                if remaining >= 0:
                    break
        return floors

    selected: list[tuple[dict[str, Any], str]] = []

    # Routine target = 70 across F01, F15, F19, F22
    routine_avail = {f: len(by_family.get(f, [])) for f in ROUTINE_FAMILIES if by_family.get(f)}
    routine_alloc = allocate(routine_avail, TARGET_ROUTINE, floor=0)
    for f, n in routine_alloc.items():
        for r in rng.sample(by_family[f], n):
            selected.append((r, "ROUTINE"))

    # v4.2 target = 30 across F24..F29, with floor=3 per family that has ≥3
    v42_avail = {f: len(by_family.get(f, [])) for f in V42_FAMILIES if by_family.get(f)}
    v42_alloc = allocate(v42_avail, TARGET_V42, floor=3)
    for f, n in v42_alloc.items():
        for r in rng.sample(by_family[f], n):
            selected.append((r, "V42"))

    # Forced-coverage cases — drive each forced node = N at least once when the
    # universe contains a scenario for that q_code path.
    # Mapping: q_code → forced node that fails to produce it.
    forced_qcode_targets = [
        ("Q11", "N0"),    # AIC-MISSING
        ("Q03", "N1"),    # ID/dyad — may be absent in universe
        ("Q02", "N2"),    # TIME
        ("Q08", "N3"),    # DOSE — may be absent
        ("Q15A", "N4"),   # OBS / CMT
        ("Q01", "N5"),    # BLQ
        ("Q18", "N1"),    # DYAD MISSING (N1 alt) — picks Q18 if Q03 absent
    ]
    used_sids = {s["scenario_id"] for s, _ in selected}
    forced_selected: list[tuple[dict[str, Any], str]] = []
    covered_forced_n: set[str] = set()
    for qcode, node in forced_qcode_targets:
        pool = [r for r in universe if r.get("q_code") == qcode and r["scenario_id"] not in used_sids]
        if not pool:
            continue
        rep = rng.choice(pool)
        forced_selected.append((rep, f"FORCED_{node}_N_{qcode}"))
        used_sids.add(rep["scenario_id"])
        covered_forced_n.add(node)
        if len(forced_selected) >= TARGET_FORCED_COVERAGE:
            break

    selected_pairs = selected + forced_selected
    if len(selected_pairs) > TOTAL_TARGET:
        selected_pairs = selected_pairs[:TOTAL_TARGET]
    if len(selected_pairs) < TOTAL_TARGET:
        all_pool = sum((by_family[f] for f in ROUTINE_FAMILIES if by_family.get(f)), [])
        used = {s["scenario_id"] for s, _ in selected_pairs}
        extras = [r for r in all_pool if r["scenario_id"] not in used]
        rng.shuffle(extras)
        need = TOTAL_TARGET - len(selected_pairs)
        for r in extras[:need]:
            selected_pairs.append((r, "ROUTINE_FILL"))

    # Emit
    args.out.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "case_id", "scenario_id", "family_id", "modality_class",
        "endpoint_data_type", "analyte_role",
        "A0_state", "A1_state", "A2_state", "A3_state", "A4_state", "A5_state",
        "A6_state", "A7_state", "A8_state", "A9_state", "A10_state",
        "expected_terminal_state", "expected_q_code",
        "expected_action_label", "expected_action_sequence",
        "policy_variant", "case_type",
    ]
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        for idx, (r, ct) in enumerate(selected_pairs, start=1):
            sid = r["scenario_id"]
            d2 = action_table.get(sid, {})
            row = {
                "case_id": f"C{idx:03d}",
                "scenario_id": sid,
                "family_id": r["family_id"],
                "modality_class": r.get("modality_class", ""),
                "endpoint_data_type": r.get("endpoint_data_type", ""),
                "analyte_role": r.get("analyte_role", ""),
                "A0_state": r.get("A0_state", ""),
                "A1_state": r.get("A1_state", ""),
                "A2_state": r.get("A2_state", ""),
                "A3_state": r.get("A3_state", ""),
                "A4_state": r.get("A4_state", ""),
                "A5_state": r.get("A5_state", ""),
                "A6_state": r.get("A6_state", ""),
                "A7_state": r.get("A7_state", ""),
                "A8_state": r.get("A8_state", ""),
                "A9_state": r.get("A9_state", ""),
                "A10_state": r.get("A10_state", ""),
                "expected_terminal_state": r.get("terminal_state", ""),
                "expected_q_code": r.get("q_code", ""),
                "expected_action_label": d2.get("candidate_action_label", ""),
                "expected_action_sequence": d2.get("action_sequence", ""),
                "policy_variant": assign_policy_variant(r["family_id"], r["terminal_state"], r["q_code"], rng),
                "case_type": ct,
            }
            w.writerow(row)

    print(f"[generate_100_synthetic_cases] {args.out}  rows={len(selected_pairs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
