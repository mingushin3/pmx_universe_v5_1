# check_phase4.py
import sys, subprocess
from pathlib import Path

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X] pmx_universe_v5_1 not found"); sys.exit(1)

print("=" * 60)
print("CHECK-4: Phase 4 (Repair Executor) verification")
print("=" * 60)

failures = []

REQUIRED = [
    "config/repair_rule_dictionary.yaml",
    "scripts/repair_executor/repair_executor.py",
    "tests/test_repair_executor_unit.py",
    "tests/test_repair_executor_contract.py",
    "tests/test_repair_executor_property.py",
    "release/v1.0/repair_executor_v1_0.sha256",
    "release/v1.0/repair_executor_lock_v1_0.md",
    "reports/repair_executor_test_report.md",
    "reports/phase4_completion_declaration.md",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f)

print("\n[v4.2 NEW functions in repair_executor.py]")
ex = BASE / "scripts/repair_executor/repair_executor.py"
if ex.is_file():
    txt = ex.read_text(encoding="utf-8")
    for fn in [
        "canonicalize_cellular_blq",
        "adjudicate_immunogenicity_positivity",
        "attach_dyad_linkage",
        "derive_time_postpartum_anchor",
        "assign_milk_matrix_lloq",
        "assign_cmt_with_analyte_role",
        "attach_covariate_product_level",
    ]:
        if f"def {fn}" in txt:
            print(f"  [OK] {fn}")
        else:
            print(f"  [XX] {fn}")
            failures.append(fn)

    for cls in ["class RepairResult", "class QuarantineResult"]:
        if cls in txt:
            print(f"  [OK] {cls}")
        else:
            failures.append(cls)

    import re
    # standalone Q15 occurrences that are not Q15A/B/C/D
    standalone = re.findall(r'q_code\s*=\s*["\']Q15["\']', txt)
    if not standalone:
        print("  [OK] no Q15 standalone")
    else:
        failures.append("Q15 standalone in executor")
    if 'q_code="Q17"' in txt or "q_code='Q17'" in txt:
        print("  [XX] Q17 used")
        failures.append("Q17 used")
    else:
        print("  [OK] Q17 absent")

# pytest run
print("\n[pytest run]")
result = subprocess.run(
    ["python", "-m", "pytest", str(BASE / "tests"), "-q", "--tb=line"],
    capture_output=True, text=True
)
out = result.stdout + result.stderr
print("\n".join(out.splitlines()[-5:]))
if result.returncode != 0:
    failures.append("pytest failure")
else:
    print("  [OK] pytest PASS")

# fixtures count
fix = BASE / "tests/fixtures"
if fix.is_dir():
    csv_n = len(list(fix.glob("*.csv")))
    yml_n = len(list(fix.glob("*.yaml"))) + len(list(fix.glob("*.yml")))
    print(f"\n[Fixtures CSV={csv_n} YAML={yml_n}]")
    if csv_n >= 20:
        print("  [OK] >= 20 CSV")
    else:
        failures.append(f"fixtures {csv_n}/20")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 4 complete")
    print("-> Next: Phase 5 (P53) - Scenario Generator + Universe Freeze")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
