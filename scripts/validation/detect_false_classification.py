#!/usr/bin/env python3
"""Detect candidate false AUTO / false REPAIR scenarios (P109 Task 1).

Heuristics:
- false AUTO candidate: a scenario labelled AUTO whose action_sequence
  contains any function that requires a parameter_policy.  AUTO should
  have *no* policy-bearing functions; if it does, the AIC must declare
  that policy → really REPAIR.
- false REPAIR candidate: a scenario labelled REPAIR but the scenario's
  required_policy_set is non-empty AND its action_sequence does NOT
  contain the corresponding repair function → really QUARANTINE.

Outputs:
- reports/false_classification_candidates.csv (CSV with priority, confidence,
  suspected_label)

This pipeline operates against D2 (action labels locked) and golden
validation results (post-H3) for cross-evidence.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
def load_action_function_library(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    funcs = data["action_function_library"]["functions"]
    if isinstance(funcs, list):
        return {f.get("function_name") or f.get("name"): f for f in funcs}
    return funcs


def parse_action_sequence(raw: str) -> list[str]:
    if not raw:
        return []
    # action_sequence may be JSON-ish list, semicolon-separated, or comma-separated
    s = raw.strip()
    if s.startswith("[") and s.endswith("]"):
        # crude parse: strip brackets, split commas, strip quotes/whitespace
        body = s[1:-1]
        return [x.strip().strip("'").strip('"') for x in body.split(",") if x.strip()]
    if ";" in s:
        return [x.strip() for x in s.split(";") if x.strip()]
    return [x.strip() for x in s.split(",") if x.strip()]


def function_requires_policy(fn_name: str, funcs: dict[str, dict[str, Any]]) -> bool:
    f = funcs.get(fn_name)
    if not f:
        return False
    req = f.get("required_policy")
    if req is None or req == [] or req == "" or req == "none":
        return False
    return True


# ---------------------------------------------------------------------------
def detect(
    action_table_path: Path,
    func_lib_path: Path,
    validation_results_path: Path | None,
) -> list[dict[str, str]]:
    with action_table_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    funcs = load_action_function_library(func_lib_path)

    # Cross-evidence from golden validation
    golden_flagged: set[str] = set()
    if validation_results_path and validation_results_path.is_file():
        with validation_results_path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("overall_status") in ("MISMATCH", "FAIL") and r.get("terminal_match") == "N":
                    # mark all scenarios in that family as evidence-flagged
                    fam = r.get("family_id", "")
                    if fam:
                        golden_flagged.add(fam)

    candidates: list[dict[str, str]] = []
    for r in rows:
        ts = r["terminal_state"]
        if ts not in ("AUTO", "REPAIR"):
            continue
        seq = parse_action_sequence(r.get("action_sequence", ""))
        if ts == "AUTO":
            policy_funcs = [fn for fn in seq if function_requires_policy(fn, funcs)]
            if policy_funcs:
                candidates.append({
                    "scenario_id": r["scenario_id"],
                    "family_id": r["family_id"],
                    "current_label": "AUTO",
                    "suspected_label": "REPAIR",
                    "detection_rule_triggered": (
                        f"AUTO has policy-requiring functions: {','.join(policy_funcs)}"
                    ),
                    "confidence": "HIGH",
                    "golden_evidence_present": "Y" if r["family_id"] in golden_flagged else "N",
                    "priority": "MAJOR",
                })
        else:  # REPAIR
            # If the action_sequence has *no* repair-class function at all, that's a
            # false REPAIR.  (Core functions like parse_source / sort_records alone
            # would mean the scenario is really AUTO, not REPAIR.)
            CORE = {"parse_source", "assign_evid", "sort_records",
                    "export_nonmem_ready", "flag_quarantine", "flag_invalid"}
            non_core = [fn for fn in seq if fn not in CORE]
            if not non_core:
                candidates.append({
                    "scenario_id": r["scenario_id"],
                    "family_id": r["family_id"],
                    "current_label": "REPAIR",
                    "suspected_label": "AUTO",  # could also be QUARANTINE; flagged for review
                    "detection_rule_triggered": (
                        "REPAIR but action_sequence contains only core functions"
                    ),
                    "confidence": "MEDIUM",
                    "golden_evidence_present": "Y" if r["family_id"] in golden_flagged else "N",
                    "priority": "MINOR",
                })
    return candidates


# ---------------------------------------------------------------------------
def emit_csv(candidates: list[dict[str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "scenario_id", "family_id", "current_label", "suspected_label",
        "detection_rule_triggered", "confidence",
        "golden_evidence_present", "priority",
    ]
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        for c in candidates:
            w.writerow(c)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--action-table", required=True, type=Path)
    p.add_argument("--func-library", default=Path("config/action_function_library.yaml"), type=Path)
    p.add_argument("--validation", type=Path, default=None)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)

    cands = detect(args.action_table, args.func_library, args.validation)
    emit_csv(cands, args.out)
    print(f"[detect_false_classification] {args.out}")
    print(f"[detect_false_classification] candidates={len(cands)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
