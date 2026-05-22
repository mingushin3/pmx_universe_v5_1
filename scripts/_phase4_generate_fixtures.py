"""One-shot helper: generate ≥20 synthetic fixtures (CSV + expected YAML)
for repair_executor testing."""
from __future__ import annotations

import csv
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "tests" / "fixtures"
FX.mkdir(parents=True, exist_ok=True)


def write_csv(name: str, header: list[str], rows: list[list]) -> None:
    with (FX / f"{name}.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def write_expected(name: str, body: str) -> None:
    (FX / f"{name}_expected.yaml").write_text(dedent(body).strip() + "\n", encoding="utf-8")


# --- ROUTINE (5) ---

write_csv("fixture_blq_policy_present",
         ["ID", "TIME", "DV", "EVID", "MDV", "LLOQ"],
         [[1, 0, 100, 1, 1, 0.1], [1, 1, 0.05, 0, 0, 0.1]])
write_expected("fixture_blq_policy_present", """
    fixture_name: fixture_blq_policy_present
    input_csv: fixture_blq_policy_present.csv
    input_aic: { blq_handling_policy: M3 }
    expected_terminal: REPAIR
    expected_q_code: null
    expected_action_sequence: [parse_source, repair_blq_canonicalization, export_nonmem_ready]
""")

write_csv("fixture_blq_policy_missing",
         ["ID", "TIME", "DV", "EVID", "MDV"],
         [[1, 0, 100, 1, 1], [1, 1, 0.05, 0, 0]])
write_expected("fixture_blq_policy_missing", """
    fixture_name: fixture_blq_policy_missing
    input_csv: fixture_blq_policy_missing.csv
    input_aic: {}
    expected_terminal: QUARANTINE
    expected_q_code: Q01
""")

write_csv("fixture_time_actual",
         ["ID", "ACTUAL_TIME", "ANCHOR_TIME", "DV"],
         [[1, 5.0, 0.0, 12.0]])
write_expected("fixture_time_actual", """
    fixture_name: fixture_time_actual
    expected_terminal: REPAIR
    expected_q_code: null
""")

write_csv("fixture_time_policy_missing",
         ["ID", "NOMINAL_TIME", "DV"],
         [[1, 1.0, 50.0]])
write_expected("fixture_time_policy_missing", """
    fixture_name: fixture_time_policy_missing
    expected_terminal: QUARANTINE
    expected_q_code: Q02
""")

write_csv("fixture_weight_based_dose",
         ["ID", "WT", "AMT"],
         [[1, 70.0, 0], [2, 80.0, 0]])
write_expected("fixture_weight_based_dose", """
    fixture_name: fixture_weight_based_dose
    input_aic: { dose_reconstruction_policy: { dose_per_kg: 0.5 } }
    expected_terminal: REPAIR
""")

# --- v4.1 EDGE (8) ---

write_csv("fixture_addl_actual_conflict",
         ["ID", "TIME", "AMT", "ADDL", "II"],
         [[1, 0, 100, 3, 24]])
write_expected("fixture_addl_actual_conflict", """
    fixture_name: fixture_addl_actual_conflict
    expected_terminal: QUARANTINE
    expected_q_code: Q14
""")

write_csv("fixture_addl_actual_conflict_policy_present",
         ["ID", "TIME", "AMT", "ADDL", "II"],
         [[1, 0, 100, 3, 24]])
write_expected("fixture_addl_actual_conflict_policy_present", """
    fixture_name: fixture_addl_actual_conflict_policy_present
    input_aic: { addl_actual_conflict_policy: actual_priority }
    expected_terminal: REPAIR
""")

write_csv("fixture_reanalysis_final_flag_present",
         ["ID", "DV", "FINAL_FLAG"],
         [[1, 1.0, 1], [1, 1.1, 0]])
write_expected("fixture_reanalysis_final_flag_present", """
    fixture_name: fixture_reanalysis_final_flag_present
    expected_terminal: REPAIR
""")

write_csv("fixture_reanalysis_final_flag_missing",
         ["ID", "DV"],
         [[1, 1.0], [1, 1.1]])
write_expected("fixture_reanalysis_final_flag_missing", """
    fixture_name: fixture_reanalysis_final_flag_missing
    expected_terminal: QUARANTINE
    expected_q_code: Q15D
""")

write_csv("fixture_infusion_stop_restart",
         ["ID", "TIME", "RATE", "AMT"],
         [[1, 0, 10, 0], [1, 1.0, 0, 0], [1, 2.0, 10, 0]])
write_expected("fixture_infusion_stop_restart", """
    fixture_name: fixture_infusion_stop_restart
    input_aic: { infusion_reconstruction_policy: stop_restart_from_events }
    expected_terminal: REPAIR
""")

write_csv("fixture_loading_maintenance",
         ["ID", "TIME", "AMT"],
         [[1, 0, 200], [1, 24, 100]])
write_expected("fixture_loading_maintenance", """
    fixture_name: fixture_loading_maintenance
    input_aic: { dose_reconstruction_policy: loading_maintenance }
    expected_terminal: REPAIR
""")

write_csv("fixture_titration_adaptive",
         ["ID", "TIME", "AMT"],
         [[1, 0, 50], [1, 24, 100]])
write_expected("fixture_titration_adaptive", """
    fixture_name: fixture_titration_adaptive
    input_aic: { dose_adaptation_policy: project_specific }
    expected_terminal: REPAIR
""")

write_csv("fixture_ddi_victim_only",
         ["ID", "TIME", "DV"],
         [[1, 1, 100]])
write_expected("fixture_ddi_victim_only", """
    fixture_name: fixture_ddi_victim_only
    input_aic: { cmt_analyte_policy: ddi_victim_only }
    expected_terminal: REPAIR
""")

write_csv("fixture_ddi_victim_perpetrator",
         ["ID", "ANALYTE_NAME", "DV"],
         [[1, "victim", 50], [1, "perp", 100]])
write_expected("fixture_ddi_victim_perpetrator", """
    fixture_name: fixture_ddi_victim_perpetrator
    input_aic: { cmt_analyte_policy: ddi_dual_cmt, dual_cmt_policy: { victim_label: victim } }
    expected_terminal: REPAIR
""")

# --- v4.2 NEW (7) ---

write_csv("fixture_cellular_kinetics_lloq_present",
         ["ID", "TIME", "DV", "EVID", "MDV"],
         [[1, 0, 100, 0, 0], [1, 24, 0.05, 0, 0]])
write_expected("fixture_cellular_kinetics_lloq_present", """
    fixture_name: fixture_cellular_kinetics_lloq_present
    input_aic: { cellular_LLOQ_derivation_policy: { cellular_lloq: 0.1, method: M3 } }
    expected_terminal: REPAIR
""")

write_csv("fixture_cellular_kinetics_lloq_missing",
         ["ID", "TIME", "DV", "EVID", "MDV"],
         [[1, 0, 0.05, 0, 0]])
write_expected("fixture_cellular_kinetics_lloq_missing", """
    fixture_name: fixture_cellular_kinetics_lloq_missing
    expected_terminal: QUARANTINE
    expected_q_code: Q01
""")

write_csv("fixture_immunogenicity_with_positivity_rule",
         ["ID", "TIME", "DV"],
         [[1, 0, 0.5], [1, 24, 2.0]])
write_expected("fixture_immunogenicity_with_positivity_rule", """
    fixture_name: fixture_immunogenicity_with_positivity_rule
    input_aic: { positivity_adjudication_rule: { screening_cutpoint: 1.0 } }
    expected_terminal: REPAIR
""")

write_csv("fixture_immunogenicity_no_positivity_rule",
         ["ID", "TIME", "DV"],
         [[1, 0, 2.0]])
write_expected("fixture_immunogenicity_no_positivity_rule", """
    fixture_name: fixture_immunogenicity_no_positivity_rule
    expected_terminal: QUARANTINE
    expected_q_code: Q19
""")

write_csv("fixture_maternal_infant_dyad",
         ["SUBJID", "TIME", "DV"],
         [["MOTHER_1", 0, 100], ["INFANT_1", 0, 5]])
write_expected("fixture_maternal_infant_dyad", """
    fixture_name: fixture_maternal_infant_dyad
    input_aic: { dyad_linkage_policy: { linkage_key: MOTHER_SUBJID } }
    expected_terminal: REPAIR
""")

write_csv("fixture_maternal_infant_no_dyad_key",
         ["SUBJID", "TIME", "DV"],
         [["MOTHER_1", 0, 100], ["INFANT_1", 0, 5]])
write_expected("fixture_maternal_infant_no_dyad_key", """
    fixture_name: fixture_maternal_infant_no_dyad_key
    expected_terminal: QUARANTINE
    expected_q_code: Q18
""")

write_csv("fixture_milk_pk_matrix_lloq",
         ["ID", "TIME", "DV", "MATRIX"],
         [[1, 0, 0.05, "milk"], [1, 24, 0.5, "milk"]])
write_expected("fixture_milk_pk_matrix_lloq", """
    fixture_name: fixture_milk_pk_matrix_lloq
    input_aic: { milk_matrix_lloq_policy: { milk_lloq: 0.1 } }
    expected_terminal: REPAIR
""")

print(f"ok: {len(list(FX.glob('*.csv')))} CSV fixtures, {len(list(FX.glob('*_expected.yaml')))} expected YAMLs")
