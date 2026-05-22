#!/usr/bin/env python3
"""Build the operational decision tree (D6) from D3 + D5.

Phase 9 / P102.  See reports/decision_tree_construction_plan.md for the design.

CLI:
  python3 scripts/decision_tree/build_decision_tree.py \\
      --decision-table data/decision_table/reduced_decision_table_v1.0.csv \\
      --node-set       data/ilp/final_minimal_node_set.csv \\
      --action-labels  config/action_label_dictionary_v1_0.yaml \\
      --node-dict      config/candidate_node_dictionary_with_costs.csv \\
      --out            config/operational_decision_tree.yaml
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Fixed ordering from P101
# ---------------------------------------------------------------------------
FORCED_ORDER = ["N0", "N1", "N8", "N2", "N3", "N4", "N5"]
OPTIONAL_ORDER = [
    "N14", "N13", "N19", "N21", "N22", "N24", "N25",
    "N11", "N17", "N20", "N27", "N29",
]
DEFAULT_NODE_ORDER = FORCED_ORDER + OPTIONAL_ORDER

CORE_FUNCTIONS = {
    "parse_source", "assign_evid", "sort_records",
    "export_nonmem_ready", "flag_quarantine", "flag_invalid",
}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_decision_table(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise RuntimeError(f"empty decision table: {path}")
    return rows


def load_node_set(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    selected = [r["node_id"] for r in rows if r["included"].strip().upper() == "Y"]
    if not selected:
        raise RuntimeError(f"no selected nodes in {path}")
    return selected


def load_action_labels(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data["action_label_dictionary"]["labels"]


def load_node_dictionary(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["node_id"]] = row
    return out


def load_repair_function_names() -> set[str]:
    """Repair-class functions are non-core functions from action_function_library."""
    lib_path = Path("config/action_function_library.yaml")
    if not lib_path.is_file():
        return set()
    data = yaml.safe_load(lib_path.read_text(encoding="utf-8"))
    funcs = data["action_function_library"]["functions"]
    names = []
    if isinstance(funcs, dict):
        names = list(funcs.keys())
    else:
        for f in funcs:
            names.append(f.get("function_name") or f.get("name"))
    return {n for n in names if n and n not in CORE_FUNCTIONS}


# ---------------------------------------------------------------------------
# Tree construction
# ---------------------------------------------------------------------------
def resolve_node_order(selected: list[str], default_order: list[str]) -> list[str]:
    selected_set = set(selected)
    ordered = [n for n in default_order if n in selected_set]
    leftover = sorted(selected_set - set(ordered))
    return ordered + leftover


def class_outcome(row: dict[str, Any]) -> tuple[str, str, str]:
    """Behavioral outcome key — what the ILP actually distinguishes.

    The 19-node ILP-selected set distinguishes every pair of D3 classes whose
    `(terminal_state, q_code, action_sequence_hash)` differs.  It does NOT
    distinguish `parameter_policy_hash` differences within the same plan —
    those are AIC-declared metadata, not data-fingerprint discriminable, so
    they are read directly from the AIC at leaf execution time rather than
    branched on in the tree.  Likewise `action_label` is a family-tagged
    alias for the same plan (e.g. REPAIR_F22_BLQ_DDIVP and
    REPAIR_F27_BLQ_DDIVP share one plan/leaf).
    """
    return (
        row["terminal_state"],
        row["q_code"],
        row["action_sequence_hash"],
    )


def build_tree(
    classes: list[dict[str, Any]],
    nodes: list[str],
    forced_set: set[str],
    node_dict: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return a tree dict.  Leaves: {"kind":"leaf", "outcome": (...), "member_classes":[...]}.
    Internal: {"kind":"internal", "node_id":n, "yes":subtree, "no":subtree}.

    Forced nodes are always emitted as internal nodes (even when they do not
    split the remaining classes) so every operational walk evaluates them.
    Their degenerate branch routes to a synthetic forced-failure leaf derived
    from the candidate_node_dictionary's `q_code_if_fail` column.
    """
    if not classes:
        raise RuntimeError("empty subtree — unreachable region in D3 partition")

    outcomes = {class_outcome(c) for c in classes}
    # Terminal-collapse only if no forced nodes remain to evaluate.
    remaining_forced = [n for n in nodes if n in forced_set]
    if len(outcomes) == 1 and not remaining_forced:
        outcome = outcomes.pop()
        return {
            "kind": "leaf",
            "outcome": outcome,
            "member_classes": [c["dc_class_id"] for c in classes],
        }

    if not nodes:
        if len(outcomes) > 1:
            raise RuntimeError(
                f"selected node set under-distinguishes outcomes: {outcomes} "
                f"on classes {[c['dc_class_id'] for c in classes]}"
            )
        outcome = outcomes.pop()
        return {
            "kind": "leaf",
            "outcome": outcome,
            "member_classes": [c["dc_class_id"] for c in classes],
        }

    n = nodes[0]
    rest = nodes[1:]
    Y, N = [], []
    for c in classes:
        v = c.get(n, "*").strip()
        if v == "Y":
            Y.append(c)
        elif v == "N":
            N.append(c)
        elif v == "*":
            Y.append(c)
            N.append(c)
        else:
            raise RuntimeError(f"unexpected value {v!r} for node {n} in {c['dc_class_id']}")

    is_forced = n in forced_set
    if not Y or not N:
        if not is_forced:
            # optional node that doesn't split — skip it
            return build_tree(classes, rest, forced_set, node_dict)
        # forced node, degenerate: emit anyway with synthetic failure leaf on empty branch
        fail_leaf = _synthetic_forced_fail_leaf(n, node_dict)
        if not N:  # all Y; failure branch = synthetic
            return {
                "kind": "internal",
                "node_id": n,
                "yes": build_tree(Y, rest, forced_set, node_dict),
                "no": fail_leaf,
            }
        # not Y; everyone failed this gate
        return {
            "kind": "internal",
            "node_id": n,
            "yes": fail_leaf,  # would have been the success path; here empty
            "no": build_tree(N, rest, forced_set, node_dict),
        }

    return {
        "kind": "internal",
        "node_id": n,
        "yes": build_tree(Y, rest, forced_set, node_dict),
        "no": build_tree(N, rest, forced_set, node_dict),
    }


