# Troubleshooting Guide (v1.0)

## 1. Decision tree routes to QUARANTINE but sponsor expects AUTO/REPAIR
- **Do NOT override.**
- Register via `SOP_change_control_v1_0.md` → `v1_1_candidate_register.csv`.
- Issue formal quarantine notice citing the Q-code.

## 2. AIC field missing at intake
- Identify which axis triggers the gate (decision_path will show first `N=N` node).
- Map to Q-code via `config/quarantine_reason_codes.yaml`.
- Request specific field from sponsor (use `external_data_request_template.md`).

## 3. pytest FAIL on repair_executor post-deployment
- Re-verify hashes:
  ```
  shasum -a 256 -c release/v1.0/repair_executor_v1_0.sha256
  ```
- If hash mismatch: file was modified post-lock — restore from release tag.
- If hash matches but tests fail: environment drift (Python version, dep version);
  recreate the locked venv per `requirements.txt`.

## 4. CAR-T (F26) cellular_LLOQ policy absent → Q01 cellular subtype
- Q01 + `endpoint_data_type == CELLULAR_KINETICS` → cellular subtype.
- Document in audit_log: `q_code=Q01`, `q_code_subtype=CELLULAR`.
- Request cellular_LLOQ from bioanalyst.

## 5. Maternal-infant dyad linkage key missing → Q18
- Required: `DYADID` column and dyad-linkage-key declaration in AIC.
- If sponsor cannot provide: cannot run F29 pipeline; suggest data
  acquisition or v1.1 deferred handling.

## 6. v1.1 register growing fast → escalation criteria
Trigger v1.1 cycle if ANY of:
- ≥10 candidates accumulated
- ≥1 CRITICAL severity
- 6 months since v1.0
- Major v4.x universe upgrade

---

*— v1.0 troubleshooting guide —*
