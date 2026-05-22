"""Generate raw_decision_table.csv from scenario_action_table_locked.csv.

For each scenario, compute deterministic Y/N/NA answer for N0..N8 per
the detection rules in candidate_node_dictionary_with_costs.csv (mirrors
pilot_node_test.py logic)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REQUIRING_ENDPOINT = {"AIC-PKPD", "AIC-ER", "AIC-TTE", "AIC-BIOMARKER",
                      "AIC-CELL_THERAPY", "AIC-IMMUNOGEN", "AIC-LACTATION"}
MULTI_ANALYTE_A8 = {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED"}
ANALYTE_MODALITIES = {"ADC", "BISPECIFIC", "CELL_THERAPY", "GENE_THERAPY"}


def _eval(r: dict[str, str]) -> dict[str, str]:
    a0 = r["A0_state"]; a1 = r["A1_state"]; a2 = r["A2_state"]; a3 = r["A3_state"]
    a4 = r["A4_state"]; a5 = r["A5_state"]; a6 = r["A6_state"]; a7 = r["A7_state"]
    a8 = r["A8_state"]; a9 = r["A9_state"]; a10 = r["A10_state"]
    modality = r["modality_class"]; edt = r["endpoint_data_type"]; role = r["analyte_role"]
    term = r["terminal_state"]

    n: dict[str, str] = {}

    # N0
    if a0 == "AIC-MISSING" or a0 == "AIC-UNRECOVERABLE":
        n["N0"] = "N"
    elif a0 in REQUIRING_ENDPOINT and not edt:
        n["N0"] = "N"
    else:
        n["N0"] = "Y"

    # N1
    if a1 in {"ID-UNRECOVERABLE", "ID-AMBIGUOUS", "ID-DYAD-UNLINKED-POLICY-MISSING"}:
        n["N1"] = "N"
    else:
        n["N1"] = "Y"

    # N2
    if a2 in {"TIME-UNRECOVERABLE", "TIME-ANCHOR-AMBIGUOUS"}:
        n["N2"] = "N"
    else:
        n["N2"] = "Y"

    # N3
    if a3 in {"DOSE-UNRECOVERABLE", "DOSE-AMBIGUOUS"}:
        n["N3"] = "N"
    elif a4 in {"UNRECOVERABLE", "MISSING-NO-POLICY"}:
        n["N3"] = "N"
    elif a4 == "ADDL-ACTUAL-CONFLICT" and a3 == "DOSE-ADDL-ACTUAL-CONFLICT":
        n["N3"] = "N"
    else:
        n["N3"] = "Y"

    # N4
    if a5 in {"ABSENT", "BIOANALYTICAL-FINAL-FLAG-MISSING",
              "BLQ-NO-POLICY", "LLOQ-MISSING",
              "CELLULAR-LLOQ-POLICY-MISSING", "IMMUNOGEN-POSITIVITY-MISSING"}:
        n["N4"] = "N"
    elif a8 == "CMT-POLICY-MISSING":
        n["N4"] = "N"
    elif a8 in MULTI_ANALYTE_A8 and modality in ANALYTE_MODALITIES and not role:
        n["N4"] = "N"
    else:
        n["N4"] = "Y"

    # N5
    if a5 in {"BLQ-NO-POLICY", "LLOQ-MISSING", "CELLULAR-LLOQ-POLICY-MISSING"}:
        n["N5"] = "N"
    else:
        n["N5"] = "Y"

    # N6 (compute always — preserves distinguishing power)
    if a6 == "COVARIATE-IMPUTATION-POLICY-MISSING":
        n["N6"] = "N"
    elif a7 in {"KEY-MISSING", "POLICY-MISSING"}:
        n["N6"] = "N"
    else:
        n["N6"] = "Y"

    # N7
    if a9 in {"REANALYSIS-FINAL-MISSING", "PROTOCOL-DEVIATION-NO-POLICY", "IRRECONCILABLE"}:
        n["N7"] = "N"
    else:
        n["N7"] = "Y"

    # N8 — policy availability for the proposed action_sequence
    if term == "QUARANTINE" and r["q_code"] in {"Q01", "Q04", "Q06", "Q07", "Q08", "Q09",
                                                  "Q12", "Q13", "Q14", "Q15A", "Q15B",
                                                  "Q15C", "Q15D", "Q16", "Q18", "Q19"}:
        n["N8"] = "N"
    elif term in {"INVALID", "UNSUPPORTED"}:
        n["N8"] = "N"
    else:
        n["N8"] = "Y"

    # N9-N12: P92 added for v4.2 endpoint/modality distinction
    n["N9"] = "Y" if edt == "CELLULAR_KINETICS" else "N"
    n["N10"] = "Y" if edt == "IMMUNOGENICITY" else "N"
    n["N11"] = "Y" if edt in {"MATERNAL_INFANT_PK", "MILK_PK"} else "N"
    n["N12"] = "Y" if modality in {"ADC", "BISPECIFIC", "CELL_THERAPY", "GENE_THERAPY", "MRNA"} else "N"

    # N13-N17: P92 round 2 — action-sequence content
    seq = r.get("action_sequence", "")
    n["N13"] = "Y" if ("canonicalize_blq" in seq or "canonicalize_cellular_blq" in seq) else "N"
    n["N14"] = "Y" if ("reconstruct_dose" in seq or "expand_addl_ii" in seq
                        or "resolve_addl_actual_conflict" in seq
                        or "reconstruct_loading_maintenance" in seq
                        or "reconstruct_infusion_stop_restart" in seq) else "N"
    n["N15"] = "Y" if "map_subject_id" in seq else "N"
    n["N16"] = "Y" if "resolve_reanalysis_final" in seq else "N"
    n["N17"] = "Y" if ("derive_time_postpartum_anchor" in seq or "derive_time_elapsed" in seq) else "N"
    n["N18"] = "Y" if ("assign_cmt_multi" in seq or "assign_cmt_ddi" in seq
                        or "assign_cmt_with_analyte_role" in seq) else "N"
    n["N19"] = "Y" if ("attach_covariate" in seq or "attach_dyad_linkage" in seq) else "N"
    n["N20"] = "Y" if a5 == "BIOANALYTICAL-FINAL-FLAG-MISSING" else "N"
    n["N21"] = "Y" if a8 in {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED"} else "N"
    n["N22"] = "Y" if a8 == "DDI-VICTIM-PERPETRATOR" else "N"
    n["N23"] = "Y" if a10 == "SEMI-STRUCTURED-LEGACY-FLAG" else "N"
    n["N24"] = "Y" if a4 == "ADDL-ACTUAL-CONFLICT" else "N"
    n["N25"] = "Y" if modality in {"ADC", "BISPECIFIC", "CELL_THERAPY", "GENE_THERAPY"} else "N"
    n["N26"] = "Y" if "assign_cmt_with_analyte_role" in seq else "N"
    n["N27"] = "Y" if a5 == "CELLULAR-BLQ-DEFINED" else "N"
    n["N28"] = "Y" if "canonicalize_cellular_blq" in seq else "N"
    n["N29"] = "Y" if "adjudicate_immunogenicity_positivity" in seq else "N"

    return n


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action-table", default=ROOT / "data" / "action_labels" / "scenario_action_table_locked.csv", type=Path)
    parser.add_argument("--universe", default=ROOT / "data" / "scenario_universe" / "scenario_universe_v1.0.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "data" / "decision_table" / "raw_decision_table.csv", type=Path)
    args = parser.parse_args(argv)

    with args.action_table.open("r", encoding="utf-8", newline="") as f:
        action_rows = list(csv.DictReader(f))
    with args.universe.open("r", encoding="utf-8", newline="") as f:
        universe_by_id = {r["scenario_id"]: r for r in csv.DictReader(f)}

    # Merge: action row + axis info from universe
    rows = []
    for ar in action_rows:
        ur = universe_by_id.get(ar["scenario_id"], {})
        rows.append({**ar, **ur})

    out_rows = []
    for r in rows:
        n = _eval(r)
        out_rows.append({
            "scenario_id": r["scenario_id"],
            "family_id": r["family_id"],
            "terminal_state": r["terminal_state"],
            "q_code": r["q_code"],
            "action_label": r["candidate_action_label"],
            "action_sequence_hash": _sha(r["action_sequence"]),
            "parameter_policy_hash": _sha(r["parameter_policy"]),
            "required_policy_set": ",".join(sorted(json.loads(r["parameter_policy"] or "{}").keys())),
            **{f"N{i}": n[f"N{i}"] for i in range(30)},
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {len(out_rows)} decision rows -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
