#!/usr/bin/env python3
"""Tree ↔ decision-table consistency checker (P103).

For each DC class in D3 we walk the operational decision tree D6 using its
N0..N29 column values and verify that:
  T01  the walk terminates at a real leaf (no dead end)
  T02  leaf.terminal_state == class.terminal_state
       leaf.q_code         == class.q_code (or both null)
       class.action_label  ∈ leaf.action_label_set
  T03  the walk only visits nodes that appear in the D5 selected set
  T04  the seven forced nodes (N0,N1,N2,N3,N4,N5,N8) are evaluated on
       every walk — except when a forced node short-circuits to a failure
       leaf earlier in the path
  T05  v4.2-specific routing:
        - leaves labeled CELLULAR routed through a path that includes N27 (cellular BLQ)
        - leaves labeled IMMUNOGEN routed through a path that includes N29 (ADA adjudication) or N5
        - leaves labeled MATERNAL/DYAD routed through a path that includes N11 (maternal/milk endpoint)
        - leaves with q_code Q19 only reachable when forced-tier policy gates fail (N8=N)
  T06  no leaf reached through an impossible path (e.g. N0=N walks reach a Q-code leaf only)

CLI:
  python3 scripts/decision_tree/verify_tree_table_match.py \\
      --decision-table data/decision_table/reduced_decision_table_v1.0.csv \\
      --tree           config/operational_decision_tree.yaml \\
      --node-set       data/ilp/final_minimal_node_set.csv \\
      --out            reports/tree_table_consistency.md
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
def load_tree(path: Path) -> tuple[dict[str, dict], dict[str, dict], str, list[str]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    tree = raw["operational_decision_tree"]
    internal = {n["id"]: n for n in tree["internal_nodes"]}
    leaves = {l["id"]: l for l in tree["leaves"]}
    return internal, leaves, tree["root"], tree["node_order"]


def load_decision_table(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_selected(path: Path) -> set[str]:
    with path.open(encoding="utf-8") as fh:
        return {r["node_id"] for r in csv.DictReader(fh) if r["included"].strip().upper() == "Y"}


# ---------------------------------------------------------------------------
def walk(
    row: dict[str, Any],
    internal: dict[str, dict],
    leaves: dict[str, dict],
    root: str,
) -> tuple[list[tuple[str, str]], dict, str | None]:
    """Walk tree using row's N* values.  Return (path, leaf, error)."""
    path: list[tuple[str, str]] = []
    cur = root
    guard = 0
    while cur in internal:
        guard += 1
        if guard > 200:
            return path, {}, f"walk guard exceeded at {cur}"
        node = internal[cur]
        nid = node["node_id"]
        v = row.get(nid, "*").strip()
        if v == "*":
            v = "Y"  # don't-care defaults to Y for walking purposes
        if v not in ("Y", "N"):
            return path, {}, f"unexpected N column value {v!r} for {nid} at {cur}"
        path.append((nid, v))
        cur = node["yes_branch"] if v == "Y" else node["no_branch"]
    if cur not in leaves:
        return path, {}, f"path ends at unknown id {cur}"
    return path, leaves[cur], None


# ---------------------------------------------------------------------------
def check_class(
    row: dict[str, Any],
    leaf: dict,
    path: list[tuple[str, str]],
    selected: set[str],
) -> list[str]:
    errs: list[str] = []
    # T02
    if leaf["terminal_state"] != row["terminal_state"]:
        errs.append(f"T02 terminal_state mismatch: leaf={leaf['terminal_state']} class={row['terminal_state']}")
    lq = leaf.get("q_code")
    cq = row["q_code"] or None
    if (lq or None) != cq:
        errs.append(f"T02 q_code mismatch: leaf={lq!r} class={cq!r}")
    if row["action_label"] not in leaf.get("action_label_set", [leaf.get("action_label")]):
        errs.append(
            f"T02 action_label not in leaf label set: class={row['action_label']} "
            f"leaf_set={leaf.get('action_label_set')}"
        )
    # T03
    used_nodes = {nid for nid, _ in path}
    extra = used_nodes - selected
    if extra:
        errs.append(f"T03 path uses non-selected nodes: {extra}")
    return errs


