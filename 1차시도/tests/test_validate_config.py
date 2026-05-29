"""Tests for scripts/config_validation/validate_config.py."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config_validation import validate_config as vc  # noqa: E402


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def real_config_copy(tmp_path: Path) -> Path:
    """Copy the real project config/ into tmp_path/config/."""
    src = PROJECT_ROOT / "config"
    dst = tmp_path / "config"
    shutil.copytree(src, dst)
    return dst


def _modify_yaml(path: Path, mutator) -> None:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutator(doc)
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


# ----------------------------------------------------------------------
# Test cases (one per failure scenario + happy path)
# ----------------------------------------------------------------------

def test_valid_config_zero_errors(real_config_copy):
    rep = vc.run(real_config_copy)
    if rep.errors:
        pytest.fail("expected 0 errors but got: " + "\n".join(
            f"{e.validator} | {e.file} | {e.detail}" for e in rep.errors
        ))


def test_q15_standalone_triggers_v06(real_config_copy):
    """Inject Q15 standalone into dependency_constraints and expect V06 to fire."""
    target = real_config_copy / "dependency_constraints.yaml"

    def mut(doc):
        doc["dependency_constraints"]["rules"].append({
            "rule_id": "DC999",
            "priority": 99,
            "if_conditions": [{"axis": "A5", "state": "BLQ-NO-POLICY"}],
            "then_terminal": "QUARANTINE",
            "then_q_code": "Q15",
            "rationale": "intentionally bad row",
        })

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V06" for e in rep.errors), \
        "expected V06 to flag Q15 standalone"


def test_q17_triggers_v07(real_config_copy):
    target = real_config_copy / "dependency_constraints.yaml"

    def mut(doc):
        doc["dependency_constraints"]["rules"].append({
            "rule_id": "DC998",
            "priority": 99,
            "if_conditions": [{"axis": "A7", "state": "POLICY-MISSING"}],
            "then_terminal": "QUARANTINE",
            "then_q_code": "Q17",
            "rationale": "intentionally introduces Q17",
        })

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V07" for e in rep.errors), \
        "expected V07 to flag Q17 outside REJECTED entry"


def test_missing_modality_class_triggers_v17(real_config_copy):
    target = real_config_copy / "axis_dictionary.yaml"

    def mut(doc):
        for ax in doc["axis_dictionary"]["axes"]:
            if ax["axis_id"] == "A0":
                ax["auxiliary_fields"] = [
                    f for f in ax.get("auxiliary_fields", [])
                    if f["field"] != "modality_class"
                ]

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V17" for e in rep.errors)


def test_missing_cellular_kinetics_triggers_v18(real_config_copy):
    target = real_config_copy / "axis_dictionary.yaml"

    def mut(doc):
        for ax in doc["axis_dictionary"]["axes"]:
            if ax["axis_id"] == "A0":
                for f in ax["auxiliary_fields"]:
                    if f["field"] == "endpoint_data_type":
                        f["allowed_values"] = [v for v in f["allowed_values"] if v != "CELLULAR_KINETICS"]

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V18" for e in rep.errors)


def test_missing_analyte_role_triggers_v19(real_config_copy):
    target = real_config_copy / "axis_dictionary.yaml"

    def mut(doc):
        for ax in doc["axis_dictionary"]["axes"]:
            if ax["axis_id"] == "A8":
                ax["auxiliary_fields"] = []

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V19" for e in rep.errors)


def test_missing_product_level_covariate_triggers_v20(real_config_copy):
    target = real_config_copy / "axis_dictionary.yaml"

    def mut(doc):
        for ax in doc["axis_dictionary"]["axes"]:
            if ax["axis_id"] == "A7":
                ax["states"] = [s for s in ax["states"] if s["state_code"] != "PRODUCT-LEVEL-COVARIATE"]

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V20" for e in rep.errors)


def test_old_f24_numbering_triggers_v22(real_config_copy):
    """If F24 is moved to operational_scope=false (old v4.1-style numbering),
    V22 must complain that F24 should be operational."""
    target = real_config_copy / "family_assignment_rules.yaml"

    def mut(doc):
        for f in doc["family_assignment_rules"]["families"]:
            if f["family_id"] == "F24":
                f["operational_scope"] = False  # wrong: F24 must be operational

    _modify_yaml(target, mut)
    rep = vc.run(real_config_copy)
    assert any(e.validator == "V22" for e in rep.errors)
