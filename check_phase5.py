# check_phase5.py
import sys, hashlib
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("[X] pandas missing"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X] base missing"); sys.exit(1)

print("=" * 60)
print("CHECK-5: Phase 5 (Scenario Universe Freeze) verification")
print("=" * 60)

failures = []

REQUIRED = [
    "scripts/scenario_generator/generate_scenarios.py",
    "scripts/scenario_generator/assign_family.py",
    "scripts/scenario_generator/check_pilot_inclusion.py",
    "scripts/validation/calculate_coverage_metrics.py",
    "data/scenario_universe/scenario_universe_v1.0.csv",
    "release/v1.0/scenario_universe_v1_0.sha256",
    "release/v1.0/scenario_universe_freeze_declaration_v1_0.md",
    "reports/coverage_metrics_initial.md",
    "reports/family_coverage_summary.md",
    "reports/pilot_inclusion_check.md",
    "reports/seed_pack_universe_coverage.md",
    "reports/phase5_completion_declaration.md",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f)

uv = BASE / "data/scenario_universe/scenario_universe_v1.0.csv"
if uv.is_file():
    df = pd.read_csv(uv)
    print(f"\n[Universe: {len(df):,} scenarios]")
    if "terminal_state" in df.columns:
        d = df["terminal_state"].value_counts()
        for s, n in d.items():
            print(f"  {s}: {n} ({n/len(df)*100:.1f}%)")
    if "q_code" in df.columns:
        q = df["q_code"].astype(str).str.strip()
        q15 = (q == "Q15").sum()
        q17 = (q == "Q17").sum()
        if q15 == 0: print("  [OK] Q15 solo 0")
        else: failures.append("Q15")
        if q17 == 0: print("  [OK] Q17 0")
        else: failures.append("Q17")
        qmask = df["terminal_state"] == "QUARANTINE"
        qmiss = (qmask & ((q == "") | q.isna())).sum()
        if qmiss == 0: print("  [OK] q_code QUARANTINE 0 missing")
        else: failures.append(f"q_missing {qmiss}")
    if "family_id" in df.columns:
        print("\n[Families]")
        for f in ["F24","F25","F26","F27","F28","F29"]:
            n = (df["family_id"] == f).sum()
            if n > 0: print(f"  [OK] {f}: {n}")
            else: failures.append(f"family {f} empty")
        f30 = (df["family_id"] == "F30").sum()
        if f30 == 0: print("  [OK] F30 reserved (none)")
        else: failures.append("F30 used")

hf = BASE / "release/v1.0/scenario_universe_v1_0.sha256"
if hf.is_file() and uv.is_file():
    computed = hashlib.sha256(uv.read_bytes()).hexdigest()
    stored = hf.read_text().strip().split()[0]
    if computed == stored:
        print(f"  [OK] hash match: {computed[:16]}...")
    else:
        failures.append("hash mismatch")

cm = BASE / "reports/coverage_metrics_initial.md"
if cm.is_file():
    txt = cm.read_text(encoding="utf-8")
    for kw in ["capture_coverage", "review_inclusive", "operational"]:
        if kw in txt:
            print(f"  [OK] {kw}")
        else:
            failures.append(kw)

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 5 complete")
    print("-> Next: Phase 6 (P66) - Decision Nodes + Cost")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
