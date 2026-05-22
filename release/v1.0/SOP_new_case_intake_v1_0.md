# SOP: New Case Intake (v1.0)

**Version:** v1.0 (locked at 2026-05-22T13:50:00+00:00)
**Next review:** at v1.1 release (planned: 6 months from v1.0)

## Purpose

Standard operating procedure for processing new PMX datasets through the v1.0
universe + decision tree + repair executor.

## Scope

Applies to any new PMX dataset arriving at the lab for NONMEM dataset
preparation under the Frozen Universe v4.2 / v1.0 release.

## Step-by-step procedure

### Step 1 — Pre-intake checklist

- [ ] Dataset has a documented analysis intent (AIC YAML with all required fields).
- [ ] Dataset is deidentified (apply `config/deidentification_checklist_v5_1.md` H1 checklist).
- [ ] Source format identified (SDTM / ADaM / EDC / Excel / SAS / etc.).
- [ ] File integrity confirmed (SHA256 of raw input recorded).

### Step 2 — AIC validation

Run:
```
python3 scripts/config_validation/validate_aic.py --aic-file <path>
```

If validation fails:

- Missing `endpoint_data_type` → request from sponsor (Q11).
- Missing v4.2-specific policies (cellular_LLOQ, positivity_adjudication_rule,
  dyad_linkage_key, delivery_anchor) → request from bioanalyst / PMX lead.
- Missing `modality_class` → reject as INVALID until clarified.

### Step 3 — Fingerprint generation

Generate an empirical fingerprint for the new case per Step 2 P32 template,
then H2-review against `data/pilot_fingerprints/fingerprint_template.csv`.

### Step 4 — Decision tree routing

```
python3 scripts/decision_tree/route_scenario.py \
    --fingerprint <path> \
    --tree config/operational_decision_tree.yaml \
    --out <decision_log>.json
```

(Routing script will be added in v1.1; for v1.0 use the
`scripts/decision_tree/verify_tree_table_match.py` walk function directly.)

Produces:
- `terminal_state` (AUTO / REPAIR / QUARANTINE / UNSUPPORTED / INVALID)
- `q_code` (if QUARANTINE)
- `recommended action_sequence`

### Step 5 — Action execution

**If AUTO:**
- Run `scripts/repair_executor/repair_executor.run_repair_pipeline` with
  the recommended `action_sequence`.
- Output: NONMEM-ready dataset.
- Run `python3 scripts/validation/nonmem_ready_qc.py --dataset <out> --aic <aic> --audit-log <log> --out <qc_report>`.
- Deliver to PMX modeler if all 21 QC checks PASS.

**If REPAIR:**
- Same as AUTO but with an audit_log that highlights repair functions used
  and the resolved parameter_policies (from AIC).

**If QUARANTINE:**
- Issue formal quarantine notice to sponsor with `q_code` rationale.
- Indicate required input to clear (per `config/quarantine_reason_codes.yaml`).
- Use the template at `release/v1.0/external_data_request_template.md`
  (issued at P128).

**If UNSUPPORTED:**
- Communicate with sponsor that data is outside operational scope
  (families F31–F34).
- Suggest alternative data acquisition or v2.0 universe upgrade.

**If INVALID:**
- Document why (corruption, missing core column, irreconcilable axis).
- Cannot proceed; requires sponsor remediation.

### Step 6 — Audit & traceability

- Save `decision_log` + `audit_log` to project folder.
- Update `reports/execution_log.csv` with the new case entry.
- All NONMEM-ready outputs require:
  - SHA256 of input
  - SHA256 of output
  - decision_path (from D6 walk)
  - executor version (v1.0 hash: `db3a0793cec04e605735dc5cec0a7d47bd3eece50df5b1358c59f410839b94f0`)
  - tree version (v1.0 hash: `dab2f6f7f44a42fa7db03e9ea83cbe8494b79580b458d31ec655be277bde4288`)

### Step 7 — Coverage tracking

- Increment running counter per `family_id` (used in quarterly metrics
  dashboard, P127).
- Quarterly review for v1.1 candidate cases (any case requiring manual
  override → register via `release/v1.0/SOP_change_control_v1_0.md`).

## Edge cases

### Decision tree routes to QUARANTINE but sponsor insists AUTO/REPAIR

- **DO NOT override.**
- Issue change request via change_control framework (P117 SOP).
- Wait for v1.1 cycle.

### AIC partially specified

- Cannot proceed under v1.0.
- Request complete AIC; do not auto-default policy values.

### New modality not in Frozen Universe v4.2

- Route to F31–F34 (UNSUPPORTED) or escalate to v1.1 candidate register.
- Cannot custom-handle within v1.0.

## Roles & responsibilities

| role | responsibility |
|---|---|
| PMX modeler | receives NONMEM-ready dataset; reports any model-level issues |
| PMX dataset wrangler (operator) | runs SOP for new cases; signs decision_log |
| Bioanalyst | provides positivity rules, cellular_LLOQ values |
| Sponsor | provides AIC and source data |
| PMX lead (H5 signer) | approves any non-routine override |

---

*— End of SOP_new_case_intake_v1_0.md —*
