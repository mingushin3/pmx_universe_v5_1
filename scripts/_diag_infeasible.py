import csv
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = np.load(ROOT / "data/ilp/pairwise_distinguishability_matrix.npz", allow_pickle=True)
inf = data["infeasible_pairs"]

with open(ROOT / "data/decision_table/reduced_decision_table_v1.0.csv","r",encoding="utf-8") as f:
    rows = {r["dc_class_id"]: r for r in csv.DictReader(f)}

print("infeasible:", len(inf))
NCOLS = [f"N{i}" for i in range(18)]
for a, b in inf[:8]:
    ra = rows[a]; rb = rows[b]
    print(f"{a} ({ra['action_label']}) vs {b} ({rb['action_label']})")
    diffs = []
    for c in NCOLS:
        if ra[c] != rb[c]:
            diffs.append(f"{c}={ra[c]}vs{rb[c]}")
    print(f"  N-diffs: {diffs}")
    print(f"  ts {ra['terminal_state']}/{rb['terminal_state']} q {ra['q_code']}/{rb['q_code']} seq_hash {ra['action_sequence_hash']}/{rb['action_sequence_hash']}")
