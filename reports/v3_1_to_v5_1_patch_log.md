# v3.1 → v5.1 Patch Log

Working basis upgrade record for the PMX-to-NONMEM Scenario Universe
prompt sequence. v5.1 incorporates Frozen Universe v4.2 and tightens
several decision-level and review-level rules over v3.1 and v4.

## Patch summary table

| Patch ID | Category | Description | Affected prompts | Risk if ignored |
|---|---|---|---|---|
| P5-01 | UNIVERSE | Frozen Universe upgrade v4.1 → v4.2 | P7–P22, P29, P31 | Silent REPAIR for CELLULAR_KINETICS, false INVALID for maternal-infant dyads, wrong Q01 for immunogenicity adjudication |
| P5-02 | ILP | Distinguishability constraint strengthened | P88, P90 | Minimal node set passes ILP but produces false REPAIR/AUTO |
| P5-03 | ILP | Forced node set made explicit | P56, P58, P90 | ILP drops a safety-critical node, false AUTO on real data |
| P5-04 | LP_PANEL | 13 panels → 7 panels (compression) | Phase 1, 2, 4, 5, 9, 12 | Process drag without proportional adversarial benefit |
| P5-05 | HUMAN | H4 strengthening — AUTO/REPAIR sample blinded audit | P116–P118 | Reviewer rubber-stamps LP-flagged items only; silent false-AUTO survives |
| P5-06 | PILOT | Edge-case seed pack required (20 categories) | P29, P31 | Pilot does not exercise new-modality + special-population paths |
| P5-07 | COVERAGE | Wording restriction (review-inclusive only) | P122, P124 | False "exhaustive" claim → regulatory exposure |
| P5-08 | PYTHON | CHECK script enrichment for v4.2 fields | All CHECK-N | v4.2 deltas merge silently with no test gate |
| P5-09 | TEST | hypothesis library introduction (property-based testing) | Phase 4 (P43–P47) | Repair functions pass spot-checks but fail random valid inputs |

---

## P5-01 — UNIVERSE: Frozen Universe v4.1 → v4.2

### Adds
- `modality_class` auxiliary field on A0 (11 values: SMALL_MOLECULE, PEPTIDE,
  MAB, ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY, MRNA, VACCINE,
  OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL, OTHER_CUSTOM).
- `endpoint_data_type` expansion (10 values total, +4 new):
  CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK.
- A7 PRODUCT-LEVEL-COVARIATE state (CAR-T / cell-therapy lot/batch attributes;
  lot→subject reverse-key join).
- A3 delivery/postpartum anchor note (treat delivery date as ELAPSED anchor).
- N1 maternal-infant dyad linkage path (dyad key + delivery anchor).
- New Q-codes: Q16 (missing analyte_role), Q18 (missing dyad linkage), Q19
  (missing immunogenicity positivity rule).
- Operational families F24–F29 (ADC, Bispecific, CAR-T cellular kinetics,
  mRNA/vaccine, pregnancy PK, lactation/dyad PK).
- F31–F34 (renumbered from old F24–F27; raw FCS, omics, unstructured, INVALID).
- F30 is intentionally not assigned — reserved as numbering buffer.

### Removes / Reclassifies
- Q17 is removed and absorbed into Q13.
- Old F24–F27 are renumbered as F31–F34 (out-of-scope).

### Risk if ignored
- CAR-T cell-count data is silently routed through a concentration LLOQ
  algorithm → false REPAIR.
- Mother-infant studies fail ID construction and are routed to INVALID
  even when dyad data are present.
- Studies lacking an ADA-positivity rule are routed through Q01 (BLQ rule
  missing) instead of Q19 (positivity rule missing) → wrong remediation.

---

## P5-02 — ILP: Distinguishability constraint strengthening

### Old definition (v3.1 / v4)
A scenario pair must differ in at least one selected node, where "differ"
meant the node returned different values.

### New definition (v5.1, HR14)
A scenario pair must be distinguishable by at least one selected node
whenever the pair's (terminal_state, action_sequence, q_code, required_policy)
tuple differs in any single component.

### Affected prompts
- P88 (pairwise matrix construction)
- P90 (ILP formulation)

### Risk if ignored
ILP returns a "minimal" node set that satisfies the weak definition but
collapses two scenarios with different action_sequence or required_policy
into the same path → false REPAIR or false AUTO on real data.

---

## P5-03 — ILP: Forced node set explicit

### Forced inclusion
N0 (AIC + endpoint_type), N1 (ID), N2 (time), N3 (dose), N4 (obs),
N5 (BLQ), N8 (policy_availability).

### Cost penalty
`cost_if_excluded = ∞` (or a sufficiently large constant that the ILP
solver always retains the node).

