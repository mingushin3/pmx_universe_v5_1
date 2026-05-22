# Success Criteria — PMX-to-NONMEM Scenario Universe v5.1

**Project:** PMX-to-NONMEM Scenario Universe (Frozen Universe v4.2)
**Version:** v5.1
**Status target:** v1.0 release

이 문서는 v1.0 release 승인의 **전제 조건**을 열거한다. 17개 항목 모두 만족해야 H5 서명 가능.

---

## Acceptance Checklist (17 items)

- [ ] **C01.** 9개 final deliverables (D1–D9) 모두 존재하며 각각 SHA256 hash가 `release/v1.0/hashes.txt`에 기록되어 있다.

- [ ] **C02.** q_code 없는 QUARANTINE row 개수 = **0** (D2 `scenario_action_table_locked.csv` 기준; HR2 검증).

- [ ] **C03.** Q15 단독 사용 row 개수 = **0** (Q15A/B/C/D만 등장; HR1 검증).

- [ ] **C04.** Q17 사용 row 개수 = **0** (모든 산출물; HR3 검증).

- [ ] **C05.** REPAIR row 중 executable function이 없는 row 개수 = **0** (D7 `repair_executor.py`의 함수 dispatch 검사; HR4 검증).

- [ ] **C06.** confirmed false AUTO 개수 = **0** (LP_C judge + H4 blinded audit 결과 모두 통과; HR5 검증).

- [ ] **C07.** confirmed false REPAIR 개수 = **0** (LP_C judge + H4 blinded audit 결과 모두 통과; HR4/HR5 검증).

- [ ] **C08.** universe freeze 서명 완료 — H2 sign-off가 `change_control/H2_universe_freeze.signed.md`에 존재.

- [ ] **C09.** action label lock 서명 완료 — H3 sign-off가 `change_control/H3_action_label_lock.signed.md`에 존재.

- [ ] **C10.** forced node set ⊆ minimal node set — `{N0, N1, N2, N3, N4, N5, N8} ⊆ D5.minimal_node_set` (HR13 검증).

- [ ] **C11.** ILP claim scope 문서화 — `release/v1.0/coverage_claim_statement.md`에 Tier A/B/C/D 중 하나가 명시되어 있다.

- [ ] **C12.** 100-case validation plan 존재 — `coverage_validation/100case_plan.md` 존재. **[PATCH MINOR-N2 Option B]** plan은 post-release operational stress test로 운용되며 release 전제 조건이 아니다.

- [ ] **C13.** CHECK-0 ~ CHECK-12 모두 PASS — 각 phase의 CHECK 스크립트 실행 로그가 `reports/check_logs/` 에 보관되어 있고 마지막 줄이 "GATE PASS"이다.

- [ ] **C14.** H1–H5 서명 모두 완료 — `change_control/H1_*.signed.md` … `change_control/H5_*.signed.md` 5개 파일 모두 존재.

- [ ] **C15.** LP Panel 7개 (CP1–CP7) 모두 escalation 해소 또는 H-checkpoint로 라우팅 완료 — `reports/llm_proxy/CP{1..7}_decision.csv` 의 마지막 행이 `final_decision ∈ {accept, accept_with_patch}` 이거나 `escalate_to_human=YES` 이고 해당 H가 sign-off 완료.

- [ ] **C16.** v4.2 patch C16–C24 모두 반영 — `reports/frozen_universe_v4_2_summary.md`에 C16–C24 patch 표 존재하고 각 patch가 어느 산출물에 반영됐는지 명시.

- [ ] **C17.** final release approval (H5) 완료 — `change_control/H5_release_approval.signed.md` 존재 + `release/v1.0/RELEASE_NOTES.md`에 release date 기록.

---

## Verification Matrix (어떤 CHECK 스크립트로 검증되는가)

| Criterion | Primary verifier | Secondary verifier |
|---|---|---|
| C01 | `check_phase12.py` (hash 비교) | manual diff |
| C02 | `check_phase5.py` (D2 column scan) | LP_B attack |
| C03 | `check_phase1.py` + `check_phase5.py` | LP_B attack |
| C04 | 전체 CHECK 스크립트 (cross-cutting) | LP_B attack |
| C05 | `check_phase4.py` (function dispatch) | property-based test |
| C06 | `check_phase11.py` (golden mismatch) | H4 blinded audit |
| C07 | `check_phase11.py` (golden mismatch) | H4 blinded audit |
| C08 | `check_phase2.py` (H2 file existence) | manual |
| C09 | `check_phase5.py` (H3 file existence) | manual |
| C10 | `check_phase9.py` (set 포함관계) | LP_C judge |
| C11 | `check_phase12.py` (wording scan) | manual |
| C12 | `check_phase12.py` (file existence) | manual |
| C13 | `check_phase12.py` (log scan) | manual |
| C14 | `check_phase12.py` (5 H files) | manual |
| C15 | `check_phase12.py` (7 CP CSV 검사) | manual |
| C16 | `check_phase1.py` (patch table scan) | LP_A grandmaster |
| C17 | `check_phase12.py` (H5 + RELEASE_NOTES) | H5 자체 |

---

## Failure Routing

| Criterion 실패 | 즉시 액션 |
|---|---|
| C01 fail | 결손 deliverable의 generating phase로 회귀 |
| C02–C05 fail | HR 위반 → 해당 phase에서 prompt 재실행 + LP_C 재검토 |
| C06–C07 fail | H4 blinded audit 강제 — false 비율이 정의 한계 이상이면 release 보류 |
| C08–C09, C14 fail | 해당 H로 escalate; 서명 누락 절대 우회 불가 |
| C10 fail | ILP cost function 또는 forced node 정의 점검 — distinguishability 완화는 금지 |
| C11 fail | claim wording을 HR11/HR12 준수로 재작성 |
| C13 fail | CHECK 로그 결손 → 해당 phase 재실행 |
| C15 fail | LP Panel 결과가 escalate인데 H sign-off 없음 → H 서명 받거나 phase 재실행 |
| C16 fail | v4.2 patch 누락 → P7 재실행 (frozen_universe_v4_2_summary.md 재생성) |
| C17 fail | H5 미서명 — release 자체 보류 |

---

## Release Gate Statement (요약)

> **All 17 criteria PASS ⟹ v1.0 release approved.**
> **Any single criterion FAIL ⟹ release blocked until criterion is resolved.**

이 문서는 v1.0 release까지 immutable. 변경 시 H5 재서명 필요.

---

*— End of success_criteria.md —*
