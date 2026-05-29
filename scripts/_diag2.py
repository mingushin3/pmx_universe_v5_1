import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "data/scenario_universe/scenario_universe_v1.0.csv").open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
with (ROOT / "data/action_labels/scenario_action_table_locked.csv").open("r", encoding="utf-8") as f:
    al = {r["scenario_id"]: r["candidate_action_label"] for r in csv.DictReader(f)}

for lab in ("AUTO_F01_MAB", "REPAIR_F01_ADA"):
    print(f"\n=== {lab} ===")
    matches = [r for r in rows if al.get(r["scenario_id"]) == lab][:3]
    for r in matches:
        print(f"  scenario={r['scenario_id']} modality={r['modality_class']} edt={r['endpoint_data_type']} A5={r['A5_state']} A7={r['A7_state']}")
