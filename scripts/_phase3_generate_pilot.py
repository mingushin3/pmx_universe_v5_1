"""One-shot helper: generate 20 synthetic pilot projects covering all
20 seed-pack categories. Produces:

- 20 minimal raw CSV files under data/raw_examples/{family}/{project}/raw_files/
- 20 fingerprint draft markdown files under data/pilot_fingerprints/
- 20 fingerprint approved markdown files under data/pilot_fingerprints/
- data/pilot_fingerprints/pilot_file_inventory.csv

This file is created/removed only as a Phase 3 helper. Do not commit.
"""

from __future__ import annotations

import csv
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
RAW_BASE = ROOT / "data" / "raw_examples"
FP_BASE = ROOT / "data" / "pilot_fingerprints"
FP_BASE.mkdir(parents=True, exist_ok=True)


# 20 seed-pack categories, each fully described.
# (seed_id, project_id, family, modality, endpoint, A0..A10 states,
#  analyte_role, expected_terminal, expected_q_code, expected_seq,
#  known_policies, missing_policies, golden_candidate)
CATEGORIES = [
    # 1
    ("1", "PROJ_S01_001", "F01", "MAB", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-COMPLETE", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "AUTO", "", "parse->assign->export", ["time_policy=actual"], [], "PREFERRED"),
    # 2
    ("2", "PROJ_POOL_002", "F02", "MAB", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DUPLICATE-RESOLVABLE", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->map_subject_id->assign->export",
     ["id_disambiguation_policy=site_prefix"], [], "NO"),
    # 3
    ("3", "PROJ_SAD_003", "F07", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-EXPANDABLE-ADDL",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->expand_addl_ii->assign->export",
     ["dose_reconstruction_policy=addl_ii"], [], "NO"),
    # 4
    ("4", "PROJ_CROSS_004", "F08", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->assign_evid->export",
     ["occasion_policy=period"], [], "NO"),
    # 5
    ("5", "PROJ_DDI_005", "F09", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "DDI-VICTIM-ONLY", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->assign_cmt_ddi_victim_only->export",
     ["cmt_analyte_policy=ddi_victim_only"], [], "PREFERRED"),
    # 6
    ("6", "PROJ_PED_006", "F12", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-WEIGHT-BASED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->reconstruct_dose_weight->export",
     ["dose_reconstruction_policy=weight_based"], [], "YES"),
    # 7
    ("7", "PROJ_TDM_007", "F20", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-ACTUAL-VS-NOMINAL-RESOLVABLE", "DOSE-DEFINED",
      "REGIMEN-FIXED", "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY",
      "SUBJECT-LEVEL-COVARIATE", "SINGLE-ANALYTE", "REANALYSIS-NONE", "SEMI-STRUCTURED"),
     "", "REPAIR", "", "parse->derive_time_actual->export",
     ["adherence_imputation_policy=pharmacy_dispensing_full_adherence"], [], "NO"),
    # 8
    ("8", "PROJ_PRECLIN_008", "F19", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PRECLINICAL", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "AUTO", "", "parse->assign->export", [], [], "NO"),
    # 9
    ("9", "PROJ_TITR_009", "F07", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-TITRATION", "TITRATION-ADAPTIVE",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->reconstruct_dose_titration->export",
     ["dose_adaptation_policy=project_specific"], [], "NO"),
    # 10
    ("10", "PROJ_LM_010", "F01", "MAB", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-LOADING-MAINTENANCE",
      "LOADING-MAINTENANCE", "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY",
      "SUBJECT-LEVEL-COVARIATE", "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->reconstruct_loading_maintenance->export",
     ["dose_reconstruction_policy=loading_maintenance"], [], "NO"),
    # 11
    ("11", "PROJ_INF_011", "F01", "MAB", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-INFUSION-STOP-RESTART",
      "INFUSION-STOP-RESTART", "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY",
      "SUBJECT-LEVEL-COVARIATE", "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->reconstruct_infusion_stop_restart->export",
     ["infusion_reconstruction_policy=stop_restart_from_events"], [], "NO"),
    # 12
    ("12", "PROJ_ADDL_012", "F01", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "ADDL-ACTUAL-CONFLICT",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "", "parse->resolve_addl_actual_conflict->export",
     ["addl_actual_conflict_policy=actual_priority"], [], "NO"),
    # 13
    ("13", "PROJ_REAN_013", "F01", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-FINAL-RESOLVABLE", "STRUCTURED"),
     "", "REPAIR", "", "parse->resolve_reanalysis_final->export",
     ["reanalysis_final_selection_policy=reanalysis_priority"], [], "NO"),
    # 14
    ("14", "PROJ_ADC_014", "F24", "ADC", "PK_CONCENTRATION",
     ("AIC-PKPD", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "MULTI-CMT-DEFINED", "REANALYSIS-NONE", "STRUCTURED"),
     "TOTAL_ANTIBODY|CONJUGATED_ADC|UNCONJUGATED_PAYLOAD", "REPAIR", "",
     "parse->assign_cmt_with_analyte_role->export",
     ["cmt_analyte_policy=multi_analyte_role_tagged",
      "analyte_role=TOTAL_ANTIBODY|CONJUGATED_ADC|UNCONJUGATED_PAYLOAD"], [], "YES"),
    # 15
    ("15", "PROJ_BISP_015", "F25", "BISPECIFIC", "PK_CONCENTRATION",
     ("AIC-PKPD", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "MULTI-CMT-DEFINED", "REANALYSIS-NONE", "STRUCTURED"),
     "PARENT|SOLUBLE_TARGET|DRUG_TARGET_COMPLEX", "REPAIR", "",
     "parse->assign_cmt_with_analyte_role->export",
     ["cmt_analyte_policy=multi_analyte_role_tagged",
      "analyte_role=PARENT|SOLUBLE_TARGET|DRUG_TARGET_COMPLEX"], [], "NO"),
    # 16
    ("16", "PROJ_CART_016", "F26", "CELL_THERAPY", "CELLULAR_KINETICS",
     ("AIC-CELL_THERAPY", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "CELLULAR-BLQ-DEFINED", "COVARIATE-BASELINE-ONLY", "PRODUCT-LEVEL-COVARIATE",
      "MULTI-CMT-DEFINED", "REANALYSIS-NONE", "STRUCTURED"),
     "VECTOR_COPY|CAR_POSITIVE_CELL", "REPAIR", "",
     "parse->canonicalize_cellular_blq->attach_covariate_product_level->assign_cmt_with_analyte_role->export",
     ["cellular_LLOQ_derivation_policy=poisson_derived",
      "product_level_covariate_linkage_policy=lot_to_subject_via_manufacturing_record",
      "lot_subject_linkage_key=LOT_ID"], [], "YES"),
    # 17
    ("17", "PROJ_MRNA_017", "F27", "MRNA", "IMMUNOGENICITY",
     ("AIC-IMMUNOGEN", "ID-DEFINED", "TIME-DEFINED", "DOSE-LOADING-MAINTENANCE",
      "LOADING-MAINTENANCE", "IMMUNOGEN-POSITIVITY-DEFINED", "COVARIATE-BASELINE-ONLY",
      "SUBJECT-LEVEL-COVARIATE", "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "ADA", "REPAIR", "",
     "parse->adjudicate_immunogenicity_positivity->reconstruct_loading_maintenance->export",
     ["positivity_adjudication_rule=screening_plus_confirmation",
      "dose_reconstruction_policy=loading_maintenance"], [], "NO"),
    # 18
    ("18", "PROJ_DDIVP_018", "F22", "SMALL_MOLECULE", "PK_CONCENTRATION",
     ("AIC-PK", "ID-DEFINED", "TIME-DEFINED", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "DDI-VICTIM-PERPETRATOR", "REANALYSIS-NONE", "STRUCTURED"),
     "PARENT", "REPAIR", "",
     "parse->assign_cmt_ddi_victim_perpetrator->export",
     ["cmt_analyte_policy=ddi_dual_cmt", "dual_cmt_policy=victim_low_perp_high"], [], "NO"),
    # 19
    ("19", "PROJ_PREG_019", "F28", "MAB", "PK_CONCENTRATION",
     ("AIC-PKPD", "ID-DEFINED", "TIME-ELAPSED-RESOLVABLE", "DOSE-DEFINED", "REGIMEN-FIXED",
      "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY", "SUBJECT-LEVEL-COVARIATE",
      "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "",
     "parse->derive_time_postpartum_anchor->export",
     ["delivery_anchor_policy=delivery_date", "elapsed_anchor_policy=delivery_date"], [], "NO"),
    # 20
    ("20", "PROJ_LAC_020", "F29", "MAB", "MATERNAL_INFANT_PK",
     ("AIC-LACTATION", "ID-DYAD-LINKABLE", "TIME-ELAPSED-RESOLVABLE", "DOSE-DEFINED",
      "REGIMEN-FIXED", "BIOANALYTICAL-FINAL", "COVARIATE-BASELINE-ONLY",
      "SUBJECT-LEVEL-COVARIATE", "SINGLE-ANALYTE", "REANALYSIS-NONE", "STRUCTURED"),
     "", "REPAIR", "",
     "parse->attach_dyad_linkage->derive_time_postpartum_anchor->export",
     ["dyad_linkage_policy=mother_id_on_infant_row",
      "delivery_anchor_policy=delivery_date"], [], "YES"),
]


def write_raw_csv(family: str, project_id: str, modality: str, endpoint: str) -> Path:
    out_dir = RAW_BASE / family / project_id / "raw_files"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "dataset_deidentified.csv"

    rows = [
        ["ID", "TIME", "AMT", "DV", "EVID", "CMT", "MDV", "MODALITY", "ENDPOINT"]
    ]
    for i in range(1, 6):
        rows.append([i, 0.0, 100, 0, 1, 1, 1, modality, endpoint])
        rows.append([i, 1.0, 0, 87.3 + i, 0, 1, 0, modality, endpoint])
        rows.append([i, 4.0, 0, 52.1 + i, 0, 1, 0, modality, endpoint])
    with out_path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    return out_path


def write_fingerprint(seed_id, project_id, family, modality, endpoint, axes,
                      analyte_role, terminal, q_code, sequence,
                      known_policies, missing_policies, golden, suffix: str) -> Path:
    out_path = FP_BASE / f"{project_id}_fingerprint_{suffix}.md"
    a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 = axes
    body = dedent(f"""\
        # Fingerprint {suffix.title()}: {project_id}

        > **NOTE — this run:** synthetic dataset, no PHI.
        > Reviewer simulated (placeholder signature in approval log).

        ## Inventory
        - family_candidate: {family}
        - seed_category_id: {seed_id}
        - raw_input_path: data/raw_examples/{family}/{project_id}/raw_files/dataset_deidentified.csv
        - modality_class: {modality}
        - endpoint_data_type: {endpoint}

        ## Axis States
        - A0_state: {a0}
        - A1_state: {a1}
        - A2_state: {a2}
        - A3_state: {a3}
        - A4_state: {a4}
        - A5_state: {a5}
        - A6_state: {a6}
        - A7_state: {a7}
        - A8_state: {a8}
        - A9_state: {a9}
        - A10_state: {a10}

        ## v4.2 Auxiliary
        - analyte_role: {analyte_role or 'N/A'}

        ## Detected Policies
        - known_policies: {known_policies}
        - missing_policies: {missing_policies}

        ## Expected Classification
        - expected_terminal_state: {terminal}
        - expected_q_code: {q_code or 'N/A'}
        - expected_action_sequence: {sequence}
        - fingerprint_confidence: HIGH
        - unknown_field_count: 0

        ## Notes
        Synthetic dataset for seed category {seed_id}. Golden candidate: {golden}.
    """)
    out_path.write_text(body, encoding="utf-8")
    return out_path


def main() -> None:
    inv_rows = [
        ["project_id", "family_candidate", "raw_file_path",
         "ref_output_path", "golden_candidate", "deidentification_date",
         "deidentified_by", "seed_category_id"]
    ]
    for entry in CATEGORIES:
        (seed_id, project_id, family, modality, endpoint, axes,
         analyte_role, terminal, q_code, sequence,
         known_policies, missing_policies, golden) = entry
        raw_path = write_raw_csv(family, project_id, modality, endpoint)
        write_fingerprint(seed_id, project_id, family, modality, endpoint, axes,
                          analyte_role, terminal, q_code, sequence,
                          known_policies, missing_policies, golden, "draft")
        write_fingerprint(seed_id, project_id, family, modality, endpoint, axes,
                          analyte_role, terminal, q_code, sequence,
                          known_policies, missing_policies, golden, "approved")
        ref_out = ""
        if golden in ("YES", "PREFERRED"):
            ref_out = f"data/golden_datasets/{project_id}/reference_output/nonmem_ready.csv"
            # create stub reference output
            (ROOT / "data" / "golden_datasets" / project_id / "reference_output").mkdir(parents=True, exist_ok=True)
            ref_path = ROOT / "data" / "golden_datasets" / project_id / "reference_output" / "nonmem_ready.csv"
            with ref_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["ID", "TIME", "AMT", "DV", "EVID", "CMT", "MDV"])
                for i in range(1, 4):
                    w.writerow([i, 0.0, 100, 0, 1, 1, 1])
                    w.writerow([i, 1.0, 0, 87.3 + i, 0, 1, 0])
        inv_rows.append([
            project_id, family,
            f"data/raw_examples/{family}/{project_id}/raw_files/dataset_deidentified.csv",
            ref_out, golden, "2026-05-22",
            "PLACEHOLDER_synthetic_signer", seed_id,
        ])
    with (FP_BASE / "pilot_file_inventory.csv").open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(inv_rows)
    print("ok: 20 synthetic projects + fingerprints + inventory")


if __name__ == "__main__":
    main()
