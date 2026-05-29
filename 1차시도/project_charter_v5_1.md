# Project Charter — PMX-to-NONMEM Scenario Universe v5.1

**Version:** v5.1
**Status:** ACTIVE (Phase 0 charter)
**Universe basis:** Frozen Universe v4.2
**Total prompts:** ~140 (P1–P118 + CHECK scripts)
**Final deliverables:** 9 (D1–D9)
**LP Panels:** 7 checkpoints (CP1–CP7)
**Human checkpoints:** 5 (H1–H5)

---

## 1. Mission Statement

실무적으로 현실성 있는 임의의 데이터셋 조합으로부터 NONMEM-ready dataset까지 발생 가능한
모든 시나리오 universe를 포착하고, 안전상 필수 forced gates(N0, N1, N2, N3, N4, N5, N8)를
고정한 상태에서 남은 optional nodes 중 강화된 distinguishability 제약을 만족하는
**최소 추가 노드 집합**을 ILP로 추출한다.

> **[PATCH MINOR-N3] ILP claim 정확화:** "최소 의사결정 노드"는 ILP가 9개 candidate 중
> 7개를 forced로 고정한 후, optional N6/N7 중 필요한 것을 선택한 결과의 합집합이다.
> "모든 시나리오를 커버하는 최소 노드"가 아니라
> "**distinguishability 제약을 만족하는 최소 추가 노드**"가 정확한 표현이다.

---

## 2. Scope

### 2.1 In scope (Frozen Universe v4.2)
- Axes: A0–A10 (modality_class, endpoint_data_type 확장, A7 PRODUCT-LEVEL-COVARIATE, A8 analyte_role 포함)
- Q-codes: Q01–Q19 (Q17 제외 — Q13으로 흡수됨)
- Families: F01–F29 (operational), F31–F34 (out-of-scope, 재번호 완료; F30은 버퍼)
- Modalities: SMALL_MOLECULE, PEPTIDE, MAB, ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY, MRNA, VACCINE, OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL, OTHER_CUSTOM (11종)
- Endpoint data types: PK_CONCENTRATION, EXPOSURE_METRIC, CONTINUOUS_PD, CATEGORICAL_PD, COUNT_PD, TTE_EVENT, CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK (10종)

### 2.2 Out of scope
- Raw FCS files, unstructured text, omics features (F31–F33)
- Decision support beyond NONMEM-ready dataset preparation (model fitting/simulation 등)
- Real-time clinical decision (이 시스템은 dataset transformation only)

---

## 3. Hard Rules (HR1–HR14) — 위반 시 시스템 실패

### HR1 — Q15 단독 사용 금지
- Q15 단독 사용 금지. **Q15A, Q15B, Q15C, Q15D만 허용.**
- 위반 시: 모든 generator/checker는 즉시 FAIL.

### HR2 — QUARANTINE은 q_code 동반
- QUARANTINE terminal_state는 반드시 q_code (Q01~Q19) 동반.
- q_code 부재 QUARANTINE = 시스템 결함, 즉시 escalate.

### HR3 — Q17 사용 금지
- Q17은 v4.2에서 Q13으로 흡수됨. **기각된 코드.**
- 모든 산출물에서 Q17 등장 시 자동 FAIL.

### HR4 — REPAIR = 정책 + 유일 출력 알고리즘
- REPAIR terminal_state는 반드시 (a) 정책 명시 + (b) 유일 출력 알고리즘 필수.
- 둘 중 하나라도 부재 시 → QUARANTINE으로 강등.

### HR5 — AUTO에 repair function 포함 금지
- AUTO terminal_state는 어떤 변환 함수도 호출하지 않는다.
- AUTO row에 repair function 호출 발견 시 false-AUTO로 판정, escalate (H4).

### HR6 — endpoint_data_type 필수 선언 (확장된 AIC)
- A0 ∈ {AIC-PKPD, AIC-ER, AIC-TTE, AIC-BIOMARKER, AIC-CELL_THERAPY, AIC-IMMUNOGEN, AIC-LACTATION} 일 때 endpoint_data_type 필수.
- 미선언 시 → Q11.

### HR7 — CELLULAR_KINETICS LLOQ policy 필수
- endpoint_data_type = CELLULAR_KINETICS 시 cellular LLOQ derivation policy 필수.
- 미선언 시 → Q05 (또는 Q07).

### HR8 — IMMUNOGENICITY positivity rule 필수
- endpoint_data_type = IMMUNOGENICITY 시 positivity adjudication rule 필수.
- 미선언 시 → **Q19**.

### HR9 — MATERNAL_INFANT_PK dyad key + delivery anchor 필수
- endpoint_data_type = MATERNAL_INFANT_PK 시 dyad linkage key + delivery anchor 필수.
- 미선언 시 → **Q18**.

### HR10 — analyte_role 필수 (modality 종속)
- analyte_role 미선언 + modality ∈ {ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY} → **Q16**.

### HR11 — Coverage 95% = review-inclusive
- Coverage 95% = AUTO + REPAIR + QUARANTINE (review-inclusive coverage of scenario classes represented in v4.2 universe).
- AUTO + REPAIR만으로 95% 주장 **금지**.

### HR12 — exhaustive completeness 주장 금지 (LLM)
- LLM 산출물은 "all practical scenarios", "exhaustive", "all modalities" 같은 wording 금지.
- Completeness 주장은 generator/checker가 산출하는 수치만 허용.

