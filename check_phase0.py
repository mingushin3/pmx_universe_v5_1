# check_phase0.py
# Phase 0 (P1-P6) 완료 검증
# 실행: python check_phase0.py

import os
import sys
from pathlib import Path

# pmx_universe_v5_1 폴더가 현재 위치 기준 어디에 있는지 자동 탐색
BASE_CANDIDATES = [
    Path("pmx_universe_v5_1"),
    Path("./pmx_universe_v5_1"),
    Path("../pmx_universe_v5_1"),
]
BASE = None
for cand in BASE_CANDIDATES:
    if cand.is_dir():
        BASE = cand
        break

if BASE is None:
    print("[X] pmx_universe_v5_1 folder not found.")
    print("    cwd:", Path.cwd())
    print("    Run from the parent directory of pmx_universe_v5_1.")
    sys.exit(1)

print(f"[OK] BASE: {BASE.resolve()}")
print("=" * 55)
print("CHECK-0: Phase 0 (P1-P6) verification")
print("=" * 55)

REQUIRED_FOLDERS = [
    "config", "data/raw_examples", "data/pilot_fingerprints",
    "data/golden_datasets", "data/scenario_universe",
    "data/action_labels", "data/decision_table", "data/ilp",
    "scripts/config_validation", "scripts/scenario_generator",
    "scripts/repair_executor", "scripts/label_workbench",
    "scripts/decision_table", "scripts/ilp", "scripts/validation",
    "reports/adversarial_reviews", "reports/llm_proxy",
    "reports/human_review", "coverage_validation",
    "change_control", "release/v1.0", "tests/fixtures",
]

REQUIRED_FILES = [
    "README.md", "CHANGELOG.md", ".gitignore",
    "requirements.txt", "pyproject.toml",
    "project_charter_v5_1.md",
    "reports/backward_artifact_dag.md",
    "reports/success_criteria.md",
    "reports/v3_1_to_v5_1_patch_log.md",
    "reports/execution_log.csv",
    "config/lp_panel_template.yaml",
    "scripts/logging_utils.py",
    "scripts/lp_panel_runner.py",
    "tests/conftest.py",
    "tests/test_logging_utils.py",
    "tests/test_lp_panel_runner.py",
]

failures = []

print("\n[Folder check]")
for folder in REQUIRED_FOLDERS:
    p = BASE / folder
    if p.is_dir():
        print(f"  [OK] {folder}")
    else:
        print(f"  [XX] {folder}")
        failures.append(f"missing folder: {folder}")

print("\n[File check]")
for f in REQUIRED_FILES:
    p = BASE / f
    if p.is_file():
        print(f"  [OK] {f}")
    else:
        print(f"  [XX] {f}")
        failures.append(f"missing file: {f}")

charter = BASE / "project_charter_v5_1.md"
if charter.is_file():
    txt = charter.read_text(encoding="utf-8", errors="ignore")
    print("\n[Hard Rules keyword check]")
    keywords = [
        "Q15A", "Q15B", "Q15C", "Q15D",  # HR1
        "Q19", "Q18", "Q16",              # HR8/9/10
        "endpoint_data_type",              # HR6
        "CELLULAR_KINETICS",               # HR7
        "MATERNAL_INFANT",                 # HR9
        "analyte_role",                    # HR10
        "review-inclusive",                # HR11
        "forced node",                     # HR13
        "distinguishability",              # HR14
    ]
    for kw in keywords:
        if kw.lower() in txt.lower():
            print(f"  [OK] {kw}")
        else:
            print(f"  [XX] {kw} missing")
            failures.append(f"hard rule keyword missing: {kw}")

print("\n[pytest run - expecting >= 11 tests pass]")
import subprocess
result = subprocess.run(
    ["python", "-m", "pytest", str(BASE / "tests"), "-v", "--tb=short", "-q"],
    capture_output=True, text=True
)
out = result.stdout + result.stderr
print("\n".join(out.splitlines()[-8:]))
if result.returncode == 0:
    print("  [OK] pytest PASS")
else:
    print("  [XX] pytest FAIL")
    failures.append("pytest failure")

print("\n" + "=" * 55)
if not failures:
    print("[GREEN] GATE PASS: Phase 0 complete")
    print("-> Next: Phase 1 (P7)")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    print("\n-> Re-run the corresponding P-prompt for missing items.")
    sys.exit(1)