### N8 definition (v5.1 NEW)
- detection_rule: "proposed action_sequence에 필요한 모든 required_policy가
  AIC에 선언되어 있으면 Y; 하나라도 부재하면 N".
- N8 = N → terminal_state = QUARANTINE (q_code = corresponding policy-absence code).

### Affected prompts
- P56 (cost function)
- P58 (universe attack and freeze)
- P90 (ILP formulation)

### Risk if ignored
Cost optimization eliminates a forced node; on a real dataset the system
proceeds without checking a safety-critical condition.

---

## P5-04 — LP_PANEL: 13 panels → 7 panels (compression)

### Kept (7)
- CP1 config_semantic
- CP2 universe_attack + freeze (merged)
- CP3 repair_semantic (CONDITIONAL)
- CP4 action_label_adjudication
- CP5 action_label_lock
- CP6 minimal_node_approval (absorbs old dangerous_merge)
- CP7 release_coverage (absorbs old claim_scope)

### Cut or merged
- cost_function (Single R-LLM is sufficient; no adversarial benefit observed.)
- ep_split (merged into action_label_adjudication)
- dangerous_merge (merged into minimal_node_approval)
- tree_mismatch (Python CHECK only)
- claim_scope (merged into release_coverage)
- universe_freeze (merged into universe_attack)
- new_case_intake (kept but lighter — single R-LLM with checklist)

### Risk if ignored
Reviewer fatigue → adversarial review becomes ceremonial. Compressing
to 7 panels keeps each review meaningful.

---

## P5-05 — HUMAN: H4 strengthening (blinded sample audit)

### Old (v3.1 / v4)
H4 reviewed only LP-flagged false-classification items.

### New (v5.1)
H4 reviews:
- All LP-flagged items, AND
- A minimum of 10 random AUTO scenarios AND 10 random REPAIR scenarios,
  blinded to their predicted terminal_state.

### Affected prompts
- P116 (audit sampling)
- P117 (audit execution)
- P118 (audit closeout)

### Risk if ignored
LP-flagged-only review systematically misses cases where LP itself was
overconfident (LP_A HIGH + LP_B no fatal attacks but actually wrong).

---

## P5-06 — PILOT: Edge-case seed pack (20 categories)

Pilot fingerprints must include all 20 categories from the seed table
covering routine + new-modality + special-population paths:

routine PK, routine PD, sparse PK, dense PK,
ADC parent + total, ADC conjugated + payload, bispecific binding,
CAR-T cellular kinetics, gene therapy vector copy,
mRNA/vaccine immune response, oligo (ASO/siRNA),
pregnancy PK (single mother), maternal-infant PK dyad,
lactation/milk PK, pediatric, geriatric,
renal impairment, hepatic impairment, DDI study, multi-site.

### Affected prompts
- P29 (pilot fingerprint generator)
- P31 (pilot review)

### Risk if ignored
Pilot only exercises classical PK/PD paths → v4.2 deltas reach release
without ever being run through the system end-to-end.

---

## P5-07 — COVERAGE: Wording restriction

### Allowed
"review-inclusive coverage of scenario classes represented in v4.2 universe"

### Forbidden
"all practical scenarios", "exhaustive", "all modalities", and any phrase
implying universal completeness.

### Affected prompts
- P122 (claim drafting)
- P124 (claim review)

### Risk if ignored
Coverage claim overstates scope; downstream consumer (regulator, internal
reviewer) treats the system as complete when its remit is bounded to v4.2.

---

## P5-08 — PYTHON: CHECK script enrichment for v4.2

All CHECK scripts add v4.2-specific assertions:

- Q16, Q18, Q19 presence in dictionaries
- F24–F29 operational classification + F31–F34 renumbering
- modality_class, analyte_role, endpoint_data_type fields present
- forced node set ⊆ minimal_node_set
- Q15 standalone count = 0
- Q17 usage count = 0
- AUTO row count of repair-function calls = 0

### Risk if ignored
v4.2 additions merge silently with no automated gate.

---

## P5-09 — TEST: hypothesis library introduction

`hypothesis` is added as a project dependency for property-based testing
of `repair_executor` functions.

### Property invariants asserted across random valid (AIC, dataset) pairs
- No Q15 standalone in the output `q_code` column.
- No Q17 in the output `q_code` column.
- `audit_log` is non-empty whenever the terminal_state is REPAIR.
- Row counts in/out are consistent with the policy declared in the AIC.
- `required_policy` declared for every REPAIR row.

### Affected prompts
- P43 (repair executor implementation)
- P44 (repair executor unit tests)
- P47 (repair semantic review)

### Risk if ignored
Hand-written spot-checks pass; random valid inputs surface latent bugs
in REPAIR functions only after action_label_lock — much more expensive
to fix at that point.

---

*— End of v3_1_to_v5_1_patch_log.md —*
