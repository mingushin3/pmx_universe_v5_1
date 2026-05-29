# v1.0 → v2.0 Migration Strategy

## Triggers for v2.0 (not v1.1)
- Breaking axis changes (A0–A10 schema shift).
- Q-code renumbering or re-use of retired codes (Q17).
- `action_function` rename (breaks backward compat).
- Decision tree node-order change (breaks audit-trail compat).
- Universe upgrade beyond v4.x (e.g., v5.0 universe).

## Frozen artifacts that cannot carry over (need full rebuild)
- D1 scenario universe
- D2 action labels
- D3 reduced decision table
- D4 pairwise matrix
- D5 minimal node set
- D6 decision tree
- D7 repair executor
- D8 golden validation report
- D9 coverage claim statement

## Re-use candidates (methodology / structure)
- Pilot fingerprint methodology (Step 2 P29–P36).
- LP Panel template (`config/lp_panel_template.yaml`).
- CHECK script patterns (CHECK-0..CHECK-11).
- 17-success-criteria framework.
- v1.1 candidate register schema.

## Timeline estimate
- v2.0 takes approximately 2× the v1.0 effort (per playbook FAQ Q2).
- v1.1 (incremental): 2–4 weeks per cycle.

---
