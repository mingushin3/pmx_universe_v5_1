"""LP Panel runner.

Reads ``config/lp_panel_template.yaml`` and a checkpoint's
``reports/llm_proxy/{checkpoint_name}_decision.csv`` produced by
the LP_C stage, then decides whether the decision can be auto-applied
or must escalate to a human checkpoint (H1–H5).

The auto-apply rule comes straight from the template:

    auto_apply = (
        lp_c.confidence == HIGH
        AND lp_c.fatal_resolved == YES
        AND lp_c.escalate_to_human == NO
        AND lp_b.unresolved_fatal_count == 0
    )

The escalation_target is selected from ``escalation_routing`` in the
template. Forbidden patches (Q15 standalone, Q17, dropping forced
nodes, HR11/HR12-violating wording) always force a reject regardless of
the auto-apply rule.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import yaml


# ----------------------------------------------------------------------
# Project root resolution (matches logging_utils).
# ----------------------------------------------------------------------

def _find_project_root(start: Path | None = None) -> Path:
    p = (start or Path(__file__).resolve()).parent
    for candidate in [p, *p.parents]:
        if (candidate / "config").is_dir() and (candidate / "reports").is_dir():
            return candidate
    return Path(__file__).resolve().parents[1]


_PROJECT_ROOT = _find_project_root()

DEFAULT_TEMPLATE_PATH = _PROJECT_ROOT / "config" / "lp_panel_template.yaml"
DEFAULT_DECISIONS_DIR = _PROJECT_ROOT / "reports" / "llm_proxy"


# ----------------------------------------------------------------------
# Forbidden-patch detectors. These are case-insensitive regex matches
# against the decision row's ``required_patch`` field.
# ----------------------------------------------------------------------

_Q15_STANDALONE = re.compile(r"\bQ15(?![A-Da-d])", re.IGNORECASE)
_Q17_ANY = re.compile(r"\bQ17\b", re.IGNORECASE)
_FORCED_NODES = {"N0", "N1", "N2", "N3", "N4", "N5", "N8"}
_FORCED_NODE_DROP = re.compile(
    r"\b(remove|drop|exclude|delete)\b[^\n]{0,80}\b(" + "|".join(_FORCED_NODES) + r")\b",
    re.IGNORECASE,
)
_HR11_VIOLATION = re.compile(
    r"\b(AUTO\s*\+\s*REPAIR)\b[^\n]{0,40}\b95\s*%",
    re.IGNORECASE,
)
_HR12_FORBIDDEN_WORDS = re.compile(
    r"\b(exhaustive|all\s+practical\s+scenarios|all\s+modalities)\b",
    re.IGNORECASE,
)


def _scan_forbidden_patch(text: str) -> list[str]:
    """Return list of forbidden-patch reason strings found in ``text``."""
    reasons: list[str] = []
    if not text:
        return reasons
    if _Q15_STANDALONE.search(text):
        reasons.append("Q15 standalone (HR1 violation)")
    if _Q17_ANY.search(text):
        reasons.append("Q17 used (HR3 violation)")
    if _FORCED_NODE_DROP.search(text):
        reasons.append("Forced node drop (HR13 violation)")
    if _HR11_VIOLATION.search(text):
        reasons.append("AUTO+REPAIR 95% claim (HR11 violation)")
    if _HR12_FORBIDDEN_WORDS.search(text):
        reasons.append("Forbidden completeness wording (HR12 violation)")
    return reasons


# ----------------------------------------------------------------------
# CSV reading.
# ----------------------------------------------------------------------

def _read_last_decision(csv_path: Path) -> dict[str, str]:
    """Return the most recent row of the decision CSV as a dict."""
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Empty decision CSV: {csv_path}")
    return rows[-1]


def _as_int(value: str, field: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Field {field!r} must be integer; got {value!r}") from exc


def _is_yes(value: str) -> bool:
    return str(value).strip().upper() in {"YES", "TRUE", "1"}


def _is_no(value: str) -> bool:
    return str(value).strip().upper() in {"NO", "FALSE", "0"}


# ----------------------------------------------------------------------
# Escalation target selection.
# ----------------------------------------------------------------------

def _select_escalation_target(
    decision_row: dict[str, str],
    template: dict[str, Any],
    forbidden_reasons: list[str],
) -> str:
    """Pick the H-checkpoint to route to. Always returns a non-empty string
    when invoked, since this is only called on the escalation path.
    """
    text_blob = " ".join(decision_row.values()).lower()
    checkpoint = decision_row.get("checkpoint_name", "").lower()

    if any("hr13" in r.lower() or "forced node" in r.lower() for r in forbidden_reasons):
        return "H5"

    if any(kw in text_blob for kw in ("phi", "irb", "legal")):
        if "release" in checkpoint or "cp7" in checkpoint:
            return "H5"
        if "validation" in checkpoint or "golden" in checkpoint or "cp4" in checkpoint or "cp5" in checkpoint:
            return "H4"
        return "H1"

    if any(kw in text_blob for kw in ("false auto", "false repair", "false-auto", "false-repair")):
        return "H4"

    if "release" in checkpoint or "coverage" in checkpoint or "cp7" in checkpoint:
        return "H5"

    if "golden" in checkpoint or "validation" in checkpoint:
        return "H3"

    if "fingerprint" in checkpoint or "phase3" in checkpoint:
        return "H2"

    # Default escalation level: highest available human checkpoint.
    return "H5"


# ----------------------------------------------------------------------
# Public API.
# ----------------------------------------------------------------------

def evaluate_auto_apply(
    checkpoint_name: str,
    template_path: Path | None = None,
    decisions_dir: Path | None = None,
) -> dict[str, Any]:
    """Decide whether the LP_C decision for ``checkpoint_name`` may auto-apply.

    Returns a dict with keys:
        auto_apply (bool)
        reason (str)
        required_patches (list[str])
        escalation_target (str | None)  -- H1..H5 when not auto-applying
    """
    template_path = template_path or DEFAULT_TEMPLATE_PATH
    decisions_dir = decisions_dir or DEFAULT_DECISIONS_DIR

    template = yaml.safe_load(template_path.read_text(encoding="utf-8")) or {}
    csv_path = decisions_dir / f"{checkpoint_name}_decision.csv"
    if not csv_path.exists():
        return {
            "auto_apply": False,
            "reason": f"missing decision CSV: {csv_path}",
            "required_patches": [],
            "escalation_target": "H5",
        }

    row = _read_last_decision(csv_path)

    required_patch = row.get("required_patch", "")
    forbidden = _scan_forbidden_patch(required_patch)

    if forbidden:
        return {
            "auto_apply": False,
            "reason": "forbidden patch detected: " + "; ".join(forbidden),
            "required_patches": forbidden,
            "escalation_target": _select_escalation_target(row, template, forbidden),
        }

    confidence_high = str(row.get("confidence", "")).strip().upper() == "HIGH"
    fatal_resolved_yes = _is_yes(row.get("fatal_resolved", ""))
    escalate_no = _is_no(row.get("escalate_to_human", ""))
    try:
        unresolved_fatal = _as_int(row.get("unresolved_fatal_count", "0"), "unresolved_fatal_count")
    except ValueError:
        unresolved_fatal = 1  # be conservative

    auto_apply = (
        confidence_high
        and fatal_resolved_yes
        and escalate_no
        and unresolved_fatal == 0
    )

    if auto_apply:
        return {
            "auto_apply": True,
            "reason": "all auto_proceed conditions met (HIGH confidence, fatal_resolved, no escalation, no unresolved fatals)",
            "required_patches": [],
            "escalation_target": None,
        }

    failures: list[str] = []
    if not confidence_high:
        failures.append(f"confidence={row.get('confidence','?')} (need HIGH)")
    if not fatal_resolved_yes:
        failures.append("fatal_resolved != YES")
    if not escalate_no:
        failures.append("escalate_to_human == YES")
    if unresolved_fatal != 0:
        failures.append(f"unresolved_fatal_count={unresolved_fatal}")

    return {
        "auto_apply": False,
        "reason": "auto_proceed conditions not met: " + "; ".join(failures),
        "required_patches": [],
        "escalation_target": _select_escalation_target(row, template, []),
    }


__all__ = ["evaluate_auto_apply", "DEFAULT_TEMPLATE_PATH", "DEFAULT_DECISIONS_DIR"]
