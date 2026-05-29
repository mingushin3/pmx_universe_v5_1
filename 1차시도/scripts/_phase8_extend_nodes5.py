"""P92 round 5: N25/N26 for modality-analyte distinction."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"
with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys())
rows = [r for r in rows if r["node_id"] not in {"N25", "N26"}]
new_nodes = [
    ("N25", "Modality supports analyte_role tagging?", "Y/N", "terminal", "terminal", "",
     "A0", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes ADC/Bispecific/Cell/Gene from MRNA.",
     "modality_class in [ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY]",
     "2", "v5.1 P92 round 5"),
    ("N26", "Sequence contains assign_cmt_with_analyte_role?", "Y/N", "terminal", "terminal", "",
     "A8", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes role-tagged CMT vs plain multi-CMT.",
     "action_sequence contains assign_cmt_with_analyte_role",
     "2", "v5.1 P92 round 5"),
]
for n in new_nodes:
    rows.append(dict(zip(headers, n)))
for tgt in (src, dst):
    with tgt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
print(f"nodes: {len(rows)}")
