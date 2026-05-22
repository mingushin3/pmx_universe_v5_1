# check_phase2.py
# Phase 2 (P23-P28) verification
import sys, re
from pathlib import Path

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X] pmx_universe_v5_1 folder not found.")
    sys.exit(1)

print("=" * 60)
print("CHECK-2: Phase 2 (Action Sequence + AIC Lock) verification")
print("=" * 60)

failures = []

REQUIRED = [
    "config/action_sequence_standard.yaml",
    "config/action_function_library.yaml",
    "config/analysis_intent_contract_template.yaml",
    "scripts/config_validation/validate_aic.py",
    "scripts/config_validation/validate_boundary_cases.py",
    "reports/repair_quarantine_boundary_cases_v4_2.csv",
    "reports/boundary_case_semantic_review.md",
    "reports/boundary_case_qcode_validation.md",
    "reports/pilot_edge_case_seed_pack_v5_1.md",
    "reports/phase2_completion_declaration.md",
    "release/v1.0/action_sequence_lock_v1_0.md",
    "release/v1.0/action_sequence_v1_0.sha256",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f)

print("\n[Action sequence v4.2 NEW functions]")
asf = BASE / "config/action_sequence_standard.yaml"
if asf.is_file():
    txt = asf.read_text(encoding="utf-8")
    for fn in [
        "canonicalize_cellular_blq",
        "adjudicate_immunogenicity_positivity",
        "attach_dyad_linkage",
        "derive_time_postpartum_anchor",
        "assign_milk_matrix_lloq",
        "assign_cmt_with_analyte_role",
        "attach_covariate_product_level",
    ]:
        if fn in txt:
            print(f"  [OK] {fn}")
        else:
            print(f"  [XX] {fn}")
            failures.append(fn)

print("\n[Pilot seed pack 20 categories]")
sp = BASE / "reports/pilot_edge_case_seed_pack_v5_1.md"
if sp.is_file():
    txt = sp.read_text(encoding="utf-8")
    keywords = [
        "SDTM", "Multi-study", "SAD/MAD", "Crossover", "DDI victim-only",
        "Pediatric", "TDM", "preclinical",
        "Titration", "Loading-maintenance", "Infusion stop", "ADDL", "Reanalysis",
        "ADC", "Bispecific", "CAR-T", "mRNA", "DDI victim+perpetrator",
        "Pregnancy", "Lactation",
    ]
    found = sum(1 for k in keywords if k.lower() in txt.lower())
    print(f"  match: {found}/20")
    if found >= 18:
        print("  [OK] >= 18 categories matched")
    else:
        print("  [XX] some categories missing")
        failures.append("seed pack categories")

print("\n[SHA256 hashes]")
hf = BASE / "release/v1.0/action_sequence_v1_0.sha256"
if hf.is_file():
    txt = hf.read_text(encoding="utf-8")
    hashes = re.findall(r'\b[a-f0-9]{64}\b', txt)
    if len(hashes) >= 4:
        print(f"  [OK] {len(hashes)} hashes (>=4 = 3 individual + 1 combined)")
    else:
        print(f"  [XX] only {len(hashes)} hashes")
        failures.append("hash count")

print("\n[pytest]")
import subprocess
result = subprocess.run(
    ["python", "-m", "pytest", str(BASE / "tests"), "-q", "--tb=short"],
    capture_output=True, text=True
)
out = result.stdout + result.stderr
print("\n".join(out.splitlines()[-5:]))
if result.returncode != 0:
    failures.append("pytest failure")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 2 complete")
    print("-> Next: Phase 3 (P29) - Pilot data + H1, H2")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
