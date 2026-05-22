"""Config schema validator for pmx_universe_v5_1 (Frozen Universe v4.2).

Runs 22 validators (V01..V22) against the config/ YAMLs and writes a
markdown report. Exits non-zero on errors so CI can gate on it.

Usage:
    python scripts/config_validation/validate_config.py \\
        --config-dir config \\
        --out reports/config_schema_validation_report.md
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------

@dataclass
class ValidationError:
    validator: str
    file: str
    detail: str


@dataclass
class Report:
    config_dir: Path
    errors: list[ValidationError] = field(default_factory=list)

    def add(self, validator: str, file: str, detail: str) -> None:
        self.errors.append(ValidationError(validator, file, detail))

    @property
    def total_errors(self) -> int:
        return len(self.errors)

    def by_validator(self) -> dict[str, int]:
        counts = {f"V{i:02d}": 0 for i in range(1, 23)}
        for e in self.errors:
            counts[e.validator] = counts.get(e.validator, 0) + 1
        return counts


def _load(yaml_path: Path) -> Any:
    if not yaml_path.exists():
        return None
    return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------
# Validators (V01..V22)
# ----------------------------------------------------------------------

# Helper accessors --------------------------------------------------

def _axes(axis_doc: Any) -> list[dict]:
    if not axis_doc:
        return []
    return list(axis_doc.get("axis_dictionary", {}).get("axes", []) or [])


def _axis(axes: list[dict], axis_id: str) -> dict | None:
    for a in axes:
        if a.get("axis_id") == axis_id:
            return a
    return None


def _states(axis: dict | None) -> list[dict]:
    if not axis:
        return []
    return list(axis.get("states", []) or [])


def _state_codes(axis: dict | None) -> set[str]:
    return {s.get("state_code", "") for s in _states(axis)}


def _aux(axis: dict | None, field_name: str) -> dict | None:
    if not axis:
        return None
    for f in axis.get("auxiliary_fields", []) or []:
        if f.get("field") == field_name:
            return f
    return None


def _qcode_entries(q_doc: Any) -> list[dict]:
    if not q_doc:
        return []
    return list(q_doc.get("quarantine_reason_codes", {}).get("codes", []) or [])


def _qcode_codes(q_doc: Any) -> set[str]:
    return {c.get("code", "") for c in _qcode_entries(q_doc)}


def _active_qcodes(q_doc: Any) -> set[str]:
    return {c.get("code", "") for c in _qcode_entries(q_doc) if c.get("status") != "REJECTED"}


def _dc_rules(dc_doc: Any) -> list[dict]:
    if not dc_doc:
        return []
    return list(dc_doc.get("dependency_constraints", {}).get("rules", []) or [])


def _families(fam_doc: Any) -> list[dict]:
    if not fam_doc:
        return []
    return list(fam_doc.get("family_assignment_rules", {}).get("families", []) or [])


def _terminal_state_codes(term_doc: Any) -> set[str]:
    if not term_doc:
        return set()
    states = term_doc.get("terminal_state_taxonomy", {}).get("states", []) or []
    return {s.get("state") for s in states}


# Validator implementations ----------------------------------------

def v01_axis_id_uniqueness(rep: Report, docs: dict[str, Any]) -> None:
    axes = _axes(docs.get("axis"))
    seen: set[str] = set()
    for a in axes:
        aid = a.get("axis_id")
        if aid in seen:
            rep.add("V01", "axis_dictionary.yaml", f"duplicate axis_id: {aid}")
        else:
            seen.add(aid)


def v02_state_uniqueness_within_axis(rep: Report, docs: dict[str, Any]) -> None:
    for a in _axes(docs.get("axis")):
        seen: set[str] = set()
        for s in _states(a):
            code = s.get("state_code")
            if code in seen:
                rep.add("V02", "axis_dictionary.yaml", f"axis {a.get('axis_id')}: duplicate state_code {code}")
            else:
                seen.add(code)


def v03_dc_axis_references(rep: Report, docs: dict[str, Any]) -> None:
    valid_axes = {a.get("axis_id") for a in _axes(docs.get("axis"))}
    for r in _dc_rules(docs.get("dc")):
        if r.get("meta_rule"):
            continue
        for cond in r.get("if_conditions", []) or []:
            axis = cond.get("axis")
            if axis and axis not in valid_axes:
                rep.add("V03", "dependency_constraints.yaml", f"{r.get('rule_id')}: unknown axis {axis}")


def v04_dc_state_references(rep: Report, docs: dict[str, Any]) -> None:
    axes = _axes(docs.get("axis"))
    for r in _dc_rules(docs.get("dc")):
        if r.get("meta_rule"):
            continue
        for cond in r.get("if_conditions", []) or []:
            axis_id = cond.get("axis")
            if not axis_id:
                continue
            axis = _axis(axes, axis_id)
            codes = _state_codes(axis)
            state = cond.get("state")
            if state and state not in codes:
                rep.add("V04", "dependency_constraints.yaml", f"{r.get('rule_id')}: state {state} not in {axis_id}")
            for state in cond.get("state_in", []) or []:
                if state not in codes:
                    rep.add("V04", "dependency_constraints.yaml", f"{r.get('rule_id')}: state {state} not in {axis_id}")


def v05_dc_qcode_references(rep: Report, docs: dict[str, Any]) -> None:
    valid = _active_qcodes(docs.get("q"))
    for r in _dc_rules(docs.get("dc")):
        q = r.get("then_q_code")
        if q and q not in valid:
            rep.add("V05", "dependency_constraints.yaml", f"{r.get('rule_id')}: q_code {q} not in quarantine_reason_codes")


_Q15_ALLOW_MARKERS = (
    "forbidden_codes", "FORBIDDEN", "forbidden", "standalone",
    "bare Q15", "no Q15", "REJECTED",
)


def v06_q15_standalone_forbidden(rep: Report, docs: dict[str, Any]) -> None:
    """Q15 standalone is HR1 violation. Allow it only inside text that
    explicitly says it is forbidden / standalone / bare / rejected."""
    import re

    for name, doc in docs.items():
        if doc is None:
            continue
        text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
        for m in re.finditer(r"\bQ15(?![A-D])", text):
            start = max(0, m.start() - 200)
            end = min(len(text), m.end() + 200)
            ctx = text[start:end]
            if any(marker in ctx for marker in _Q15_ALLOW_MARKERS):
                continue
            snippet = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            rep.add("V06", f"{name}.yaml", f"Q15 standalone reference near: '{snippet}'")


_Q17_ALLOW_MARKERS = (
    "REJECTED", "absorbed", "FORBIDDEN", "forbidden",
    "absorb", "former Q17", "rejected",
    # Q17 may also appear in failure_condition listings alongside
    # 'Q15 standalone' — those are descriptive prohibitions, not usages.
    "standalone",
)


def v07_q17_forbidden_except_rejected(rep: Report, docs: dict[str, Any]) -> None:
    """Q17 is HR3 violation. Allow only when surrounding text marks it
    as rejected / absorbed / forbidden."""
    import re

    for name, doc in docs.items():
        if doc is None:
            continue
        text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
        for m in re.finditer(r"\bQ17\b", text):
            start = max(0, m.start() - 300)
            end = min(len(text), m.end() + 300)
            ctx = text[start:end]
            if any(marker in ctx for marker in _Q17_ALLOW_MARKERS):
                continue
            snippet = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            rep.add("V07", f"{name}.yaml", f"unexpected Q17 reference: '{snippet}'")


def v08_family_axis_state_refs(rep: Report, docs: dict[str, Any]) -> None:
    axes = _axes(docs.get("axis"))
    by_id = {a.get("axis_id"): a for a in axes}
    for fam in _families(docs.get("fam")):
        patterns = fam.get("matching_axis_patterns") or {}
        for axis_id, spec in patterns.items():
            axis = by_id.get(axis_id)
            if not axis:
                rep.add("V08", "family_assignment_rules.yaml", f"{fam.get('family_id')}: unknown axis {axis_id}")
                continue
            codes = _state_codes(axis)
            spec = spec or {}
            for state in spec.get("state_in", []) or []:
                if state not in codes:
                    rep.add("V08", "family_assignment_rules.yaml", f"{fam.get('family_id')}: state {state} not in {axis_id}")


def v09_terminal_state_references(rep: Report, docs: dict[str, Any]) -> None:
    valid = _terminal_state_codes(docs.get("term"))
    if not valid:
        rep.add("V09", "terminal_state_taxonomy.yaml", "terminal_state_taxonomy missing or empty")
        return
    # Check axes terminal_hint
    for a in _axes(docs.get("axis")):
        for s in _states(a):
            t = s.get("terminal_hint")
            if t and "/" in str(t):
                # allow "REPAIR/Q08" or "REPAIR / Q08" notation
                t = str(t).split("/")[0].strip()
            if t and t not in valid:
                rep.add("V09", "axis_dictionary.yaml", f"axis {a.get('axis_id')} state {s.get('state_code')}: terminal_hint {t} not in taxonomy")
    # Check DC then_terminal
    for r in _dc_rules(docs.get("dc")):
        t = r.get("then_terminal")
        if t and t not in valid:
            rep.add("V09", "dependency_constraints.yaml", f"{r.get('rule_id')}: terminal {t} not in taxonomy")
    # Check families expected_terminal
    for f in _families(docs.get("fam")):
        t = f.get("expected_terminal")
        if t and t not in valid:
            rep.add("V09", "family_assignment_rules.yaml", f"{f.get('family_id')}: expected_terminal {t} not in taxonomy")


def v10_aic_endpoint_rule_exists(rep: Report, docs: dict[str, Any]) -> None:
    # Need a DC rule that triggers Q11 when endpoint_data_type missing under AIC-PKPD/ER/TTE/BIOMARKER.
    rules = _dc_rules(docs.get("dc"))
    found = False
    for r in rules:
        if r.get("then_q_code") != "Q11":
            continue
        conds = r.get("if_conditions", []) or []
        has_aic_state = any("state_in" in c and "AIC-PKPD" in (c.get("state_in") or []) for c in conds)
        has_endpoint = any(c.get("aic_field") == "endpoint_data_type" for c in conds)
        if has_aic_state and has_endpoint:
            found = True
            break
    if not found:
        rep.add("V10", "dependency_constraints.yaml", "no rule maps (AIC-PKPD/ER/TTE/BIOMARKER + endpoint_data_type missing) → Q11")


def v11_addl_actual_q14_rule(rep: Report, docs: dict[str, Any]) -> None:
    rules = _dc_rules(docs.get("dc"))
    if not any(
        r.get("then_q_code") == "Q14"
        and any(c.get("state") == "ADDL-ACTUAL-CONFLICT" for c in (r.get("if_conditions") or []))
        for r in rules
    ):
        rep.add("V11", "dependency_constraints.yaml", "no rule maps A4=ADDL-ACTUAL-CONFLICT → Q14")


def v12_a5_bioanal_final_flag_q15a(rep: Report, docs: dict[str, Any]) -> None:
    # PATCH m-4: BIOANALYTICAL-FINAL-FLAG-MISSING maps to Q15A (not Q15D)
    rules = _dc_rules(docs.get("dc"))
    if not any(
        r.get("then_q_code") == "Q15A"
        and any(c.get("state") == "BIOANALYTICAL-FINAL-FLAG-MISSING" for c in (r.get("if_conditions") or []))
        for r in rules
    ):
        rep.add("V12", "dependency_constraints.yaml", "no rule maps A5=BIOANALYTICAL-FINAL-FLAG-MISSING → Q15A (PATCH m-4)")


def v13_a9_reanalysis_q15d(rep: Report, docs: dict[str, Any]) -> None:
    rules = _dc_rules(docs.get("dc"))
    if not any(
        r.get("then_q_code") == "Q15D"
        and any(c.get("state") == "REANALYSIS-FINAL-MISSING" for c in (r.get("if_conditions") or []))
        for r in rules
    ):
        rep.add("V13", "dependency_constraints.yaml", "no rule maps A9=REANALYSIS-FINAL-MISSING → Q15D")


def v14_a8_ddi_states_present(rep: Report, docs: dict[str, Any]) -> None:
    a8 = _axis(_axes(docs.get("axis")), "A8")
    codes = _state_codes(a8)
    for needed in ("DDI-VICTIM-ONLY", "DDI-VICTIM-PERPETRATOR"):
        if needed not in codes:
            rep.add("V14", "axis_dictionary.yaml", f"A8 missing state {needed}")


def v15_f09_f22_separate(rep: Report, docs: dict[str, Any]) -> None:
    fams = _families(docs.get("fam"))
    ids = {f.get("family_id") for f in fams}
    for fid in ("F09", "F22"):
        if fid not in ids:
            rep.add("V15", "family_assignment_rules.yaml", f"missing family {fid}")


def v16_qcode_count(rep: Report, docs: dict[str, Any]) -> None:
    active = _active_qcodes(docs.get("q"))
    expected = {f"Q{i:02d}" for i in range(1, 15)} | {"Q15A", "Q15B", "Q15C", "Q15D", "Q16", "Q18", "Q19"}
    missing = expected - active
    extra = active - expected
    if missing:
        rep.add("V16", "quarantine_reason_codes.yaml", f"missing active codes: {sorted(missing)}")
    if extra:
        rep.add("V16", "quarantine_reason_codes.yaml", f"unexpected active codes: {sorted(extra)}")
    if len(active) != 21:
        rep.add("V16", "quarantine_reason_codes.yaml", f"expected 21 active codes, got {len(active)}")


def v17_modality_class_11(rep: Report, docs: dict[str, Any]) -> None:
    a0 = _axis(_axes(docs.get("axis")), "A0")
    f = _aux(a0, "modality_class")
    if not f:
        rep.add("V17", "axis_dictionary.yaml", "A0 missing auxiliary_fields.modality_class")
        return
    vals = f.get("allowed_values", []) or []
    if len(vals) < 11:
        rep.add("V17", "axis_dictionary.yaml", f"modality_class has {len(vals)} values; expected ≥ 11")


def v18_endpoint_data_type_full(rep: Report, docs: dict[str, Any]) -> None:
    a0 = _axis(_axes(docs.get("axis")), "A0")
    f = _aux(a0, "endpoint_data_type")
    if not f:
        rep.add("V18", "axis_dictionary.yaml", "A0 missing auxiliary_fields.endpoint_data_type")
        return
    vals = set(f.get("allowed_values", []) or [])
    needed = {"CELLULAR_KINETICS", "IMMUNOGENICITY", "MILK_PK", "MATERNAL_INFANT_PK"}
    missing = needed - vals
    if missing:
        rep.add("V18", "axis_dictionary.yaml", f"endpoint_data_type missing v4.2 values: {sorted(missing)}")
    if len(vals) < 10:
        rep.add("V18", "axis_dictionary.yaml", f"endpoint_data_type has {len(vals)} values; expected 10")


def v19_analyte_role_12(rep: Report, docs: dict[str, Any]) -> None:
    a8 = _axis(_axes(docs.get("axis")), "A8")
    f = _aux(a8, "analyte_role")
    if not f:
        rep.add("V19", "axis_dictionary.yaml", "A8 missing auxiliary_fields.analyte_role")
        return
    vals = f.get("allowed_values", []) or []
    if len(vals) < 12:
        rep.add("V19", "axis_dictionary.yaml", f"analyte_role has {len(vals)} values; expected ≥ 12")


def v20_a7_product_level_covariate(rep: Report, docs: dict[str, Any]) -> None:
    a7 = _axis(_axes(docs.get("axis")), "A7")
    if "PRODUCT-LEVEL-COVARIATE" not in _state_codes(a7):
        rep.add("V20", "axis_dictionary.yaml", "A7 missing PRODUCT-LEVEL-COVARIATE state")


def v21_q16_q18_q19_present_q17_rejected(rep: Report, docs: dict[str, Any]) -> None:
    entries = _qcode_entries(docs.get("q"))
    by_code = {e.get("code"): e for e in entries}
    for needed in ("Q16", "Q18", "Q19"):
        if needed not in by_code:
            rep.add("V21", "quarantine_reason_codes.yaml", f"missing required v4.2 code {needed}")
    q17 = by_code.get("Q17")
    if q17 is None:
        rep.add("V21", "quarantine_reason_codes.yaml", "Q17 entry missing (must be present with status: REJECTED)")
    elif q17.get("status") != "REJECTED":
        rep.add("V21", "quarantine_reason_codes.yaml", "Q17 present but not marked status: REJECTED")


def v22_family_numbering(rep: Report, docs: dict[str, Any]) -> None:
    fams = _families(docs.get("fam"))
    by_id = {f.get("family_id"): f for f in fams}
    for fid in ("F24", "F25", "F26", "F27", "F28", "F29"):
        f = by_id.get(fid)
        if f is None:
            rep.add("V22", "family_assignment_rules.yaml", f"missing v4.2 operational family {fid}")
        elif not f.get("operational_scope"):
            rep.add("V22", "family_assignment_rules.yaml", f"{fid} should be operational_scope=true (v4.2)")
    for fid in ("F31", "F32", "F33", "F34"):
        f = by_id.get(fid)
        if f is None:
            rep.add("V22", "family_assignment_rules.yaml", f"missing renumbered out-of-scope family {fid}")
        elif f.get("operational_scope"):
            rep.add("V22", "family_assignment_rules.yaml", f"{fid} should be operational_scope=false")
    if "F30" in by_id:
        rep.add("V22", "family_assignment_rules.yaml", "F30 is reserved/buffer; should not exist as an entry")


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------

VALIDATORS: list[tuple[str, Callable[[Report, dict[str, Any]], None]]] = [
    ("V01", v01_axis_id_uniqueness),
    ("V02", v02_state_uniqueness_within_axis),
    ("V03", v03_dc_axis_references),
    ("V04", v04_dc_state_references),
    ("V05", v05_dc_qcode_references),
    ("V06", v06_q15_standalone_forbidden),
    ("V07", v07_q17_forbidden_except_rejected),
    ("V08", v08_family_axis_state_refs),
    ("V09", v09_terminal_state_references),
    ("V10", v10_aic_endpoint_rule_exists),
    ("V11", v11_addl_actual_q14_rule),
    ("V12", v12_a5_bioanal_final_flag_q15a),
    ("V13", v13_a9_reanalysis_q15d),
    ("V14", v14_a8_ddi_states_present),
    ("V15", v15_f09_f22_separate),
    ("V16", v16_qcode_count),
    ("V17", v17_modality_class_11),
    ("V18", v18_endpoint_data_type_full),
    ("V19", v19_analyte_role_12),
    ("V20", v20_a7_product_level_covariate),
    ("V21", v21_q16_q18_q19_present_q17_rejected),
    ("V22", v22_family_numbering),
]


def run(config_dir: Path) -> Report:
    docs = {
        "axis": _load(config_dir / "axis_dictionary.yaml"),
        "term": _load(config_dir / "terminal_state_taxonomy.yaml"),
        "q": _load(config_dir / "quarantine_reason_codes.yaml"),
        "dc": _load(config_dir / "dependency_constraints.yaml"),
        "fam": _load(config_dir / "family_assignment_rules.yaml"),
        "act_seq": _load(config_dir / "action_sequence_standard.yaml"),
        "act_lib": _load(config_dir / "action_function_library.yaml"),
        "aic": _load(config_dir / "analysis_intent_contract_template.yaml"),
    }
    rep = Report(config_dir=config_dir)
    for _vid, fn in VALIDATORS:
        try:
            fn(rep, docs)
        except Exception as exc:  # never let a validator bug crash the whole run
            rep.add(_vid, "(validator)", f"validator raised {type(exc).__name__}: {exc}")
    return rep


def write_report(rep: Report, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    counts = rep.by_validator()
    lines = [
        "# Config Schema Validation Report",
        "",
        f"generated_at: {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}",
        f"config_dir: {rep.config_dir}",
        f"total_validators: 22",
        f"total_errors: {rep.total_errors}",
        "",
        "## error_count_by_validator",
        "",
    ]
    for vid in sorted(counts):
        lines.append(f"- {vid}: {counts[vid]}")
    lines.append("")
    lines.append("## errors")
    lines.append("")
    if not rep.errors:
        lines.append("(none)")
    else:
        for e in rep.errors:
            lines.append(f"- validator: {e.validator} | file: {e.file} | detail: {e.detail}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate pmx_universe_v5_1 config YAMLs.")
    parser.add_argument("--config-dir", required=True, type=Path)
    parser.add_argument("--out", default=Path("reports/config_schema_validation_report.md"), type=Path)
    args = parser.parse_args(argv)
    rep = run(args.config_dir)
    write_report(rep, args.out)
    print(f"total_errors: {rep.total_errors}")
    for e in rep.errors:
        print(f"ERROR | {e.validator} | {e.file} | {e.detail}")
    return 0 if rep.total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
