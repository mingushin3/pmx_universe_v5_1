"""Tests for scripts/validation/run_golden_validation.py."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validation.run_golden_validation import (  # noqa: E402
    load_decision_table, load_tree, validate_one, walk_tree,
    pick_representative_class,
)


# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def real_tree():
    return load_tree(ROOT / "config/operational_decision_tree.yaml")


@pytest.fixture(scope="module")
def real_classes():
    return load_decision_table(ROOT / "data/decision_table/reduced_decision_table_v1.0.csv")


# ---------------------------------------------------------------------------
def test_walk_tree_with_dc_class(real_tree, real_classes):
    internal, leaves, root = real_tree
    rep = real_classes[0]
    node_values = {f"N{i}": rep[f"N{i}"] for i in range(30)}
    path, leaf, err = walk_tree(node_values, internal, leaves, root)
    assert err is None
    assert leaf["terminal_state"] == rep["terminal_state"]
    assert (leaf.get("q_code") or "") == rep["q_code"]


def test_pick_representative_class_f01_auto(real_classes):
    rep = pick_representative_class(real_classes, "F01", "AUTO")
    assert rep is not None
    assert "F01" in rep["action_label"]
    assert rep["terminal_state"] == "AUTO"


def test_pick_representative_class_f26_repair(real_classes):
    rep = pick_representative_class(real_classes, "F26", "REPAIR")
    assert rep is not None
    assert "F26" in rep["action_label"]
    assert rep["terminal_state"] == "REPAIR"


def test_pick_representative_class_unknown_family(real_classes):
    rep = pick_representative_class(real_classes, "F09", "REPAIR")
    # F09 is not in the synthetic v5.1 universe (HANDOVER §2.1).  Pipeline should
    # return None and flag the golden as MISMATCH at the validate_one level.
    assert rep is None


def test_validate_one_f01_auto_pass(real_classes, real_tree):
    internal, leaves, root = real_tree
    golden = {
        "golden_id": "G_TEST_F01",
        "project_id": "PROJ_TEST",
        "family_id": "F01",
        "expected_terminal_state": "AUTO",
        "expected_q_code": "",
        "reference_output_path": "",
    }
    r = validate_one(golden, real_classes, internal, leaves, root)
    assert r["overall_status"] == "PASS", r
    assert r["terminal_match"] == "Y"


def test_validate_one_f26_repair_pass(real_classes, real_tree):
    internal, leaves, root = real_tree
    golden = {
        "golden_id": "G_TEST_F26",
        "project_id": "PROJ_TEST",
        "family_id": "F26",
        "expected_terminal_state": "REPAIR",
        "expected_q_code": "",
        "reference_output_path": "",
    }
    r = validate_one(golden, real_classes, internal, leaves, root)
    assert r["overall_status"] == "PASS", r


def test_validate_one_family_not_in_universe(real_classes, real_tree):
    internal, leaves, root = real_tree
    golden = {
        "golden_id": "G_TEST_F09",
        "project_id": "PROJ_DDI",
        "family_id": "F09",
        "expected_terminal_state": "REPAIR",
        "expected_q_code": "",
        "reference_output_path": "",
    }
    r = validate_one(golden, real_classes, internal, leaves, root)
    assert r["overall_status"] == "MISMATCH"
    assert "not in synthetic universe" in r["mismatch_detail"]


def test_validate_one_terminal_mismatch(real_classes, real_tree):
    internal, leaves, root = real_tree
    # F26 is REPAIR in the universe; assert that an expected=AUTO golden produces MISMATCH
    golden = {
        "golden_id": "G_TEST_F26_BAD",
        "project_id": "PROJ_X",
        "family_id": "F26",
        "expected_terminal_state": "AUTO",
        "expected_q_code": "",
        "reference_output_path": "",
    }
    r = validate_one(golden, real_classes, internal, leaves, root)
    # representative falls back to family-only since AUTO+F26 doesn't exist; expected fallback class is REPAIR
    # so the actual terminal will be REPAIR; mismatch with expected AUTO
    assert r["overall_status"] == "MISMATCH"
    assert r["terminal_match"] == "N"


def test_validate_one_f24_adc_repair_pass(real_classes, real_tree):
    internal, leaves, root = real_tree
    golden = {
        "golden_id": "G_TEST_F24",
        "project_id": "PROJ_ADC",
        "family_id": "F24",
        "expected_terminal_state": "REPAIR",
        "expected_q_code": "",
        "reference_output_path": "",
    }
    r = validate_one(golden, real_classes, internal, leaves, root)
    assert r["overall_status"] == "PASS"


def test_validate_one_f29_maternal_repair_pass(real_classes, real_tree):
    internal, leaves, root = real_tree
    golden = {
        "golden_id": "G_TEST_F29",
        "project_id": "PROJ_LAC",
        "family_id": "F29",
        "expected_terminal_state": "REPAIR",
        "expected_q_code": "",
        "reference_output_path": "",
    }
    r = validate_one(golden, real_classes, internal, leaves, root)
    assert r["overall_status"] == "PASS"
