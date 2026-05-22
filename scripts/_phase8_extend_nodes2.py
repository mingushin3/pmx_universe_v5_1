"""P92 round 2: append N13..N17 (action-sequence content discriminators)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"

with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys())

# Remove any existing N13..N17 entries so this is idempotent
rows = [r for r in rows if r["node_id"] not in {"N13","N14","N15","N16","N17"}]

new_nodes = [
    ("N13", "Does sequence include BLQ canonicalization?", "Y/N", "terminal", "terminal", "",
     "A5", "n.a.", "FALSE", "1.50", "1.50",
     "Distinguishes BLQ-handling vs no-BLQ paths.",
     "action_sequence contains canonicalize_blq or canonicalize_cellular_blq",
     "2", "v5.1 P92 round 2"),
    ("N14", "Does sequence include dose reconstruction?", "Y/N", "terminal", "terminal", "",
     "A3+A4", "n.a.", "FALSE", "1.50", "1.50",
     "Distinguishes dose-reconstruction paths.",
     "action_sequence contains any of reconstruct_dose_* / expand_addl_ii / resolve_addl_actual_conflict",
     "2", "v5.1 P92 round 2"),
    ("N15", "Does sequence include subject_id mapping?", "Y/N", "terminal", "terminal", "",
     "A1", "n.a.", "FALSE", "1.20", "1.20",
     "Distinguishes pooled-study ID disambiguation.",
     "action_sequence contains map_subject_id",
     "2", "v5.1 P92 round 2"),
    ("N16", "Does sequence include reanalysis final selection?", "Y/N", "terminal", "terminal", "",
     "A9", "n.a.", "FALSE", "1.20", "1.20",
     "Distinguishes reanalysis-resolved paths.",
     "action_sequence contains resolve_reanalysis_final",
     "2", "v5.1 P92 round 2"),
    ("N17", "Does sequence include postpartum/elapsed time anchor?", "Y/N", "terminal", "terminal", "",
     "A2", "n.a.", "FALSE", "1.20", "1.20",
     "Distinguishes pregnancy/lactation time-anchor paths.",
     "action_sequence contains derive_time_postpartum_anchor or derive_time_elapsed",
     "2", "v5.1 P92 round 2"),
]
for n in new_nodes:
    rows.append(dict(zip(headers, n)))

for tgt in (src, dst):
    with tgt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
print(f"nodes: {len(rows)}")
