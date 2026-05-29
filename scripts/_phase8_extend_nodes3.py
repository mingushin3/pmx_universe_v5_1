"""P92 round 3: add N18 (CMT mapping repair) + N19 (covariate attach repair)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"

with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys())

rows = [r for r in rows if r["node_id"] not in {"N18", "N19"}]
new_nodes = [
    ("N18", "Does sequence include any multi-CMT assignment?", "Y/N", "terminal", "terminal", "",
     "A8", "n.a.", "FALSE", "1.30", "1.30",
     "Distinguishes multi-CMT scenarios.",
     "action_sequence contains assign_cmt_multi / assign_cmt_ddi_* / assign_cmt_with_analyte_role",
     "2", "v5.1 P92 round 3"),
    ("N19", "Does sequence include any covariate attachment?", "Y/N", "terminal", "terminal", "",
     "A7", "n.a.", "FALSE", "1.30", "1.30",
     "Distinguishes product-level / time-varying / external covariate scenarios.",
     "action_sequence contains attach_covariate_* or attach_dyad_linkage",
     "2", "v5.1 P92 round 3"),
]
for n in new_nodes:
    rows.append(dict(zip(headers, n)))
for tgt in (src, dst):
    with tgt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
print(f"nodes: {len(rows)}")
