"""P92 round 7: add N29 (ADA function in sequence)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"
with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys())
rows = [r for r in rows if r["node_id"] != "N29"]
rows.append(dict(zip(headers, (
    "N29", "Sequence contains adjudicate_immunogenicity_positivity?", "Y/N", "terminal", "terminal", "",
    "A5", "n.a.", "FALSE", "1.00", "1.00",
    "Distinguishes ADA-adjudication paths from clean immunogenicity.",
    "action_sequence contains adjudicate_immunogenicity_positivity",
    "2", "v5.1 P92 round 7"))))
for tgt in (src, dst):
    with tgt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
print(f"nodes: {len(rows)}")
