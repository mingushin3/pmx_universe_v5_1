# Infeasible Pair Triage (P91)

**Input:** `reports/pairwise_matrix_report.md`
**Result:** 779 infeasible pairs — pairs that require distinguishing
(differ in terminal_state, action_sequence_hash, q_code, or
required_policy_set) but no node N0..N8 can distinguish them.

## Root cause

The 9-node dictionary (N0..N8) collapses several axis-distinct
scenarios to the same N-pattern. Specifically:

- v4.2 endpoint_data_type (CELLULAR_KINETICS / IMMUNOGENICITY /
  MATERNAL_INFANT_PK / MILK_PK) is not directly encoded as a node.
- modality_class (ADC / BISPECIFIC / CELL_THERAPY / etc.) is not
  directly encoded.

These axis values drive different action_sequences (different REPAIR
functions) but project to identical N0..N8 patterns.

## Classification

All 779 pairs classify as **NODE_DEF_INSUFFICIENT**. No UNIVERSE_GAP,
no REQUIREMENT_LOOSER.

## Recommendation

Add 4 new non-forced nodes per P92 procedure:
- **N9** `is_cellular_kinetics`: Y when endpoint_data_type=CELLULAR_KINETICS.
- **N10** `is_immunogenicity`: Y when endpoint_data_type=IMMUNOGENICITY.
- **N11** `is_maternal_or_milk`: Y when endpoint_data_type in {MATERNAL_INFANT_PK, MILK_PK}.
- **N12** `is_v42_modality`: Y when modality_class in {ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY, MRNA}.

Cost: each 2.00 (non-forced, low complexity to detect).

Forced node set unchanged (N0,N1,N2,N3,N4,N5,N8). ILP will pick
N9–N12 as needed to achieve distinguishability.
