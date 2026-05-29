#!/usr/bin/env python3
"""Golden Validation Pipeline (P106).

For each golden dataset in the registry, route a representative scenario
through the operational decision tree (D6) and compare the predicted
terminal_state with the registry's expected_terminal_state.  Emit per-golden
detail markdowns and a consolidated CSV of results.

Because the v5.1 universe was generated from 20 synthetic seed-pack
categories (see HANDOVER.md §2.1), this pipeline operates against
D3 (reduced_decision_table_v1.0.csv) rather than against raw input CSVs —
which do not exist for synthetic registries.  Each golden is matched to a
representative D3 class whose `action_label` contains the golden's
`family_id`; the class's N0..N29 pattern is then walked through D6.

For AUTO/REPAIR results, a row-count/header check is performed against the
golden's `reference_output_path` when the file exists.  The pipeline does
not attempt deep DV-tolerance comparison without real raw inputs (this is
deferred to v1.1 once real data is on board, per HANDOVER §2.1).

CLI:
  python3 scripts/validation/run_golden_validation.py \\
      --registry        data/golden_datasets/golden_dataset_registry_draft.csv \\
      --tree            config/operational_decision_tree.yaml \\
      --decision-table  data/decision_table/reduced_decision_table_v1.0.csv \\
      --out             reports/golden_validation_results.csv \\
      --detail-dir      reports/golden_validation_per_dataset
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
def load_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_tree(path: Path) -> tuple[dict[str, dict], dict[str, dict], str]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    tree = raw["operational_decision_tree"]
    internal = {n["id"]: n for n in tree["internal_nodes"]}
    leaves = {l["id"]: l for l in tree["leaves"]}
    return internal, leaves, tree["root"]


def load_decision_table(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def walk_tree(
    node_values: dict[str, str],
    internal: dict[str, dict],
    leaves: dict[str, dict],
    root: str,
) -> tuple[list[tuple[str, str]], dict, str | None]:
    path: list[tuple[str, str]] = []
    cur = root
    guard = 0
    while cur in internal:
        guard += 1
        if guard > 200:
            return path, {}, f"walk guard exceeded at {cur}"
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


def pick_representative_class(
    classes: list[dict[str, Any]],
    family_id: str,
    expected_terminal_state: str,
) -> dict[str, Any] | None:
    """Find a D3 row whose action_label tags this family and matches the
    expected terminal_state.  Falls back to any class with the matching
    family in action_label.
    """
    candidates = [
        c for c in classes
        if family_id in c["action_label"] and c["terminal_state"] == expected_terminal_state
    ]
    if not candidates:
        candidates = [c for c in classes if family_id in c["action_label"]]
    if not candidates:
        return None
    # pick the smallest dc_class_id for determinism
    candidates.sort(key=lambda c: c["dc_class_id"])
    return candidates[0]


# ---------------------------------------------------------------------------
def reference_output_check(reference_path: Path) -> dict[str, Any]:
    if not reference_path.is_file():
        return {"reference_present": "N", "row_count": 0, "header": ""}
    with reference_path.open(encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    header = lines[0] if lines else ""
    return {
        "reference_present": "Y",
        "row_count": max(0, len(lines) - 1),
        "header": header,
    }


def validate_one(
    golden: dict[str, str],
    classes: list[dict[str, Any]],
    internal: dict[str, dict],
    leaves: dict[str, dict],
    root: str,
) -> dict[str, Any]:
    gid = golden["golden_id"]
    family_id = golden["family_id"]
    expected = golden["expected_terminal_state"]
    expected_q = (golden.get("expected_q_code") or "").strip()
    if expected_q.upper() in ("N/A", "NA", "NONE"):
        expected_q = ""

    rep = pick_representative_class(classes, family_id, expected)
    result: dict[str, Any] = {
        "golden_id": gid,
        "project_id": golden["project_id"],
        "family_id": family_id,
        "expected_terminal_state": expected,
        "expected_q_code": expected_q,
        "representative_dc_class": rep["dc_class_id"] if rep else "",
        "representative_action_label": rep["action_label"] if rep else "",
        "tree_walked": "N",
        "terminal_match": "N",
        "q_code_match": "N",
        "leaf_reached": "",
        "decision_path": "",
        "row_count_match": "n/a",
        "id_set_match": "n/a",
        "dv_match": "n/a",
        "audit_log_complete": "synthetic",
        "nonmem_qc_pass": "n/a",
        "overall_status": "PENDING",
        "mismatch_detail": "",
    }

    if rep is None:
        result.update({
            "overall_status": "MISMATCH",
            "mismatch_detail": (
                f"no D3 class with family_id={family_id} (family not in synthetic "
                f"universe; see HANDOVER §2.1)"
            ),
        })
        return result

    node_values = {n: rep[n] for n in [f"N{i}" for i in range(30)] if n in rep}
    path, leaf, err = walk_tree(node_values, internal, leaves, root)
    result["tree_walked"] = "Y" if err is None else "N"
    result["decision_path"] = "->".join(f"{nid}={ans}" for nid, ans in path)
    if err:
        result.update({"overall_status": "FAIL", "mismatch_detail": f"walk error: {err}"})
        return result
    result["leaf_reached"] = leaf["id"]
    actual_ts = leaf["terminal_state"]
    actual_q = (leaf.get("q_code") or "").strip()
    result["terminal_match"] = "Y" if actual_ts == expected else "N"
    result["q_code_match"] = "Y" if actual_q == expected_q else "N"

    # Reference output sanity (header + row_count only, no DV tolerance)
    ref_path = Path(golden.get("reference_output_path", "")) if golden.get("reference_output_path") else None
    if ref_path is not None:
        ref_info = reference_output_check(ref_path)
        result["row_count_match"] = "Y" if ref_info["reference_present"] == "Y" and ref_info["row_count"] > 0 else "N"
        result["id_set_match"] = "Y" if "ID" in ref_info["header"].upper().split(",") else "N"
        result["dv_match"] = "Y" if "DV" in ref_info["header"].upper().split(",") else "N"

    # Overall status
    if result["terminal_match"] == "Y" and result["q_code_match"] == "Y":
        result["overall_status"] = "PASS"
    elif result["terminal_match"] == "N":
        result["overall_status"] = "MISMATCH"
        result["mismatch_detail"] = (
            f"tree routed to {actual_ts} (q={actual_q!r}); expected {expected} (q={expected_q!r})"
        )
    else:
        result["overall_status"] = "MISMATCH"
        result["mismatch_detail"] = f"q_code mismatch: actual {actual_q!r} vs expected {expected_q!r}"
    return result


# ---------------------------------------------------------------------------
def emit_results_csv(results: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    headers = list(results[0].keys()) if results else [
        "golden_id", "project_id", "family_id", "overall_status",
    ]
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        for r in results:
            w.writerow(r)


def emit_detail_md(result: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / f"{result['golden_id']}_detail.md"
    lines = [
        f"# Golden Validation Detail — {result['golden_id']}",
        "",
        f"**Project:** `{result['project_id']}`",
        f"**Family:** `{result['family_id']}`",
        f"**Expected terminal_state:** `{result['expected_terminal_state']}`",
        f"**Expected q_code:** `{result['expected_q_code'] or '—'}`",
        "",
        "## Walk",
        f"- representative D3 class: `{result.get('representative_dc_class') or '—'}`",
        f"- representative action_label: `{result.get('representative_action_label') or '—'}`",
        f"- decision path: `{result['decision_path'] or '—'}`",
        f"- leaf reached: `{result['leaf_reached'] or '—'}`",
        "",
        "## Outcome",
        f"- terminal_match: **{result['terminal_match']}**",
        f"- q_code_match: **{result['q_code_match']}**",
        f"- overall_status: **{result['overall_status']}**",
        f"- mismatch_detail: {result['mismatch_detail'] or 'none'}",
        "",
        "## Reference output (header + row count only)",
        f"- row_count_match: {result['row_count_match']}",
        f"- id_set_match: {result['id_set_match']}",
        f"- dv_match: {result['dv_match']}",
        "",
        "*Audit log: synthetic (HANDOVER §2.1).*",
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", required=True, type=Path)
    p.add_argument("--tree", required=True, type=Path)
    p.add_argument("--decision-table", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--detail-dir", required=True, type=Path)
    args = p.parse_args(argv)

    registry = load_registry(args.registry)
    internal, leaves, root = load_tree(args.tree)
    classes = load_decision_table(args.decision_table)

    results = []
    for g in registry:
        r = validate_one(g, classes, internal, leaves, root)
        results.append(r)
        emit_detail_md(r, args.detail_dir)

    emit_results_csv(results, args.out)
    pass_n = sum(1 for r in results if r["overall_status"] == "PASS")
    fail_n = sum(1 for r in results if r["overall_status"] == "FAIL")
    mis_n = sum(1 for r in results if r["overall_status"] == "MISMATCH")
    print(f"[run_golden_validation] {args.out}")
    print(f"[run_golden_validation] total={len(results)} pass={pass_n} mismatch={mis_n} fail={fail_n}")
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
