import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "data/decision_table/reduced_decision_table_v1.0.csv").open("r", encoding="utf-8") as f:
    rows = {r["dc_class_id"]: r for r in csv.DictReader(f)}

NCOLS = [f"N{i}" for i in range(29)]
for cid in ("DC00189", "DC00204"):
    r = rows[cid]
    print(f"\n{cid} ({r['action_label']}):")
    for c in NCOLS:
        print(f"  {c}={r[c]}", end="")
    print()
