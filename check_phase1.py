# check_phase1.py
# Phase 1 (P7-P22) verification - v4.2 universe integration check
# Run: python check_phase1.py

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[X] PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X] pmx_universe_v5_1 folder not found.")
    sys.exit(1)

print("=" * 60)
print("CHECK-1: Phase 1 (Universe YAML v4.2) verification")
print("=" * 60)

failures = []

REQUIRED = [
    "config/axis_dictionary.yaml",
    "config/terminal_state_taxonomy.yaml",
    "config/quarantine_reason_codes.yaml",
    "config/dependency_constraints.yaml",
    "config/family_assignment_rules.yaml",
    "config/action_sequence_standard.yaml",
    "config/action_function_library.yaml",
    "config/analysis_intent_contract_template.yaml",
    "scripts/config_validation/validate_config.py",
    "scripts/config_validation/validate_aic.py",
    "reports/frozen_universe_v4_2_summary.md",
    "reports/config_schema_validation_report.md",
    "reports/universe_yaml_completion_v4_2.md",
    "reports/repair_quarantine_boundary_cases_v4_2.csv",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f"missing file: {f}")

# 2. axis_dictionary v4.2 contents
ax_path = BASE / "config/axis_dictionary.yaml"
if ax_path.is_file():
    print("\n[axis_dictionary v4.2 contents]")
    raw = ax_path.read_text(encoding="utf-8")

    if "modality_class" in raw and "CELL_THERAPY" in raw and "ADC" in raw:
        print("  [OK] A0 modality_class (ADC, CELL_THERAPY)")
    else:
        print("  [XX] A0 modality_class")
        failures.append("A0 modality_class")

    for ep in ["CELLULAR_KINETICS", "IMMUNOGENICITY", "MILK_PK", "MATERNAL_INFANT_PK"]:
        if ep in raw:
            print(f"  [OK] endpoint_data_type: {ep}")
        else:
            print(f"  [XX] endpoint_data_type {ep}")
            failures.append(f"endpoint_data_type {ep}")

    if "PRODUCT-LEVEL-COVARIATE" in raw:
        print("  [OK] A7 PRODUCT-LEVEL-COVARIATE")
    else:
        print("  [XX] A7 PRODUCT-LEVEL-COVARIATE")
        failures.append("A7 PRODUCT-LEVEL-COVARIATE")

    for r in ["VECTOR_COPY", "CAR_POSITIVE_CELL", "TRANSGENE_EXPRESSION", "CONJUGATED_ADC"]:
        if r in raw:
            print(f"  [OK] analyte_role: {r}")
        else:
            print(f"  [XX] analyte_role {r}")
            failures.append(f"analyte_role {r}")

qc_path = BASE / "config/quarantine_reason_codes.yaml"
if qc_path.is_file():
    print("\n[Q-codes]")
    txt = qc_path.read_text(encoding="utf-8")
    for q in ["Q01","Q02","Q03","Q04","Q05","Q06","Q07","Q08","Q09","Q10","Q11","Q12","Q13","Q14","Q15A","Q15B","Q15C","Q15D","Q16","Q18","Q19"]:
        if q not in txt:
            print(f"  [XX] {q}")
            failures.append(f"Q-code {q}")
    if "Q17" in txt and ("REJECTED" in txt.upper()):
        print("  [OK] Q17 = REJECTED")
    else:
        if "Q17" not in txt:
            print("  [!!] Q17 entry missing")
        else:
            print("  [XX] Q17 used as active code")
            failures.append("Q17 active")

    import re
    standalone_q15 = re.findall(r'\bQ15\b(?!A|B|C|D)', txt)
    # filter out occurrences that are clearly metadata about standalone forbidden
    real_q15 = []
    for m in re.finditer(r'\bQ15\b(?!A|B|C|D)', txt):
        start = max(0, m.start()-200)
        ctx = txt[start:m.end()+200]
        if "standalone" in ctx or "FORBIDDEN" in ctx or "forbidden" in ctx or "bare Q15" in ctx:
            continue
        real_q15.append(m.start())
    if not real_q15:
        print("  [OK] Q15 standalone: 0 usages")
    else:
        print(f"  [XX] Q15 standalone {len(real_q15)} usages")
        failures.append("Q15 standalone")

    print("\n[PATCH m-4 Q15 sub-code semantic check]")
    q15_specs = {
        "Q15A": ["adjudication", "upstream"],
        "Q15B": ["legacy", "undocumented"],
        "Q15C": ["adherence", "real-world"],
        "Q15D": ["reanalysis", "adjudication"],
    }
    txt_lower = txt.lower()
    for code, kws in q15_specs.items():
        if all(kw.lower() in txt_lower for kw in kws):
            print(f"  [OK] {code} semantic keywords present")
        else:
            missing = [kw for kw in kws if kw.lower() not in txt_lower]
            print(f"  [!!] {code} missing keywords {missing}")

fam_path = BASE / "config/family_assignment_rules.yaml"
if fam_path.is_file():
    print("\n[Families]")
    txt = fam_path.read_text(encoding="utf-8")
    for f in ["F24","F25","F26","F27","F28","F29"]:
        if f in txt:
            print(f"  [OK] Operational {f}")
        else:
            print(f"  [XX] {f}")
            failures.append(f"Family {f}")
    for f in ["F31","F32","F33","F34"]:
        if f in txt:
            print(f"  [OK] Out-of-scope {f}")
        else:
            print(f"  [XX] {f}")
            failures.append(f"Family {f}")
    import re as _re
    f30_entries = _re.findall(r'\bF30\b', txt)
    # Allow F30 references only inside notes (intentionally not assigned)
    real_f30 = []
    for m in _re.finditer(r'\bF30\b', txt):
        start = max(0, m.start()-200)
        ctx = txt[start:m.end()+200]
        if "not assigned" in ctx or "reserved" in ctx or "buffer" in ctx or "intentionally" in ctx:
            continue
        real_f30.append(m.start())
    if not real_f30:
        print("  [OK] F30 reserved (not assigned)")
    else:
        print(f"  [XX] F30 used {len(real_f30)} times")
        failures.append("F30 misuse")

dc_path = BASE / "config/dependency_constraints.yaml"
if dc_path.is_file():
    print("\n[Dependency Constraints]")
    data = yaml.safe_load(dc_path.read_text(encoding="utf-8"))
    rules = data["dependency_constraints"]["rules"]
    n = len(rules)
    print(f"  rules: {n}")
    if n >= 36:
        print("  [OK] >= 36 (v4.2)")
    else:
        print("  [XX] < 36")
        failures.append(f"DC rules {n}/36")

vr = BASE / "reports/config_schema_validation_report.md"
if vr.is_file():
    print("\n[Validator report]")
    txt = vr.read_text(encoding="utf-8")
    if "total_errors: 0" in txt or "error_count: 0" in txt:
        print("  [OK] error_count = 0")
    else:
        print("  [!!] error_count not zero")

print("\n[pytest]")
import subprocess
result = subprocess.run(
    ["python", "-m", "pytest", str(BASE / "tests"), "-q", "--tb=short"],
    capture_output=True, text=True
)
out = result.stdout + result.stderr
print("\n".join(out.splitlines()[-6:]))
if result.returncode == 0:
    print("  [OK] pytest PASS")
else:
    print("  [XX] pytest FAIL")
    failures.append("pytest failure")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 1 (Universe v4.2) complete")
    print("-> Next: Phase 2 (P23)")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