### HR13 — Forced node 빠지면 escalate
- Forced node set = **{N0 (AIC + endpoint_type), N1 (ID), N2 (time), N3 (dose), N4 (obs), N5 (BLQ), N8 (policy_availability)}**.
- ILP 결과에서 forced node가 빠지면 무조건 escalate → cost function 또는 ILP 정의 오류로 판정.
- N8 정의 (v5.1 NEW): "proposed action_sequence에 필요한 모든 required_policy가 AIC에 선언되어 있으면 Y; 하나라도 부재하면 N". forced=TRUE, cost_if_excluded=∞.
- N8=N 시 terminal_state = QUARANTINE (q_code = 해당 policy 부재 대응 코드).

### HR14 — ILP distinguishability (강화)
- 두 시나리오의 **(terminal_state, action_sequence, q_code, required_policy)** 중 하나라도 다르면 반드시 distinguish 가능해야 함.
- (단순 terminal_state 차이만 보던 v3.1/v4 정의는 폐기.)

---

## 4. Backward Deliverable DAG (요약)

```
D9 ← D8 ← {D6 ← D5 ← D4 ← D3 ← D2 ← (D1, D7)}
        + D7
```

상세는 `reports/backward_artifact_dag.md` 참조.

---

## 5. LP Panel Checkpoints (CP1–CP7)

| CP | 이름 | Phase | 트리거 시점 |
|---|---|---|---|
| CP1 | config_semantic_review | Phase 1 | config YAML 작성 후 (P15–P17) |
| CP2 | universe_attack_and_freeze | Phase 2 | D1 생성 후 (P57) — H2 입구 |
| CP3 | repair_semantic_review (CONDITIONAL) | Phase 4 | D7 구현 후 (P47) |
| CP4 | action_label_adjudication | Phase 5 | label 초안 후 (P73) |
| CP5 | action_label_lock | Phase 5 | label 확정 후 (P80) — H3 입구 |
| CP6 | minimal_node_approval | Phase 9 | ILP 해 후 (P95) |
| CP7 | release_coverage_approval | Phase 12 | release 직전 (P111) — H5 입구 |

LP Panel 구조는 `config/lp_panel_template.yaml` 참조 (P2 산출물).

---

## 6. Human Checkpoints (H1–H5)

| H# | 시점 | 책임 |
|---|---|---|
| H1 | Phase 1 config freeze (pre-pilot) | PHI/legal/IRB risk 검토 |
| H2 | Phase 2 universe freeze (CP2 통과 후) | D1 lock 서명 |
| H3 | Phase 4–5 action label lock (CP3/CP5 통과 후) | D7 + D2 lock 서명 |
| H4 | Phase 11 golden audit (강화) | AUTO 10개 + REPAIR 10개 blinded audit |
| H5 | Phase 12 release approval (CP7 통과 후) | D5/D6/D9 final sign-off |

---

## 7. Coverage Targets (v4.2)

| 항목 | 목표 |
|---|---|
| capture_coverage | ≥ 99% (universe 표현률) |
| review_inclusive (AUTO+REPAIR+QUARANTINE) | ≥ 95% |
| operational (AUTO+REPAIR) | ≥ 75% |
| auto_only (AUTO) | ≥ 35% |
| unsupported+invalid | ≤ 5% |

> HR11에 따라 95% claim은 review-inclusive 기준으로만 허용. AUTO+REPAIR만으로 95% 주장 금지.

---

## 8. LLM Routing Policy

| 역할 태그 | 모델 특성 | 채팅창 분리 |
|---|---|---|
| R-LLM (PMX Grandmaster) | 긴 컨텍스트 + 강한 추론 (Claude Opus 계열 최신 또는 동급) | 같은 창 유지 가능 |
| A-LLM (Adversarial) | **R-LLM과 다른 계열·회사** (Gemini/GPT 최신) | **반드시 새 창** |
| C-LLM (Coding) | Cursor IDE + Claude Sonnet 계열 최신 또는 Claude Code | Cursor 내부 |
| LP-A (Grandmaster) | 고성능 추론 (R-LLM과 동일 계열 가능) | LP Panel 내부 |
| LP-B (Adversarial) | **LP-A와 다른 계열** 필수 | **반드시 새 창** |
| LP-C (Judge) | 고성능 추론, LP-A/B 결과 종합 | LP-A/B 결과 첨부한 새 세션 |
| 간단 문서 작업 | 효율 모델 (Sonnet 계열 최신) | 자유 |

> [PATCH m-6] 모델명은 예시이며 실행 시점 기준 최신 모델로 업데이트. **역할 기준**이지 모델명이 아님.

---

## 9. v4.1 → v4.2가 차단하는 위험 (왜 v4.2가 필요한가)

1. **CELLULAR_KINETICS silent REPAIR** — CAR-T 세포 수 데이터에 농도 LLOQ 알고리즘 잘못 적용 (HR7로 차단)
2. **MATERNAL_INFANT INVALID 오판** — 모체-영아 dyad가 ID 구성 실패로 잘못 INVALID 처리 (HR9로 차단)
3. **IMMUNOGENICITY 잘못된 Q01** — ADA positivity 결정 부재를 BLQ 문제로 오인 (HR8로 차단)

---

## 10. Snowball Execution Principles

1. 프롬프트 → LLM 입력 → 산출물 받기
2. 산출물 → 지정된 폴더에 정확한 파일명으로 저장
3. Python CHECK 스크립트 실행 → PASS면 다음 / FAIL이면 명시된 fallback으로 회귀
4. "다음 액션" 섹션을 따라 다음 프롬프트 진행

각 프롬프트 블록은 5필드를 가짐:
🔹 LLM 라우팅 / 🔹 진입 조건 / 🔹 첨부 파일 / 🔹 산출물 / 🔹 다음 액션

---

## 11. Charter Immutability

본 charter (HR1–HR14, scope, deliverable list)는 v1.0 release까지 immutable.
변경 필요 시 `change_control/` 디렉터리에 RFC 등록 + H5 재서명 필요.

---

*— End of project_charter_v5_1.md —*
