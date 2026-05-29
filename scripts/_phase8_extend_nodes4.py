"""P92 round 4: add 5 more discriminator nodes (N20..N24)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"

with src.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    headers = list(rows[0].keys())
rows = [r for r in rows if r["node_id"] not in {f"N{i}" for i in range(20,25)}]

new_nodes = [
    ("N20", "Is A5=BIOANALYTICAL-FINAL-FLAG-MISSING?", "Y/N", "terminal", "terminal", "",
     "A5", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes Q15A (data package incomplete) from other quarantines.",
     "A5_state == BIOANALYTICAL-FINAL-FLAG-MISSING",
     "2", "v5.1 P92 round 4"),
    ("N21", "Is A8 multi-CMT-class state (drives analyte_role check)?", "Y/N", "terminal", "terminal", "",
     "A8", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes multi-CMT scenarios (Q09/Q16 paths).",
     "A8_state in [MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED]",
     "2", "v5.1 P92 round 4"),
    ("N22", "Is A8=DDI-VICTIM-PERPETRATOR?", "Y/N", "terminal", "terminal", "",
     "A8", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes DDI dual-CMT from other multi-CMT.",
     "A8_state == DDI-VICTIM-PERPETRATOR",
     "2", "v5.1 P92 round 4"),
    ("N23", "Is A10=SEMI-STRUCTURED-LEGACY-FLAG?", "Y/N", "terminal", "terminal", "",
     "A10", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes Q15B from other quarantines.",
     "A10_state == SEMI-STRUCTURED-LEGACY-FLAG",
     "2", "v5.1 P92 round 4"),
    ("N24", "Is A4=ADDL-ACTUAL-CONFLICT?", "Y/N", "terminal", "terminal", "",
     "A4", "n.a.", "FALSE", "1.10", "1.10",
     "Distinguishes ADDL-conflict paths from other regimen paths.",
     "A4_state == ADDL-ACTUAL-CONFLICT",
     "2", "v5.1 P92 round 4"),
]
for n in new_nodes:
    rows.append(dict(zip(headers, n)))
for tgt in (src, dst):
    with tgt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
print(f"nodes: {len(rows)}")