_N8_FALLBACK_QCODE = "Q15A"  # AIC-policy incomplete → maps to data-package incomplete

def _synthetic_forced_fail_leaf(node_id: str, node_dict: dict[str, dict[str, Any]]) -> dict[str, Any]:
    info = node_dict.get(node_id, {})
    qcode = (info.get("q_code_if_fail") or "").strip()
    # N8 carries placeholder "(Q-code per policy)" — normalize to Q15A.
    if not qcode or qcode.startswith("("):
        qcode = _N8_FALLBACK_QCODE if node_id == "N8" else "Q11"
    terminal = (info.get("terminal_if_fail") or "QUARANTINE").strip()
    synth_hash = f"forced_fail_{node_id}".ljust(12, "0")[:12]
    return {
        "kind": "leaf",
        "outcome": (terminal, qcode, synth_hash),
        "member_classes": [],
        "synthetic_forced_failure_for": node_id,
        "synthetic_q_code": qcode,
        "synthetic_terminal_state": terminal,
    }


# ---------------------------------------------------------------------------
# YAML serialization
# ---------------------------------------------------------------------------
def leaf_id_for(outcome: tuple[str, str, str]) -> str:
    terminal_state, q_code, as_hash = outcome
    return f"leaf_{terminal_state}_{q_code or 'NA'}_{as_hash[:8]}"


def collect_leaves(tree: dict[str, Any], out: dict[str, dict[str, Any]]) -> str:
    """Walk tree, populate out[leaf_id] with leaf descriptor, return leaf_id reference."""
    if tree["kind"] == "leaf":
        lid = leaf_id_for(tree["outcome"])
        if lid not in out:
            out[lid] = {
                "id": lid,
                "outcome": tree["outcome"],
                "member_classes": [],
                "synthetic_forced_failure_for": tree.get("synthetic_forced_failure_for"),
            }
        out[lid]["member_classes"].extend(tree["member_classes"])
        # If two paths reach the same synthetic id, keep the marker.
        if tree.get("synthetic_forced_failure_for") and not out[lid].get("synthetic_forced_failure_for"):
            out[lid]["synthetic_forced_failure_for"] = tree["synthetic_forced_failure_for"]
        return lid
    yid = collect_leaves(tree["yes"], out)
    nid = collect_leaves(tree["no"], out)
    return f"internal::{tree['node_id']}"


