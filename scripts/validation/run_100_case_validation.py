#!/usr/bin/env python3
"""Run 100-case stress test (P120).

Walks D6 for each of the 100 generated cases and compares the predicted
terminal_state / q_code against the expectations CSV.

CLI:
  python3 scripts/validation/run_100_case_validation.py \\
      --expectations data/validation/100_case_expectations.csv \\
      --tree config/operational_decision_tree.yaml \\
      --decision-table data/decision_table/reduced_decision_table_v1.0.csv \\
      --out reports/100_case_validation_results.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


def load_tree(path: Path) -> tuple[dict[str, dict], dict[str, dict], str]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    tree = raw["operational_decision_tree"]
    internal = {n["id"]: n for n in tree["internal_nodes"]}
    leaves = {l["id"]: l for l in tree["leaves"]}
    return internal, leaves, tree["root"]


def walk_tree(node_values, internal, leaves, root):
    path = []
    cur = root
    guard = 0
    while cur in internal:
        guard += 1
        if guard > 200:
            return path, {}, "walk guard exceeded"
        node = internal[cur]
        nid = node["node_id"]
        v = (node_values.get(nid) or "Y").strip()
        if v not in ("Y", "N"):
            v = "Y"
        path.append((nid, v))
        cur = node["yes_branch"] if v == "Y" else node["no_branch"]
    if cur not in leaves:
        return path, {}, f"path ends at unknown id {cur}"
    return path, leaves[cur], None


def find_representative_class(d3_classes, scenario_id, family_id, expected_terminal):
    """Find a D3 class that represents this case for routing purposes."""
    by_member = [c for c in d3_classes if scenario_id in (c.get("member_scenario_ids") or "")]
    if by_member:
        return by_member[0]
    candidates = [c for c in d3_classes
                  if family_id in c["action_label"] and c["terminal_state"] == expected_terminal]
    if candidates:
        candidates.sort(key=lambda c: c["dc_class_id"])
        return candidates[0]
    fallback = [c for c in d3_classes if family_id in c["action_label"]]
    if fallback:
        fallback.sort(key=lambda c: c["dc_class_id"])
        return fallback[0]
    return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expectations", required=True, type=Path)
    p.add_argument("--tree", required=True, type=Path)
    p.add_argument("--decision-table", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)

    expectations = list(csv.DictReader(args.expectations.open(encoding="utf-8")))
    internal, leaves, root = load_tree(args.tree)
    d3 = list(csv.DictReader(args.decision_table.open(encoding="utf-8")))

    out_rows = []
    forced_yn: dict[str, set[str]] = defaultdict(set)
    qcodes_seen: set[str] = set()

    for case in expectations:
        cid = case["case_id"]
        sid = case["scenario_id"]
        family = case["family_id"]
        exp_ts = case["expected_terminal_state"]
        exp_q = (case.get("expected_q_code") or "").strip()
        rep = find_representative_class(d3, sid, family, exp_ts)
        result = {
            "case_id": cid,
            "scenario_id": sid,
            "family_id": family,
            "expected_terminal_state": exp_ts,
            "expected_q_code": exp_q,
            "representative_dc_class": rep["dc_class_id"] if rep else "",
            "decision_path": "",
            "leaf_reached": "",
            "actual_terminal_state": "",
            "actual_q_code": "",
            "terminal_match": "N",
            "q_code_match": "N",
            "overall_status": "PENDING",
            "case_type": case.get("case_type", ""),
            "mismatch_detail": "",
        }
        if rep is None:
            result["overall_status"] = "MISMATCH"
            result["mismatch_detail"] = f"no D3 representative for family {family} / {sid}"
            out_rows.append(result)
            continue
        node_values = {f"N{i}": rep.get(f"N{i}", "") for i in range(30)}
        path, leaf, err = walk_tree(node_values, internal, leaves, root)
        if err:
            result["overall_status"] = "FAIL"
            result["mismatch_detail"] = f"walk error: {err}"
            out_rows.append(result)
            continue
        result["decision_path"] = "->".join(f"{n}={a}" for n, a in path)
        result["leaf_reached"] = leaf["id"]
        actual_ts = leaf["terminal_state"]
        actual_q = (leaf.get("q_code") or "").strip()
        result["actual_terminal_state"] = actual_ts
        result["actual_q_code"] = actual_q
        result["terminal_match"] = "Y" if actual_ts == exp_ts else "N"
        result["q_code_match"] = "Y" if actual_q == exp_q else "N"
        result["overall_status"] = "PASS" if (result["terminal_match"] == "Y" and result["q_code_match"] == "Y") else "MISMATCH"
        if result["overall_status"] != "PASS":
            result["mismatch_detail"] = (
                f"expected ({exp_ts},{exp_q!r}) actual ({actual_ts},{actual_q!r})"
            )
        # track forced-node coverage
        for nid, ans in path:
            if nid in ("N0", "N1", "N2", "N3", "N4", "N5", "N8"):
                forced_yn[nid].add(ans)
        if actual_q:
            qcodes_seen.add(actual_q)
        out_rows.append(result)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    pass_n = sum(1 for r in out_rows if r["overall_status"] == "PASS")
    mis_n = sum(1 for r in out_rows if r["overall_status"] == "MISMATCH")
    fail_n = sum(1 for r in out_rows if r["overall_status"] == "FAIL")
    rate = pass_n / len(out_rows) if out_rows else 0
    print(f"[run_100_case_validation] {args.out}")
    print(f"[run_100_case_validation] total={len(out_rows)} pass={pass_n} mismatch={mis_n} fail={fail_n} rate={rate:.1%}")
    print(f"[run_100_case_validation] forced Y∧N coverage: " +
          ", ".join(f"{n}={'YN' if forced_yn[n]>={'Y','N'} else (next(iter(forced_yn[n])) if forced_yn[n] else '-')}"
                    for n in ("N0", "N1", "N2", "N3", "N4", "N5", "N8")))
    print(f"[run_100_case_validation] Q-codes seen: {sorted(qcodes_seen)}")
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
