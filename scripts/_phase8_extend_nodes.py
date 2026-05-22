"""P92: append N9..N12 to candidate_node_dictionary_with_costs.csv."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"

with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys()) if rows else []

new_nodes = [
    ("N9", "is_endpoint CELLULAR_KINETICS?", "Y/N", "terminal", "terminal", "",
     "A0", "n.a.", "FALSE", "2.00", "2.00",
     "Distinguishes cellular-kinetics path from other endpoints.",
     "endpoint_data_type == CELLULAR_KINETICS",
     "3", "v5.1 P92 patch — added to resolve infeasible pairs"),
    ("N10", "is_endpoint IMMUNOGENICITY?", "Y/N", "terminal", "terminal", "",
     "A0", "n.a.", "FALSE", "2.00", "2.00",
     "Distinguishes immunogenicity path.",
     "endpoint_data_type == IMMUNOGENICITY",
     "3", "v5.1 P92 patch"),
    ("N11", "is_endpoint MATERNAL_INFANT_PK or MILK_PK?", "Y/N", "terminal", "terminal", "",
     "A0", "n.a.", "FALSE", "2.00", "2.00",
     "Distinguishes maternal-infant / milk paths.",
     "endpoint_data_type in [MATERNAL_INFANT_PK, MILK_PK]",
     "3", "v5.1 P92 patch"),
    ("N12", "is_v4.2 modality (ADC/BISPECIFIC/CELL/GENE/MRNA)?", "Y/N", "terminal", "terminal", "",
     "A0", "n.a.", "FALSE", "2.00", "2.00",
     "Distinguishes v4.2 modality-driven paths.",
     "modality_class in [ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY, MRNA]",
     "3", "v5.1 P92 patch"),
]

# Build dicts matching column order
for n in new_nodes:
    rows.append(dict(zip(headers, n)))

dst.write_text("", encoding="utf-8")
with dst.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=headers)
    w.writeheader()
    w.writerows(rows)

# Also update v5_1.csv so future regenerations stay consistent
with src.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=headers)
    w.writeheader()
    w.writerows(rows)

print(f"nodes now: {len(rows)}")
