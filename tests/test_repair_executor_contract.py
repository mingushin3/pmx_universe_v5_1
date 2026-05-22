"""Contract tests for the repair executor — system-level invariants
that hold across all functions and the orchestrator."""

from __future__ import annotations

import re
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
    repair_unit_conversion,
    repair_column_synonym,
    repair_subject_id_mapping,
    run_repair_pipeline,
)


ACTIVE_Q_CODES = {f"Q{i:02d}" for i in range(1, 15)} | {"Q15A", "Q15B", "Q15C", "Q15D", "Q16", "Q18", "Q19"}


# ---------- C01: every quarantine has q_code in active set ----------


@pytest.mark.parametrize("call", [
    lambda: canonicalize_cellular_blq(pd.DataFrame({"DV": [0.1], "EVID": [0]}), None),
    lambda: adjudicate_immunogenicity_positivity(pd.DataFrame({"DV": [1.0]}), None),
    lambda: attach_dyad_linkage(pd.DataFrame({"SUBJID": ["M"]}), None),
    lambda: derive_time_postpartum_anchor(pd.DataFrame({"EVENT_TIME": [1]}), None),
    lambda: assign_milk_matrix_lloq(pd.DataFrame({"DV": [1.0], "MATRIX": ["milk"]}), None),
    lambda: assign_cmt_with_analyte_role(pd.DataFrame({"ANALYTE_NAME": ["x"]}), None),
    lambda: attach_covariate_product_level(pd.DataFrame({"LOT_ID": ["L"]}), None, []),
])
def test_C01_quarantines_have_valid_q_code(call):
    r = call()
    assert isinstance(r, QuarantineResult)
    assert r.q_code in ACTIVE_Q_CODES


# ---------- C02: no function ever returns q_code="Q15" standalone ----------
# ---------- C03: no function ever returns q_code="Q17" ----------


def test_C02_C03_construction_rejects_Q15_and_Q17():
    with pytest.raises(ValueError):
        QuarantineResult(q_code="Q15", reason="x", audit_log={})
    with pytest.raises(ValueError):
        QuarantineResult(q_code="Q17", reason="x", audit_log={})


# ---------- C04: every RepairResult has non-empty audit_log ----------


@pytest.mark.parametrize("call", [
    lambda: repair_column_synonym(pd.DataFrame({"old": [1]}), {"old": "ID"}),
    lambda: repair_unit_conversion(pd.DataFrame({"DV": [1.0]}), {"column": "DV", "factor": 1.0}),
    lambda: canonicalize_cellular_blq(pd.DataFrame({"DV": [0.5], "EVID": [0], "MDV": [0]}),
                                       {"cellular_lloq": 0.1, "method": "M1"}),
    lambda: adjudicate_immunogenicity_positivity(pd.DataFrame({"DV": [1.0]}),
                                                  {"screening_cutpoint": 0.5}),
])
def test_C04_repair_audit_non_empty(call):
    r = call()
    assert isinstance(r, RepairResult)
    assert r.audit_log
    assert "rule_id" in r.audit_log or "function_name" in r.audit_log


# ---------- C05: RepairResult.df is a different object than input ----------


def test_C05_repair_does_not_mutate_input():
    df = pd.DataFrame({"DV": [1.0, 2.0]})
    r = repair_unit_conversion(df, {"column": "DV", "factor": 2.0})
    assert isinstance(r, RepairResult)
    assert r.df is not df
    assert df["DV"].tolist() == [1.0, 2.0]


# ---------- C06: applied_rules non-empty when transformation occurred ----------


def test_C06_applied_rules_non_empty():
    r = repair_column_synonym(pd.DataFrame({"old": [1]}), {"old": "ID"})
    assert r.applied_rules
    assert r.applied_rules[0].startswith("RR")


# ---------- C07: orchestrator halts on first QuarantineResult ----------


def test_C07_orchestrator_halts_on_quarantine():
    df = pd.DataFrame({"DV": [0.5], "EVID": [0], "MDV": [0]})
    seq = [
        ("repair_unit_conversion", {"column": "DV", "factor": 1.0}),
        ("canonicalize_cellular_blq", {}),  # AIC missing → halts here
    ]
    aic = {}  # cellular_LLOQ_derivation_policy missing
    r = run_repair_pipeline(df, seq, aic)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q01"


# ---------- C08: orchestrator returns QuarantineResult when AIC missing ----------


def test_C08_missing_aic_policy_returns_quarantine():
    df = pd.DataFrame({"SUBJID": ["M1"]})
    seq = [("attach_dyad_linkage", {})]
    aic = {}
    r = run_repair_pipeline(df, seq, aic)
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q18"


# ---------- C09: v4.2 specific quarantine mappings ----------


@pytest.mark.parametrize("fn, expected_q", [
    (lambda: canonicalize_cellular_blq(pd.DataFrame({"DV": [0.0], "EVID": [0]}), None), "Q01"),
    (lambda: adjudicate_immunogenicity_positivity(pd.DataFrame({"DV": [0.0]}), None), "Q19"),
    (lambda: attach_dyad_linkage(pd.DataFrame({"SUBJID": ["x"]}), None), "Q18"),
    (lambda: derive_time_postpartum_anchor(pd.DataFrame({"EVENT_TIME": [0]}), None), "Q12"),
    (lambda: assign_milk_matrix_lloq(pd.DataFrame({"DV": [0.0], "MATRIX": ["milk"]}), None), "Q01"),
    (lambda: assign_cmt_with_analyte_role(pd.DataFrame({"ANALYTE_NAME": ["x"]}), None), "Q16"),
])
def test_C09_v42_qcode_mapping(fn, expected_q):
    r = fn()
    assert isinstance(r, QuarantineResult)
    assert r.q_code == expected_q


# ---------- C10: audit_log timestamps are ISO 8601 strings ----------


def test_C10_timestamps_iso_format():
    r = repair_unit_conversion(pd.DataFrame({"DV": [1.0]}), {"column": "DV", "factor": 1.0})
    ts = r.audit_log.get("timestamp_iso", "")
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts)


# ---------- C11: original ID values preserved across pipeline ----------


def test_C11_id_column_preserved():
    df = pd.DataFrame({"ID": [1, 2, 3], "DV": [1.0, 2.0, 3.0]})
    seq = [("repair_unit_conversion", {"column": "DV", "factor": 0.5})]
    r = run_repair_pipeline(df, seq, {})
    assert isinstance(r, RepairResult)
    assert r.df["ID"].tolist() == [1, 2, 3]
