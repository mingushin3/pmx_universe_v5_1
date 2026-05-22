"""Shared pytest fixtures for pmx_universe_v5_1.

Adds the project root to ``sys.path`` so tests can ``import scripts.*``
regardless of where pytest is invoked from, and provides fixtures used
across multiple test files.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ----------------------------------------------------------------------
# Shared fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def tmp_universe_dir(tmp_path: Path) -> Path:
    """Copy a minimal config subset to a temp directory.

    Currently copies only ``config/lp_panel_template.yaml`` since that is
    the only YAML the Phase 0 code path consumes. Later phases will
    extend this to copy axis_dictionary.yaml, q_code_dictionary.yaml,
    etc., once those exist.
    """
    src_config = PROJECT_ROOT / "config"
    dst_config = tmp_path / "config"
    dst_config.mkdir(parents=True, exist_ok=True)

    candidates = ["lp_panel_template.yaml"]
    for name in candidates:
        src = src_config / name
        if src.exists():
            shutil.copy2(src, dst_config / name)

    (tmp_path / "reports" / "llm_proxy").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def sample_scenario_row() -> dict:
    """A minimum-valid scenario row spanning axes A0..A10."""
    return {
        "scenario_id": "S0001",
        "A0": "AIC-PKPD",
        "A0_modality_class": "MAB",
        "A0_endpoint_data_type": "PK_CONCENTRATION",
        "A1": "ID-DEFINED",
        "A2": "TIME-DEFINED",
        "A3": "DOSE-DEFINED",
        "A4": "REGIMEN-FIXED",
        "A5": "BIOANALYTICAL-FINAL",
        "A6": "COVARIATE-COMPLETE",
        "A7": "SUBJECT-LEVEL-COVARIATE",
        "A8": "SINGLE-ANALYTE",
        "A8_analyte_role": "PARENT",
        "A9": "REANALYSIS-NONE",
        "A10": "STRUCTURED",
    }


@pytest.fixture
def q_code_set() -> set[str]:
    """All valid Q-codes in v4.2 (Q01..Q19, Q17 EXCLUDED)."""
    codes = {f"Q{i:02d}" for i in range(1, 20)}
    codes.discard("Q17")
    # Replace bare Q15 with Q15A/B/C/D (HR1).
    codes.discard("Q15")
    codes.update({"Q15A", "Q15B", "Q15C", "Q15D"})
    return codes


@pytest.fixture
def forced_node_set() -> set[str]:
    """Forced node set per HR13."""
    return {"N0", "N1", "N2", "N3", "N4", "N5", "N8"}
