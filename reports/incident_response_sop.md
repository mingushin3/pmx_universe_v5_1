# Incident Response SOP (P137)

## Scope

Procedure when a confirmed false AUTO/REPAIR is detected post-release.

## Steps

1. **Detection.**
   - Source: PMX modeler report, H4 spot-check, sponsor complaint, internal QC.
   - Document in v1.1 register: `issue_type=CLASSIFICATION_FIX`, `severity=CRITICAL`.

2. **Scope assessment.**
   - How many real projects affected?
   - Pull `reports/execution_log.csv` to find all projects routed via the
     same path / leaf.

3. **Escalation.**
   - If ≥1 project with submitted data → escalate to PMX lead + regulatory.
   - If ≥1 project pending submission → halt submission pipeline.

4. **Patch decision.**
   - **Immediate v1.1 micro-release:** for CRITICAL severity affecting active
     submissions.  Standard v1.1 pipeline applied but on accelerated timeline.
   - **Wait for batch v1.1:** for non-critical issues.

5. **Communication.**
   - Notify affected project modelers.
   - Issue formal incident notice to sponsor with the v1.0 → v1.1 patch ETA.

6. **Documentation.**
   - Update `audit_log` for affected cases with "post-release correction".
   - Record the incident in a dedicated `reports/incidents/INC_YYYYMMDD.md`.
   - Append to v1.1 candidate register.

## Severity matrix

| severity | criteria | response |
|---|---|---|
| CRITICAL | submitted data potentially affected | immediate v1.1 + regulatory notification |
| MAJOR | pending submissions affected | v1.1 within 4 weeks |
| MINOR | development-only impact | wait for batch v1.1 |

---
