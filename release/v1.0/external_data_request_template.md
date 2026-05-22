# External Data Request Template (v1.0)

## Quarantine notification

**To:** [Sponsor / data steward]
**From:** [PMX lab]
**Subject:** Dataset placed in QUARANTINE — Q-code `[Q-code]` — `[project_id]`

## Reason for quarantine

Dataset `[project_id]` was routed to QUARANTINE by the v1.0 decision tree at
node `[node_id]`.  Q-code: `[Q-code]`.  See decision_log SHA256:
`[decision_log_hash]`.

## Required information to clear

Refer to `config/quarantine_reason_codes.yaml` `[Q-code]` entry for the
canonical clearance requirement.  Common requests:

| Q | required info |
|---|---|
| Q01 | BLQ policy (M1/M3/M4 specification); cellular_LLOQ if endpoint=CELLULAR_KINETICS |
| Q02 | TIME column mapping (actual / nominal / elapsed / postpartum) |
| Q08 | Dose record completeness (regimen + infusion + ADDL fields) |
| Q11 | Complete AIC YAML with `endpoint_data_type` declared |
| Q12 | Maternal-infant delivery anchor (`delivery_anchor` field) |
| Q15A | Bioanalytical-final flag values |
| Q15B | Legacy flag/field definitions |
| Q15C | Real-world administration log |
| Q15D | Assay reanalysis final-result adjudication rule |
| Q16 | Analyte_role tagging for each CMT |
| Q18 | `DYADID` column + dyad_linkage_key declaration in AIC |
| Q19 | Immunogenicity positivity adjudication rule |

## v4.2-specific requests

- `cellular_LLOQ`: numeric LLOQ for cellular endpoints (CAR-T, F26).
- `positivity_adjudication_rule`: binary rule for immunogenicity (F26+, F27).
- `dyad_linkage_key`: mother-infant linkage variable name (F29).
- `delivery_anchor`: delivery time for postpartum anchor (F29).
- `product_level_linkage`: lot/product identifier for CAR-T product covariates (F26).

## Escalation path

- First response window: 5 business days from notification.
- If sponsor unresponsive: escalate to PMX lead (H5 contact).
- Long-term unresponsive: register `UNIVERSE_GAP` candidate in v1.1 register.

## Signature

- Requester: [FILL-IN]
- Date: [FILL-IN]
- Project ID: `[project_id]`

---
