"""P90: build the pairwise distinguishability matrix (D4) as an npz."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
NODE_IDS = [f"N{i}" for i in range(30)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reduced", default=ROOT / "data" / "decision_table" / "reduced_decision_table_v1.0.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "data" / "ilp" / "pairwise_distinguishability_matrix.npz", type=Path)
    parser.add_argument("--report", default=ROOT / "reports" / "pairwise_matrix_report.md", type=Path)
    args = parser.parse_args(argv)

    with args.reduced.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    M = len(rows)
    N = len(NODE_IDS)
    R = np.zeros((M, M), dtype=np.uint8)
    D = np.zeros((M, M, N), dtype=np.uint8)
    class_ids = [r["dc_class_id"] for r in rows]

    for i in range(M):
        for j in range(i + 1, M):
            a = rows[i]
            b = rows[j]
            required = (
                a["terminal_state"] != b["terminal_state"]
                or a["action_sequence_hash"] != b["action_sequence_hash"]
                or a["q_code"] != b["q_code"]
                or a["required_policy_set"] != b["required_policy_set"]
            )
            if required:
                R[i, j] = R[j, i] = 1
                for k, n in enumerate(NODE_IDS):
                    av = a[n]
                    bv = b[n]
                    if av != "*" and bv != "*" and av != bv:
                        D[i, j, k] = D[j, i, k] = 1

    infeasible = []
    for i in range(M):
        for j in range(i + 1, M):
            if R[i, j] == 1 and D[i, j].sum() == 0:
                infeasible.append((class_ids[i], class_ids[j]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out,
        R=R, D=D,
        class_ids=np.array(class_ids),
        node_ids=np.array(NODE_IDS),
        infeasible_pairs=np.array(infeasible) if infeasible else np.array([]),
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    node_power = D.sum(axis=(0, 1)) // 2
    lines = [
        "# Pairwise Matrix Report",
        "",
        f"M (DC classes): {M}",
        f"total_pairs: {M * (M - 1) // 2}",
        f"distinguishable_required_count: {int(R.sum() // 2)}",
        f"infeasible_pair_count: {len(infeasible)}",
        "",
        "## Per-node distinguishing power",
    ]
    for k, nid in enumerate(NODE_IDS):
        lines.append(f"- {nid}: distinguishes {int(node_power[k])} pairs")
    if infeasible:
        lines.append("")
        lines.append("## Infeasible pairs")
        for a, b in infeasible[:50]:
            lines.append(f"- {a} ↔ {b}")
        if len(infeasible) > 50:
            lines.append(f"- ... ({len(infeasible)} total)")
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"M={M}, required_pairs={int(R.sum()//2)}, infeasible={len(infeasible)}")
    return 0 if not infeasible else 1


if __name__ == "__main__":
    raise SystemExit(main())
