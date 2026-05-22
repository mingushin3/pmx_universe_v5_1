"""Property-based tests (hypothesis) for repair_executor.

v5.1 PATCH-9: hypothesis-driven exploration of edge cases in random
valid (AIC, dataset) pairs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st


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
    run_repair_pipeline,
)


Q_CODE_RE = re.compile(r"^(Q0[1-9]|Q1[0-46]|Q15[ABCD]|Q1[89])$")


# ---------- P01 — pipeline always returns Result, never None / exception ----------


@given(
    n=st.integers(min_value=1, max_value=20),
    have_policy=st.booleans(),
)
@settings(max_examples=50, deadline=None)
def test_P01_pipeline_returns_a_result(n: int, have_policy: bool):
    df = pd.DataFrame({"ID": list(range(1, n + 1)),
                       "DV": [1.0] * n,
                       "EVID": [0] * n,
                       "MDV": [0] * n})
    seq = [("canonicalize_cellular_blq", {})]
    aic = {"cellular_LLOQ_derivation_policy": {"cellular_lloq": 0.1, "method": "M1"}} if have_policy else {}
    r = run_repair_pipeline(df, seq, aic)
    assert isinstance(r, (RepairResult, QuarantineResult))


# ---------- P02 — missing required_policy yields correct QuarantineResult ----------


@given(
    fn_and_q=st.sampled_from([
        ("canonicalize_cellular_blq", "cellular_LLOQ_derivation_policy", "Q01"),
        ("adjudicate_immunogenicity_positivity", "positivity_adjudication_rule", "Q19"),
        ("attach_dyad_linkage", "dyad_linkage_policy", "Q18"),
        ("derive_time_postpartum_anchor", "delivery_anchor_policy", "Q12"),
        ("assign_milk_matrix_lloq", "milk_matrix_lloq_policy", "Q01"),
        ("assign_cmt_with_analyte_role", "analyte_role_declaration", "Q16"),
    ]),
)
@settings(max_examples=20, deadline=None)
def test_P02_missing_aic_policy_specific_qcode(fn_and_q):
    fn_name, field, expected_q = fn_and_q
    df = pd.DataFrame({"ID": [1], "DV": [1.0], "EVID": [0], "MDV": [0],
                       "SUBJID": ["S1"], "MATRIX": ["milk"],
                       "ANALYTE_NAME": ["totAb"], "EVENT_TIME": [1.0]})
    r = run_repair_pipeline(df, [(fn_name, {})], {})  # AIC empty
    assert isinstance(r, QuarantineResult)
    assert r.q_code == expected_q


# ---------- P03 — idempotency: same input, same output ----------


@given(
    dv=st.lists(st.floats(min_value=0.01, max_value=10.0, allow_nan=False), min_size=1, max_size=10),
)
@settings(max_examples=20, deadline=None)
def test_P03_idempotency(dv):
    df = pd.DataFrame({"ID": list(range(len(dv))), "DV": dv,
                       "EVID": [0] * len(dv), "MDV": [0] * len(dv)})
    aic = {"cellular_LLOQ_derivation_policy": {"cellular_lloq": 0.5, "method": "M3"}}
    seq = [("canonicalize_cellular_blq", {})]
    r1 = run_repair_pipeline(df, seq, aic)
    r2 = run_repair_pipeline(df, seq, aic)
    assert type(r1) is type(r2)
    if isinstance(r1, RepairResult) and isinstance(r2, RepairResult):
        pd.testing.assert_frame_equal(
            r1.df.reset_index(drop=True),
            r2.df.reset_index(drop=True),
            check_like=False,
        )


# ---------- P04 — audit_log always contains required keys ----------


@given(cutpoint=st.floats(min_value=0.001, max_value=10.0, allow_nan=False))
@settings(max_examples=30, deadline=None)
def test_P04_audit_log_keys(cutpoint):
    df = pd.DataFrame({"ID": [1], "DV": [cutpoint + 0.1]})
    r = adjudicate_immunogenicity_positivity(df, {"screening_cutpoint": cutpoint})
    assert isinstance(r, RepairResult)
    keys = set(r.audit_log.keys())
    assert {"rule_id", "function_name", "timestamp_iso"} <= keys


# ---------- P05 — every QuarantineResult.q_code matches active regex ----------


@given(fn=st.sampled_from([
    canonicalize_cellular_blq,
    adjudicate_immunogenicity_positivity,
    attach_dyad_linkage,
    derive_time_postpartum_anchor,
    assign_milk_matrix_lloq,
    assign_cmt_with_analyte_role,
]))
@settings(max_examples=20, deadline=None)
def test_P05_quarantine_q_code_active_set(fn):
    df = pd.DataFrame({"ID": [1], "DV": [1.0], "EVID": [0], "MDV": [0],
                       "SUBJID": ["S1"], "MATRIX": ["milk"],
                       "ANALYTE_NAME": ["x"], "EVENT_TIME": [1.0]})
    r = fn(df, None)
    assert isinstance(r, QuarantineResult)
    assert Q_CODE_RE.match(r.q_code), f"unexpected q_code: {r.q_code}"


# ---------- P06 — RepairResult.q_code is None ----------


@given(n=st.integers(min_value=1, max_value=5))
@settings(max_examples=20, deadline=None)
def test_P06_repair_q_code_none(n):
    df = pd.DataFrame({"ID": list(range(n)), "DV": [1.0] * n,
                       "EVID": [0] * n, "MDV": [0] * n})
    r = canonicalize_cellular_blq(df, {"cellular_lloq": 0.1, "method": "M1"})
    assert isinstance(r, RepairResult)
    assert r.q_code is None


# ---------- P07 — v4.2: CELLULAR_KINETICS without policy → Q01 ----------


@given(n=st.integers(min_value=1, max_value=5))
@settings(max_examples=10, deadline=None)
def test_P07_cellular_no_policy_q01(n):
    df = pd.DataFrame({"ID": list(range(n)), "DV": [0.05] * n,
                       "EVID": [0] * n, "MDV": [0] * n})
    r = run_repair_pipeline(df, [("canonicalize_cellular_blq", {})], {})
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q01"


# ---------- P08 — input df not mutated ----------


@given(values=st.lists(st.floats(min_value=0.01, max_value=10.0, allow_nan=False),
                       min_size=1, max_size=10))
@settings(max_examples=20, deadline=None)
def test_P08_no_input_mutation(values):
    df = pd.DataFrame({"DV": values})
    original = df.copy(deep=True)
    _ = adjudicate_immunogenicity_positivity(df, {"screening_cutpoint": 1.0})
    pd.testing.assert_frame_equal(df, original)


# ---------- P09 — orchestrator: unknown function → QuarantineResult Q15A ----------


def test_P09_unknown_function_returns_quarantine():
    r = run_repair_pipeline(pd.DataFrame({"ID": [1]}),
                            [("not_a_real_function", {})],
                            {})
    assert isinstance(r, QuarantineResult)
    assert r.q_code == "Q15A"


# ---------- P10 — RepairResult always has applied_rules non-empty ----------


@given(method=st.sampled_from(["M1", "M3"]))
@settings(max_examples=10, deadline=None)
def test_P10_applied_rules_present(method):
    df = pd.DataFrame({"ID": [1], "DV": [0.05], "EVID": [0], "MDV": [0]})
    r = canonicalize_cellular_blq(df, {"cellular_lloq": 0.1, "method": method})
    assert isinstance(r, RepairResult)
    assert r.applied_rules == ["RR020"]
