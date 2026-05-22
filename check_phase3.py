# check_phase3.py
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("[X] pandas missing"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X] pmx_universe_v5_1 not found"); sys.exit(1)

print("=" * 60)
print("CHECK-3: Phase 3 (Pilot + H1 + H2) verification")
print("=" * 60)

failures = []

KEY = [
    "config/deidentification_checklist_v5_1.md",
    "reports/pilot_sampling_plan_v5_1.md",
    "data/pilot_fingerprints/fingerprint_template.csv",
    "data/pilot_fingerprints/pilot_file_inventory.csv",
    "data/pilot_fingerprints/empirical_fingerprints_pilot.csv",
    "data/golden_datasets/golden_dataset_registry_draft.csv",
    "reports/fingerprint_coding_guide_v5_1.md",
    "reports/pilot_fingerprint_integration_report.md",
    "reports/empirical_gap_analysis.md",
    "reports/seed_pack_coverage_report.md",
    "reports/phase3_completion_declaration.md",
    "reports/human_review/h2_fingerprint_approval_log.md",
]
print("\n[Files]")
for f in KEY:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f"missing: {f}")

deid = BASE / "config/deidentification_checklist_v5_1.md"
if deid.is_file():
    txt = deid.read_text(encoding="utf-8")
    if "checked_by" in txt.lower() and "approved" in txt.lower():
        print("  [OK] H1 deidentification checklist signed")
    else:
        failures.append("H1 signature missing")

raw = BASE / "data/raw_examples"
print("\n[Raw examples]")
if raw.is_dir():
    cnt = sum(1 for p in raw.rglob("*") if p.is_file() and not p.name.startswith("."))
    print(f"  raw files: {cnt}")
    if cnt >= 20:
        print("  [OK] >= 20 files")
    else:
        failures.append(f"raw {cnt}/20")

print("\n[Fingerprint CSV]")
fp = BASE / "data/pilot_fingerprints/empirical_fingerprints_pilot.csv"
if fp.is_file():
    df = pd.read_csv(fp)
    print(f"  total fingerprints: {len(df)}")
    for col in ["modality_class", "endpoint_data_type", "analyte_role", "seed_category_id"]:
        if col in df.columns:
            print(f"  [OK] col {col}")
        else:
            failures.append(f"col {col}")

    total = df.shape[0] * df.shape[1]
    unk = (df.map(lambda x: isinstance(x, str) and x.upper().strip() == "UNKNOWN")).sum().sum()
    rate = unk / total if total else 0
    print(f"  UNKNOWN rate: {rate:.1%}")
    if rate < 0.40:
        print("  [OK] <40%")
    else:
        failures.append("UNKNOWN rate")

    if "expected_q_code" in df.columns:
        q = df["expected_q_code"].astype(str).str.strip()
        q15 = (q == "Q15").sum()
        q17 = (q == "Q17").sum()
        if q15 == 0:
            print("  [OK] Q15 standalone 0")
        else:
            failures.append("Q15 standalone")
        if q17 == 0:
            print("  [OK] Q17 0")
        else:
            failures.append("Q17")

    if "seed_category_id" in df.columns:
        seen = df["seed_category_id"].dropna().astype(str).unique()
        n = len([x for x in seen if x not in ("", "nan")])
        print(f"  seed coverage: {n}/20")
        if n == 20:
            print("  [OK] 20/20")
        else:
            failures.append(f"seed {n}/20")

print("\n[Golden Registry]")
gr = BASE / "data/golden_datasets/golden_dataset_registry_draft.csv"
if gr.is_file():
    df = pd.read_csv(gr)
    print(f"  golden candidates: {len(df)}")
    if len(df) >= 3:
        print("  [OK] >=3")
    else:
        failures.append(f"golden {len(df)}/3")

print("\n[H2 approval log]")
h2 = BASE / "reports/human_review/h2_fingerprint_approval_log.md"
if h2.is_file():
    if "APPROVED" in h2.read_text(encoding="utf-8").upper():
        print("  [OK] APPROVED recorded")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 3 complete")
    print("-> Next: Phase 4 (P41) - Repair Executor")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
