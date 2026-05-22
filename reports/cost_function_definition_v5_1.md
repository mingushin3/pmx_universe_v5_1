# Cost Function Definition v5.1 (PATCH-4: no LP Panel; single R-LLM)

**Date:** 2026-05-22

## Cost components (each 1–5 scale)

| Component | Weight | Description |
|---|---|---|
| failure_risk | 0.30 | NONMEM error probability if node is wrong |
| downstream_impact | 0.25 | Number of subsequent decisions affected |
| implementation_complexity | 0.15 | Code complexity to detect node's answer |
| audit_risk | 0.20 | Regulatory / audit consequence |
| manual_burden | 0.10 | Human review cost when node fails |

`total_cost = 0.30·failure + 0.25·downstream + 0.15·impl + 0.20·audit + 0.10·manual`

## Proposed costs (locked)

| Node | failure | downstream | impl | audit | manual | total | forced |
|---|---|---|---|---|---|---|---|
| N0 | 5 | 5 | 1 | 5 | 3 | **4.20** | YES |
| N1 | 5 | 5 | 1 | 4 | 2 | **3.90** | YES |
| N2 | 5 | 4 | 3 | 4 | 4 | **4.10** | YES |
| N3 | 5 | 5 | 4 | 4 | 4 | **4.50** | YES (v5.1 +) |
| N4 | 5 | 4 | 3 | 4 | 4 | **4.10** | YES (v5.1 +) |
| N5 | 4 | 3 | 2 | 3 | 3 | **3.10** | YES (PATCH-3) |
| N6 | 2 | 2 | 2 | 2 | 2 | **2.00** | NO |
| N7 | 3 | 1 | 1 | 2 | 3 | **2.10** | NO |
| N8 | 5 | 5 | 2 | 5 | 3 | **4.40** | YES (v5.1 NEW) |

## Forced node cost policy (PATCH-3)

`cost_if_excluded = INFINITY` for N0, N1, N2, N3, N4, N5, N8.
ILP constraint (Phase 8): `x_N0 = x_N1 = x_N2 = x_N3 = x_N4 = x_N5 = x_N8 = 1`.

## Immutability

**These costs are LOCKED before ILP execution.** Post-ILP cost changes
are forbidden in v1.0; modification requires v1.1 candidate registration
+ H5 re-signature.
