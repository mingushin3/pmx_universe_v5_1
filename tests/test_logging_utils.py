"""Tests for scripts.logging_utils."""

from __future__ import annotations

import csv
import importlib
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def fresh_logging_utils(tmp_path, monkeypatch):
    """Reload logging_utils with its log files pointed at tmp_path."""
    if "scripts.logging_utils" in sys.modules:
        del sys.modules["scripts.logging_utils"]
    import scripts.logging_utils as lu

    log_dir = tmp_path / "reports"
    log_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(lu, "EXECUTION_LOG", log_dir / "execution_log.csv")
    monkeypatch.setattr(lu, "GATE_LOG", log_dir / "gate_results.csv")
    monkeypatch.setattr(lu, "LP_DECISION_LOG", log_dir / "lp_decisions.csv")
    return lu


def _read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def test_append_execution_log_creates_header_when_missing(fresh_logging_utils):
    lu = fresh_logging_utils
    assert not lu.EXECUTION_LOG.exists()

    lu.append_execution_log(
        step_id="P1", prompt_number="1", llm_used="R-LLM",
        input_files=["a.md"], output_files=["b.md"],
    )

    rows = _read_csv(lu.EXECUTION_LOG)
    assert rows[0] == lu.EXECUTION_HEADER
    assert len(rows) == 2
    assert rows[1][0] == "P1"
    assert rows[1][3] == "R-LLM"


def test_append_execution_log_appends_without_duplicating_header(fresh_logging_utils):
    lu = fresh_logging_utils
    lu.append_execution_log("P1", "1", "R-LLM", [], [])
    lu.append_execution_log("P2", "2", "C-LLM", ["x.py"], ["y.py"])

    rows = _read_csv(lu.EXECUTION_LOG)
    assert rows[0] == lu.EXECUTION_HEADER
    assert len(rows) == 3
    assert rows[1][0] == "P1"
    assert rows[2][0] == "P2"


def test_append_execution_log_handles_missing_parent_dir(tmp_path, monkeypatch):
    if "scripts.logging_utils" in sys.modules:
        del sys.modules["scripts.logging_utils"]
    import scripts.logging_utils as lu

    target = tmp_path / "does" / "not" / "exist" / "execution_log.csv"
    monkeypatch.setattr(lu, "EXECUTION_LOG", target)

    lu.append_execution_log("P1", "1", "R-LLM", [], [])
    assert target.exists()


def test_append_execution_log_unicode_in_notes(fresh_logging_utils):
    lu = fresh_logging_utils
    lu.append_execution_log(
        "P1", "1", "R-LLM", [], [],
        notes="시나리오 universe 생성 — 한글 OK ✅",
    )
    rows = _read_csv(lu.EXECUTION_LOG)
    assert "시나리오" in rows[1][-1]


def test_append_execution_log_atomic_with_existing_data(fresh_logging_utils):
    """If the log already has rows, appending preserves them all."""
    lu = fresh_logging_utils
    for i in range(5):
        lu.append_execution_log(f"P{i}", str(i), "R-LLM", [], [])
    rows = _read_csv(lu.EXECUTION_LOG)
    assert len(rows) == 1 + 5
    assert [r[0] for r in rows[1:]] == [f"P{i}" for i in range(5)]


def test_write_gate_result_pass(fresh_logging_utils):
    lu = fresh_logging_utils
    lu.write_gate_result("P6", "CHECK-0", "PASS")
    rows = _read_csv(lu.GATE_LOG)
    assert rows[0] == lu.GATE_HEADER
    assert rows[1][2] == "CHECK-0"
    assert rows[1][3] == "PASS"


def test_write_gate_result_invalid_status_raises(fresh_logging_utils):
    lu = fresh_logging_utils
    with pytest.raises(ValueError):
        lu.write_gate_result("P6", "CHECK-0", "OK")


def test_record_lp_decision(fresh_logging_utils):
    lu = fresh_logging_utils
    lu.record_lp_decision(
        checkpoint_name="CP1_config_semantic_review",
        grandmaster_confidence="HIGH",
        adversarial_fatal_count=0,
        judge_decision="accept",
        escalated=False,
        auto_applied=True,
    )
    rows = _read_csv(lu.LP_DECISION_LOG)
    assert rows[0] == lu.LP_DECISION_HEADER
    assert rows[1][1] == "CP1_config_semantic_review"
    assert rows[1][2] == "HIGH"
    assert rows[1][3] == "0"
    assert rows[1][5] == "false"
    assert rows[1][6] == "true"
