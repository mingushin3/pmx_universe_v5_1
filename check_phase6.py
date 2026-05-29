# check_phase6.py
import csv, sys
from pathlib import Path

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("[X] base missing"); sys.exit(1)

print("=" * 60)
print("CHECK-6: Phase 6 (Decision Nodes + Cost) verification")
print("=" * 60)

failures = []

REQUIRED = [
    "config/candidate_node_dictionary_v5_1.csv",
    "config/candidate_node_dictionary_with_costs.csv",
    "config/action_sequence_standard_v1_final.yaml",
    "scripts/decision_table/pilot_node_test.py",
    "reports/pilot_node_test_report.md",
    "reports/cost_function_definition_v5_1.md",
    "reports/phase6_completion_declaration.md",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f)

nd = BASE / "config/candidate_node_dictionary_v5_1.csv"
if nd.is_file():
    with nd.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"\n[Nodes: {len(rows)} expected 9 or 30 per PATCH P92]")
    if len(rows) in (9, 30):
        print(f"  [OK] {len(rows)} nodes")
    else:
        failures.append(f"nodes {len(rows)}/9 or 30")
    forced = [r for r in rows if r["forced_inclusion"] == "TRUE"]
    forced_ids = sorted([r["node_id"] for r in forced])
    expected = ["N0","N1","N2","N3","N4","N5","N8"]
    if forced_ids == expected:
        print(f"  [OK] forced nodes = {forced_ids}")
    else:
        failures.append(f"forced mismatch: {forced_ids} vs {expected}")
    # N8 detection_rule present
    n8 = next((r for r in rows if r["node_id"] == "N8"), None)
    if n8 and n8.get("detection_rule"):
        print("  [OK] N8 detection_rule present")
    else:
        failures.append("N8 detection_rule missing")
    # INFINITY for forced
    inf_ok = all(r.get("cost_if_excluded") == "INFINITY" for r in forced)
    if inf_ok:
        print("  [OK] all forced nodes have cost_if_excluded=INFINITY")
    else:
        failures.append("forced cost_if_excluded != INFINITY")

pnt = BASE / "reports/pilot_node_test_report.md"
if pnt.is_file():
    if "100.0%" in pnt.read_text(encoding="utf-8"):
        print("\n  [OK] pilot node test 100% match")
    else:
        failures.append("pilot node match < 100%")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 6 complete")
    print("-> Next: Phase 7 (P71) - Action Label + CP4/CP5")
else:
    print(f"[RED] GATE FAIL: {len(failures)} items")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