def collect_internal_nodes(
    tree: dict[str, Any],
    out: list[dict[str, Any]],
    seen: set[str],
    node_dict: dict[str, dict[str, Any]],
    leaves: dict[str, dict[str, Any]],
) -> str:
    """Emit internal nodes in pre-order with stable ids; return root ref id."""
    if tree["kind"] == "leaf":
        return leaf_id_for(tree["outcome"])
    n = tree["node_id"]
    base = f"tree_{n}"
    tid = base
    i = 1
    while tid in seen:
        i += 1
        tid = f"{base}_v{i}"
    seen.add(tid)
    yes_ref = collect_internal_nodes(tree["yes"], out, seen, node_dict, leaves)
    no_ref = collect_internal_nodes(tree["no"], out, seen, node_dict, leaves)
    out.append({
        "id": tid,
        "node_id": n,
        "question": node_dict.get(n, {}).get("question", ""),
        "detection_rule": node_dict.get(n, {}).get("detection_rule", ""),
        "yes_branch": yes_ref,
        "no_branch": no_ref,
    })
    return tid


def family_examples_for(action_label: str, scenario_table: Path) -> list[str]:
    fams: set[str] = set()
    if not scenario_table.is_file():
        return []
    with scenario_table.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("action_label") == action_label:
                fid = row.get("family_id")
                if fid:
                    fams.add(fid)
    return sorted(fams)


