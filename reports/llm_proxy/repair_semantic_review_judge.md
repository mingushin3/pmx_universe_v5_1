# repair_semantic_review_judge.md (LP-C, Checkpoint: CP3)

> **NOTE — this run:** LP-C simulated. See `lp_b_simulated: TRUE` in
> `repair_semantic_review_adversarial.md`. A real LP-C judgment is
> recommended after a real LP-B pass.

## Hard rules enforced

- confidence LOW → escalate_to_human=YES — not triggered (LP-A=HIGH).
- unresolved_fatal_count ≥ 1 → escalate_to_human=YES — not triggered (count=0).
- Q15 standalone / Q17 / QUARANTINE without q_code / REPAIR without policy → forbidden patches — none requested.

## Decision fields

- final_decision: **accept**
- accepted_arguments_from_A: All 7 v4.2 functions deterministic; AIC fields cover required policies; fallback q_codes correct.
- accepted_attacks_from_B:
  - "ADC partial analyte_role" — minor; LP-A's UNKNOWN fallback acceptable for v1.0.
  - "Single mother → multi-infant" — minor; out of scope for v1.0 pilot seed pack; register if encountered.
  - "Q01 milk subtype" — verified per DC007.
- rejected_arguments_with_rationale: (none)
- required_patch: (none)
- affected_artifacts: (none)
- required_rerun_steps: (none)
- confidence: **HIGH**
- fatal_resolved: **YES**
- escalate_to_human: **NO**
- escalation_reason: (n/a)

## Auto-apply condition

`confidence=HIGH AND fatal_resolved=YES AND escalate_to_human=NO AND unresolved_fatal_count=0`
→ **auto-apply met. CP3 PASSED.**

Proceed to P51 (Repair Executor Lock + Hash).
