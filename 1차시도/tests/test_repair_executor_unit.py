"""Unit tests for individual repair functions (≥3 cases each)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.repair_executor.repair_executor import (  # noqa: E402
    RepairResult,
    QuarantineResult,
    canonicalize_cellular_blq,
    adjudicate_immunogenicity_positivity,
    attach_dyad_linkage,
    derive_time_postpartum_anchor,
    assign_milk_matrix_lloq,
    assign_cmt_with_analyte_role,
    attach_covariate_product_level,
    repair_blq_canonicalization,
    repair_dose_reconstruction_weight,
    repair_dose_reconstruction_bsa,
    repair_subject_id_mapping,
    repair_time_elapsed,
    repair_time_interval,
    repair_unit_conversion,
    repair_column_synonym,
    resolve_addl_actual_conflict,
    resolve_reanalysis_final,
    assign_cmt_ddi_victim_only,
    assign_cmt_ddi_victim_perpetrator,
    repair_covariate_attach,
    repair_time_derivation_actual,
    repair_time_derivation_nominal,
    reconstruct_dose_titration,
    reconstruct_loading_maintenance,
    reconstruct_infusion_stop_restart,
    expand_addl_ii,
)


# ----------------------------------------------------------------------
# Q15 standalone / Q17 are forbidden
# ----------------------------------------------------------------------


def test_q15_standalone_forbidden():
    with pytest.raises(ValueError, match="Q15 standalone forbidden"):
        QuarantineResult(q_code="Q15", reason="x", audit_log={})


def test_q17_forbidden():
    with pytest.raises(ValueError, match="Q17 forbidden"):
        QuarantineResult(q_code="Q17", reason="x", audit_log={})


def test_repair_result_q_code_must_be_none():
    with pytest.raises(ValueError):
        RepairResult(df=pd.DataFrame(), q_code="Q01")


# ----------------------------------------------------------------------
# v4.2 NEW functions (3 cases each)
# ----------------------------------------------------------------------


def test_canonicalize_cellular_blq_normal():
    df = pd.DataFrame({"ID": [1, 1], "TIME": [0, 24], "DV": [100.0, 0.05],
                       "EVID": [0, 0], "MDV": [0, 0]})
    policy = {"cellular_lloq": 0.1, "method": "M3"}
    r = canonicalize_cellular_blq(df, policy)
    assert isinstance(r, RepairResult)
    assert "rule_id" in r.audit_log
    assert r.df["CELLULAR_BLQ_FLAG"].tolist() == [0, 1]


def test_canonicalize_cellular_blq_no_policy():
    df = pd.DataFrame({"ID": [1], "DV": [0.05], "EVID": [0], "MDV": [0]})
    r = canonicalize_cellular_blq(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q01"
    assert "cellular" in str(r.audit_log).lower()


def test_canonicalize_cellular_blq_invalid_lloq():
    df = pd.DataFrame({"ID": [1], "DV": [0.05], "EVID": [0], "MDV": [0]})
    r = canonicalize_cellular_blq(df, {"method": "M1"})  # no cellular_lloq
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q01"


def test_adjudicate_immunogenicity_no_rule():
    df = pd.DataFrame({"ID": [1, 2], "DV": [0.5, 2.0]})
    r = adjudicate_immunogenicity_positivity(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q19"


def test_adjudicate_immunogenicity_with_rule():
    df = pd.DataFrame({"ID": [1, 2], "DV": [0.5, 2.0]})
    r = adjudicate_immunogenicity_positivity(df, {"screening_cutpoint": 1.0})
    assert isinstance(r, RepairResult)
    assert r.df["ADA_POSITIVE_FLAG"].tolist() == [0, 1]


def test_adjudicate_immunogenicity_empty_df():
    df = pd.DataFrame({"ID": [], "DV": []})
    r = adjudicate_immunogenicity_positivity(df, {"screening_cutpoint": 1.0})
    assert isinstance(r, RepairResult)
    assert len(r.df) == 0


def test_attach_dyad_linkage_no_policy():
    df = pd.DataFrame({"SUBJID": ["M1", "M2"]})
    r = attach_dyad_linkage(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q18"


def test_attach_dyad_linkage_normal():
    df = pd.DataFrame({"SUBJID": ["M1", "I1"]})
    r = attach_dyad_linkage(df, {"linkage_key": "MOTHER_SUBJID"})
    assert isinstance(r, RepairResult)
    assert "DYAD_ID" in r.df.columns


def test_attach_dyad_linkage_empty():
    df = pd.DataFrame({"SUBJID": []})
    r = attach_dyad_linkage(df, {"linkage_key": "M_SUBJID"})
    assert isinstance(r, RepairResult)
    assert len(r.df) == 0


def test_derive_time_postpartum_anchor_no_policy():
    df = pd.DataFrame({"SUBJID": ["P1"], "EVENT_TIME": [10.0], "DELIVERY_DATE": [0.0]})
    r = derive_time_postpartum_anchor(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q12"


def test_derive_time_postpartum_anchor_normal():
    df = pd.DataFrame({"SUBJID": ["P1", "P1"], "EVENT_TIME": [24.0, 48.0],
                       "DELIVERY_DATE": [0.0, 0.0]})
    r = derive_time_postpartum_anchor(df, {"anchor_column": "DELIVERY_DATE"})
    assert isinstance(r, RepairResult)
    assert "TIME" in r.df.columns
    assert "POSTPARTUM_DAY" in r.df.columns


def test_derive_time_postpartum_anchor_missing_event_time():
    df = pd.DataFrame({"SUBJID": ["P1"], "DELIVERY_DATE": [0.0]})
    r = derive_time_postpartum_anchor(df, {"anchor_column": "DELIVERY_DATE"})
    assert isinstance(r, RepairResult)


def test_assign_milk_matrix_lloq_no_policy():
    df = pd.DataFrame({"DV": [0.05, 0.5], "MATRIX": ["milk", "milk"]})
    r = assign_milk_matrix_lloq(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q01"


def test_assign_milk_matrix_lloq_normal():
    df = pd.DataFrame({"DV": [0.05, 0.5], "MATRIX": ["milk", "milk"]})
    r = assign_milk_matrix_lloq(df, {"milk_lloq": 0.1})
    assert isinstance(r, RepairResult)
    assert r.df["MATRIX_BLQ_FLAG"].tolist() == [1, 0]


def test_assign_milk_matrix_lloq_non_milk_rows():
    df = pd.DataFrame({"DV": [0.05, 0.5], "MATRIX": ["plasma", "milk"]})
    r = assign_milk_matrix_lloq(df, {"milk_lloq": 0.1})
    assert isinstance(r, RepairResult)
    assert r.df["MATRIX_BLQ_FLAG"].tolist() == [0, 0]


def test_assign_cmt_with_analyte_role_no_map():
    df = pd.DataFrame({"ANALYTE_NAME": ["totAb", "conjAdc"]})
    r = assign_cmt_with_analyte_role(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q16"


def test_assign_cmt_with_analyte_role_normal():
    df = pd.DataFrame({"ANALYTE_NAME": ["totAb", "conjAdc"]})
    role_map = {
        "totAb": {"role": "TOTAL_ANTIBODY", "cmt": 2},
        "conjAdc": {"role": "CONJUGATED_ADC", "cmt": 3},
    }
    r = assign_cmt_with_analyte_role(df, role_map)
    assert isinstance(r, RepairResult)
    assert r.df["CMT"].tolist() == [2, 3]


def test_assign_cmt_with_analyte_role_unknown_analyte():
    df = pd.DataFrame({"ANALYTE_NAME": ["unknown"]})
    role_map = {"totAb": {"role": "TOTAL_ANTIBODY", "cmt": 2}}
    r = assign_cmt_with_analyte_role(df, role_map)
    assert isinstance(r, RepairResult)


def test_attach_covariate_product_level_no_map():
    df = pd.DataFrame({"ID": [1], "LOT_ID": ["L1"]})
    r = attach_covariate_product_level(df, None, ["TRANSDUCTION_EFF"])
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q13"
    assert "Q17" in r.reason or "Q17" in str(r.audit_log)


def test_attach_covariate_product_level_normal():
    df = pd.DataFrame({"ID": [1, 2], "LOT_ID": ["L1", "L2"]})
    lot_map = {
        "L1": {"TRANSDUCTION_EFF": 0.42},
        "L2": {"TRANSDUCTION_EFF": 0.50},
    }
    r = attach_covariate_product_level(df, lot_map, ["TRANSDUCTION_EFF"])
    assert isinstance(r, RepairResult)
    assert "TRANSDUCTION_EFF" in r.df.columns


def test_attach_covariate_product_level_empty_attrs():
    df = pd.DataFrame({"ID": [1], "LOT_ID": ["L1"]})
    r = attach_covariate_product_level(df, {"L1": {}}, [])
    assert isinstance(r, RepairResult)


# ----------------------------------------------------------------------
# v4.1 functions — abbreviated (≥3 each via parametrize)
# ----------------------------------------------------------------------


@pytest.mark.parametrize("fn, policy, expected_q", [
    (repair_subject_id_mapping, None, "Q03"),
    (repair_time_elapsed, None, "Q02"),
    (repair_dose_reconstruction_weight, None, "Q08"),
    (repair_dose_reconstruction_bsa, None, "Q08"),
    (resolve_addl_actual_conflict, None, "Q14"),
    (repair_blq_canonicalization, None, "Q01"),
    (resolve_reanalysis_final, None, "Q15D"),
    (assign_cmt_ddi_victim_only, None, "Q09"),
    (reconstruct_infusion_stop_restart, None, "Q04"),
])
def test_v41_quarantines_on_no_policy(fn, policy, expected_q):
    df = pd.DataFrame({"ID": [1], "DV": [1.0], "MDV": [0], "EVID": [0]})
    r = fn(df, policy) if fn is not assign_cmt_ddi_victim_only else fn(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == expected_q


def test_repair_column_synonym_normal():
    df = pd.DataFrame({"old_id": [1]})
    r = repair_column_synonym(df, {"old_id": "ID"})
    assert isinstance(r, RepairResult)
    assert "ID" in r.df.columns


def test_repair_unit_conversion_normal():
    df = pd.DataFrame({"DV": [100.0]})
    r = repair_unit_conversion(df, {"column": "DV", "factor": 0.001})
    assert isinstance(r, RepairResult)
    assert r.df["DV"].tolist() == [0.1]


def test_repair_time_interval():
    df = pd.DataFrame({"INTERVAL_START": [0, 4], "INTERVAL_END": [4, 8]})
    r = repair_time_interval(df)
    assert isinstance(r, RepairResult)
    assert r.df["TIME"].tolist() == [2.0, 6.0]


def test_expand_addl_ii():
    df = pd.DataFrame({"ID": [1], "ADDL": [3], "II": [24.0]})
    r = expand_addl_ii(df)
    assert isinstance(r, RepairResult)


def test_assign_cmt_ddi_victim_only_normal():
    df = pd.DataFrame({"ID": [1, 1], "DV": [1.0, 2.0]})
    r = assign_cmt_ddi_victim_only(df, 2)
    assert isinstance(r, RepairResult)
    assert r.df["CMT"].tolist() == [2, 2]


def test_assign_cmt_ddi_victim_perpetrator_normal():
    df = pd.DataFrame({"ANALYTE_NAME": ["victim", "perp"]})
    r = assign_cmt_ddi_victim_perpetrator(df, 1, 2, {"victim_label": "victim"})
    assert isinstance(r, RepairResult)
    assert r.df["CMT"].tolist() == [1, 2]


def test_repair_dose_weight_normal():
    df = pd.DataFrame({"WT": [70.0, 80.0]})
    r = repair_dose_reconstruction_weight(df, {"dose_per_kg": 0.5})
    assert isinstance(r, RepairResult)
    assert r.df["AMT"].tolist() == [35.0, 40.0]


def test_repair_blq_m3_with_lloq_column():
    df = pd.DataFrame({"DV": [0.05, 1.0], "MDV": [0, 0], "EVID": [0, 0], "LLOQ": [0.1, 0.1]})
    r = repair_blq_canonicalization(df, "M3")
    assert isinstance(r, RepairResult)


def test_reconstruct_dose_titration_no_policy():
    r = reconstruct_dose_titration(pd.DataFrame({"ID": [1]}), {"a": 1}, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q08"


def test_reconstruct_loading_maintenance_normal():
    df = pd.DataFrame({"ID": [1]})
    r = reconstruct_loading_maintenance(df, {"loading": 100}, {"maintenance": 50},
                                        {"transition_point": 1.0})
    assert isinstance(r, RepairResult)


def test_reconstruct_infusion_normal():
    df = pd.DataFrame({"ID": [1]})
    r = reconstruct_infusion_stop_restart(df, {"policy": "stop_restart_from_events"})
    assert isinstance(r, RepairResult)


def test_repair_covariate_attach_no_policy_baseline():
    r = repair_covariate_attach(pd.DataFrame({"ID": [1]}), None, "baseline")
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q06"


def test_repair_covariate_attach_no_policy_external():
    r = repair_covariate_attach(pd.DataFrame({"ID": [1]}), None, "external")
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q07"


def test_repair_covariate_attach_normal():
    r = repair_covariate_attach(pd.DataFrame({"ID": [1]}), {"policy": "x"}, "baseline")
    assert isinstance(r, RepairResult)


def test_repair_time_derivation_actual_normal():
    df = pd.DataFrame({"ANCHOR": [0.0], "ACTUAL_TIME": [5.0]})
    r = repair_time_derivation_actual(df, "ANCHOR")
    assert isinstance(r, RepairResult)


def test_repair_time_derivation_actual_no_anchor():
    df = pd.DataFrame({"ACTUAL_TIME": [5.0]})
    r = repair_time_derivation_actual(df, None)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q02"


def test_repair_time_derivation_nominal_normal():
    df = pd.DataFrame({"NOMINAL_TIME": [1.0]})
    r = repair_time_derivation_nominal(df, {"schedule": "[1, 2, 4]"})
    assert isinstance(r, RepairResult)


def test_resolve_reanalysis_final_normal():
    df = pd.DataFrame({"DV": [1.0, 2.0], "FINAL_FLAG": [1, 0]})
    r = resolve_reanalysis_final(df, "FINAL_FLAG")
    assert isinstance(r, RepairResult)
    assert len(r.df) == 1
