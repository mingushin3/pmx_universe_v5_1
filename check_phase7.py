# check_phase7.py
import csv, sys, hashlib
from pathlib import Path

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X]"); sys.exit(1)

print("=" * 60)
print("CHECK-7: Phase 7 (Action Label Lock) verification")
print("=" * 60)
failures = []

REQUIRED = [
    "data/action_labels/scenario_action_table_locked.csv",
    "config/action_label_dictionary_v1_0.yaml",
    "release/v1.0/action_label_lock_v1_0.sha256",
    "release/v1.0/action_label_lock_declaration.md",
    "change_control/H3_action_label_lock.signed.md",
    "reports/label_conflict_report.csv",
    "reports/equivalence_partition_report.md",
    "reports/llm_proxy/action_label_adjudication_decision.csv",
    "reports/llm_proxy/action_label_lock_decision.csv",
    "reports/phase7_completion_declaration.md",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}"); failures.append(f)

# Hash match
d2 = BASE / "data/action_labels/scenario_action_table_locked.csv"
sf = BASE / "release/v1.0/action_label_lock_v1_0.sha256"
if d2.is_file() and sf.is_file():
    h = hashlib.sha256(d2.read_bytes()).hexdigest()
    stored = sf.read_text().strip().split()[0]
    if h == stored:
        print(f"  [OK] D2 hash match {h[:16]}...")
    else:
        failures.append("hash mismatch")

# Label content check
if d2.is_file():
    with d2.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"\n[D2: {len(rows)} rows]")
    labels = {r["candidate_action_label"] for r in rows}
    print(f"  unique labels: {len(labels)}")

    # Hard rule checks
    q15 = sum(1 for r in rows if r["q_code"] == "Q15")
    q17 = sum(1 for r in rows if r["q_code"] == "Q17")
    q_missing = sum(1 for r in rows if r["terminal_state"] == "QUARANTINE" and not r["q_code"])
    if q15 == 0: print("  [OK] Q15 solo 0")
    else: failures.append("Q15 solo")
    if q17 == 0: print("  [OK] Q17 0")
    else: failures.append("Q17")
    if q_missing == 0: print("  [OK] QUARANTINE no missing q_code")
    else: failures.append(f"q_missing {q_missing}")

    # v4.2 label presence
    for tag in ["F26_CBLQ", "F27_ADA", "F29_DYAD", "F24_CMTROLE", "Q19", "Q18", "Q16", "Q01"]:
        if any(tag in lab for lab in labels):
            print(f"  [OK] label contains {tag}")
        else:
            failures.append(f"label missing {tag}")

# CP decisions
for cp in ("action_label_adjudication", "action_label_lock"):
    p = BASE / f"reports/llm_proxy/{cp}_decision.csv"
    if p.is_file():
        rows = list(csv.DictReader(p.open("r", encoding="utf-8", newline="")))
        if rows and rows[-1]["final_decision"] == "accept":
            print(f"  [OK] {cp} accepted")
        else:
            failures.append(f"{cp} not accepted")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 7 complete")
    print("-> Next: Phase 8 (P86) - Decision Table + ILP")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
