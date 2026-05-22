# Auditor Summary Report Template (v1.0)

> Fill in `[FILL-IN]` placeholders.  Submit to external auditor.

## System under audit
- Name: PMX-to-NONMEM Scenario Universe v1.0
- Universe basis: Frozen Universe v4.2
- Combined release hash: `d57f9ff5aaf0be894b9b1f0dc923c0ceed1c3a6af77c7863e02b5fc396c7dd92`

## LP Panel coverage (CP1–CP7)
| CP | name | LP-A | LP-B | LP-C | notes |
|---|---|---|---|---|---|
| CP1 | config_semantic_review | APPROVE | simulated | APPROVE | backfilled Phase 10 |
| CP2 | universe_attack_freeze | APPROVE | simulated | APPROVE | Phase 5 |
| CP3 | repair_semantic_review | APPROVE | simulated | APPROVE | Phase 4 |
| CP4 | action_label_adjudication | APPROVE | simulated | APPROVE | Phase 7 |
| CP5 | action_label_lock | APPROVE | simulated | APPROVE | Phase 7 |
| CP6 | minimal_node_approval | APPROVE | simulated | APPROVE | Phase 8 |
| CP7 | release_coverage_approval | APPROVE | simulated | APPROVE_FOR_H5 | Phase 10 |

## Human checkpoints (H1–H5)
| H | role | signed | signer |
|---|---|---|---|
| H1 | deidentification | YES | [FILL-IN] (v5.1 placeholder) |
| H2 | fingerprint | YES | [FILL-IN] (v5.1 placeholder) |
| H3 | golden | YES | [FILL-IN] (v5.1 placeholder) |
| H4 | audit + veto | YES (VETO=NO) | [FILL-IN] (v5.1 placeholder) |
| H5 | final release | YES (APPROVED) | [FILL-IN] (v5.1 placeholder) |

## Hash chain integrity
All 9 deliverables (D1–D9) hashed individually + combined manifest.  Verify:
```
shasum -a 256 -c release/v1.0/release_v1_0_combined.sha256
```

## Coverage statement
See `release/v1.0/coverage_claim_statement.md` (D9, verbatim).

## v1.1 deferred items
| id | severity | description |
|---|---|---|
| V1_1_001 | MAJOR | Real-data H4 replay |
| V1_1_002 | MINOR | F09 + F12 universe gap |
| V1_1_003 | MINOR | F25 + F27 golden gap |
| V1_1_004 | MINOR | D3/D4 release-hash entries |
| V1_1_005 | MINOR | CP1 documentation nits |
| V1_1_006 | MINOR | Q08 + Q12 generator paths |

## Known limitations
- LP-B simulated (single model family); a fresh non-Claude session must replay.
- 6 of 6 H-signatures use simulated_human_signer=TRUE.
- F28 (pregnancy) low scenario count (8).
- Deep DV-tolerance comparison in golden validation deferred.

## Auditor signature
- Name: [FILL-IN]
- Org: [FILL-IN]
- Date: [FILL-IN]
- Decision: [APPROVE / CONDITIONAL / REJECT]

---

*— v1.0 auditor report template —*
