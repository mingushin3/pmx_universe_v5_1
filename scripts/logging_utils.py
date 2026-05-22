"""Logging utilities for pmx_universe_v5_1.

Provides three functions used across all phases to record execution
state into CSV files under reports/. All writes are atomic (write to a
temp file in the same directory, then rename) so an interrupted run
never leaves a partial row visible.

Functions:
    append_execution_log: append one row to reports/execution_log.csv.
    write_gate_result:    append one row to reports/gate_results.csv.
    record_lp_decision:   append one row to reports/lp_decisions.csv.
"""

from __future__ import annotations

import csv
import datetime as _dt
import os
import tempfile
from pathlib import Path
from typing import Iterable

# ----------------------------------------------------------------------
# Resolve project root (folder that contains 'reports/').
# ----------------------------------------------------------------------

def _find_project_root(start: Path | None = None) -> Path:
    p = (start or Path(__file__).resolve()).parent
    for candidate in [p, *p.parents]:
        if (candidate / "reports").is_dir():
            return candidate
    # Fall back to one level above 'scripts/' if nothing found.
    return Path(__file__).resolve().parents[1]


_PROJECT_ROOT = _find_project_root()
_LOG_DIR = _PROJECT_ROOT / "reports"

EXECUTION_LOG = _LOG_DIR / "execution_log.csv"
GATE_LOG = _LOG_DIR / "gate_results.csv"
LP_DECISION_LOG = _LOG_DIR / "lp_decisions.csv"

EXECUTION_HEADER = [
    "step_id", "datetime_iso", "prompt_number", "llm_used",
    "input_files", "output_files",
    "lp_panel_used", "lp_confidence", "lp_escalated",
    "human_required", "gate_status", "fallback_step", "notes",
]

GATE_HEADER = ["step_id", "datetime_iso", "gate_name", "status", "error_detail"]

LP_DECISION_HEADER = [
    "datetime_iso", "checkpoint_name",
    "grandmaster_confidence", "adversarial_fatal_count",
    "judge_decision", "escalated", "auto_applied",
]


# ----------------------------------------------------------------------
# Atomic append helper.
# ----------------------------------------------------------------------

def _atomic_append_row(path: Path, header: list[str], row: list[str]) -> None:
    """Append a single row to ``path``. Writes header if absent.

    Uses write-to-temp + os.replace to make the operation atomic on
    the platforms we support. Never raises on a missing parent directory:
    we create it first.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[list[str]] = []
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows or rows[0] != header:
            rows = [header] + [r for r in rows if r != header]
    else:
        rows = [header]

    rows.append(row)

    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _join(values: Iterable[str] | None) -> str:
    if not values:
        return ""
    return "; ".join(str(v) for v in values)


# ----------------------------------------------------------------------
# Public API.
# ----------------------------------------------------------------------

def append_execution_log(
    step_id: str,
    prompt_number: str,
    llm_used: str,
    input_files: list[str],
    output_files: list[str],
    lp_panel_used: bool = False,
    lp_confidence: str | None = None,
    lp_escalated: bool = False,
    human_required: bool = False,
    gate_status: str = "pending",
    fallback_step: str | None = None,
    notes: str = "",
) -> None:
    """Append one row to reports/execution_log.csv."""
    row = [
        step_id, _now_iso(), prompt_number, llm_used,
        _join(input_files), _join(output_files),
        str(lp_panel_used).lower(),
        lp_confidence or "",
        str(lp_escalated).lower(),
        str(human_required).lower(),
        gate_status,
        fallback_step or "",
        notes,
    ]
    _atomic_append_row(EXECUTION_LOG, EXECUTION_HEADER, row)


def write_gate_result(
    step_id: str,
    gate_name: str,
    status: str,
    error_detail: str | None = None,
) -> None:
    """Append one row to reports/gate_results.csv.

    ``status`` must be one of: PASS / FAIL / CONDITIONAL / ESCALATE.
    """
    allowed = {"PASS", "FAIL", "CONDITIONAL", "ESCALATE"}
    if status not in allowed:
        raise ValueError(f"status must be one of {sorted(allowed)}; got {status!r}")
    row = [step_id, _now_iso(), gate_name, status, error_detail or ""]
    _atomic_append_row(GATE_LOG, GATE_HEADER, row)


def record_lp_decision(
    checkpoint_name: str,
    grandmaster_confidence: str,
    adversarial_fatal_count: int,
    judge_decision: str,
    escalated: bool,
    auto_applied: bool,
) -> None:
    """Append one row to reports/lp_decisions.csv."""
    row = [
        _now_iso(), checkpoint_name,
        grandmaster_confidence,
        str(int(adversarial_fatal_count)),
        judge_decision,
        str(bool(escalated)).lower(),
        str(bool(auto_applied)).lower(),
    ]
    _atomic_append_row(LP_DECISION_LOG, LP_DECISION_HEADER, row)


__all__ = [
    "append_execution_log",
    "write_gate_result",
    "record_lp_decision",
    "EXECUTION_LOG",
    "GATE_LOG",
    "LP_DECISION_LOG",
    "EXECUTION_HEADER",
    "GATE_HEADER",
    "LP_DECISION_HEADER",
]
