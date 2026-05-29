import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# inspect raw decision table for AUTO_F01_MAB scenarios
with (ROOT / "data/decision_table/raw_decision_table.csv").open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
for sid in ("81532230f032", "9a478d270948"):
    r = next((x for x in rows if x["scenario_id"] == sid), None)
    if r:
        print(f"{sid} ({r['action_label']}): N9={r['N9']} N10={r['N10']} N11={r['N11']} N12={r['N12']}")

# Inspect DC00189 members
with (ROOT / "data/decision_table/reduced_decision_table_v1.0.csv").open("r", encoding="utf-8") as f:
    red = {r["dc_class_id"]: r for r in csv.DictReader(f)}
print(f"\nDC00189 members: {red['DC00189']['member_count']} count")
ids = red["DC00189"]["member_scenario_ids"].split(";")
for sid in ids[:3]:
    r = next((x for x in rows if x["scenario_id"] == sid), None)
    if r:
        print(f"  {sid} label={r['action_label']} N10={r['N10']}")

# Universe row for a425bcdbc01e
with (ROOT / "data/scenario_universe/scenario_universe_v1.0.csv").open("r", encoding="utf-8") as f:
    universe = {r["scenario_id"]: r for r in csv.DictReader(f)}
u = universe.get("a425bcdbc01e")
if u:
    print(f"\nuniverse a425bcdbc01e: A0={u['A0_state']} edt={u['endpoint_data_type']} A5={u['A5_state']} terminal={u['terminal_state']}")
with (ROOT / "data/action_labels/scenario_action_table_locked.csv").open("r", encoding="utf-8") as f:
    al = {r["scenario_id"]: r for r in csv.DictReader(f)}
a = al.get("a425bcdbc01e")
if a:
    print(f"action: label={a['candidate_action_label']} seq={a['action_sequence']}")
