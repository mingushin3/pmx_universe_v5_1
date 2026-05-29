"""Derive action_label, action_sequence and parameter_policy for every
scenario in `scenario_universe_v1.0.csv` and write
`data/action_labels/scenario_action_table_draft.csv` (P71)."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _label(scn: dict[str, str]) -> tuple[str, list[str], dict]:
    term = scn["terminal_state"]
    q = scn["q_code"]
    fam = scn["family_id"]
    a5 = scn["A5_state"]
    a4 = scn["A4_state"]
    a8 = scn["A8_state"]
    a10 = scn["A10_state"]
    a9 = scn["A9_state"]
    modality = scn["modality_class"]
    edt = scn["endpoint_data_type"]
    role = scn["analyte_role"]

    seq: list[str] = ["parse_source"]
    policy: dict = {}

    if term == "INVALID":
        return (f"INVALID_{fam}", ["flag_invalid"], {})
    if term == "UNSUPPORTED":
        return (f"UNSUPPORTED_{fam}", ["flag_unsupported"], {})
    if term == "QUARANTINE":
        # name = QUARANTINE_<reason>_<q_code>
        reason = "GENERIC"
        if a5 == "BIOANALYTICAL-FINAL-FLAG-MISSING":
            reason = "BIO_FINAL_FLAG"
        elif a5 == "BLQ-NO-POLICY":
            reason = "BLQ_NO_POLICY"
        elif a5 == "LLOQ-MISSING":
            reason = "LLOQ_MISSING"
        elif a5 == "CELLULAR-LLOQ-POLICY-MISSING":
            reason = "CELLULAR_NO_LLOQ"
        elif a5 == "IMMUNOGEN-POSITIVITY-MISSING":
            reason = "IMMUNOGEN_NO_RULE"
        elif edt == "MATERNAL_INFANT_PK" and scn["A1_state"] == "ID-DYAD-UNLINKED-POLICY-MISSING":
            reason = "MATERNAL_NO_DYAD"
        elif edt == "MATERNAL_INFANT_PK" and scn["A2_state"] == "TIME-ANCHOR-AMBIGUOUS":
            reason = "MATERNAL_NO_ANCHOR"
        elif a4 == "ADDL-ACTUAL-CONFLICT":
            reason = "ADDL_CONFLICT"
        elif a4 == "MISSING-NO-POLICY":
            reason = "REGIMEN_NO_POLICY"
        elif a8 == "CMT-POLICY-MISSING":
            reason = "CMT_POLICY_MISSING"
        elif (a8 in {"MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED"}
              and modality in {"ADC", "BISPECIFIC", "CELL_THERAPY"} and not role):
            reason = "ANALYTE_ROLE_MISSING"
        elif a9 == "REANALYSIS-FINAL-MISSING":
            reason = "REANALYSIS_NO_FINAL"
        elif a10 == "SEMI-STRUCTURED-LEGACY-FLAG":
            reason = "LEGACY_FLAG_UNDOC"
        elif a10 == "RWD-ADHERENCE-UNRESOLVED":
            reason = "RWD_ADHERENCE"
        elif scn["A0_state"] == "AIC-MISSING":
            reason = "AIC_MISSING"
        return (f"QUARANTINE_{reason}_{q}", ["parse_source", "flag_quarantine"], {"q_code": q})

    # REPAIR or AUTO
    if scn["A1_state"] == "ID-DUPLICATE-RESOLVABLE":
        seq.append("map_subject_id")
        policy["id_disambiguation_policy"] = "site_prefix"
    if scn["A1_state"] == "ID-DYAD-LINKABLE":
        seq.append("attach_dyad_linkage")
        policy["dyad_linkage_policy"] = "mother_id_on_infant_row"

    if scn["A2_state"] == "TIME-ACTUAL-VS-NOMINAL-RESOLVABLE":
        seq.append("derive_time_nominal")
        policy["time_policy"] = "actual_preferred"
    if scn["A2_state"] == "TIME-ELAPSED-RESOLVABLE":
        if edt == "MATERNAL_INFANT_PK" or edt == "MILK_PK" or fam == "F28":
            seq.append("derive_time_postpartum_anchor")
            policy["delivery_anchor_policy"] = "delivery_date"
        else:
            seq.append("derive_time_elapsed")
            policy["elapsed_anchor_policy"] = "first_dose"

    if scn["A3_state"] == "DOSE-WEIGHT-BASED":
        seq.append("reconstruct_dose_weight")
        policy["dose_reconstruction_policy"] = "weight_based"
    elif scn["A3_state"] == "DOSE-BSA-BASED":
        seq.append("reconstruct_dose_bsa")
        policy["dose_reconstruction_policy"] = "bsa_based"
    elif scn["A3_state"] == "DOSE-LOADING-MAINTENANCE":
        seq.append("reconstruct_loading_maintenance")
        policy["dose_reconstruction_policy"] = "loading_maintenance"
    elif scn["A3_state"] == "DOSE-INFUSION-STOP-RESTART":
        seq.append("reconstruct_infusion_stop_restart")
        policy["infusion_reconstruction_policy"] = "stop_restart_from_events"
    elif scn["A3_state"] == "DOSE-TITRATION":
        seq.append("reconstruct_dose_titration")
        policy["dose_adaptation_policy"] = "project_specific"
    elif scn["A3_state"] == "DOSE-ADDL-ACTUAL-CONFLICT":
        seq.append("resolve_addl_actual_conflict")
        policy["addl_actual_conflict_policy"] = "actual_priority"

    if scn["A4_state"] == "TITRATION-ADAPTIVE" and "reconstruct_dose_titration" not in seq:
        seq.append("reconstruct_dose_titration")
        policy["dose_adaptation_policy"] = "project_specific"
    elif scn["A4_state"] == "LOADING-MAINTENANCE" and "reconstruct_loading_maintenance" not in seq:
        seq.append("reconstruct_loading_maintenance")
        policy["dose_reconstruction_policy"] = "loading_maintenance"
    elif scn["A4_state"] == "INFUSION-STOP-RESTART" and "reconstruct_infusion_stop_restart" not in seq:
        seq.append("reconstruct_infusion_stop_restart")
        policy["infusion_reconstruction_policy"] = "stop_restart_from_events"

    if scn["A5_state"] == "BLQ-DEFINED-POLICY":
        seq.append("canonicalize_blq")
        policy["blq_handling_policy"] = "M3"
    if scn["A5_state"] == "CELLULAR-BLQ-DEFINED":
        seq.append("canonicalize_cellular_blq")
        policy["cellular_LLOQ_derivation_policy"] = "poisson_derived"
    if scn["A5_state"] == "IMMUNOGEN-POSITIVITY-DEFINED":
        seq.append("adjudicate_immunogenicity_positivity")
        policy["positivity_adjudication_rule"] = "screening_plus_confirmation"
    if edt == "MILK_PK":
        seq.append("assign_milk_matrix_lloq")
        policy["milk_matrix_lloq_policy"] = "matrix_specific_lloq"

    if a8 == "SINGLE-ANALYTE":
        seq.append("assign_cmt_single")
    elif a8 == "DDI-VICTIM-ONLY":
        seq.append("assign_cmt_ddi_victim_only")
        policy["cmt_analyte_policy"] = "ddi_victim_only"
    elif a8 == "DDI-VICTIM-PERPETRATOR":
        seq.append("assign_cmt_ddi_victim_perpetrator")
        policy["cmt_analyte_policy"] = "ddi_dual_cmt"
        policy["dual_cmt_policy"] = "victim_low_perp_high"
    elif a8 == "MULTI-CMT-DEFINED" or a8 == "METABOLITE-DEFINED":
        if modality in {"ADC", "BISPECIFIC", "CELL_THERAPY"} and role:
            seq.append("assign_cmt_with_analyte_role")
            policy["analyte_role_declaration"] = role
            policy["cmt_analyte_policy"] = "multi_analyte_role_tagged"
        else:
            seq.append("assign_cmt_multi")
            policy["cmt_analyte_policy"] = "multi_with_rules"

    if scn["A7_state"] == "PRODUCT-LEVEL-COVARIATE":
        seq.append("attach_covariate_product_level")
        policy["product_level_covariate_linkage_policy"] = "lot_to_subject_via_manufacturing_record"

    seq.append("assign_evid")
    if scn["A9_state"] == "REANALYSIS-FINAL-RESOLVABLE":
        seq.append("resolve_reanalysis_final")
        policy["reanalysis_final_selection_policy"] = "reanalysis_priority"

    seq.append("sort_records")
    seq.append("export_nonmem_ready")

    repair_set = {"map_subject_id", "attach_dyad_linkage", "derive_time_nominal",
                  "derive_time_elapsed", "derive_time_postpartum_anchor",
                  "reconstruct_dose_weight", "reconstruct_dose_bsa",
                  "reconstruct_dose_titration", "reconstruct_loading_maintenance",
                  "reconstruct_infusion_stop_restart", "resolve_addl_actual_conflict",
                  "canonicalize_blq", "canonicalize_cellular_blq",
                  "adjudicate_immunogenicity_positivity", "assign_milk_matrix_lloq",
                  "assign_cmt_with_analyte_role", "assign_cmt_multi",
                  "assign_cmt_ddi_victim_only", "assign_cmt_ddi_victim_perpetrator",
                  "attach_covariate_product_level", "resolve_reanalysis_final"}
    repair_fns_in_seq = [fn for fn in seq if fn in repair_set]

    if term == "AUTO":
        seq = [fn for fn in seq if fn not in repair_set]
        name = f"AUTO_{fam}_{modality}"
    elif not repair_fns_in_seq:
        # No repair function found despite REPAIR terminal -> reclassify AUTO.
        seq = [fn for fn in seq if fn not in repair_set]
        name = f"AUTO_{fam}_{modality}"
    else:
        SHORT = {
            "map_subject_id": "MAPID",
            "attach_dyad_linkage": "DYAD",
            "derive_time_nominal": "TNOM",
            "derive_time_elapsed": "TEL",
            "derive_time_postpartum_anchor": "TPP",
            "reconstruct_dose_weight": "DWT",
            "reconstruct_dose_bsa": "DBSA",
            "reconstruct_dose_titration": "DTITR",
            "reconstruct_loading_maintenance": "DLM",
            "reconstruct_infusion_stop_restart": "DINF",
            "resolve_addl_actual_conflict": "DADDL",
            "canonicalize_blq": "BLQ",
            "canonicalize_cellular_blq": "CBLQ",
            "adjudicate_immunogenicity_positivity": "ADA",
            "assign_milk_matrix_lloq": "MILK",
            "assign_cmt_with_analyte_role": "CMTROLE",
            "assign_cmt_multi": "CMTM",
            "assign_cmt_ddi_victim_only": "DDIV",
            "assign_cmt_ddi_victim_perpetrator": "DDIVP",
            "attach_covariate_product_level": "PROD",
            "resolve_reanalysis_final": "REAN",
        }
        codes = [SHORT[fn] for fn in repair_fns_in_seq]
        name = f"REPAIR_{fam}_{'_'.join(codes)}"
    return (name, seq, policy)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default=ROOT / "data" / "scenario_universe" / "scenario_universe_v1.0.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "data" / "action_labels" / "scenario_action_table_draft.csv", type=Path)
    args = parser.parse_args(argv)

    with args.universe.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    out_rows = []
    for r in rows:
        label, seq, policy = _label(r)
        # If REPAIR row collapsed to AUTO above, also flip terminal_state
        eff_terminal = r["terminal_state"]
        if label.startswith("AUTO_") and eff_terminal == "REPAIR":
            eff_terminal = "AUTO"
            seq = [s for s in seq if not s.startswith("reconstruct")]
        out_rows.append({
            "scenario_id": r["scenario_id"],
            "family_id": r["family_id"],
            "terminal_state": eff_terminal,
            "q_code": r["q_code"],
            "candidate_action_label": label,
            "action_sequence": " -> ".join(seq),
            "parameter_policy": json.dumps(policy, sort_keys=True),
            "rationale": "auto-derived per v5.1 label rules",
            "confidence": "HIGH",
            "label_status": "draft",
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {len(out_rows)} draft labels -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
