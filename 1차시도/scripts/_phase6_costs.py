"""One-shot helper: write candidate_node_dictionary_with_costs.csv
(copies the v5_1.csv and is the locked input for ILP)."""
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "config" / "candidate_node_dictionary_v5_1.csv"
dst = ROOT / "config" / "candidate_node_dictionary_with_costs.csv"
shutil.copyfile(src, dst)
print(f"wrote {dst}")
