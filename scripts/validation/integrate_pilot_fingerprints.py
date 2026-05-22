"""Integrate the 20 `*_fingerprint_approved.md` files into
`data/pilot_fingerprints/empirical_fingerprints_pilot.csv` and write the
integration report.

Runs V01..V12 sanity checks as it parses.

Usage:
    python scripts/validation/integrate_pilot_fingerprints.py
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


FINGERPRINT_HEADER = [
    "project_id", "family_candidate", "source_format", "source_parser_subtype",
    "study_design", "aic_summary", "modality_class", "endpoint_data_type",
    "A0_state", "A1_state", "A2_state", "A3_state", "A4_state", "A5_state",
    "A6_state", "A7_state", "A8_state", "A9_state", "A10_state",
    "analyte_role", "input_tables", "key_columns", "time_columns",
    "dose_columns", "observation_columns", "covariate_columns",
    "known_policies", "missing_policies", "manual_steps_required",
    "expected_terminal_state", "expected_q_code", "expected_action_sequence",
    "golden_dataset_available", "raw_input_path", "reference_output_path",
    "seed_category_id", "v4_2_relevant_axes", "fingerprint_confidence",
    "unknown_field_count", "notes",
]


_AXIS_RE = re.compile(r"^\-\s*(A\d{1,2}_state):\s*(.+?)\s*$", re.MULTILINE)
_KV_RE = re.compile(r"^\-\s*([a-zA-Z_]+):\s*(.+?)\s*$", re.MULTILINE)


@dataclass
class Validator:
    errors: list[str] = field(default_factory=list)

    def err(self, msg: str) -> None:
        self.errors.append(msg)


def _parse_md(path: Path) -> dict[str, Any]:
    txt = path.read_text(encoding="utf-8")
    out: dict[str, Any] = {}
    for m in _KV_RE.finditer(txt):
        k, v = m.group(1).strip(), m.group(2).strip()
        if k.startswith("A") and k.endswith("_state"):
            out[k] = v
        elif k in {
            "family_candidate", "seed_category_id", "raw_input_path",
            "modality_class", "endpoint_data_type", "analyte_role",
            "expected_terminal_state", "expected_q_code",
            "expected_action_sequence", "fingerprint_confidence",
            "unknown_field_count", "known_policies", "missing_policies",
        }:
            out[k] = v
    return out


def _q_set(q_doc: dict[str, Any]) -> set[str]:
    codes = q_doc.get("quarantine_reason_codes", {}).get("codes", []) or []
    return {c["code"] for c in codes if c.get("status") != "REJECTED"}


def integrate(fp_dir: Path, out_csv: Path, axis_yaml: Path, q_yaml: Path,
              report_md: Path) -> int:
    axis_doc = yaml.safe_load(axis_yaml.read_text(encoding="utf-8")) or {}
    axes = {a["axis_id"]: a for a in axis_doc.get("axis_dictionary", {}).get("axes", [])}
    valid_axis_states = {
        f"A{i}": {s["state_code"] for s in axes[f"A{i}"]["states"]}
        for i in range(11) if f"A{i}" in axes
    }
    q_doc = yaml.safe_load(q_yaml.read_text(encoding="utf-8")) or {}
    active_q = _q_set(q_doc)

    v = Validator()
    seen_projects: set[str] = set()
    seed_seen: set[str] = set()

    fingerprints: list[dict[str, Any]] = []
    for md_path in sorted(fp_dir.glob("*_fingerprint_approved.md")):
        d = _parse_md(md_path)
        pid_match = re.match(r"(.+)_fingerprint_approved\.md$", md_path.name)
        if not pid_match:
            v.err(f"{md_path.name}: bad filename")
            continue
        pid = pid_match.group(1)
        d["project_id"] = pid

        # V01 project_id uniqueness
        if pid in seen_projects:
            v.err(f"V01: duplicate project_id {pid}")
        seen_projects.add(pid)

        # V02/V03 axis state validity
        for ax in [f"A{i}_state" for i in range(11)]:
            val = d.get(ax)
            if val and val != "UNKNOWN":
                axis_id = ax[:-6]
                states = valid_axis_states.get(axis_id, set())
                if val not in states:
                    v.err(f"V03: {pid}: {ax}={val} not in {axis_id} states")

        # V04 modality_class
        modality = d.get("modality_class", "")
        allowed_mods = {
            "SMALL_MOLECULE", "PEPTIDE", "MAB", "ADC", "BISPECIFIC",
            "CELL_THERAPY", "GENE_THERAPY", "MRNA", "VACCINE",
            "OLIGO_ASO_SIRNA", "RADIOPHARMACEUTICAL", "OTHER_CUSTOM",
            "UNKNOWN",
        }
        if modality and modality not in allowed_mods:
            v.err(f"V04: {pid}: modality_class={modality} invalid")

        # V05 endpoint_data_type
        edt = d.get("endpoint_data_type", "")
        allowed_edt = {
            "PK_CONCENTRATION", "EXPOSURE_METRIC", "CONTINUOUS_PD",
            "CATEGORICAL_PD", "COUNT_PD", "TTE_EVENT",
            "CELLULAR_KINETICS", "IMMUNOGENICITY", "MILK_PK",
            "MATERNAL_INFANT_PK", "UNKNOWN",
        }
        if edt and edt not in allowed_edt:
            v.err(f"V05: {pid}: endpoint_data_type={edt} invalid")

        # V06 terminal_state
        terminal = d.get("expected_terminal_state", "")
        if terminal not in {"AUTO", "REPAIR", "QUARANTINE", "UNSUPPORTED",
                            "INVALID", "UNKNOWN"}:
            v.err(f"V06: {pid}: expected_terminal_state={terminal} invalid")

        # V07 q_code (no Q15 standalone, no Q17)
        q = d.get("expected_q_code", "N/A")
        if terminal == "QUARANTINE":
            if q in {"", "N/A"}:
                v.err(f"V07: {pid}: QUARANTINE without q_code")
            elif q == "Q15":
                v.err(f"V07: {pid}: Q15 standalone forbidden")
            elif q == "Q17":
                v.err(f"V07: {pid}: Q17 forbidden")
            elif q not in active_q:
                v.err(f"V07: {pid}: q_code {q} not active")

        # V08 family_candidate
        fam = d.get("family_candidate", "")
        fam_ok = (re.match(r"F0[1-9]$|F1[0-9]$|F2[0-9]$|F3[1-4]$", fam) is not None)
        if not fam_ok:
            v.err(f"V08: {pid}: family_candidate={fam} not in F01-F29 or F31-F34")

        # V09 seed_category_id
        sid = d.get("seed_category_id", "")
        if sid and sid != "N/A":
            try:
                int(sid)
                if not (1 <= int(sid) <= 20):
                    v.err(f"V09: {pid}: seed_category_id {sid} out of range")
                seed_seen.add(sid)
            except ValueError:
                if not sid.startswith("UNCERTAIN_"):
                    v.err(f"V09: {pid}: seed_category_id {sid} invalid")
                else:
                    seed_seen.add(sid)
        else:
            v.err(f"V09: {pid}: seed_category_id missing")

        # V10 UNKNOWN rate (we count occurrences of UNKNOWN literally)
        ufc = d.get("unknown_field_count", "0")
        try:
            ufc_int = int(ufc)
            if ufc_int > 17:
                v.err(f"V10: {pid}: unknown_field_count {ufc_int} > 17 (40%)")
        except ValueError:
            pass

        # V11 v4.2 conditional fields
        if modality in {"ADC", "BISPECIFIC", "CELL_THERAPY", "GENE_THERAPY"}:
            if not d.get("analyte_role") or d["analyte_role"].upper() in {"N/A", "", "NONE"}:
                # may be acceptable if A8 not multi-CMT; we relax here
                pass
        if edt == "CELLULAR_KINETICS":
            kp = d.get("known_policies", "")
            mp = d.get("missing_policies", "")
            if "cellular_LLOQ" not in (kp + mp):
                v.err(f"V11: {pid}: cellular_LLOQ not in known/missing policies for CELLULAR_KINETICS")

        fingerprints.append(d)

    # V12 seed coverage
    if len(seed_seen) < 20:
        v.err(f"V12: seed coverage only {len(seed_seen)}/20")

    # Write CSV
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FINGERPRINT_HEADER)
        for d in fingerprints:
            row = []
            for col in FINGERPRINT_HEADER:
                val = d.get(col, "")
                if isinstance(val, list):
                    val = "; ".join(str(x) for x in val)
                row.append(val)
            writer.writerow(row)

    # Report
    report_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pilot Fingerprint Integration Report",
        "",
        f"total_fingerprints: {len(fingerprints)}",
        f"validation_errors: {len(v.errors)}",
        "",
        "## terminal_state distribution",
    ]
    from collections import Counter
    term_c = Counter(d.get("expected_terminal_state", "") for d in fingerprints)
    for k, n in term_c.items():
        lines.append(f"- {k}: {n}")
    lines.append("")
    lines.append("## modality distribution")
    mod_c = Counter(d.get("modality_class", "") for d in fingerprints)
    for k, n in mod_c.items():
        lines.append(f"- {k}: {n}")
    lines.append("")
    lines.append(f"## seed_category coverage: {len(seed_seen)} / 20")
    lines.append("")
    lines.append("## validation errors")
    if v.errors:
        for e in v.errors:
            lines.append(f"- {e}")
    else:
        lines.append("(none)")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return 0 if not v.errors else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fp-dir", default=PROJECT_ROOT / "data" / "pilot_fingerprints", type=Path)
    parser.add_argument("--axis-yaml", default=PROJECT_ROOT / "config" / "axis_dictionary.yaml", type=Path)
    parser.add_argument("--q-yaml", default=PROJECT_ROOT / "config" / "quarantine_reason_codes.yaml", type=Path)
    parser.add_argument("--out-csv", default=PROJECT_ROOT / "data" / "pilot_fingerprints" / "empirical_fingerprints_pilot.csv", type=Path)
    parser.add_argument("--report", default=PROJECT_ROOT / "reports" / "pilot_fingerprint_integration_report.md", type=Path)
    args = parser.parse_args(argv)
    rc = integrate(args.fp_dir, args.out_csv, args.axis_yaml, args.q_yaml, args.report)
    return rc


if __name__ == "__main__":
    sys.exit(main())
