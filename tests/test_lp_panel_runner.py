"""Tests for scripts.lp_panel_runner."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.lp_panel_runner as lpr  # noqa: E402


DECISION_HEADER = [
    "checkpoint_name", "final_decision",
    "confidence", "fatal_resolved", "escalate_to_human",
    "unresolved_fatal_count", "required_patch",
    "affected_artifacts", "required_rerun_steps",
]


def _write_decision_csv(
    tmp_path: Path,
    checkpoint_name: str,
    *,
    confidence: str = "HIGH",
    fatal_resolved: str = "YES",
    escalate: str = "NO",
    unresolved_fatal: int = 0,
    required_patch: str = "",
    final_decision: str = "accept",
) -> Path:
    decisions_dir = tmp_path / "reports" / "llm_proxy"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    csv_path = decisions_dir / f"{checkpoint_name}_decision.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(DECISION_HEADER)
        w.writerow([
            checkpoint_name, final_decision,
            confidence, fatal_resolved, escalate,
            str(unresolved_fatal), required_patch,
            "", "",
        ])
    return csv_path


def _write_template(tmp_path: Path) -> Path:
    template_path = tmp_path / "config" / "lp_panel_template.yaml"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(
        "lp_panel_template:\n  version: 'v5.1'\n  escalation_routing: []\n",
        encoding="utf-8",
    )
    return template_path


def test_auto_apply_when_all_conditions_met(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(tmp_path, "CP1_config_semantic_review")
    result = lpr.evaluate_auto_apply(
        "CP1_config_semantic_review",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is True
    assert result["escalation_target"] is None


def test_low_confidence_escalates(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(tmp_path, "CP1_config_semantic_review", confidence="LOW")
    result = lpr.evaluate_auto_apply(
        "CP1_config_semantic_review",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is False
    assert "LOW" in result["reason"] or "HIGH" in result["reason"]
    assert result["escalation_target"] is not None


def test_unresolved_fatal_escalates(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(tmp_path, "CP4_action_label_adjudication", unresolved_fatal=2)
    result = lpr.evaluate_auto_apply(
        "CP4_action_label_adjudication",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is False
    assert "fatal" in result["reason"].lower()


def test_q15_standalone_in_patch_is_forbidden(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(
        tmp_path, "CP1_config_semantic_review",
        required_patch="Replace Q15A with Q15 to simplify the q_code list.",
    )
    result = lpr.evaluate_auto_apply(
        "CP1_config_semantic_review",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is False
    assert any("HR1" in p or "Q15" in p for p in result["required_patches"])


def test_q15a_in_patch_is_not_flagged(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(
        tmp_path, "CP1_config_semantic_review",
        required_patch="Add Q15A to the disallowed list for A7.",
    )
    result = lpr.evaluate_auto_apply(
        "CP1_config_semantic_review",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is True


def test_q17_in_patch_is_forbidden(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(
        tmp_path, "CP3_repair_semantic_review",
        required_patch="Add Q17 mapping for A5 ambiguity.",
    )
    result = lpr.evaluate_auto_apply(
        "CP3_repair_semantic_review",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is False
    assert any("HR3" in p or "Q17" in p for p in result["required_patches"])


def test_forced_node_drop_is_forbidden(tmp_path):
    template = _write_template(tmp_path)
    _write_decision_csv(
        tmp_path, "CP6_minimal_node_approval",
        required_patch="Remove N5 from the candidate_node_dictionary to reduce cost.",
    )
    result = lpr.evaluate_auto_apply(
        "CP6_minimal_node_approval",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is False
    assert any("HR13" in p or "Forced" in p for p in result["required_patches"])
    assert result["escalation_target"] == "H5"


def test_missing_decision_csv_returns_escalate(tmp_path):
    template = _write_template(tmp_path)
    result = lpr.evaluate_auto_apply(
        "CP1_config_semantic_review",
        template_path=template,
        decisions_dir=tmp_path / "reports" / "llm_proxy",
    )
    assert result["auto_apply"] is False
    assert result["escalation_target"] is not None
    assert "missing" in result["reason"].lower()
