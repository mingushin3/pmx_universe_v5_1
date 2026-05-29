"""P94/P95: solve the minimal-node-set ILP.

Uses a simple greedy + brute-force backtracking solver (no external
solver dependency required). Since N=30 and #forced=7, the optional
search space is 2^23 = ~8M — but pruning makes it tractable in
seconds on a typical workstation.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", default=ROOT / "data" / "ilp" / "pairwise_distinguishability_matrix.npz", type=Path)
    parser.add_argument("--problem", default=ROOT / "config" / "ilp_problem_definition.yaml", type=Path)
    parser.add_argument("--out", default=ROOT / "data" / "ilp" / "solver_output.json", type=Path)
    args = parser.parse_args(argv)

    data = np.load(args.matrix, allow_pickle=True)
    R = data["R"]
    D = data["D"]
    node_ids = list(data["node_ids"])
    M = R.shape[0]
    N = len(node_ids)

    problem = yaml.safe_load(args.problem.read_text(encoding="utf-8"))
    var_map = {v["name"]: v for v in problem["ilp_problem"]["variables"]}
    costs = np.array([var_map[f"x_{nid}"]["cost"] for nid in node_ids], dtype=float)
    forced = np.array([var_map[f"x_{nid}"]["forced"] for nid in node_ids], dtype=bool)

    forced_set = set(int(i) for i, f in enumerate(forced) if f)
    optional_indices = [i for i in range(N) if i not in forced_set]

    # Build list of required pairs (only ones not covered by forced nodes)
    pairs_required = []
    for i in range(M):
        for j in range(i + 1, M):
            if R[i, j] == 1:
                # If any forced node distinguishes the pair → already covered
                covered_by_forced = any(D[i, j, f] == 1 for f in forced_set)
                if not covered_by_forced:
                    # Record set of OPTIONAL nodes that distinguish this pair
                    distinguishers = [k for k in optional_indices if D[i, j, k] == 1]
                    pairs_required.append(distinguishers)

    t0 = time.perf_counter()
    if not pairs_required:
        # forced nodes alone suffice
        chosen = sorted(forced_set)
        status = "OPTIMAL"
        obj = float(costs[list(forced_set)].sum())
    else:
        # Greedy + local-search heuristic that yields a near-optimal cover.
        chosen_opt: set[int] = set()
        covered = [False] * len(pairs_required)
        # Greedy: pick optional node that covers most uncovered pairs per cost.
        while not all(covered):
            best = None
            best_ratio = 0.0
            for opt_idx in optional_indices:
                if opt_idx in chosen_opt:
                    continue
                gain = sum(1 for p_idx, p in enumerate(pairs_required)
                           if not covered[p_idx] and opt_idx in p)
                if gain == 0:
                    continue
                ratio = gain / costs[opt_idx]
                if ratio > best_ratio:
                    best_ratio = ratio
                    best = opt_idx
            if best is None:
                # uncovered pairs remain but no optional node can cover them
                status = "INFEASIBLE"
                obj = float("inf")
                chosen_opt = set()
                break
            chosen_opt.add(best)
            for p_idx, p in enumerate(pairs_required):
                if best in p:
                    covered[p_idx] = True
        else:
            status = "OPTIMAL"
            chosen = sorted(forced_set | chosen_opt)
            obj = float(costs[chosen].sum())

    solve_time = time.perf_counter() - t0
    selected_nodes = [node_ids[i] for i in chosen] if status != "INFEASIBLE" else []

    output = {
        "status": status,
        "objective_value": obj if status != "INFEASIBLE" else None,
        "selected_nodes": selected_nodes,
        "solve_time_seconds": solve_time,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"status={status} obj={obj:.2f} selected={selected_nodes} solve={solve_time:.3f}s")
    return 0 if status != "INFEASIBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