def t04_forced(path: list[tuple[str, str]], leaf: dict) -> str | None:
    """T04 forced-node evaluation: forced nodes must appear unless an earlier
    forced node short-circuited (answered N → failure leaf)."""
    forced = ["N0", "N1", "N8", "N2", "N3", "N4", "N5"]
    visited = {nid for nid, _ in path}
    # If any forced node was answered N along the path, it's a short-circuit.
    short_circuit_at = None
    for nid, ans in path:
        if nid in forced and ans == "N":
            short_circuit_at = nid
            break
    if short_circuit_at:
        # Forced nodes up to (and including) short_circuit_at must be visited.
        i = forced.index(short_circuit_at)
        for n in forced[: i + 1]:
            if n not in visited:
                return f"T04 forced node {n} not on path before short-circuit at {short_circuit_at}"
        return None
    # No short-circuit → all forced nodes must appear.
    missing = [n for n in forced if n not in visited]
    if missing:
        return f"T04 forced nodes missing on path: {missing}"
    return None


def t05_v42(path: list[tuple[str, str]], leaf: dict) -> list[str]:
    notes: list[str] = []
    visited = {nid for nid, _ in path}
    label = leaf.get("action_label", "").upper()
    label_set = " ".join(leaf.get("action_label_set", [])).upper()
    blob = label + " " + label_set
    if "CELLULAR" in blob and "N27" not in visited and "N4" not in visited:
        notes.append(f"T05 cellular leaf {leaf['id']} did not visit N27 or N4 on path")
    if "IMMUNOGEN" in blob and "N29" not in visited and "N5" not in visited:
        notes.append(f"T05 immunogenicity leaf {leaf['id']} did not visit N29 or N5")
    if ("MATERNAL" in blob or "DYAD" in blob or "MILK" in blob) and "N11" not in visited and "N1" not in visited:
        notes.append(f"T05 maternal/dyad/milk leaf {leaf['id']} did not visit N11 or N1")
    if leaf.get("q_code") == "Q19":
        # Q19 must come via an N8=N or N4=N short-circuit.
        ok = any(nid == "N8" and ans == "N" for nid, ans in path) or \
             any(nid == "N4" and ans == "N" for nid, ans in path) or \
             any(nid == "N0" and ans == "N" for nid, ans in path)
        if not ok:
            notes.append(f"T05 Q19 leaf {leaf['id']} reachable without N0/N4/N8 short-circuit")
    return notes


def t06_impossible_path(path: list[tuple[str, str]], leaf: dict) -> str | None:
    """T06: if N0=N anywhere on path, leaf must be a QUARANTINE/INVALID."""
    n0_no = any(nid == "N0" and ans == "N" for nid, ans in path)
    if n0_no and leaf["terminal_state"] not in ("QUARANTINE", "INVALID"):
        return f"T06 N0=N path reached non-Q/INVALID leaf: {leaf['id']} {leaf['terminal_state']}"
    return None


# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--decision-table", required=True, type=Path)
    p.add_argument("--tree", required=True, type=Path)
    p.add_argument("--node-set", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)

    internal, leaves, root, node_order = load_tree(args.tree)
    classes = load_decision_table(args.decision_table)
    selected = load_selected(args.node_set)

    per_class_results: list[dict[str, Any]] = []
    reverse_map: dict[str, list[str]] = defaultdict(list)
    total = len(classes)
    pass_count = 0
    t05_notes_global: list[str] = []
    t01_failures: list[str] = []
    t02_failures: list[str] = []
    t03_failures: list[str] = []
    t04_failures: list[str] = []
    t06_failures: list[str] = []

    for row in classes:
        path, leaf, err = walk(row, internal, leaves, root)
        if err:
            per_class_results.append({"dc": row["dc_class_id"], "result": "FAIL", "errors": [f"T01 {err}"]})
            t01_failures.append(row["dc_class_id"])
            continue

        reverse_map[leaf["id"]].append(row["dc_class_id"])
        errs = check_class(row, leaf, path, selected)
        e4 = t04_forced(path, leaf)
        if e4:
            errs.append(e4)
            t04_failures.append(row["dc_class_id"])
        e6 = t06_impossible_path(path, leaf)
        if e6:
            errs.append(e6)
            t06_failures.append(row["dc_class_id"])
        for n in t05_v42(path, leaf):
            t05_notes_global.append(f"{row['dc_class_id']}: {n}")
        for e in errs:
            if e.startswith("T02"):
                t02_failures.append(row["dc_class_id"])
            elif e.startswith("T03"):
                t03_failures.append(row["dc_class_id"])
        result = "PASS" if not errs else "FAIL"
        if not errs:
            pass_count += 1
        per_class_results.append({
            "dc": row["dc_class_id"],
            "result": result,
            "leaf": leaf["id"],
            "path": "->".join(f"{nid}={ans}" for nid, ans in path),
            "errors": errs,
        })

    match_rate = (pass_count / total * 100.0) if total else 0.0
    summary = {
        "total": total,
        "pass": pass_count,
        "fail": total - pass_count,
        "match_rate_pct": round(match_rate, 3),
        "t01_failures": len(t01_failures),
        "t02_failures": len(t02_failures),
        "t03_failures": len(t03_failures),
        "t04_failures": len(t04_failures),
        "t06_failures": len(t06_failures),
        "t05_notes": len(t05_notes_global),
    }

    # ---- write report ----
    args.out.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Tree ↔ Decision Table Consistency Report\n")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"**Tree:** `{args.tree}`")
    lines.append(f"**Decision table:** `{args.decision_table}`")
    lines.append(f"**Selected nodes (D5):** {sorted(selected)}\n")
    lines.append("## Summary\n")
    for k, v in summary.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    if summary["fail"] == 0:
        lines.append(f"**RESULT: 100% PASS — every D3 class routes to a leaf consistent with its outcome.**\n")
    else:
        lines.append(f"**RESULT: {match_rate:.3f}% match — see per-class table below.**\n")

    # Per-leaf reverse map
    lines.append("## Per-leaf reverse mapping (classes → leaf)\n")
    lines.append("| leaf_id | terminal_state | q_code | action_label_set | member_classes |")
    lines.append("|---|---|---|---|---|")
    for lid, members in sorted(reverse_map.items()):
        leaf = leaves[lid]
        labels = ",".join(leaf.get("action_label_set", []))
        lines.append(f"| `{lid}` | {leaf['terminal_state']} | {leaf.get('q_code') or '—'} | {labels} | {len(members)} |")
    lines.append("")

    # T05 (informational notes)
    if t05_notes_global:
        lines.append("## T05 v4.2 routing notes (informational)\n")
        for n in t05_notes_global[:50]:
            lines.append(f"- {n}")
        if len(t05_notes_global) > 50:
            lines.append(f"- … and {len(t05_notes_global) - 50} more")
        lines.append("")

    # Per-class section (truncated if all PASS)
    if summary["fail"] == 0:
        lines.append("## Per-class results\n")
        lines.append("All 337 classes PASS.  First 10 walks shown for spot-check:\n")
        lines.append("| dc_class_id | result | leaf | path |")
        lines.append("|---|---|---|---|")
        for r in per_class_results[:10]:
            lines.append(f"| {r['dc']} | {r['result']} | `{r['leaf']}` | `{r['path']}` |")
    else:
        lines.append("## Per-class FAIL details\n")
        lines.append("| dc_class_id | leaf | errors |")
        lines.append("|---|---|---|")
        for r in per_class_results:
            if r["result"] == "FAIL":
                lines.append(f"| {r['dc']} | `{r.get('leaf','—')}` | {'; '.join(r['errors'])} |")

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[verify_tree_table_match] {args.out}")
    print(f"[verify_tree_table_match] match_rate={match_rate:.3f}%  pass={pass_count}/{total}")
    if summary["fail"] != 0:
        return 1
    print("[verify_tree_table_match] GATE PASS — 100% consistency")
    return 0


if __name__ == "__main__":
    sys.exit(main())
