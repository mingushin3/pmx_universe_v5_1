"""Validate the v4.2 boundary case CSV against axis / q-code / action vocab.

Runs 9 checks (BC1..BC9) against
``reports/repair_quarantine_boundary_cases_v4_2.csv`` and writes a markdown
report. Exits non-zero on any failed check.

Usage:
    python scripts/config_validation/validate_boundary_cases.py \\
        --csv reports/repair_quarantine_boundary_cases_v4_2.csv \\
        --config-dir config \\
        --out reports/boundary_case_qcode_validation.md
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Check:
    check_id: str
    name: str
    status: str = "PENDING"  # PASS / FAIL
    detail: str = ""


@dataclass
class BCReport:
    csv_path: Path
    config_dir: Path
    checks: list[Check] = field(default_factory=list)
    distribution: dict[str, int] = field(default_factory=dict)
    by_family: dict[str, int] = field(default_factory=dict)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if c.status == "FAIL")


def _load(path: Path) -> Any:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _row_seq(row: dict) -> str:
    return (row.get("action_sequence_pattern") or "").strip()


def _is_repair(row: dict) -> bool:
    return (row.get("terminal_state") or "").strip().upper() == "REPAIR"


def _is_auto(row: dict) -> bool:
    return (row.get("terminal_state") or "").strip().upper() == "AUTO"


def _is_quarantine(row: dict) -> bool:
    return (row.get("terminal_state") or "").strip().upper() == "QUARANTINE"


REPAIR_FUNCTIONS = {
    "reconstruct_dose_weight", "reconstruct_dose_bsa",
    "reconstruct_dose_titration", "reconstruct_loading_maintenance",
    "reconstruct_infusion_stop_restart", "expand_addl_ii",
    "resolve_addl_actual_conflict", "canonicalize_blq",
    "canonicalize_cellular_blq", "adjudicate_immunogenicity_positivity",
    "resolve_reanalysis_final", "assign_milk_matrix_lloq",
    "assign_cmt_multi", "assign_cmt_ddi_victim_only",
    "assign_cmt_ddi_victim_perpetrator", "assign_cmt_with_analyte_role",
    "attach_dyad_linkage", "attach_covariate_time_varying",
    "attach_covariate_external", "attach_covariate_product_level",
    "derive_time_postpartum_anchor",
}


def run(csv_path: Path, config_dir: Path) -> BCReport:
    rep = BCReport(csv_path=csv_path, config_dir=config_dir)

    q_doc = _load(config_dir / "quarantine_reason_codes.yaml") or {}
    active_qcodes = {
        c["code"] for c in q_doc.get("quarantine_reason_codes", {}).get("codes", []) or []
        if c.get("status") != "REJECTED"
    }

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    # Distribution
    from collections import Counter
    dist = Counter((r["terminal_state"] or "").strip() for r in rows)
    rep.distribution = dict(dist)
    rep.by_family = dict(Counter(r.get("family_id_hint", "") for r in rows))

    # ---- BC1: every QUARANTINE row's q_code exists in active codes ----
    bad: list[str] = []
    for r in rows:
        if _is_quarantine(r):
            q = (r.get("q_code") or "").strip()
            if not q:
                bad.append(f"{r['case_id']}: empty q_code on QUARANTINE")
            elif q not in active_qcodes:
                bad.append(f"{r['case_id']}: q_code {q} not in active codes")
    rep.checks.append(Check("BC1", "QUARANTINE rows have valid q_code",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    # ---- BC2: no Q15 standalone ----
    bad = [r["case_id"] for r in rows if (r.get("q_code") or "").strip() == "Q15"]
    rep.checks.append(Check("BC2", "No Q15 standalone",
                            "PASS" if not bad else "FAIL",
                            "rows: " + ", ".join(bad) if bad else ""))

    # ---- BC3: no Q17 ----
    bad = [r["case_id"] for r in rows if (r.get("q_code") or "").strip() == "Q17"]
    rep.checks.append(Check("BC3", "No Q17",
                            "PASS" if not bad else "FAIL",
                            "rows: " + ", ".join(bad) if bad else ""))

    # ---- BC4: action_sequence starts with parse_source / parse... ----
    bad = []
    for r in rows:
        if _is_quarantine(r) or (r["terminal_state"] in ("INVALID", "UNSUPPORTED")):
            # Quarantine/invalid/unsupported may still start with parse->flag_*
            pattern = _row_seq(r)
            if not (pattern.startswith("parse") or pattern.startswith("flag_")):
                bad.append(f"{r['case_id']}: starts with '{pattern[:25]}'")
            continue
        if not _row_seq(r).startswith("parse"):
            bad.append(f"{r['case_id']}: starts with '{_row_seq(r)[:25]}'")
    rep.checks.append(Check("BC4", "action_sequence starts with parse_source (AUTO/REPAIR)",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    # ---- BC5: AUTO/REPAIR end with export; QUARANTINE/etc end with flag_* ----
    bad = []
    for r in rows:
        seq = _row_seq(r)
        if _is_auto(r) or _is_repair(r):
            if not seq.endswith("export"):
                bad.append(f"{r['case_id']}: AUTO/REPAIR pattern ends with '{seq[-30:]}'")
        else:
            if "flag_" not in seq:
                bad.append(f"{r['case_id']}: non-AUTO/REPAIR pattern has no flag_*")
    rep.checks.append(Check("BC5", "Terminal endings consistent (export vs flag_*)",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    # ---- BC6: AUTO rows have no repair_* functions ----
    bad = []
    for r in rows:
        if not _is_auto(r):
            continue
        seq = _row_seq(r)
        for fn in REPAIR_FUNCTIONS:
            if fn in seq:
                bad.append(f"{r['case_id']}: AUTO row contains REPAIR function {fn}")
                break
    rep.checks.append(Check("BC6", "AUTO rows contain no REPAIR functions",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    # ---- BC7: v4.2 endpoint-specific repair functions present when needed ----
    bad = []
    for r in rows:
        if not _is_repair(r):
            continue
        edt = (r.get("endpoint_data_type") or "").strip()
        seq = _row_seq(r)
        a8 = (r.get("A8_state") or "").strip()
        role = (r.get("analyte_role") or "").strip()
        if edt == "CELLULAR_KINETICS" and "canonicalize_cellular_blq" not in seq:
            bad.append(f"{r['case_id']}: CELLULAR_KINETICS REPAIR missing canonicalize_cellular_blq")
        if edt == "IMMUNOGENICITY" and "adjudicate_immunogenicity_positivity" not in seq:
            bad.append(f"{r['case_id']}: IMMUNOGENICITY REPAIR missing adjudicate_immunogenicity_positivity")
        if edt == "MATERNAL_INFANT_PK" and "attach_dyad_linkage" not in seq:
            bad.append(f"{r['case_id']}: MATERNAL_INFANT_PK REPAIR missing attach_dyad_linkage")
        # analyte_role declared → must use assign_cmt_with_analyte_role
        if role and role != "" and a8 in {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED"}:
            if "assign_cmt_with_analyte_role" not in seq and "assign_cmt_multi" not in seq and "assign_cmt_ddi" not in seq:
                bad.append(f"{r['case_id']}: analyte_role declared but no assign_cmt_with_analyte_role / multi / ddi function")
    rep.checks.append(Check("BC7", "v4.2 endpoint-specific REPAIR functions present",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    # ---- BC8: family_id_hint references that exist in family_assignment_rules ----
    fam_doc = _load(config_dir / "family_assignment_rules.yaml") or {}
    fam_ids = {
        f.get("family_id")
        for f in fam_doc.get("family_assignment_rules", {}).get("families", []) or []
    }
    bad = []
    for r in rows:
        fid = (r.get("family_id_hint") or "").strip()
        if fid and fid not in fam_ids:
            bad.append(f"{r['case_id']}: family_id_hint {fid} not in family_assignment_rules")
    rep.checks.append(Check("BC8", "family_id_hint references exist",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    # ---- BC9: distribution roughly matches required ----
    target = {"AUTO": 4, "REPAIR": 30, "QUARANTINE": 22, "UNSUPPORTED": 2, "INVALID": 2}
    tol = 2  # allow ±2 per terminal
    bad = []
    for k, v in target.items():
        actual = dist.get(k, 0)
        if abs(actual - v) > tol:
            bad.append(f"{k}: {actual} vs target {v} (Δ>{tol})")
    rep.checks.append(Check("BC9", "Distribution within tolerance of (4/30/22/2/2)",
                            "PASS" if not bad else "FAIL",
                            "; ".join(bad)))

    return rep


def write_report(rep: BCReport, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Boundary Case Q-code Validation Report",
        "",
        f"generated_at: {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}",
        f"csv_file: {rep.csv_path}",
        f"config_dir: {rep.config_dir}",
        "",
        "## Distribution",
        "",
    ]
    for k in ("AUTO", "REPAIR", "QUARANTINE", "UNSUPPORTED", "INVALID"):
        lines.append(f"- {k}: {rep.distribution.get(k, 0)}")
    lines.append("")
    lines.append("## By family_id_hint")
    lines.append("")
    for fid, n in sorted(rep.by_family.items()):
        if fid:
            lines.append(f"- {fid}: {n}")
    lines.append("")
    lines.append("## Checks (BC1..BC9)")
    lines.append("")
    for c in rep.checks:
        lines.append(f"- [{c.status}] {c.check_id}: {c.name}")
        if c.detail:
            lines.append(f"    detail: {c.detail}")
    lines.append("")
    lines.append(f"failed_checks: {rep.failed}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate v4.2 boundary cases CSV.")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--config-dir", required=True, type=Path)
    parser.add_argument("--out", default=Path("reports/boundary_case_qcode_validation.md"), type=Path)
    args = parser.parse_args(argv)
    rep = run(args.csv, args.config_dir)
    write_report(rep, args.out)
    print(f"failed_checks: {rep.failed}")
    for c in rep.checks:
        print(f"[{c.status}] {c.check_id}: {c.name}")
        if c.detail:
            print(f"    {c.detail}")
    return 0 if rep.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
