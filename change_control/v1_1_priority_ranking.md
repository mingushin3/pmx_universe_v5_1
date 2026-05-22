# v1.1 Candidate Priority Ranking (P139)

**Input:** `change_control/v1_1_candidate_register.csv` (snapshot 2026-05-22)

## Ranking criteria applied

- CRITICAL severity → top tier (none currently)
- Affects F24–F29 (v4.2 new modalities) → high priority
- Affects multiple cases or downstream artifacts → higher priority
- Single AIC-field / doc fix → low effort, move up
- Requires full phase re-execution → high effort, move down

## Ranked list

| rank | candidate_id | severity | effort | reason | target_v1_1_sprint |
|---|---|---|---|---|---|
| 1 | V1_1_001 | MAJOR | medium | Real-data H4 replay; required for any sponsor-facing release | Sprint A (audit & sign-off) |
| 2 | V1_1_002 | MINOR | medium | F09 + F12 generator gap (closes 2 deferred goldens, enables F12 pediatric SOP rollout) | Sprint A (universe expansion) |
| 3 | V1_1_003 | MINOR | low | F25 + F27 golden registration (golden-validation evidence for 2 more v4.2 families) | Sprint A (validation) |
| 4 | V1_1_006 | MINOR | low | Q08 + Q12 generator paths (closes 100-case soft gaps; same Sprint A as V1_1_002) | Sprint A (universe expansion) |
| 5 | V1_1_005 | MINOR | trivial | CP1 doc nits (N8 Q15A normalization, F30 reservation comment) | Sprint A (docs) |
| 6 | V1_1_004 | MINOR | trivial | D3 / D4 release-hash entries (housekeeping) | Sprint A (docs) |

## v1.1 sprint plan (illustrative)

**Sprint A (week 1–2):**
- V1_1_001: schedule real reviewer; re-issue H1–H5 logs
- V1_1_002 + V1_1_006: extend seed-pack with F09 + F12 + Q08-triggering scenarios; regenerate
- V1_1_003: add F25 + F27 golden registry entries
- V1_1_005 + V1_1_004: documentation pass

**Sprint B (week 3):**
- Re-run CHECK-3..CHECK-11
- Re-run CP1–CP7 LP panels with real LP-B (non-Claude)
- H5 sign-off + v1.1.0 tag

Total effort estimate: 2–4 weeks (matches playbook v1.1 cycle expectations).

---
