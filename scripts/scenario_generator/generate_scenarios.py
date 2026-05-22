"""Generate the Frozen Universe v4.2 scenario universe.

Strategy: rather than full cartesian product (which would explode),
enumerate over each `modality_class × endpoint_data_type` combination
and a carefully-chosen subset of states on the other axes. This
produces ~1500–4000 scenarios — within the playbook's 1000–5000 target.

modality_class is treated as an AUXILIARY field on A0 (per P53 rule),
not as an independent axis. Same for analyte_role on A8.

Outputs:
- data/scenario_universe/scenario_universe_raw.csv (all enumerated combos)
- data/scenario_universe/scenario_universe_valid_candidate.csv (with terminal_state)
- reports/invalid_scenario_log.csv (rejected combos w/ reason)
- reports/scenario_generation_report.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------------------
# Axis state choices for enumeration. Not the full state space — a
# representative subset that exercises every terminal_state and every
# Q-code.
# ----------------------------------------------------------------------

A0_STATES = [
    "AIC-MISSING", "AIC-PK", "AIC-PKPD", "AIC-ER", "AIC-TTE",
    "AIC-BIOMARKER", "AIC-CELL_THERAPY", "AIC-IMMUNOGEN", "AIC-LACTATION",
    "AIC-PRECLINICAL", "AIC-UNRECOVERABLE",
]

A1_STATES = [
    "ID-DEFINED", "ID-DUPLICATE-RESOLVABLE", "ID-AMBIGUOUS",
    "ID-DYAD-LINKABLE", "ID-DYAD-UNLINKED-POLICY-MISSING", "ID-UNRECOVERABLE",
]
A2_STATES = [
    "TIME-DEFINED", "TIME-ACTUAL-VS-NOMINAL-RESOLVABLE",
    "TIME-INTERVAL-RESOLVABLE", "TIME-ELAPSED-RESOLVABLE",
    "TIME-ANCHOR-AMBIGUOUS", "TIME-UNRECOVERABLE",
]
A3_STATES = [
    "DOSE-DEFINED", "DOSE-WEIGHT-BASED", "DOSE-BSA-BASED",
    "DOSE-TITRATION", "DOSE-LOADING-MAINTENANCE",
    "DOSE-INFUSION-STOP-RESTART", "DOSE-ADDL-ACTUAL-CONFLICT",
    "DOSE-AMBIGUOUS", "DOSE-UNRECOVERABLE",
]
A4_STATES = [
    "REGIMEN-FIXED", "REGIMEN-EXPANDABLE-ADDL", "TITRATION-ADAPTIVE",
    "LOADING-MAINTENANCE", "INFUSION-STOP-RESTART", "ADDL-ACTUAL-CONFLICT",
    "MISSING-NO-POLICY", "UNRECOVERABLE",
]
A5_STATES = [
    "BIOANALYTICAL-FINAL", "BIOANALYTICAL-FINAL-FLAG-MISSING",
    "BLQ-DEFINED-POLICY", "BLQ-NO-POLICY", "LLOQ-MISSING",
    "CELLULAR-BLQ-DEFINED", "CELLULAR-LLOQ-POLICY-MISSING",
    "IMMUNOGEN-POSITIVITY-DEFINED", "IMMUNOGEN-POSITIVITY-MISSING",
    "ABSENT",
]
A6_STATES = [
    "COVARIATE-COMPLETE", "COVARIATE-BASELINE-ONLY",
    "COVARIATE-TIME-VARYING-RESOLVABLE", "COVARIATE-PARTIAL-POLICY",
    "COVARIATE-IMPUTATION-POLICY-MISSING", "COVARIATE-ABSENT",
]
A7_STATES = [
    "SUBJECT-LEVEL-COVARIATE", "BASELINE-CLEAN", "TIME-VARYING",
    "EXTERNAL-LINKABLE", "PRODUCT-LEVEL-COVARIATE",
    "KEY-MISSING", "POLICY-MISSING", "UNRECOVERABLE",
]
A8_STATES = [
    "SINGLE-ANALYTE", "MULTI-CMT-DEFINED", "DDI-VICTIM-ONLY",
    "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED", "CMT-POLICY-MISSING",
]
A9_STATES = [
    "REANALYSIS-NONE", "REANALYSIS-FINAL-RESOLVABLE",
    "REANALYSIS-FINAL-MISSING", "PROTOCOL-DEVIATION-RESOLVABLE",
    "PROTOCOL-DEVIATION-NO-POLICY", "IRRECONCILABLE",
]
A10_STATES = [
    "STRUCTURED", "SEMI-STRUCTURED", "NON-TABULAR", "CORRUPTED",
    "SEMI-STRUCTURED-LEGACY-FLAG", "RWD-ADHERENCE-UNRESOLVED",
]

MODALITIES = [
    "SMALL_MOLECULE", "MAB", "ADC", "BISPECIFIC", "CELL_THERAPY", "MRNA",
]
ENDPOINTS_BY_AIC = {
    "AIC-PK": ["PK_CONCENTRATION"],
    "AIC-PKPD": ["PK_CONCENTRATION", "CONTINUOUS_PD"],
    "AIC-ER": ["EXPOSURE_METRIC"],
    "AIC-TTE": ["TTE_EVENT", "COUNT_PD", "CATEGORICAL_PD"],
    "AIC-BIOMARKER": ["CONTINUOUS_PD"],
    "AIC-CELL_THERAPY": ["CELLULAR_KINETICS"],
    "AIC-IMMUNOGEN": ["IMMUNOGENICITY"],
    "AIC-LACTATION": ["MATERNAL_INFANT_PK", "MILK_PK"],
    "AIC-PRECLINICAL": ["PK_CONCENTRATION"],
    "AIC-MISSING": [""],
    "AIC-UNRECOVERABLE": [""],
}


# ----------------------------------------------------------------------
# Terminal-state resolver (mirrors dependency_constraints.yaml)
# ----------------------------------------------------------------------


def _resolve(scn: dict[str, Any]) -> tuple[str, str | None, str | None]:
    """Return (terminal_state, q_code, family_hint)."""
    a0 = scn["A0_state"]
    a1 = scn["A1_state"]
    a2 = scn["A2_state"]
    a3 = scn["A3_state"]
    a4 = scn["A4_state"]
    a5 = scn["A5_state"]
    a6 = scn["A6_state"]
    a7 = scn["A7_state"]
    a8 = scn["A8_state"]
    a9 = scn["A9_state"]
    a10 = scn["A10_state"]
    modality = scn["modality_class"]
    edt = scn["endpoint_data_type"]
    role = scn["analyte_role"]

    # Highest-priority INVALIDs
    if a0 == "AIC-UNRECOVERABLE": return ("INVALID", None, None)
    if a1 == "ID-UNRECOVERABLE": return ("INVALID", None, None)
    if a2 == "TIME-UNRECOVERABLE": return ("INVALID", None, None)
    if a3 == "DOSE-UNRECOVERABLE": return ("INVALID", None, None)
    if a4 == "UNRECOVERABLE": return ("INVALID", None, None)
    if a5 == "ABSENT": return ("INVALID", None, None)
    if a6 == "COVARIATE-ABSENT": return ("INVALID", None, None)
    if a7 == "UNRECOVERABLE": return ("INVALID", None, None)
    if a9 == "IRRECONCILABLE": return ("INVALID", None, None)
    if a10 == "CORRUPTED": return ("INVALID", None, None)

    # UNSUPPORTED
    if a10 == "NON-TABULAR": return ("UNSUPPORTED", None, None)

    # AIC-MISSING
    if a0 == "AIC-MISSING": return ("QUARANTINE", "Q11", None)

    # v4.2 endpoint policy checks
    if edt == "CELLULAR_KINETICS" and a5 == "CELLULAR-LLOQ-POLICY-MISSING":
        return ("QUARANTINE", "Q01", "F26")
    if edt == "IMMUNOGENICITY" and a5 == "IMMUNOGEN-POSITIVITY-MISSING":
        return ("QUARANTINE", "Q19", "F27")
    if edt == "MATERNAL_INFANT_PK" and a1 == "ID-DYAD-UNLINKED-POLICY-MISSING":
        return ("QUARANTINE", "Q18", "F29")
    if edt == "MATERNAL_INFANT_PK" and a2 == "TIME-ANCHOR-AMBIGUOUS":
        return ("QUARANTINE", "Q12", "F29")
    if edt == "MILK_PK" and a5 == "LLOQ-MISSING":
        return ("QUARANTINE", "Q01", "F29")

    # A1 ambiguous
    if a1 == "ID-AMBIGUOUS": return ("QUARANTINE", "Q03", None)

    # A2 ambiguous
    if a2 == "TIME-ANCHOR-AMBIGUOUS": return ("QUARANTINE", "Q02", None)

    # A3 ambiguous
    if a3 == "DOSE-AMBIGUOUS": return ("QUARANTINE", "Q02", None)

    # A4
    if a4 == "MISSING-NO-POLICY": return ("QUARANTINE", "Q08", None)
    if a4 == "ADDL-ACTUAL-CONFLICT" and a3 == "DOSE-ADDL-ACTUAL-CONFLICT":
        return ("QUARANTINE", "Q14", None)

    # A5 BLQ
    if a5 == "BIOANALYTICAL-FINAL-FLAG-MISSING":
        return ("QUARANTINE", "Q15A", None)
    if a5 == "BLQ-NO-POLICY": return ("QUARANTINE", "Q01", None)
    if a5 == "LLOQ-MISSING": return ("QUARANTINE", "Q01", None)

    # A6
    if a6 == "COVARIATE-IMPUTATION-POLICY-MISSING":
        return ("QUARANTINE", "Q06", None)

    # A7
    if a7 == "KEY-MISSING": return ("QUARANTINE", "Q13", None)
    if a7 == "POLICY-MISSING": return ("QUARANTINE", "Q07", None)
    if a7 == "PRODUCT-LEVEL-COVARIATE" and modality == "CELL_THERAPY":
        # If no lot linkage policy noted, → Q13. But we represent linkage
        # availability via "policy declared" implicit in the absence of
        # any policy-missing state. Default: REPAIR with F26.
        if a5 == "CELLULAR-LLOQ-POLICY-MISSING":
            return ("QUARANTINE", "Q01", "F26")

    # A8
    if a8 == "CMT-POLICY-MISSING": return ("QUARANTINE", "Q09", None)
    if a8 in {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED"} \
            and modality in {"ADC", "BISPECIFIC", "CELL_THERAPY"} \
            and not role:
        return ("QUARANTINE", "Q16", None)

    # A9
    if a9 == "REANALYSIS-FINAL-MISSING": return ("QUARANTINE", "Q15D", None)
    if a9 == "PROTOCOL-DEVIATION-NO-POLICY": return ("QUARANTINE", "Q06", None)

    # A10
    if a10 == "SEMI-STRUCTURED-LEGACY-FLAG":
        return ("QUARANTINE", "Q15B", None)
    if a10 == "RWD-ADHERENCE-UNRESOLVED":
        return ("QUARANTINE", "Q15C", None)

    # AIC consistency: endpoint required but absent
    if a0 in {"AIC-PKPD", "AIC-ER", "AIC-TTE", "AIC-BIOMARKER",
              "AIC-CELL_THERAPY", "AIC-IMMUNOGEN", "AIC-LACTATION"} and not edt:
        return ("QUARANTINE", "Q11", None)

    # Now classify REPAIR vs AUTO
    repair_states = {
        "ID-DUPLICATE-RESOLVABLE", "ID-DYAD-LINKABLE",
        "TIME-ACTUAL-VS-NOMINAL-RESOLVABLE", "TIME-INTERVAL-RESOLVABLE",
        "TIME-ELAPSED-RESOLVABLE",
        "DOSE-WEIGHT-BASED", "DOSE-BSA-BASED", "DOSE-TITRATION",
        "DOSE-LOADING-MAINTENANCE", "DOSE-INFUSION-STOP-RESTART",
        "REGIMEN-EXPANDABLE-ADDL", "TITRATION-ADAPTIVE",
        "LOADING-MAINTENANCE", "INFUSION-STOP-RESTART",
        "BLQ-DEFINED-POLICY", "CELLULAR-BLQ-DEFINED",
        "IMMUNOGEN-POSITIVITY-DEFINED",
        "COVARIATE-TIME-VARYING-RESOLVABLE", "COVARIATE-PARTIAL-POLICY",
        "TIME-VARYING", "EXTERNAL-LINKABLE", "PRODUCT-LEVEL-COVARIATE",
        "MULTI-CMT-DEFINED", "DDI-VICTIM-ONLY", "DDI-VICTIM-PERPETRATOR",
        "METABOLITE-DEFINED",
        "REANALYSIS-FINAL-RESOLVABLE", "PROTOCOL-DEVIATION-RESOLVABLE",
        "SEMI-STRUCTURED",
    }
    if any(scn[k] in repair_states for k in
           ["A1_state", "A2_state", "A3_state", "A4_state", "A5_state",
            "A6_state", "A7_state", "A8_state", "A9_state", "A10_state"]):
        return ("REPAIR", None, None)
    return ("AUTO", None, None)


# ----------------------------------------------------------------------
# Family hint (priority order)
# ----------------------------------------------------------------------


def _family(scn: dict[str, Any], terminal: str, family_hint: str | None) -> str:
    if scn.get("_family_override"):
        return scn["_family_override"]
    if family_hint:
        return family_hint
    if terminal in {"UNSUPPORTED"}:
        if scn["A10_state"] == "NON-TABULAR":
            return "F31"
    if terminal == "INVALID":
        return "F34"
    modality = scn["modality_class"]
    edt = scn["endpoint_data_type"]
    a8 = scn["A8_state"]
    a1 = scn["A1_state"]

    if modality == "ADC" and a8 in {"MULTI-CMT-DEFINED", "METABOLITE-DEFINED"}:
        return "F24"
    if modality == "BISPECIFIC" and a8 in {"MULTI-CMT-DEFINED", "METABOLITE-DEFINED"}:
        return "F25"
    if modality == "CELL_THERAPY" and edt == "CELLULAR_KINETICS":
        return "F26"
    if modality == "MRNA":
        return "F27"
    if edt == "MATERNAL_INFANT_PK" or edt == "MILK_PK":
        return "F29"
    if a1 == "ID-DYAD-LINKABLE":
        return "F29"
    if a8 == "DDI-VICTIM-PERPETRATOR":
        return "F22"
    if a8 == "DDI-VICTIM-ONLY":
        return "F09"
    if scn["A0_state"] == "AIC-PRECLINICAL":
        return "F19"
    if scn["A0_state"] in {"AIC-TTE"}:
        return "F15"
    return "F01"


# ----------------------------------------------------------------------
# Enumeration strategy
# ----------------------------------------------------------------------


def _enumerate() -> list[dict[str, Any]]:
    """Produce a deterministic universe of ~2000-4000 scenarios."""
    scenarios: list[dict[str, Any]] = []

    # Drive enumeration off (A0, A4, A5, A8, A10) — the high-impact axes.
    # Other axes get representative subsets.
    a1_sub = ["ID-DEFINED", "ID-DUPLICATE-RESOLVABLE", "ID-AMBIGUOUS",
              "ID-DYAD-LINKABLE", "ID-DYAD-UNLINKED-POLICY-MISSING"]
    a2_sub = ["TIME-DEFINED", "TIME-ACTUAL-VS-NOMINAL-RESOLVABLE",
              "TIME-ELAPSED-RESOLVABLE", "TIME-ANCHOR-AMBIGUOUS"]
    a3_sub = ["DOSE-DEFINED", "DOSE-WEIGHT-BASED", "DOSE-AMBIGUOUS"]
    a6_sub = ["COVARIATE-COMPLETE", "COVARIATE-BASELINE-ONLY",
              "COVARIATE-IMPUTATION-POLICY-MISSING"]
    a7_sub = ["SUBJECT-LEVEL-COVARIATE", "PRODUCT-LEVEL-COVARIATE",
              "KEY-MISSING"]
    a9_sub = ["REANALYSIS-NONE", "REANALYSIS-FINAL-MISSING",
              "PROTOCOL-DEVIATION-RESOLVABLE"]

    for a0 in A0_STATES:
        edts = ENDPOINTS_BY_AIC.get(a0, [""])
        for edt in edts:
            for modality in MODALITIES:
                # Skip nonsensical pairs
                if a0 == "AIC-CELL_THERAPY" and modality not in {"CELL_THERAPY", "GENE_THERAPY"}:
                    continue
                if a0 == "AIC-IMMUNOGEN" and modality not in {"MRNA", "MAB", "VACCINE"}:
                    continue
                if a0 == "AIC-LACTATION" and modality not in {"MAB", "SMALL_MOLECULE"}:
                    continue
                if a0 in {"AIC-MISSING", "AIC-UNRECOVERABLE"} and modality != "SMALL_MOLECULE":
                    continue  # one representative; we don't need 6 copies
                # iterate other axes (compact: 2x3x3x2 = 36 per outer combo)
                for a4 in ["REGIMEN-FIXED", "ADDL-ACTUAL-CONFLICT"]:
                    for a5 in ["BIOANALYTICAL-FINAL", "BLQ-DEFINED-POLICY",
                               "BIOANALYTICAL-FINAL-FLAG-MISSING",
                               "CELLULAR-BLQ-DEFINED",
                               "IMMUNOGEN-POSITIVITY-DEFINED"]:
                        # gate v4.2 obs by endpoint
                        if a5 == "CELLULAR-BLQ-DEFINED" and edt != "CELLULAR_KINETICS":
                            continue
                        if a5 == "IMMUNOGEN-POSITIVITY-DEFINED" and edt != "IMMUNOGENICITY":
                            continue
                        for a8 in ["SINGLE-ANALYTE", "MULTI-CMT-DEFINED",
                                   "DDI-VICTIM-PERPETRATOR"]:
                            for a10 in ["STRUCTURED", "SEMI-STRUCTURED-LEGACY-FLAG"]:
                                # default values for less-impactful axes
                                a1 = "ID-DEFINED"
                                a2 = "TIME-DEFINED"
                                a3 = "DOSE-DEFINED"
                                a6 = "COVARIATE-BASELINE-ONLY"
                                a7 = "SUBJECT-LEVEL-COVARIATE"
                                a9 = "REANALYSIS-NONE"
                                # specialize for endpoint
                                if edt == "MATERNAL_INFANT_PK":
                                    a1 = "ID-DYAD-LINKABLE"
                                    a2 = "TIME-ELAPSED-RESOLVABLE"
                                if modality == "CELL_THERAPY" and edt == "CELLULAR_KINETICS":
                                    a7 = "PRODUCT-LEVEL-COVARIATE"
                                # analyte_role
                                if modality in {"ADC", "BISPECIFIC", "CELL_THERAPY"} \
                                        and a8 in {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR",
                                                   "METABOLITE-DEFINED"}:
                                    role = (
                                        "TOTAL_ANTIBODY|CONJUGATED_ADC|UNCONJUGATED_PAYLOAD"
                                        if modality == "ADC" else
                                        "PARENT|SOLUBLE_TARGET|DRUG_TARGET_COMPLEX"
                                        if modality == "BISPECIFIC" else
                                        "VECTOR_COPY|CAR_POSITIVE_CELL"
                                    )
                                else:
                                    role = ""
                                scenarios.append({
                                    "A0_state": a0, "A1_state": a1, "A2_state": a2,
                                    "A3_state": a3, "A4_state": a4, "A5_state": a5,
                                    "A6_state": a6, "A7_state": a7, "A8_state": a8,
                                    "A9_state": a9, "A10_state": a10,
                                    "modality_class": modality,
                                    "endpoint_data_type": edt,
                                    "analyte_role": role,
                                })
                                # additionally create a "no analyte_role" variant
                                # for multi-CMT/ADC/etc to trigger Q16
                                if role and a8 in {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR"}:
                                    scenarios.append({
                                        **scenarios[-1],
                                        "analyte_role": "",
                                    })

    # v4.2 policy-missing variants — must produce Q01 (cellular), Q19, Q18, Q12, Q16
    v42_missing = [
        # CELLULAR_KINETICS missing LLOQ -> Q01
        ("AIC-CELL_THERAPY", "CELLULAR_KINETICS", "CELL_THERAPY",
         "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
         "CELLULAR-LLOQ-POLICY-MISSING", "PRODUCT-LEVEL-COVARIATE",
         "MULTI-CMT-DEFINED", "VECTOR_COPY|CAR_POSITIVE_CELL"),
        # IMMUNOGENICITY missing positivity -> Q19
        ("AIC-IMMUNOGEN", "IMMUNOGENICITY", "MRNA",
         "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
         "IMMUNOGEN-POSITIVITY-MISSING", "SUBJECT-LEVEL-COVARIATE",
         "SINGLE-ANALYTE", ""),
        ("AIC-IMMUNOGEN", "IMMUNOGENICITY", "MAB",
         "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
         "IMMUNOGEN-POSITIVITY-MISSING", "SUBJECT-LEVEL-COVARIATE",
         "SINGLE-ANALYTE", ""),
        # MATERNAL_INFANT missing dyad -> Q18
        ("AIC-LACTATION", "MATERNAL_INFANT_PK", "MAB",
         "ID-DYAD-UNLINKED-POLICY-MISSING", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
         "BIOANALYTICAL-FINAL", "SUBJECT-LEVEL-COVARIATE",
         "SINGLE-ANALYTE", ""),
        # MATERNAL_INFANT missing anchor -> Q12
        ("AIC-LACTATION", "MATERNAL_INFANT_PK", "MAB",
         "ID-DYAD-LINKABLE", "TIME-ANCHOR-AMBIGUOUS", "DOSE-DEFINED", "REGIMEN-FIXED",
         "BIOANALYTICAL-FINAL", "SUBJECT-LEVEL-COVARIATE",
         "SINGLE-ANALYTE", ""),
        # MILK_PK missing matrix lloq -> Q01
        ("AIC-LACTATION", "MILK_PK", "SMALL_MOLECULE",
         "ID-DYAD-LINKABLE", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
         "LLOQ-MISSING", "SUBJECT-LEVEL-COVARIATE",
         "SINGLE-ANALYTE", ""),
    ]
    for (a0, edt, mod, a1, a2, a3, a4, a5, a7, a8, role) in v42_missing:
        scenarios.append({
            "A0_state": a0, "A1_state": a1, "A2_state": a2, "A3_state": a3,
            "A4_state": a4, "A5_state": a5,
            "A6_state": "COVARIATE-BASELINE-ONLY",
            "A7_state": a7, "A8_state": a8,
            "A9_state": "REANALYSIS-NONE", "A10_state": "STRUCTURED",
            "modality_class": mod, "endpoint_data_type": edt,
            "analyte_role": role,
        })

    # Pregnancy PK variants (F28): elapsed-anchor MAB scenarios
    for a4 in ["REGIMEN-FIXED", "LOADING-MAINTENANCE"]:
        for a5 in ["BIOANALYTICAL-FINAL", "BLQ-DEFINED-POLICY"]:
            for a2 in ["TIME-ELAPSED-RESOLVABLE", "TIME-ANCHOR-AMBIGUOUS"]:
                scenarios.append({
                    "A0_state": "AIC-PKPD",
                    "A1_state": "ID-DEFINED",
                    "A2_state": a2,
                    "A3_state": "DOSE-DEFINED",
                    "A4_state": a4,
                    "A5_state": a5,
                    "A6_state": "COVARIATE-BASELINE-ONLY",
                    "A7_state": "SUBJECT-LEVEL-COVARIATE",
                    "A8_state": "SINGLE-ANALYTE",
                    "A9_state": "REANALYSIS-NONE",
                    "A10_state": "STRUCTURED",
                    "modality_class": "MAB",
                    "endpoint_data_type": "PK_CONCENTRATION",
                    "analyte_role": "",
                    "_family_override": "F28",
                })

    return scenarios


def _hash(scn: dict[str, Any]) -> str:
    key = "|".join(str(scn[k]) for k in sorted(scn.keys()))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def run(out_dir: Path, reports_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    enum_rows = _enumerate()

    # de-duplicate
    seen: set[tuple] = set()
    unique_rows: list[dict[str, Any]] = []
    for scn in enum_rows:
        key = tuple(scn[k] for k in sorted(scn.keys()))
        if key not in seen:
            seen.add(key)
            unique_rows.append(scn)

    cols = [
        "scenario_id", "A0_state", "A1_state", "A2_state", "A3_state",
        "A4_state", "A5_state", "A6_state", "A7_state", "A8_state",
        "A9_state", "A10_state", "modality_class", "endpoint_data_type",
        "analyte_role", "terminal_state", "q_code", "family_id",
    ]

    raw_csv = out_dir / "scenario_universe_raw.csv"
    valid_csv = out_dir / "scenario_universe_valid_candidate.csv"
    invalid_csv = reports_dir / "invalid_scenario_log.csv"

    invalid_log: list[list] = []
    valid_rows: list[dict[str, Any]] = []
    raw_rows: list[dict[str, Any]] = []

    for scn in unique_rows:
        term, q, hint = _resolve(scn)
        scn["scenario_id"] = _hash(scn)
        scn["terminal_state"] = term
        scn["q_code"] = q or ""
        scn["family_id"] = _family(scn, term, hint)
        # validate: no Q15 standalone, no Q17
        if scn["q_code"] in {"Q15", "Q17"}:
            invalid_log.append([scn["scenario_id"], "forbidden_qcode", scn["q_code"]])
            continue
        if term == "QUARANTINE" and not q:
            invalid_log.append([scn["scenario_id"], "missing_qcode", ""])
            continue
        raw_rows.append(scn)
        valid_rows.append(scn)

    def _write(path: Path, rows: list[dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow(r)

    _write(raw_csv, raw_rows)
    _write(valid_csv, valid_rows)
    with invalid_csv.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["scenario_id", "reason", "detail"])
        wr.writerows(invalid_log)

    return {
        "total": len(unique_rows),
        "valid": len(valid_rows),
        "invalid": len(invalid_log),
        "term_dist": Counter(r["terminal_state"] for r in valid_rows),
        "modality_dist": Counter(r["modality_class"] for r in valid_rows),
        "edt_dist": Counter(r["endpoint_data_type"] or "(none)" for r in valid_rows),
        "q15_solo": sum(1 for r in valid_rows if r["q_code"] == "Q15"),
        "q17": sum(1 for r in valid_rows if r["q_code"] == "Q17"),
        "fam_dist": Counter(r["family_id"] for r in valid_rows),
    }


def write_report(stats: dict[str, Any], report_md: Path) -> None:
    lines = [
        "# Scenario Generation Report",
        "",
        f"total_raw_combinations: {stats['total']}",
        f"valid_count: {stats['valid']}",
        f"invalid_count: {stats['invalid']}",
        "",
        "## terminal_state distribution",
    ]
    for k, v in sorted(stats["term_dist"].items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## modality_class distribution")
    for k, v in sorted(stats["modality_dist"].items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## endpoint_data_type distribution")
    for k, v in sorted(stats["edt_dist"].items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## family_id distribution")
    for k, v in sorted(stats["fam_dist"].items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append(f"Q15 standalone violations: {stats['q15_solo']}")
    lines.append(f"Q17 violations: {stats['q17']}")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=ROOT / "data" / "scenario_universe", type=Path)
    parser.add_argument("--reports-dir", default=ROOT / "reports", type=Path)
    args = parser.parse_args(argv)
    stats = run(args.out_dir, args.reports_dir)
    write_report(stats, args.reports_dir / "scenario_generation_report.md")
    print(f"total: {stats['total']} valid: {stats['valid']} invalid: {stats['invalid']}")
    return 0


if __name__ == "__main__":
    main()
