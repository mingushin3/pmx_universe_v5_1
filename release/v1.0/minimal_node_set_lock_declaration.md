# Minimal Node Set Lock Declaration v1.0

**Locked at:** 2026-05-22T08:37:29+00:00

## Selected nodes (19)

- N0
- N1
- N11
- N13
- N14
- N17
- N19
- N2
- N20
- N21
- N22
- N24
- N25
- N27
- N29
- N3
- N4
- N5
- N8

## Forced node compliance (HR13)

forced set {N0, N1, N2, N3, N4, N5, N8} ⊆ selected set — **PASS**.

## ILP solver result

- status: OPTIMAL
- objective: 43.30
- solve_time: 0.071s
- distinguishability coverage: 100% of 50867 required pairs

## LP Panel CP6

simulated `accept` (HIGH confidence, no escalation). Real LP-B
adversarial pass recommended before external release.

## SHA256 hashes

| Artifact | SHA256 |
|---|---|
| `data/ilp/final_minimal_node_set.csv` | `ca40f5e8f6e092b2031e7438c4b07b423a4a69906b6f09bdf71ba00cc92afa5b` |
| `data/ilp/pairwise_distinguishability_matrix.npz` | `20bd7f426ed66edc86a1630e387e3726bff0c3a47dedcde867bf34d7a607498b` |
| `config/ilp_problem_definition.yaml` | `e715e9e4a1bee5d9c2804905b068f0449d3cc76215c553aa173808b092fce082` |
| **COMBINED** | `d95bfd2ac6333f2efd7cca92fade5249644846d8249c7949ed084955ea2f0db6` |

## Modification policy

Any change requires v1.1 release.
