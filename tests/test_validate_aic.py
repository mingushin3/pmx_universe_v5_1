"""Tests for scripts/config_validation/validate_aic.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config_validation import validate_aic as va  # noqa: E402


def _write_aic(tmp_path: Path, aic: dict) -> Path:
    path = tmp_path / "aic.yaml"
    path.write_text(yaml.safe_dump(aic, sort_keys=False), encoding="utf-8")
    return path


# ----------------------------------------------------------------------
# One test per validator (A01..A08)
# ----------------------------------------------------------------------

def test_a01_missing_core_fields(tmp_path):
    path = _write_aic(tmp_path, {"aic_type": "AIC-PK"})
    rep = va.run(path)
    assert any(e.validator == "A01" for e in rep.errors)


def test_a02_endpoint_required_when_pkpd(tmp_path):
    path = _write_aic(tmp_path, {
        "model_family": "popPKPD",
        "analysis_objective": "dose_recommendation",
        "aic_type": "AIC-PKPD",
    })
    rep = va.run(path)
    assert any(e.validator == "A02" for e in rep.errors)


def test_a03_cellular_lloq_required(tmp_path):
    path = _write_aic(tmp_path, {
        "model_family": "popPK",
        "analysis_objective": "dose_recommendation",
        "aic_type": "AIC-CELL_THERAPY",
        "endpoint_data_type": "CELLULAR_KINETICS",
    })
    rep = va.run(path)
    assert any(e.validator == "A03" and e.q_code == "Q01" for e in rep.errors)


def test_a04_positivity_required_for_immunogenicity(tmp_path):
    path = _write_aic(tmp_path, {
        "model_family": "popPKPD",
        "analysis_objective": "label_support",
        "aic_type": "AIC-IMMUNOGEN",
        "endpoint_data_type": "IMMUNOGENICITY",
    })
    rep = va.run(path)
    assert any(e.validator == "A04" and e.q_code == "Q19" for e in rep.errors)


def test_a05_dyad_and_anchor_required(tmp_path):
    path = _write_aic(tmp_path, {
        "model_family": "popPK",
        "analysis_objective": "regulatory_submission",
        "aic_type": "AIC-LACTATION",
        "endpoint_data_type": "MATERNAL_INFANT_PK",
    })
    rep = va.run(path)
    detected_qcodes = {e.q_code for e in rep.errors if e.validator == "A05"}
    assert "Q18" in detected_qcodes
    assert "Q12" in detected_qcodes


def test_a06_milk_lloq_required(tmp_path):
    path = _write_aic(tmp_path, {
        "model_family": "popPK",
        "analysis_objective": "label_support",
        "aic_type": "AIC-LACTATION",
        "endpoint_data_type": "MILK_PK",
        "dyad_linkage_policy": "mother_id_on_infant_row",
        "delivery_anchor_policy": "delivery_date",
    })
    rep = va.run(path)
    assert any(e.validator == "A06" and e.q_code == "Q01" for e in rep.errors)


def test_a07_analyte_role_required_for_adc(tmp_path):
    path = _write_aic(tmp_path, {
        "model_family": "popPKPD",
        "analysis_objective": "dose_recommendation",
        "aic_type": "AIC-PKPD",
        "endpoint_data_type": "PK_CONCENTRATION",
        "modality_class": "ADC",
        "A8_state": "MULTI-CMT-DEFINED",
        "cmt_analyte_policy": "multi_analyte_role_tagged",
    })
    rep = va.run(path)
    assert any(e.validator == "A07" and e.q_code == "Q16" for e in rep.errors)


def test_a08_consistent_when_all_required_present(tmp_path):
    """Fully populated AIC for CAR-T cellular kinetics → A08 should not flag
    any inconsistencies and overall errors should be 0."""
    path = _write_aic(tmp_path, {
        "model_family": "popPK",
        "analysis_objective": "regulatory_submission",
        "aic_type": "AIC-CELL_THERAPY",
        "modality_class": "CELL_THERAPY",
        "endpoint_data_type": "CELLULAR_KINETICS",
        "cellular_LLOQ_derivation_policy": "poisson_derived",
        "A8_state": "MULTI-CMT-DEFINED",
        "analyte_role": ["VECTOR_COPY", "CAR_POSITIVE_CELL"],
        "cmt_analyte_policy": "multi_analyte_role_tagged",
        "product_level_covariate_linkage_policy": "lot_to_subject_via_manufacturing_record",
        "lot_subject_linkage_key": "LOT_ID",
    })
    rep = va.run(path)
    assert not rep.errors, (
        "expected no errors for fully populated CAR-T AIC; got: "
        + "; ".join(f"{e.validator}/{e.q_code}: {e.detail}" for e in rep.errors)
    )
