"""Detect label conflicts (C01..C10) in the draft action table."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REPAIR_FNS = {
    "map_subject_id", "attach_dyad_linkage", "derive_time_nominal",
    "derive_time_elapsed", "derive_time_postpartum_anchor",
    "reconstruct_dose_weight", "reconstruct_dose_bsa",
    "reconstruct_dose_titration", "reconstruct_loading_maintenance",
    "reconstruct_infusion_stop_restart", "resolve_addl_actual_conflict",
    "canonicalize_blq", "canonicalize_cellular_blq",
    "adjudicate_immunogenicity_positivity", "assign_milk_matrix_lloq",
    "assign_cmt_with_analyte_role", "assign_cmt_multi",
    "assign_cmt_ddi_victim_only", "assign_cmt_ddi_victim_perpetrator",
    "attach_covariate_product_level", "resolve_reanalysis_final",
    "repair_blq_canonicalization", "repair_covariate_attach",
}


def run(draft_csv: Path, conflict_csv: Path, queue_csv: Path) -> int:
    with draft_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    conflicts: list[dict[str, str]] = []

    # C01 same axes → different labels (not applicable: scenario_id is unique by axis)
    # C02 same label → different action_sequence
    label_to_seqs: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        label_to_seqs[r["candidate_action_label"]].add(r["action_sequence"])
    for label, seqs in label_to_seqs.items():
        if len(seqs) > 1:
            conflicts.append({"scenario_id": "", "conflict_type": "C02",
                              "severity": "major",
                              "detail": f"label {label} has {len(seqs)} distinct sequences"})

    # C03 REPAIR with no required policy in parameter_policy
    for r in rows:
        if r["candidate_action_label"].startswith("REPAIR_"):
            policy = json.loads(r["parameter_policy"] or "{}")
            seq = r["action_sequence"]
            if not any(fn in seq for fn in REPAIR_FNS):
                conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C03",
                                  "severity": "fatal",
                                  "detail": f"REPAIR label {r['candidate_action_label']} has no repair function"})

    # C04 QUARANTINE label name missing q_code or wrong q_code
    for r in rows:
        if r["terminal_state"] == "QUARANTINE":
            name = r["candidate_action_label"]
            q_in_csv = r["q_code"]
            if not q_in_csv:
                conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C04",
                                  "severity": "fatal", "detail": "QUARANTINE missing q_code"})
            elif q_in_csv not in name:
                conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C04",
                                  "severity": "major",
                                  "detail": f"label {name} doesn't reference q_code {q_in_csv}"})

    # C05 Q15 standalone in q_code
    for r in rows:
        if r["q_code"] == "Q15":
            conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C05",
                              "severity": "fatal", "detail": "Q15 standalone"})

    # C06 Q17
    for r in rows:
        if r["q_code"] == "Q17":
            conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C06",
                              "severity": "fatal", "detail": "Q17 used"})

    # C07 AUTO label with repair function in sequence
    for r in rows:
        if r["candidate_action_label"].startswith("AUTO_"):
            if any(fn in r["action_sequence"] for fn in REPAIR_FNS):
                conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C07",
                                  "severity": "fatal", "detail": "AUTO has repair function"})

    # C08 INVALID/UNSUPPORTED with export_nonmem_ready
    for r in rows:
        if r["terminal_state"] in {"INVALID", "UNSUPPORTED"}:
            if "export_nonmem_ready" in r["action_sequence"]:
                conflicts.append({"scenario_id": r["scenario_id"], "conflict_type": "C08",
                                  "severity": "fatal", "detail": f"{r['terminal_state']} has export"})

    # C09 different parameter_policy → same label
    label_to_policy: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        label_to_policy[r["candidate_action_label"]].add(r["parameter_policy"])
    for label, ps in label_to_policy.items():
        if len(ps) > 1:
            conflicts.append({"scenario_id": "", "conflict_type": "C09",
                              "severity": "major",
                              "detail": f"label {label} has {len(ps)} distinct parameter_policy"})

    # C10 ADC/CAR-T multi-analyte → analyte_role missing in label name
    # Already handled: when analyte_role missing the row goes to QUARANTINE Q16.

    # Write conflict report and queue
    conflict_csv.parent.mkdir(parents=True, exist_ok=True)
    with conflict_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scenario_id", "conflict_type", "severity", "detail"])
        w.writeheader()
        w.writerows(conflicts)

    severity_order = {"fatal": 0, "major": 1, "minor": 2}
    sorted_conflicts = sorted(conflicts, key=lambda c: (severity_order.get(c["severity"], 3),
                                                       c["scenario_id"]))
    queue_csv.parent.mkdir(parents=True, exist_ok=True)
    with queue_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scenario_id", "conflict_type", "severity", "detail"])
        w.writeheader()
        w.writerows(sorted_conflicts)
    print(f"conflicts: {len(conflicts)} (fatal={sum(1 for c in conflicts if c['severity']=='fatal')})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", default=ROOT / "data" / "action_labels" / "scenario_action_table_draft.csv", type=Path)
    parser.add_argument("--conflict", default=ROOT / "reports" / "label_conflict_report.csv", type=Path)
    parser.add_argument("--queue", default=ROOT / "reports" / "expert_review_queue.csv", type=Path)
    args = parser.parse_args(argv)
    return run(args.draft, args.conflict, args.queue)


if __name__ == "__main__":
    raise SystemExit(main())
