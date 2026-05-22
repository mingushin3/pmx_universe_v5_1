"""P92 round 6: add N27/N28 (cellular BLQ explicit)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"
with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys())
rows = [r for r in rows if r["node_id"] not in {"N27", "N28"}]
new_nodes = [
    ("N27", "Is A5=CELLULAR-BLQ-DEFINED?", "Y/N", "terminal", "terminal", "",
     "A5", "n.a.", "FALSE", "1.00", "1.00",
     "Distinguishes cellular vs concentration BLQ.",
     "A5_state == CELLULAR-BLQ-DEFINED",
     "2", "v5.1 P92 round 6"),
    ("N28", "Sequence contains canonicalize_cellular_blq specifically?", "Y/N", "terminal", "terminal", "",
     "A5", "n.a.", "FALSE", "1.00", "1.00",
     "Distinguishes cellular BLQ function from concentration BLQ.",
     "action_sequence contains canonicalize_cellular_blq (Poisson-LLOQ subset)",
     "2", "v5.1 P92 round 6"),
]
for n in new_nodes:
    rows.append(dict(zip(headers, n)))
for tgt in (src, dst):
    with tgt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
print(f"nodes: {len(rows)}")
