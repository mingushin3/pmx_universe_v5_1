# check_phase8.py
import csv, sys, hashlib
from pathlib import Path
try:
    import numpy as np
except ImportError:
    print("[X] numpy missing"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("[X]"); sys.exit(1)

print("=" * 60)
print("CHECK-8: Phase 8 (Decision Table + ILP) verification")
print("=" * 60)
failures = []

REQUIRED = [
    "data/decision_table/reduced_decision_table_v1.0.csv",
    "data/ilp/pairwise_distinguishability_matrix.npz",
    "data/ilp/final_minimal_node_set.csv",
    "data/ilp/solver_output.json",
    "config/ilp_problem_definition.yaml",
    "release/v1.0/minimal_node_set_v1_0.sha256",
    "release/v1.0/minimal_node_set_lock_declaration.md",
    "reports/ilp_solution_report.md",
    "reports/distinguishability_definition_v5_1.md",
    "reports/llm_proxy/minimal_node_approval_decision.csv",
    "reports/phase8_completion_declaration.md",
]
print("\n[Files]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  [OK] {f.split('/')[-1]}")
    else:
        print(f"  [XX] {f}")
        failures.append(f)

# Forced ⊆ selected
import json
solver = json.loads((BASE / "data/ilp/solver_output.json").read_text(encoding="utf-8"))
selected = set(solver["selected_nodes"])
for forced in ("N0","N1","N2","N3","N4","N5","N8"):
    if forced in selected:
        print(f"  [OK] forced {forced} in selected")
    else:
        failures.append(f"forced {forced} missing")

# Infeasible = 0
mat = np.load(BASE / "data/ilp/pairwise_distinguishability_matrix.npz", allow_pickle=True)
inf_count = len(mat.get("infeasible_pairs", []))
if inf_count == 0:
    print(f"  [OK] infeasible pairs = 0")
else:
    print(f"  [XX] infeasible {inf_count}")
    failures.append(f"infeasible {inf_count}")

# Hash match
d5 = BASE / "data/ilp/final_minimal_node_set.csv"
sf = BASE / "release/v1.0/minimal_node_set_v1_0.sha256"
if d5.is_file() and sf.is_file():
    h = hashlib.sha256(d5.read_bytes()).hexdigest()
    if any(h in line for line in sf.read_text().splitlines()):
        print(f"  [OK] D5 hash recorded")
    else:
        failures.append("hash not recorded")

# CP6 accept
cp = BASE / "reports/llm_proxy/minimal_node_approval_decision.csv"
if cp.is_file():
    last = list(csv.DictReader(cp.open("r", encoding="utf-8", newline="")))[-1]
    if last["final_decision"] == "accept":
        print(f"  [OK] CP6 accept")
    else:
        failures.append("CP6 not accepted")

print("\n" + "=" * 60)
if not failures:
    print("[GREEN] GATE PASS: Phase 8 complete")
    print("-> Next: Phase 9 (P101)")
else:
    print(f"[RED] GATE FAIL: {len(failures)}")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