# ---------------------------------------------------------------------------
# YAML emission
# ---------------------------------------------------------------------------
class IndentDumper(yaml.SafeDumper):
    """Slightly nicer YAML indentation for lists under mappings."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:  # noqa: D401
        return super().increase_indent(flow, False)


def _represent_ordereddict(dumper: yaml.SafeDumper, data: OrderedDict) -> Any:
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


IndentDumper.add_representer(OrderedDict, _represent_ordereddict)


def emit_yaml(tree_doc: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.dump(
        tree_doc,
        Dumper=IndentDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=120,
    )
    out_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_tree(
    tree_doc: dict[str, Any],
    selected_nodes: list[str],
    repair_fns: set[str],
) -> list[str]:
    errs: list[str] = []
    tree = tree_doc["operational_decision_tree"]

    # forced nodes present
    forced = {"N0", "N1", "N2", "N3", "N4", "N5", "N8"}
    order = set(tree["node_order"])
    if not forced.issubset(order):
        errs.append(f"forced nodes missing from node_order: {forced - order}")

    # no Q17, no Q15-solo, AUTO → export_nonmem_ready, REPAIR → ≥1 repair fn
    auto_no_export = []
    repair_no_repair = []
    q15_solo = []
    q17 = []
    leaves = tree["leaves"]
    for leaf in leaves:
        q = leaf.get("q_code")
        ts = leaf["terminal_state"]
        seq = leaf.get("action_sequence", []) or []
        if q == "Q17":
            q17.append(leaf["id"])
        if q == "Q15":  # standalone Q15 (not Q15A/Q15B) is forbidden
            q15_solo.append(leaf["id"])
        if ts == "AUTO" and "export_nonmem_ready" not in seq:
            auto_no_export.append(leaf["id"])
        if ts == "REPAIR" and not (set(seq) & repair_fns):
            repair_no_repair.append(leaf["id"])

    if q17:
        errs.append(f"Q17 leaves found: {q17}")
    if q15_solo:
        errs.append(f"Q15-solo leaves found: {q15_solo}")
    if auto_no_export:
        errs.append(f"AUTO leaves missing export_nonmem_ready: {auto_no_export}")
    if repair_no_repair:
        errs.append(f"REPAIR leaves with no repair-class function: {repair_no_repair}")

    # excluded nodes must not appear
    used_nodes = {n["node_id"] for n in tree["internal_nodes"]}
    excluded = used_nodes - set(selected_nodes)
    if excluded:
        errs.append(f"internal_nodes references excluded nodes: {excluded}")

    # terminal_states from D3 should all be reachable as leaves
    reached_ts = {leaf["terminal_state"] for leaf in leaves}
    needed_ts = {"AUTO", "REPAIR", "QUARANTINE", "INVALID"}
    missing_ts = needed_ts - reached_ts
    if missing_ts:
        errs.append(f"terminal_states unreachable: {missing_ts}")

    # v4.2 leaf-pattern coverage (warning, not hard error)
    labels = " ".join(str(l.get("action_label", "")) for l in leaves).upper()
    soft_warnings = []
    for kw in ["CELLULAR", "IMMUNOGEN", "MATERNAL", "DYAD", "MILK"]:
        if kw not in labels:
            soft_warnings.append(f"v4.2 leaf pattern '{kw}' not present")
    # surface as informational
    if soft_warnings:
        tree_doc.setdefault("_soft_warnings", []).extend(soft_warnings)

    return errs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--decision-table", required=True, type=Path)
    p.add_argument("--node-set", required=True, type=Path)
    p.add_argument("--action-labels", required=True, type=Path)
    p.add_argument("--node-dict", required=True, type=Path)
    p.add_argument("--scenario-table",
                   default=Path("data/action_labels/scenario_action_table_locked.csv"),
                   type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)

    classes = load_decision_table(args.decision_table)
    selected = load_node_set(args.node_set)
    action_labels = load_action_labels(args.action_labels)
    node_dict = load_node_dictionary(args.node_dict)
    repair_fns = load_repair_function_names()

    node_order = resolve_node_order(selected, DEFAULT_NODE_ORDER)
    forced_set = set(FORCED_ORDER)
    print(f"[build_decision_tree] D3 classes: {len(classes)}")
    print(f"[build_decision_tree] selected nodes ({len(selected)}): {selected}")
    print(f"[build_decision_tree] resolved order: {node_order}")

    tree = build_tree(classes, node_order, forced_set, node_dict)

    # Collect leaves and internal nodes
    leaf_specs: dict[str, dict[str, Any]] = {}
    collect_leaves(tree, leaf_specs)
    internal: list[dict[str, Any]] = []
    root_ref = collect_internal_nodes(tree, internal, set(), node_dict, leaf_specs)

    # Build per-DC class → action_label lookup for leaf assembly.
    class_label: dict[str, str] = {c["dc_class_id"]: c["action_label"] for c in classes}

    # Build leaf entries.  A leaf can carry multiple action_labels (same
    # executable plan, different source-family tags) and multiple
    # parameter_policy_hashes (same plan, AIC declares concrete policy at runtime).
    class_pp_hash: dict[str, str] = {c["dc_class_id"]: c["parameter_policy_hash"] for c in classes}
    leaves_out: list[dict[str, Any]] = []
    for lid, spec in leaf_specs.items():
        ts, q, as_hash = spec["outcome"]
        members = sorted(set(spec["member_classes"]))
        synth_node = spec.get("synthetic_forced_failure_for")
        if synth_node:
            # Synthetic leaf for a forced-node degenerate failure path
            leaves_out.append({
                "id": lid,
                "terminal_state": ts,
                "q_code": q if q else None,
                "action_label": f"FORCED_FAIL_{synth_node}_{q or 'NA'}",
                "action_label_set": [f"FORCED_FAIL_{synth_node}_{q or 'NA'}"],
                "action_sequence_hash": as_hash,
                "parameter_policy_hashes": [],
                "action_sequence": ["parse_source", "flag_quarantine"]
                                    if ts == "QUARANTINE" else ["parse_source", "flag_invalid"],
                "parameter_policy": {"q_code": q} if q else {},
                "family_id_examples": [],
                "member_classes": [],
                "member_class_count": 0,
                "synthetic_forced_failure_for": synth_node,
                "note": (
                    f"Synthetic leaf for {synth_node}=N. Not present in D3 "
                    f"(no scenario in the universe failed this gate after earlier ones passed), "
                    f"but emitted so the tree always evaluates {synth_node} for new inputs."
                ),
            })
            continue
        labels_set = sorted({class_label[m] for m in members})
        pp_hashes = sorted({class_pp_hash[m] for m in members})
        rep_label = labels_set[0]
        ald_entry = action_labels.get(rep_label, {})
        seq = ald_entry.get("action_sequence", [])
        pp = ald_entry.get("parameter_policy", {})
        fam_examples = sorted({
            f for lbl in labels_set
            for f in family_examples_for(lbl, args.scenario_table)
        })
        leaves_out.append({
            "id": lid,
            "terminal_state": ts,
            "q_code": q if q else None,
            "action_label": rep_label,
            "action_label_set": labels_set,
            "action_sequence_hash": as_hash,
            "parameter_policy_hashes": pp_hashes,
            "action_sequence": seq,
            "parameter_policy": pp,
            "family_id_examples": fam_examples,
            "member_classes": members,
            "member_class_count": len(members),
        })
    leaves_out.sort(key=lambda x: x["id"])

    # Sort internal nodes by node_order position (then by id) for stable output
    pos = {n: i for i, n in enumerate(node_order)}
    internal.sort(key=lambda n: (pos.get(n["node_id"], 999), n["id"]))

    timestamp_iso = datetime.now(timezone.utc).isoformat()

    tree_doc: dict[str, Any] = OrderedDict()
    tree_doc["operational_decision_tree"] = OrderedDict([
        ("version", "v1.0"),
        ("generated_at_utc", timestamp_iso),
        ("source_decision_table", str(args.decision_table)),
        ("source_node_set", str(args.node_set)),
        ("node_order", node_order),
        ("forced_nodes", FORCED_ORDER),
        ("optional_nodes", [n for n in node_order if n in OPTIONAL_ORDER]),
        ("root", root_ref),
        ("internal_nodes", internal),
        ("leaves", leaves_out),
        ("audit_log_template", {
            "fields": [
                "decision_path",
                "terminal_state",
                "q_code",
                "action_sequence_executed",
                "parameter_policies",
                "timestamp_iso",
                "input_data_summary",
                "row_counts_before_after",
                "operator",
                "aic_hash",
            ],
            "decision_path_format": "list of (node_id, answer) tuples in evaluation order",
            "input_data_summary_keys": ["row_count", "columns_used", "fingerprint_sha256"],
            "emit_one_per": "AUTO/REPAIR invocation; written next to NONMEM-ready CSV",
        }),
        ("statistics", {
            "internal_node_count": len(internal),
            "leaf_count": len(leaves_out),
            "terminal_state_counts": _terminal_counts(leaves_out),
            "covered_d3_classes": sum(l["member_class_count"] for l in leaves_out),
            "source_d3_class_count": len(classes),
        }),
    ])

    errs = validate_tree(dict(tree_doc), selected, repair_fns)

    soft_warnings = tree_doc["operational_decision_tree"].pop("_soft_warnings", None) \
        if isinstance(tree_doc["operational_decision_tree"], dict) else None
    if soft_warnings:
        print("[build_decision_tree] soft warnings:")
        for w in soft_warnings:
            print(f"  ⚠️  {w}")
            tree_doc["operational_decision_tree"].setdefault("soft_warnings", []).append(w)

    if errs:
        print("[build_decision_tree] VALIDATION FAILED:")
        for e in errs:
            print(f"  ❌ {e}")
        return 2

    emit_yaml(tree_doc, args.out)
    print(f"[build_decision_tree] wrote {args.out}")
    print(f"[build_decision_tree] internal_nodes={len(internal)}  leaves={len(leaves_out)}")
    return 0


def _terminal_counts(leaves: list[dict[str, Any]]) -> dict[str, int]:
    c: dict[str, int] = defaultdict(int)
    for l in leaves:
        c[l["terminal_state"]] += 1
    return dict(sorted(c.items()))


if __name__ == "__main__":
    sys.exit(main())
