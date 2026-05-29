"""Tests for scripts/validation/nonmem_ready_qc.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validation.nonmem_ready_qc import (  # noqa: E402
    QCContext, load_context, run_qc,
    check_s01, check_s02, check_s03, check_s05,
    check_e01, check_e02, check_e03, check_e04, check_e05,
    check_b01, check_c01, check_c02, check_c03,
    check_v01, check_v02, check_v03, check_v04,
    check_a01,
)


# ---------------------------------------------------------------------------
def _write_dataset(tmp_path: Path, header: list[str], rows: list[list]) -> Path:
    p = tmp_path / "dataset.csv"
    lines = [",".join(header)]
    for r in rows:
        lines.append(",".join("" if v is None else str(v) for v in r))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _write_aic(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "aic.yaml"
    p.write_text(yaml.safe_dump({"analysis_intent_contract": payload}), encoding="utf-8")
    return p


def _write_audit(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "audit.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _audit_full() -> dict:
    return {
        "decision_path": [["N0", "Y"], ["N1", "Y"]],
        "terminal_state": "AUTO",
        "q_code": None,
        "action_sequence_executed": ["parse_source", "export_nonmem_ready"],
        "parameter_policies": {},
        "timestamp_iso": "2026-05-22T12:00:00+00:00",
        "input_data_summary": {"row_count": 4, "columns_used": []},
    }


# ---------------------------------------------------------------------------
# 1. Clean AUTO dataset — all checks PASS
# ---------------------------------------------------------------------------
def test_clean_auto_dataset_passes(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "AMT", "CMT"],
        [
            [1, 0,   "",  1, 1, 100, 1],
            [1, 0.5, 5.0, 0, 0, "",  2],
            [1, 1.0, 4.5, 0, 0, "",  2],
            [2, 0,   "",  1, 1, 100, 1],
        ],
    )
    aic = _write_aic(tmp_path, {"endpoint_data_type": "PK", "allow_negative_dv": False})
    audit = _write_audit(tmp_path, _audit_full())
    ctx = load_context(ds, aic, audit)
    results = run_qc(ctx)
    fails = [r for r in results if r.status == "FAIL"]
    assert not fails, f"unexpected failures: {[(r.code, r.detail) for r in fails]}"


# ---------------------------------------------------------------------------
# 2. Clean REPAIR dataset — also passes (different action_sequence but same shape)
# ---------------------------------------------------------------------------
def test_clean_repair_dataset_passes(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "AMT", "CMT", "BLQ_FLAG"],
        [
            [1, 0, "",   1, 1, 50, 1, ""],
            [1, 1, 0.5,  0, 0, "", 2, ""],
            [1, 2, "",   1, 0, "", 2, "M3"],
        ],
    )
    aic = _write_aic(tmp_path, {"endpoint_data_type": "PK"})
    audit_data = _audit_full()
    audit_data["action_sequence_executed"] = ["parse_source", "canonicalize_blq", "export_nonmem_ready"]
    audit = _write_audit(tmp_path, audit_data)
    ctx = load_context(ds, aic, audit)
    results = run_qc(ctx)
    fails = [r for r in results if r.status == "FAIL"]
    assert not fails, f"unexpected failures: {fails}"


# ---------------------------------------------------------------------------
# 3. EVID violation → E03 FAIL
# ---------------------------------------------------------------------------
def test_evid_out_of_range_fails(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "AMT"],
        [
            [1, 0, "",  1, 9, 100],  # bad EVID
        ],
    )
    aic = _write_aic(tmp_path, {})
    audit = _write_audit(tmp_path, _audit_full())
    ctx = load_context(ds, aic, audit)
    r = check_e03(ctx)
    assert r.status == "FAIL"
    assert "9" in r.detail


# ---------------------------------------------------------------------------
# 4. MDV / DV inconsistency → B01 FAIL
# ---------------------------------------------------------------------------
def test_mdv_dv_inconsistent_fails(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID"],
        [
            [1, 0, "",  0, 0],  # DV NA but MDV=0
        ],
    )
    ctx = load_context(ds, None, None)
    r = check_b01(ctx)
    assert r.status == "FAIL"


# ---------------------------------------------------------------------------
# 5. Missing CMT but multi-analyte AIC → S01 OK, C01 OK, C02 FAIL
# ---------------------------------------------------------------------------
def test_missing_cmt_role_map(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "CMT"],
        [
            [1, 0,   "", 1, 1, 1],
            [1, 0.5, 1.0, 0, 0, 2],
        ],
    )
    aic = _write_aic(tmp_path, {"analyte_role": "parent_metabolite"})  # but no cmt_role_map
    ctx = load_context(ds, aic, None)
    r = check_c02(ctx)
    assert r.status == "FAIL"
    assert "cmt_role_map" in r.detail


# ---------------------------------------------------------------------------
# 6. CELLULAR_KINETICS with negative DV → V01 FAIL
# ---------------------------------------------------------------------------
def test_cellular_negative_dv_fails(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "BLQ_FLAG"],
        [
            [1, 0,   "",   1, 1, ""],
            [1, 0.5, -1.5, 0, 0, ""],  # negative DV under CELLULAR_KINETICS
        ],
    )
    aic = _write_aic(tmp_path, {"endpoint_data_type": "CELLULAR_KINETICS"})
    ctx = load_context(ds, aic, None)
    r = check_v01(ctx)
    assert r.status == "FAIL"
    assert "negative" in r.detail.lower()


# ---------------------------------------------------------------------------
# 7. MATERNAL_INFANT_PK missing DYADID → V03 FAIL
# ---------------------------------------------------------------------------
def test_maternal_infant_missing_dyadid(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID"],
        [
            [1, 0,   "", 1, 1],
            [1, 0.5, 2.0, 0, 0],
        ],
    )
    aic = _write_aic(tmp_path, {"endpoint_data_type": "MATERNAL_INFANT_PK"})
    ctx = load_context(ds, aic, None)
    r = check_v03(ctx)
    assert r.status == "FAIL"
    assert "DYADID" in r.detail


# ---------------------------------------------------------------------------
# 8. Audit log missing → A01 FAIL
# ---------------------------------------------------------------------------
def test_audit_log_missing(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID"],
        [[1, 0, "", 1, 1]],
    )
    ctx = load_context(ds, None, None)  # audit_log=None
    r = check_a01(ctx)
    assert r.status == "FAIL"
    assert "missing or empty" in r.detail


# ---------------------------------------------------------------------------
# 9. EVID=1 missing AMT → E05 FAIL
# ---------------------------------------------------------------------------
def test_evid1_missing_amt(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "AMT"],
        [[1, 0, "", 1, 1, ""]],  # dose row with AMT empty
    )
    ctx = load_context(ds, None, None)
    r = check_e05(ctx)
    assert r.status == "FAIL"


# ---------------------------------------------------------------------------
# 10. Column with non-conformant character → S03 FAIL
# ---------------------------------------------------------------------------
def test_bad_column_name(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID", "BAD-COL"],  # hyphen
        [[1, 0, "", 1, 1, "x"]],
    )
    ctx = load_context(ds, None, None)
    r = check_s03(ctx)
    assert r.status == "FAIL"


# ---------------------------------------------------------------------------
# 11. UTF-8 BOM present → S05 FAIL
# ---------------------------------------------------------------------------
def test_bom_present(tmp_path):
    p = tmp_path / "with_bom.csv"
    p.write_bytes("﻿".encode("utf-8") + b"ID,TIME,DV,MDV,EVID\n1,0,,1,1\n")
    ctx = load_context(p, None, None)
    r = check_s05(ctx)
    assert r.status == "FAIL"


# ---------------------------------------------------------------------------
# 12. ID not monotonic non-decreasing → E01 FAIL
# ---------------------------------------------------------------------------
def test_id_decreasing(tmp_path):
    ds = _write_dataset(
        tmp_path,
        ["ID", "TIME", "DV", "MDV", "EVID"],
        [
            [2, 0,   "", 1, 1],
            [1, 0.5, 1.0, 0, 0],  # ID decreases
        ],
    )
    ctx = load_context(ds, None, None)
    r = check_e01(ctx)
    assert r.status == "FAIL"
