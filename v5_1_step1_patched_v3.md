# PMX-to-NONMEM Scenario Universe v5.1
## Python-Integrated Prompt Sequence (LLM-Maximal Edition)
### Step 1 / 3 — 환경 세팅 + Phase 0~2 (P1~P28)

> **이 문서가 무엇인가요?**
>
> 민구 씨가 LLM에게 "프롬프트만 복사-붙여넣기"하면서 PMX-to-NONMEM 변환 의사결정 시스템을 완성하는 실행 가이드입니다.
>
> 위에서 아래로 순서대로 읽고 따라하면 됩니다. Python 지식이 전혀 없어도 됩니다.
> 각 단계마다 "지금 상태", "다음 액션", "첨부 파일", "Python 검증"이 명시됩니다.

---

## 📜 v5.1의 정체성 (v3.1 → v4 → v5.1 변경 요약)

| 항목 | v3.1 | v4 (파편1) | **v5.1 (이 문서)** |
|---|---|---|---|
| Universe 기준 | v4.1 | v4.1 | **v4.2** (modality 확장 반영) |
| 총 프롬프트 수 | 132 | 136 | **약 140** |
| Python CHECK | 없음 | 11개 | **12개 (강화)** |
| LP Panel | 13개 | 13개 | **7개 (압축)** |
| Forced node | 암묵적 | 암묵적 | **명시적 (A0,A3,A4,A5,A8,A10,policy)** |
| ILP 제약 | 단순 distinguishability | 단순 | **terminal+action_seq+q_code+policy 보존** |
| H4 강화 | 단순 veto | 단순 veto | **AUTO/REPAIR 표본 blinded audit** |
| Pilot edge-case | 미명시 | 미명시 | **20개 seed pack 표 제공** |
| Q-code 수 | Q01-Q15D (18) | Q01-Q15D (18) | **Q01-Q19 (21, Q17 기각)** |
| Family 수 | F01-F23 op + F24-F27 out | 동일 | **F01-F29 op + F31-F34 out** (F30: 번호 예약 — op/out 구분 버퍼) |
| Coverage wording | "review-inclusive" | "review-inclusive" | **"scenario classes represented" 추가 제한** |

### v4.2가 v4.1보다 차단하는 위험

1. **CELLULAR_KINETICS silent REPAIR** — CAR-T 세포 수 데이터에 농도 LLOQ 알고리즘 잘못 적용
2. **MATERNAL_INFANT INVALID 오판** — 모체-영아 dyad가 ID 구성 실패로 잘못 INVALID 처리
3. **IMMUNOGENICITY 잘못된 Q01** — ADA positivity 결정 부재를 BLQ 문제로 오인

이 3개는 v4.1로 그대로 가면 진짜 임상 오류로 이어지는 코드 경로 오류입니다. v5.1은 이를 차단합니다.

---

## 🎯 최종 목표 (역방향 설계의 출발점)

```
실무적으로 현실성 있는 임의의 데이터셋 조합으로부터
NONMEM-ready dataset까지 도달하는 모든 시나리오 universe를 포착하고,
안전상 필수 forced gates(N0, N1, N2, N3, N4, N5, N8)를 고정한 상태에서
남은 optional nodes 중 distinguishability를 만족하는 최소 추가 노드 집합을 ILP로 추출한다.

> ⚠️ **[PATCH MINOR-N3]** "최소 의사결정 노드"는 ILP가 9개 중 7개를 forced로 고정한 후 N6/N7 중 필요 노드를 선택하는 구조입니다. "모든 시나리오를 커버하는 최소 노드"가 아니라 "distinguishability 제약을 만족하는 최소 추가 노드"가 정확한 표현입니다. coverage_claim_statement.md 작성 시 이 표현을 사용하세요.
```

이 한 문장에서 거꾸로 추적한 **9개 핵심 산출물**이 모든 작업의 도달점입니다.

| # | 산출물 | 정의 | 의존하는 산출물 |
|---|---|---|---|
| D1 | `scenario_universe_v1.0.csv` | A0~A10 모든 valid 조합 (v4.2 기준) | config/*.yaml |
| D2 | `scenario_action_table_locked.csv` | 각 시나리오의 terminal_state + q_code + action_label + action_sequence | D1 + repair_executor.py |
| D3 | `reduced_decision_table_v1.0.csv` | N0~N8 답변 매트릭스 (DC reduction 적용) | D2 + node_dictionary |
| D4 | `pairwise_distinguishability_matrix.npz` | scenario pair × node 행렬 | D3 + 강화된 distinguishability 정의 |
| D5 | `final_minimal_node_set.csv` | ILP 최적해로 추출된 최소 결정 노드 집합 | D4 + cost function + forced nodes |
| D6 | `operational_decision_tree.yaml` | 실행 가능한 결정 트리 | D5 + Q-code mapping |
| D7 | `repair_executor.py` | 26+ 변환 함수 (v4.2 신규 7개 포함, 총 26개 이상) | repair_rule_dictionary.yaml |
| D8 | `golden_validation_report.md` | reference output과의 일치 보고서 | D6 + D7 + golden datasets |
| D9 | `coverage_claim_statement.md` | review-inclusive coverage 주장문 | D8 + H4 blinded audit + pilot/seed-pack coverage |

> ✅ **[PATCH MINOR-N2 — Option B 확정]** 이 플레이북은 **Option B를 선택합니다**: 100-case validation은 post-release operational stress test로 운용합니다. D9의 근거는 `D8(golden validation) + H4(blinded audit) + pilot/seed-pack coverage`이며, 100-case 결과는 coverage claim의 전제가 아닌 v1.1 candidate register 트리거 용도입니다. 이 결정은 S3 Phase 11 목적 섹션에서도 동일하게 선언됩니다.
>
> **coverage_claim_statement.md 작성 시 권장 문구 (문서10 기반):**
> ```
> 본 v5.1의 minimal node set은 safety-critical forced gates
> (N0, N1, N2, N3, N4, N5, N8)를 고정한 상태에서,
> 강화된 distinguishability 제약을 만족하는 최소 추가 노드 조합을 ILP로 추출한 것이다.
> 100-case validation은 post-release operational stress test이며,
> release 승인의 전제 조건이 아닌 v1.1 candidate register 트리거 용도이다.
> ```
> 이 문구를 `coverage_claim_statement.md`, `PROJECT_FINAL_COMPLETION_v5_1.md`에 포함하세요.

### 의존성 DAG (역방향)

```
D9 (coverage claim)
 └── D8 (golden validation)
      ├── D6 (decision tree)
      │    └── D5 (minimal node set)
      │         └── D4 (pairwise matrix)
      │              └── D3 (decision table)
      │                   └── D2 (action label table) ← LOCKED
      │                        ├── D1 (scenario universe) ← FROZEN
      │                        │    └── config/*.yaml (v4.2)
      │                        └── D7 (repair executor) ← LOCKED
      └── D7 (repair executor)
```

**정방향 실행 순서:** config → D1 → D7 → D2 → D3 → D4 → D5 → D6 → D8 → D9

---

## 🚦 Hard Rules (전 프롬프트 공통, 위반 시 시스템 실패)

```
HR1.  Q15 단독 사용 금지. Q15A, Q15B, Q15C, Q15D만 허용.
HR2.  QUARANTINE은 반드시 q_code (Q01~Q19) 동반.
HR3.  Q17 사용 금지 (v4.2에서 Q13으로 흡수됨, 기각된 코드).
HR4.  REPAIR는 정책 명시 + 유일 출력 알고리즘 필수. 정책 없으면 QUARANTINE.
HR5.  AUTO에 repair function 포함 금지.
HR6.  AIC-PKPD/ER/TTE/BIOMARKER → endpoint_data_type 필수 선언.
HR7.  endpoint_data_type=CELLULAR_KINETICS → cellular LLOQ derivation policy 필수.
HR8.  endpoint_data_type=IMMUNOGENICITY → positivity adjudication rule 필수, 없으면 Q19.
HR9.  endpoint_data_type=MATERNAL_INFANT_PK → dyad linkage key + delivery anchor 필수, 없으면 Q18.
HR10. analyte_role 미선언 + modality∈{ADC,BISPECIFIC,CELL_THERAPY,GENE_THERAPY} → Q16.
HR11. Coverage 95% = AUTO+REPAIR+QUARANTINE (review-inclusive). AUTO+REPAIR만으로 95% 주장 금지.
HR12. LLM은 exhaustive completeness 주장 금지. completeness는 generator/checker로만 주장.
HR13. Forced node 집합 = {N0(AIC+endpoint_type), N1(ID), N2(time), N3(dose), N4(obs), N5(BLQ), N8(policy_availability)} 중 ILP에서 빠지면 무조건 escalate.
      ※ N8 정의 (v5.1 NEW — Step 2 Phase 6에서 candidate_node_dictionary에 반드시 추가):
         N8 detection_rule: "proposed action_sequence에 필요한 모든 required_policy가 AIC에 선언되어 있으면 Y; 하나라도 부재하면 N"
         N8 forced=TRUE, cost_if_excluded=INFINITY (ILP 문제 설정 시 강제 포함)
         N8=N 시 terminal_state: QUARANTINE (q_code = 해당 policy 부재에 대응하는 Q-code)
HR14. ILP distinguishability 정의: 두 시나리오의 (terminal_state, action_sequence, q_code, required_policy) 중 하나라도 다르면 반드시 distinguish 가능해야 함.
```

---

## 🤖 LLM 라우팅 가이드 (각 프롬프트별 권장 모델)

> ⚠️ **[PATCH m-6]** 아래 표의 모델명은 예시입니다. 실행 시점 기준 최신 최고성능 모델로 업데이트하세요.
> 특정 버전명(예: Opus 4.7, Gemini Pro 3.1)은 이 문서 작성 시점 기준이며 실제 운영 시 존재하지 않을 수 있습니다.
> **역할 기준으로 선택하세요** — 모델명이 아니라 역할 특성이 중요합니다.

| 역할 태그 | 권장 역할 특성 | 실행 시점 예시 모델 (업데이트 필요) | 채팅창 분리 | 용도 |
|---|---|---|---|---|
| **R-LLM (PMX Grandmaster)** | 긴 컨텍스트 + 강한 추론 능력을 가진 고성능 모델 | Claude Opus 계열 최신 (또는 동급 추론 모델) | 같은 채팅창 유지 가능 | 추론, 초안 생성, 판정 |
| **A-LLM (Adversarial Reviewer)** | **R-LLM과 다른 계열·회사** 모델 필수 | Google Gemini 또는 OpenAI GPT 최신 추론 모델 | **반드시 새 채팅창** | 적대적 공격 |
| **C-LLM (Coding Agent)** | IDE 통합 코딩 에이전트 | Cursor IDE + Claude Sonnet 계열 최신 또는 Claude Code | Cursor 내부 | Python 구현, pytest |
| **LP-A** | 고성능 추론 모델 (R-LLM과 동일 계열 가능) | Claude Opus 계열 최신 | LP Panel 내부 | Grandmaster 판정 |
| **LP-B** | **LP-A와 다른 계열** 필수 | Google Gemini 또는 OpenAI GPT 최신 추론 모델 | **반드시 새 채팅창** | 적대적 공격 |
| **LP-C (Judge)** | 고성능 추론 모델, LP-A/B 결과 종합 | Claude Opus 계열 최신 (또는 동급) | LP-A,B 결과 첨부한 새 세션 권장 | 통합 판정 |
| **간단 문서 작업** | 빠르고 효율적인 모델 | Claude Sonnet 계열 최신 | 자유 | 선언문, 요약 |

> **A-LLM과 LP-B를 R-LLM과 다른 모델로 두는 이유:** 같은 모델 계열은 같은 학습 편향을 공유합니다. 적대적 검토에서 다른 계열을 투입해야 진짜 약점이 드러납니다. 이것은 특정 모델명의 문제가 아니라 **모델 계열 다양성**의 문제입니다.

---

## ⚡ 스노우볼 실행 원칙 (4가지만 기억)

```
1. 프롬프트 → LLM 입력 → 산출물 받기
2. 산출물 → 지정된 폴더에 정확한 파일명으로 저장
3. Python CHECK 스크립트 실행 → PASS면 다음 / FAIL이면 명시된 fallback으로 회귀
4. "다음 액션" 섹션을 따라 다음 프롬프트 진행
```

각 프롬프트 블록은 다음 5필드를 가집니다:

```
🔹 LLM 라우팅: [어떤 모델에게 입력하는가]
🔹 진입 조건: [이전 단계 무엇이 완료되어야 하는가]
🔹 첨부 파일: [LLM 채팅창에 무엇을 올려야 하는가]
🔹 산출물: [무엇을 어디에 저장하는가]
🔹 다음 액션: [다음에 무엇을 해야 하는가]
```

---

## 🔧 환경 세팅 (단 한 번만 수행)

### Step 1. Python 설치

1. https://www.python.org/downloads/ 접속
2. "Download Python 3.11.x" 클릭
3. **반드시** "Add Python to PATH" 체크 후 Install
4. 설치 확인:
   - **Windows**: 시작 메뉴 → "명령 프롬프트" 검색 → 열기
   - **Mac**: Spotlight(⌘+Space) → "터미널" → 열기
5. 터미널에서:
   ```
   python --version
   ```
   `Python 3.11.x` 같은 숫자가 나오면 성공.

### Step 2. 필요 패키지 설치

터미널에서 (한 줄로):
```
pip install pandas pyyaml scipy numpy ortools pytest pytest-cov openpyxl pyarrow hypothesis
```

> `hypothesis`는 v5.1에서 새로 추가. property-based testing으로 LLM 산출물의 엣지 케이스를 자동 탐색합니다.

### Step 3. Cursor IDE 설치

1. https://cursor.sh 접속
2. Download → 설치
3. 실행 후 Claude Sonnet 계열 최신 버전 또는 Claude Code 연결

### Step 4. 프로젝트 폴더 생성

**Windows:**
```
mkdir C:\Users\%USERNAME%\Documents\pmx_universe_v5_1
cd C:\Users\%USERNAME%\Documents\pmx_universe_v5_1
```

**Mac:**
```
mkdir ~/Documents/pmx_universe_v5_1
cd ~/Documents/pmx_universe_v5_1
```

이 폴더가 모든 작업의 기준 위치입니다. 앞으로 모든 경로는 이 폴더 기준 상대 경로로 표기됩니다.

### Step 5. CHECK 스크립트 저장 방법

각 Phase 끝에 `CHECK-N.py` 코드가 있습니다:

1. 코드 블록 전체 복사
2. 메모장(Windows) 또는 TextEdit(Mac) → 새 파일
3. 붙여넣기 → 인코딩 UTF-8로 저장
4. 파일명: `check_phase0.py` 형식
5. **저장 위치: `pmx_universe_v5_1` 폴더의 상위 폴더** (즉 `Documents` 폴더)
6. 실행:
   ```
   python check_phase0.py
   ```

---

## 📐 Phase 0: 프로젝트 헌장 & LP Panel 템플릿 고정 (P1~P6)

### 📌 이 단계 목적

이후 모든 프롬프트가 따라야 할 **시스템 프롬프트(Hard Rules + LP Panel 정의)**를 확정하고, 폴더 구조와 로깅 유틸리티를 만듭니다.

### 진입 조건
- [x] 환경 세팅 완료

---

### P1 — 프로젝트 헌장 + 역방향 DAG

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 실행 시점 기준 최신 Claude Opus 계열 또는 동급)
🔹 **진입 조건:** 환경 세팅 완료
🔹 **첨부 파일:** 없음 (이 문서의 "최종 목표" 섹션만 복사해서 LLM에 보여주면 됨)
🔹 **산출물:**
  - `reports/backward_artifact_dag.md`
  - `project_charter_v5_1.md`
  - `reports/success_criteria.md`
🔹 **다음 액션:** 산출물 3개를 위 경로에 저장 → P2 진행

**[프롬프트 본문 — R-LLM (고성능 추론 모델)에 붙여넣기]**

```
ROLE: PMX-to-NONMEM scenario universe project architect.

PROJECT GOAL (immutable):
실무적으로 현실성 있는 임의의 데이터셋 조합으로부터 NONMEM-ready dataset까지
발생 가능한 모든 시나리오 universe를 포착하고,
안전상 필수 forced gates(N0, N1, N2, N3, N4, N5, N8)를 고정한 상태에서
남은 optional nodes 중 강화된 distinguishability 제약을 만족하는
최소 추가 노드 집합을 ILP로 추출한다.

# [PATCH MINOR-N3] ILP claim 정확화:
# - N0,N1,N2,N3,N4,N5,N8 (7개)는 forced — ILP 이전에 결정됨
# - ILP가 실제 최적화하는 대상은 optional인 N6, N7
# - "최소 의사결정 노드"는 forced(7) + ILP-selected(0~2)의 합집합
# - coverage_claim_statement.md와 PROJECT_FINAL_COMPLETION_v5_1.md에도 이 표현 사용

TASK 1: 9개 final deliverables의 backward dependency DAG를 작성하라.
Final deliverables:
  D1. data/scenario_universe/scenario_universe_v1.0.csv
  D2. data/action_labels/scenario_action_table_locked.csv
  D3. data/decision_table/reduced_decision_table_v1.0.csv
  D4. data/ilp/pairwise_distinguishability_matrix.npz
  D5. data/ilp/final_minimal_node_set.csv
  D6. config/operational_decision_tree.yaml
  D7. scripts/repair_executor/repair_executor.py
  D8. reports/golden_validation_report.md
  D9. release/v1.0/coverage_claim_statement.md

각 deliverable에 대해:
  purpose, upstream_files, generating_step (P 번호 범위),
  validation_gate (CHECK-N), failure_fallback,
  immutable (true/false), human_approval_required (H1-H5 중 무엇)

TASK 2: project_charter_v5_1.md 작성. 다음 14개 Hard Rules 모두 포함:
HR1. Q15 단독 금지 (Q15A-D만)
HR2. QUARANTINE은 q_code (Q01-Q19) 필수
HR3. Q17 금지 (Q13으로 흡수됨)
HR4. REPAIR = 정책 + 유일 알고리즘
HR5. AUTO에 repair function 금지
HR6. AIC-PKPD/ER/TTE/BIOMARKER → endpoint_data_type 필수
HR7. CELLULAR_KINETICS → cellular LLOQ policy 필수
HR8. IMMUNOGENICITY → positivity rule 필수, 없으면 Q19
HR9. MATERNAL_INFANT_PK → dyad key + delivery anchor 필수, 없으면 Q18
HR10. analyte_role 미선언 + modality∈{ADC,BISPECIFIC,CELL_THERAPY,GENE_THERAPY} → Q16
HR11. Coverage 95% = review-inclusive (AUTO+REPAIR+QUARANTINE)
HR12. LLM은 exhaustive completeness 주장 금지
HR13. Forced node 빠지면 escalate
HR14. ILP distinguishability = (terminal, action_seq, q_code, policy) 중 하나라도 다르면 distinguish

TASK 3: success_criteria.md 작성. 다음 17개 완수 조건:
[ ] 9개 final deliverables 존재 (각각 SHA256 hash)
[ ] q_code 없는 QUARANTINE = 0
[ ] Q15 단독 사용 = 0
[ ] Q17 사용 = 0
[ ] REPAIR without executable function = 0
[ ] confirmed false AUTO = 0
[ ] confirmed false REPAIR = 0
[ ] universe freeze 서명 완료
[ ] action label lock 완료
[ ] forced node ⊆ minimal node set
[ ] ILP claim scope 문서화 (Tier A/B/C/D 중 하나)
[ ] 100-case validation plan 존재
[ ] CHECK-0 ~ CHECK-11 모두 PASS
[ ] H1-H5 서명 완료
[ ] LP Panel 7개 모두 escalation 해소 또는 H-checkpoint 라우팅
[ ] v4.2 patch C16-C24 모두 반영
[ ] final release approval (H5) 완료

OUTPUT FORMAT: 3개 파일을 각각 markdown 코드 블록으로 명확히 구분해서 출력.
파일별 시작에 "=== FILE: [path] ===" 헤더 사용.

CONSTRAINT: 출력 외 다른 자연어 설명 금지. 사람이 그대로 복사-저장할 수 있게 출력하라.
```

---

### P2 — LP Panel 표준 템플릿 정의 (전 시퀀스 기준 문서)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P1 완료
🔹 **첨부 파일:** P1의 `project_charter_v5_1.md`
🔹 **산출물:** `config/lp_panel_template.yaml`
🔹 **다음 액션:** YAML 파일을 위 경로에 저장 → P3 진행

> ⚠️ **[PATCH M-5]** 아래 CP 위치의 `after P??` 번호는 이 Step 1 작성 시점 기준 **추정치**입니다.
> 실제 배치는 Step 2 실행 후 확정됩니다. `config/lp_panel_template.yaml` 생성 후,
> Step 2 Phase 4~7 진행 과정에서 실제 P번호로 반드시 업데이트하세요.
> 실제 확정값 (Step 2 기준): CP2=P58~P60, CP3=P48~P51, CP4=P74~P76, CP5=P81~P83

```
ROLE: System architect for LLM-Panel adjudication framework.

CONTEXT: This project uses LP Panels at exactly 7 critical decision points:
  CP1. config_semantic_review        (after P15-P17, panel P18-P20)
  CP2. universe_attack_and_freeze    (after P57, panel P58-P60)   # ← Step2 실제 확정값
  CP3. repair_semantic_review        (after P47, panel P48-P50, CONDITIONAL)  # ← Step2 실제 확정값
  CP4. action_label_adjudication     (after P73, panel P74-P76)   # ← Step2 실제 확정값
  CP5. action_label_lock             (after P80, panel P81-P83)   # ← Step2 실제 확정값
  CP6. minimal_node_approval         (after P95, panel P96-P98)   # ← Step3 실제 확정값
  CP7. release_coverage_approval     (after P111, panel P112-P114) # ← Step3 실제 확정값

  # [PATCH M-5] 위 P번호는 Step2/3 실행 기준 실제 확정값입니다.
  # lp_panel_template.yaml 생성 시 위 번호를 그대로 사용하되,
  # 실제 실행 중 프롬프트 재번호가 발생하면 이 YAML을 업데이트하세요.

TASK: Define the canonical LP Panel template as machine-readable YAML.

REQUIRED STRUCTURE:

lp_panel_template:
  version: "v5.1"
  stages:
    - stage: LP_A
      role: "PMX Grandmaster (30 yrs PMX/NONMEM dataset wrangling)"
      llm_routing: "고성능 추론 모델 (실행 시점 기준 최신 Claude Opus 계열 또는 동급)"
      output_fields:
        - recommended_decision  # accept/reject/revise/split
        - rationale_pmx_evidence
        - confidence            # HIGH/MEDIUM/LOW
        - fatal_issues          # list, [] if none
        - residual_risk
        - must_escalate_to_human  # YES/NO
        - escalation_reason
      file_pattern: "reports/llm_proxy/{checkpoint_name}_grandmaster.md"

    - stage: LP_B
      role: "Adversarial reviewer specialized in false-AUTO/false-REPAIR detection"
      llm_routing: "반드시 LP_A와 다른 계열·회사 모델 (예: Google Gemini 또는 OpenAI GPT 최신)"
      session_constraint: "MUST be in a fresh chat with no LP_A context except the LP_A output file."
      attack_axes:
        - "REPAIR claim with absent policy"
        - "AUTO claim with hidden analytical judgment"
        - "QUARANTINE q_code mismatched with root cause"
        - "Q15 used standalone (must be Q15A/B/C/D)"
        - "Q17 used (forbidden, absorbed into Q13)"
        - "v4.2 endpoint_data_type omission (CELLULAR/IMMUNOGENICITY/MILK/MATERNAL_INFANT)"
        - "analyte_role missing for ADC/BISPECIFIC/CELL/GENE"
        - "PHI/legal/IRB risk overlooked"
        - "LP_A overconfidence"
      output_fields:
        - attack_list  # [{issue, severity:fatal/major/minor, evidence, correction}]
        - unresolved_fatal_count
        - escalate_to_human_override  # YES/NO
      file_pattern: "reports/llm_proxy/{checkpoint_name}_adversarial.md"

    - stage: LP_C
      role: "Judge integrating LP_A and LP_B outputs"
      llm_routing: "고성능 추론 모델 — LP_A, LP_B 결과 모두 첨부한 새 세션"
      hard_rules:
        - "confidence=LOW → escalate_to_human=YES (forced)"
        - "unresolved_fatal_count >= 1 → escalate_to_human=YES (forced)"
        - "Accept QUARANTINE with no q_code = forbidden"
        - "Accept REPAIR with no policy = forbidden"
        - "Accept Q15 standalone = forbidden"
        - "Accept Q17 = forbidden"
      output_fields:
        - final_decision  # accept/reject/revise/split/escalate_to_human
        - accepted_arguments_from_A
        - accepted_attacks_from_B
        - rejected_arguments_with_rationale
        - required_patch
        - affected_artifacts
        - required_rerun_steps  # P-number list
        - confidence
        - fatal_resolved  # YES/NO
        - escalate_to_human  # YES/NO
        - escalation_reason
      file_pattern_md: "reports/llm_proxy/{checkpoint_name}_judge.md"
      file_pattern_csv: "reports/llm_proxy/{checkpoint_name}_decision.csv"

  auto_proceed_condition:
    all_must_be_true:
      - "lp_c.confidence == HIGH"
      - "lp_c.fatal_resolved == YES"
      - "lp_c.escalate_to_human == NO"
      - "lp_b.unresolved_fatal_count == 0"

  escalation_routing:
    - condition: "PHI/legal/IRB content"
      route_to: "H1 if pre-pilot, H4 if post-validation, H5 if release"
    - condition: "false AUTO/REPAIR detected"
      route_to: "H4"
    - condition: "release-stage decision"
      route_to: "H5"
    - condition: "fingerprint factual ambiguity"
      route_to: "H2"
    - condition: "golden dataset reference uncertainty"
      route_to: "H3"

OUTPUT FORMAT: Single YAML file. Output only the YAML content, no prose.
File header comment: "# config/lp_panel_template.yaml — v5.1 LP Panel canonical definition"
```

---

### P3 — Repository 구조 + 폴더/파일 생성

🔹 **LLM 라우팅:** C-LLM (Cursor IDE + Claude Sonnet 계열 최신 또는 Claude Code)
🔹 **진입 조건:** P2 완료
🔹 **첨부 파일:** P1의 charter, P2의 lp_panel_template.yaml
🔹 **산출물:** 아래 폴더 트리 + 빈 파일들
🔹 **다음 액션:** Cursor에서 "Apply" 또는 "Accept" 버튼 클릭 필수 → P4 진행

```
ROLE: Coding agent. Generate scaffolding for pmx_universe_v5_1 repository.

CWD: pmx_universe_v5_1/

CREATE THE FOLLOWING STRUCTURE:

pmx_universe_v5_1/
├── config/
├── data/
│   ├── raw_examples/
│   ├── pilot_fingerprints/
│   ├── golden_datasets/
│   ├── scenario_universe/
│   ├── action_labels/
│   ├── decision_table/
│   └── ilp/
├── scripts/
│   ├── config_validation/
│   ├── scenario_generator/
│   ├── repair_executor/
│   ├── label_workbench/
│   ├── decision_table/
│   ├── ilp/
│   └── validation/
├── reports/
│   ├── adversarial_reviews/
│   ├── llm_proxy/
│   └── human_review/
├── coverage_validation/
├── change_control/
├── release/
│   └── v1.0/
└── tests/
    └── fixtures/

CREATE FILES:

1. README.md
   Header: "PMX-to-NONMEM Scenario Universe v5.1"
   Sections: Overview, Phases summary, How to run, Final deliverables list

2. CHANGELOG.md
   Initial entry: "## v0.1.0 (initialization) — repository scaffold created"

3. .gitignore
   Include: data/raw_examples/, *.pyc, __pycache__/, .pytest_cache/, .DS_Store

4. requirements.txt
   pandas>=2.0
   numpy>=1.24
   scipy>=1.11
   pyyaml>=6.0
   pydantic>=2.0
   ortools>=9.7
   pytest>=7.4
   pytest-cov>=4.1
   openpyxl>=3.1
   pyarrow>=14.0
   hypothesis>=6.90

5. pyproject.toml (with pytest config)

6. reports/execution_log.csv (header only)
   Columns: step_id, datetime_iso, prompt_number, llm_used, input_files,
            output_files, lp_panel_used, lp_confidence, lp_escalated,
            human_required, gate_status, fallback_step, notes

CONSTRAINT:
- All new files must end with newline
- All YAML/markdown files use UTF-8 encoding
- Use forward-slash paths even on Windows

OUTPUT: After creating files, output "OK: scaffold created" and a `tree` listing of all created paths.
Do not run any tests yet.
```

---

### P4 — 실행 로그 유틸리티 + LP Panel 자동 적용 러너

🔹 **LLM 라우팅:** C-LLM (Cursor IDE + Claude Sonnet 계열 최신)
🔹 **진입 조건:** P3 완료, Cursor에서 Apply 클릭 완료
🔹 **첨부 파일:** P2의 lp_panel_template.yaml
🔹 **산출물:**
  - `scripts/logging_utils.py`
  - `scripts/lp_panel_runner.py`
  - `tests/test_logging_utils.py`
  - `tests/test_lp_panel_runner.py`
🔹 **다음 액션:** Cursor에서 `pytest tests/test_logging_utils.py tests/test_lp_panel_runner.py -v` 실행 → 전체 PASS 확인 → P5

```
ROLE: Coding agent.

TASK 1: Implement scripts/logging_utils.py

REQUIREMENTS:
- Python 3.11, type-hinted, docstring-complete
- Functions:
    def append_execution_log(
        step_id: str,
        prompt_number: str,
        llm_used: str,
        input_files: list[str],
        output_files: list[str],
        lp_panel_used: bool = False,
        lp_confidence: str | None = None,
        lp_escalated: bool = False,
        human_required: bool = False,
        gate_status: str = "pending",
        fallback_step: str | None = None,
        notes: str = ""
    ) -> None
    """Append one row to reports/execution_log.csv."""

    def write_gate_result(
        step_id: str,
        gate_name: str,
        status: str,  # PASS/FAIL/CONDITIONAL/ESCALATE
        error_detail: str | None = None
    ) -> None

    def record_lp_decision(
        checkpoint_name: str,
        grandmaster_confidence: str,
        adversarial_fatal_count: int,
        judge_decision: str,
        escalated: bool,
        auto_applied: bool
    ) -> None

- Use atomic write (write to temp file, rename)
- Never raise on missing log file; create with header if absent

TASK 2: Implement scripts/lp_panel_runner.py

REQUIREMENTS:
- Reads config/lp_panel_template.yaml
- Reads reports/llm_proxy/{checkpoint_name}_decision.csv
- Function:
    def evaluate_auto_apply(checkpoint_name: str) -> dict
    Returns: {
      "auto_apply": bool,
      "reason": str,
      "required_patches": list[str],
      "escalation_target": str | None  # H1-H5
    }
- Apply hard rules from lp_panel_template.yaml
- If auto_apply==False, set escalation_target based on lp_panel_template.escalation_routing

TASK 3: tests/test_logging_utils.py
- Use pytest tmp_path fixture
- 5+ test cases: header creation, append, atomic write, missing dir handling, unicode

TASK 4: tests/test_lp_panel_runner.py
- 6+ test cases including auto_apply for HIGH/YES/NO scenario,
  escalation for LOW confidence, escalation for fatal_count>=1,
  forbidden Q15-standalone in patch, forbidden Q17 in patch

CONSTRAINT:
- Do not import any external libraries beyond stdlib + pandas + pyyaml
- All file paths use pathlib.Path
- Run pytest after writing; if any test fails, fix code, not tests (unless test is wrong)

OUTPUT:
- After all tests pass, output the pytest summary line
- List of created files
```

---

### P5 — v3.1 → v5.1 패치 로그 (참고용 문서)

🔹 **LLM 라우팅:** R-LLM (효율 모델 — 단순 문서 작업)
🔹 **진입 조건:** P4 완료
🔹 **첨부 파일:** 없음
🔹 **산출물:** `reports/v3_1_to_v5_1_patch_log.md`
🔹 **다음 액션:** 파일 저장 → P6 진행

```
ROLE: Documentation writer.

TASK: Generate reports/v3_1_to_v5_1_patch_log.md documenting all upgrades from
v3.1 prompt sequence to v5.1.

REQUIRED PATCH ENTRIES (each: patch_id, category, description, affected_prompts, risk_if_ignored):

P5-01  UNIVERSE   Frozen Universe upgrade v4.1 → v4.2
                  Adds: modality_class field, endpoint_data_type expansion (10 types),
                  analyte_role auxiliary field, A7 PRODUCT-LEVEL-COVARIATE state,
                  A3 delivery/postpartum anchor note, N1 maternal-infant dyad path,
                  Q16/Q18/Q19 codes, F24-F29 operational families,
                  F31-F34 (renumbered out-of-scope).
                  Risk if ignored: silent REPAIR for CELLULAR_KINETICS (CAR-T),
                  false INVALID for maternal-infant dyads,
                  wrong Q01 for immunogenicity adjudication absence.

P5-02  ILP        Distinguishability constraint strengthening
                  Old: scenario pair must differ in at least one selected node.
                  New: pair must differ if (terminal_state OR action_sequence OR q_code OR required_policy) differs.
                  Affected prompts: P88, P90.
                  Risk if ignored: minimal node set passes ILP but produces false REPAIR/AUTO.

P5-03  ILP        Forced node set explicit
                  Forced inclusion: N0, N1, N2, N3, N4, N5, N8(policy_availability).
                  Cost penalty for excluding any forced node = infinity (or very large).
                  Affected prompts: P56, P58, P90.

P5-04  LP_PANEL   13 panels → 7 panels (compression)
                  Kept: config_semantic, universe_attack+freeze, repair_semantic,
                  action_label_adjudication, action_label_lock, minimal_node_approval,
                  release_coverage.
                  Cut/merged: cost_function (single R-LLM only),
                  ep_split (merged into action_label_adjudication),
                  dangerous_merge (merged into minimal_node_approval),
                  tree_mismatch (Python CHECK only),
                  claim_scope (merged into release_coverage),
                  universe_freeze (merged into universe_attack),
                  new_case_intake (kept but lighter).

P5-05  HUMAN      H4 strengthening: AUTO/REPAIR sample blinded audit
                  Old: review false-classification flags from LP Panel.
                  New: audit minimum 10 random AUTO + 10 random REPAIR scenarios blinded
                  before veto, plus all LP-flagged items.
                  Affected prompts: P116-P118.

P5-06  PILOT      Edge-case seed pack required
                  Pilot fingerprints must include all 20 categories from the seed table
                  (routine + new-modality + special-population).
                  Affected prompts: P29, P31.

P5-07  COVERAGE   Wording restriction
                  Allowed: "review-inclusive coverage of scenario classes represented in v4.2 universe"
                  Forbidden: "all practical scenarios", "exhaustive", "all modalities".
                  Affected prompts: P122, P124.

P5-08  PYTHON     CHECK script enrichment
                  All CHECK scripts add v4.2-specific assertions:
                  Q16/Q18/Q19 presence,
                  F24-F29 operational classification,
                  F31-F34 renumbering,
                  modality_class + analyte_role + endpoint_data_type fields presence,
                  forced node ⊆ minimal_node_set.

P5-09  TEST       hypothesis library introduction
                  Property-based testing for repair_executor functions.
                  Generates random valid AIC + dataset combinations and asserts
                  invariants (no Q15 standalone, audit_log non-empty, etc.).

OUTPUT: Single markdown file with table-of-patches and per-patch detail sections.
```

---

### P6 — 테스트 프레임워크 + Makefile (또는 ps1 스크립트)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P5 완료
🔹 **첨부 파일:** 없음 (Cursor가 폴더 구조를 자체 파악)
🔹 **산출물:**
  - `tests/conftest.py`
  - `Makefile` (Mac/Linux) 또는 `run.ps1` (Windows)
🔹 **다음 액션:** `pytest tests/ -v` 실행 → CHECK-0으로

```
ROLE: Coding agent.

TASK 1: tests/conftest.py
- Common fixtures:
  - tmp_universe_dir: copy a minimal config/*.yaml subset to tmp_path for tests
  - sample_scenario_row: dict with A0..A10 minimum valid combo
  - q_code_set: set of all valid Q-codes (Q01..Q19, EXCLUDE Q17)
  - forced_node_set: {"N0","N1","N2","N3","N4","N5","N8"}
- Pytest configuration: -v -ra --strict-markers

TASK 2: Cross-platform runner

For Unix/Mac, Makefile:
  test:
      pytest tests/ -v
  validate:
      python scripts/config_validation/validate_config.py --config-dir config
  generate:
      python scripts/scenario_generator/generate_scenarios.py
  all: validate test

For Windows, run.ps1:
  param([string]$cmd = "test")
  switch ($cmd) {
    "test" { pytest tests/ -v }
    "validate" { python scripts/config_validation/validate_config.py --config-dir config }
    "generate" { python scripts/scenario_generator/generate_scenarios.py }
    "all" { pytest tests/ -v ; python scripts/config_validation/validate_config.py --config-dir config }
  }

OUTPUT: After creating, run `pytest tests/ -v` and report the summary.
Expected: existing 11 tests from P4 all pass. No new tests required here.
```

---

### 🐍 CHECK-0 (Phase 0 검증)

`check_phase0.py`로 저장 후 `Documents` 폴더에서 `python check_phase0.py` 실행.

```python
# check_phase0.py
# Phase 0 (P1-P6) 완료 검증
# 실행: python check_phase0.py

import os
import sys
from pathlib import Path

# pmx_universe_v5_1 폴더가 현재 위치 기준 어디에 있는지 자동 탐색
BASE_CANDIDATES = [
    Path("pmx_universe_v5_1"),
    Path("./pmx_universe_v5_1"),
    Path("../pmx_universe_v5_1"),
]
BASE = None
for cand in BASE_CANDIDATES:
    if cand.is_dir():
        BASE = cand
        break

if BASE is None:
    print("❌ pmx_universe_v5_1 폴더를 찾지 못했습니다.")
    print("   현재 위치:", Path.cwd())
    print("   pmx_universe_v5_1 폴더가 있는 상위 폴더에서 실행하세요.")
    sys.exit(1)

print(f"✅ BASE 디렉터리: {BASE.resolve()}")
print("=" * 55)
print("CHECK-0: Phase 0 (P1-P6) 완료 검증")
print("=" * 55)

REQUIRED_FOLDERS = [
    "config", "data/raw_examples", "data/pilot_fingerprints",
    "data/golden_datasets", "data/scenario_universe",
    "data/action_labels", "data/decision_table", "data/ilp",
    "scripts/config_validation", "scripts/scenario_generator",
    "scripts/repair_executor", "scripts/label_workbench",
    "scripts/decision_table", "scripts/ilp", "scripts/validation",
    "reports/adversarial_reviews", "reports/llm_proxy",
    "reports/human_review", "coverage_validation",
    "change_control", "release/v1.0", "tests/fixtures",
]

REQUIRED_FILES = [
    "README.md", "CHANGELOG.md", ".gitignore",
    "requirements.txt", "pyproject.toml",
    "project_charter_v5_1.md",
    "reports/backward_artifact_dag.md",
    "reports/success_criteria.md",
    "reports/v3_1_to_v5_1_patch_log.md",
    "reports/execution_log.csv",
    "config/lp_panel_template.yaml",
    "scripts/logging_utils.py",
    "scripts/lp_panel_runner.py",
    "tests/conftest.py",
    "tests/test_logging_utils.py",
    "tests/test_lp_panel_runner.py",
]

failures = []

print("\n[폴더 검사]")
for folder in REQUIRED_FOLDERS:
    p = BASE / folder
    if p.is_dir():
        print(f"  ✅ {folder}")
    else:
        print(f"  ❌ {folder}")
        failures.append(f"폴더 없음: {folder}")

print("\n[파일 검사]")
for f in REQUIRED_FILES:
    p = BASE / f
    if p.is_file():
        print(f"  ✅ {f}")
    else:
        print(f"  ❌ {f}")
        failures.append(f"파일 없음: {f}")

# Hard rules 14개 charter에 모두 반영됐는지 키워드 검사
charter = BASE / "project_charter_v5_1.md"
if charter.is_file():
    txt = charter.read_text(encoding="utf-8", errors="ignore")
    print("\n[Hard Rules 키워드 검사]")
    keywords = [
        "Q15A", "Q15B", "Q15C", "Q15D",  # HR1
        "Q19", "Q18", "Q16",              # HR8/9/10
        "endpoint_data_type",              # HR6
        "CELLULAR_KINETICS",               # HR7
        "MATERNAL_INFANT",                 # HR9
        "analyte_role",                    # HR10
        "review-inclusive",                # HR11
        "forced node",                     # HR13
        "distinguishability",              # HR14
    ]
    for kw in keywords:
        if kw.lower() in txt.lower():
            print(f"  ✅ {kw} 언급됨")
        else:
            print(f"  ❌ {kw} 누락")
            failures.append(f"Hard Rule 키워드 누락: {kw}")

# pytest 자동 실행
print("\n[pytest 실행 — 11개 이상 테스트 통과 기대]")
import subprocess
result = subprocess.run(
    ["python", "-m", "pytest", str(BASE / "tests"), "-v", "--tb=short", "-q"],
    capture_output=True, text=True
)
out = result.stdout + result.stderr
# 마지막 5줄만 보여주기
print("\n".join(out.splitlines()[-8:]))
if result.returncode == 0:
    print("  ✅ pytest PASS")
else:
    print("  ❌ pytest FAIL")
    failures.append("pytest 실패")

print("\n" + "=" * 55)
if not failures:
    print("🟢 GATE PASS: Phase 0 완료")
    print("→ 다음: Phase 1 (P7) 시작")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개 항목")
    for f in failures:
        print(f"  - {f}")
    print("\n→ 누락 항목에 해당하는 P 번호를 재실행하세요.")
    sys.exit(1)
```

**기대 출력 (PASS):**
```
🟢 GATE PASS: Phase 0 완료
→ 다음: Phase 1 (P7) 시작
```

---

## 🏗️ Phase 1: Frozen Universe v4.2 Machine-Readable YAML (P7~P22)

### 📌 이 단계 목적

PMX 데이터가 가질 수 있는 모든 상태의 사전(Dictionary)을 **v4.2 기준으로** YAML로 만듭니다. 이후 모든 단계는 이 YAML을 참조합니다.

### v4.2 핵심 변경 (v4.1 대비)

```
A0:  + modality_class (보조 필드, 11종)
     + endpoint_data_type 확장 (CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK)
A3:  + delivery/postpartum anchor 주석
A7:  + PRODUCT-LEVEL-COVARIATE state (CAR-T lot→subject)
A8:  + analyte_role 보조 필드 (12종)
N1:  + maternal-infant dyad linkage path
Q-codes: + Q16, Q18, Q19  (Q17 기각)
Family:  F24-F29 신규 operational, F31-F34는 구 F24-F27 재번호
Constraints: 8개 (기존 6개에 7,8번 추가)
```

### 진입 조건
- [x] CHECK-0 PASS

---

### P7 — Frozen Universe v4.2 구조화 요약

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** CHECK-0 PASS
🔹 **첨부 파일:** 없음 (이 v5.1 문서의 "v4.2 핵심 변경" 섹션 + 첨부 v4.2 문서 전체)
🔹 **산출물:** `reports/frozen_universe_v4_2_summary.md`
🔹 **다음 액션:** P8 진행

```
ROLE: PMX/NONMEM dataset wrangling grandmaster (30 yrs).

TASK: Produce reports/frozen_universe_v4_2_summary.md — a dense, structured summary
of Frozen Universe v4.2 organized by axes A0-A10, Q-codes, families, and nodes.

MUST INCLUDE:

A. AXES A0-A10
   For each axis: axis_id, axis_name, definition, list of states with terminal_hint
   v4.2 NEW STATES (must be present):
     A0: modality_class auxiliary field with 11 values
         (SMALL_MOLECULE, PEPTIDE, MAB, ADC, BISPECIFIC, CELL_THERAPY,
          GENE_THERAPY, MRNA, VACCINE, OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL, OTHER_CUSTOM)
     A0: endpoint_data_type expanded with 4 new values
         (CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK)
     A3: note on delivery/postpartum anchor
     A7: NEW state PRODUCT-LEVEL-COVARIATE (REPAIR if linkage policy, else Q13)
     A8: analyte_role auxiliary field with 12 values
         (PARENT, TOTAL_ANTIBODY, CONJUGATED_ADC, UNCONJUGATED_PAYLOAD,
          ACTIVE_METABOLITE, SOLUBLE_TARGET, DRUG_TARGET_COMPLEX, ADA, NAB,
          VECTOR_COPY, TRANSGENE_EXPRESSION, CAR_POSITIVE_CELL, OTHER_CUSTOM)

B. Q-CODES (Q01..Q19, Q17 EXCLUDED)
   For each: code, short_name, definition, detection_rule, linked_axis, linked_node
   v4.2 NEW: Q16, Q18, Q19 (full definitions per v4.2 doc)
   Q17: explicitly state "REJECTED — absorbed into Q13"

C. FAMILIES (F01-F29 operational, F31-F34 out-of-scope)
   NOTE: F30 is intentionally not assigned — reserved as numbering buffer
         between the operational range (F01-F29) and the out-of-scope range (F31-F34).
         Do NOT create an F30 entry.
   v4.2 NEW operational: F24 (ADC), F25 (Bispecific/T-cell engager),
                          F26 (CAR-T cellular kinetics), F27 (mRNA/vaccine),
                          F28 (Pregnancy PK), F29 (Lactation/dyad PK)
   v4.2 RENUMBERED: F31 = old F24 (raw FCS), F32 = old F25 (omics),
                     F33 = old F26 (unstructured), F34 = old F27 (INVALID)

D. DECISION NODES N0-N8 (master)  <!-- [PATCH] v5.1: N8 추가 — N0-N7은 v4.1 기준, N8은 v5.1 신규 -->
   Note: N0 must include endpoint_data_type check.
   Note: N1 must support MATERNAL_INFANT_PK dyad linkage path
         (mother and infant separate IDs allowed if dyad key exists,
          else INVALID; if dyad linkage policy absent → Q18).
   Note: N8 (v5.1 NEW) = policy_availability gate — checks ALL required_policies
         for proposed action_sequence are declared in AIC.
         Y = all policies present; N = any required policy absent → QUARANTINE.
         N8 is FORCED (cost_if_excluded=INFINITY in ILP). Placed after N1 in tree order.

E. AIC FIELDS (auxiliary structure for A0)
   modality_class (11 values listed),
   endpoint_data_type (10 values listed),
   plus existing fields (blq_handling_policy, time_policy, etc).

F. COVERAGE TARGETS
   capture_coverage ≥99%, review_inclusive ≥95%,
   operational ≥75%, auto_only ≥35%, unsupported+invalid ≤5%.

G. 8 SCOPE CONSTRAINTS (full text of all 8 from v4.2 spec)
   Especially constraints 7 (CELLULAR_KINETICS Poisson LLOQ) and
   8 (MATERNAL_INFANT_PK dyad key + delivery anchor).

H. v4.1 → v4.2 PATCHES C16-C24 (full list)

OUTPUT FORMAT:
- Markdown with H2 sections per category
- Tables where appropriate (especially Q-codes and Families)
- File header: "# Frozen Universe v4.2 — Structured Summary (v5.1 working basis)"

CONSTRAINT:
- Q15 standalone forbidden in any state list
- Q17 must appear only in "REJECTED" note
- All 4 v4.2-new endpoint_data_types must be present
- All 6 v4.2-new operational families F24-F29 must be present
```

---

### P8 — Axis Dictionary YAML (v4.2 반영)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P7 완료
🔹 **첨부 파일:** P7의 `reports/frozen_universe_v4_2_summary.md`
🔹 **산출물:** `config/axis_dictionary.yaml`
🔹 **다음 액션:** P9 진행

```
ROLE: PMX dataset architect.

INPUT: reports/frozen_universe_v4_2_summary.md (attached).

TASK: Produce config/axis_dictionary.yaml — fully populated for v4.2.

REQUIRED YAML STRUCTURE:

axis_dictionary:
  version: "v4.2"
  axes:
    - axis_id: A0
      axis_name: Analysis_Intent_Contract
      definition: "..."
      auxiliary_fields:
        - field: modality_class
          allowed_values: [SMALL_MOLECULE, PEPTIDE, MAB, ADC, BISPECIFIC,
                          CELL_THERAPY, GENE_THERAPY, MRNA, VACCINE,
                          OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL, OTHER_CUSTOM]
          required_when: "always (auxiliary, but recommended)"
          missing_q_code: null  # informational only
        - field: endpoint_data_type
          allowed_values: [PK_CONCENTRATION, EXPOSURE_METRIC, CONTINUOUS_PD,
                          CATEGORICAL_PD, COUNT_PD, TTE_EVENT,
                          CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK,
                          MATERNAL_INFANT_PK]
          required_when: "A0 in [AIC-PKPD, AIC-ER, AIC-TTE, AIC-BIOMARKER, AIC-CELL_THERAPY, AIC-IMMUNOGEN, AIC-LACTATION]"
          missing_q_code: Q11
      states:
        - state_code: AIC-MISSING
          definition: "..."
          terminal_hint: QUARANTINE
          q_code: Q11
        - state_code: AIC-PK
          ...
        # all states from v4.2 doc

    - axis_id: A1
      ...

    - axis_id: A3
      ...
      notes:
        - "v4.2 (C20): delivery/postpartum date as TIME anchor — treat as ELAPSED anchor"

    - axis_id: A7
      ...
      states:
        - state_code: PRODUCT-LEVEL-COVARIATE   # v4.2 NEW (C19)
          definition: "CAR-T/cell-therapy lot/batch/manufacturing attributes; lot→subject reverse-key join"
          terminal_hint: REPAIR
          q_code_if_linkage_missing: Q13
          q_code_if_attribute_absent_from_data_package: Q15A
        # ... existing states

    - axis_id: A8
      ...
      auxiliary_fields:
        - field: analyte_role
          allowed_values: [PARENT, TOTAL_ANTIBODY, CONJUGATED_ADC,
                          UNCONJUGATED_PAYLOAD, ACTIVE_METABOLITE,
                          SOLUBLE_TARGET, DRUG_TARGET_COMPLEX, ADA, NAB,
                          VECTOR_COPY, TRANSGENE_EXPRESSION,
                          CAR_POSITIVE_CELL, OTHER_CUSTOM]
          required_when: "A8 in [MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED] AND modality_class in [ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY]"
          missing_q_code: Q16

    - axis_id: A4
      ...  # existing v4.1 states (TITRATION-ADAPTIVE, LOADING-MAINTENANCE,
           # INFUSION-STOP-RESTART, ADDL-ACTUAL-CONFLICT) all retained

    - axis_id: A5
      ...  # BIOANALYTICAL-FINAL-FLAG-MISSING retained

    - axis_id: A9
      ...  # REANALYSIS-FINAL-MISSING retained

    - axis_id: A10
      ...  # SEMI-STRUCTURED + source_parser_subtype retained

VALIDATION CONSTRAINTS:
- A0 must have auxiliary_fields (modality_class, endpoint_data_type)
- A8 must have auxiliary_fields (analyte_role)
- A7 must have PRODUCT-LEVEL-COVARIATE state
- No state_code = "Q15" (use Q15A/B/C/D in q_code field instead)
- No q_code = Q17 anywhere

OUTPUT: Single YAML file, valid YAML 1.2, UTF-8.
File header comment: "# config/axis_dictionary.yaml — Frozen Universe v4.2"
```

---

### P9 — Terminal State Taxonomy YAML

🔹 **LLM 라우팅:** R-LLM (효율 모델 — Claude Sonnet 계열 최신)
🔹 **진입 조건:** P8 완료
🔹 **첨부 파일:** P8의 axis_dictionary.yaml
🔹 **산출물:** `config/terminal_state_taxonomy.yaml`
🔹 **다음 액션:** P10 진행

```
ROLE: System architect.

INPUT: config/axis_dictionary.yaml (attached).

TASK: Produce config/terminal_state_taxonomy.yaml — formal definitions of the 5 terminal states.

STRUCTURE:

terminal_state_taxonomy:
  version: "v5.1"
  states:
    - state: AUTO
      definition: "..."
      entry_condition: "..."
      allowed_next_action: "..."
      required_output: "NONMEM-ready dataset + audit_log"
      required_audit_log_fields: [policy_used, function_sequence, row_counts, timestamps]
      failure_condition: "Contains repair function OR has hidden policy dependency"
      examples_count: 2

    - state: REPAIR
      ...
      failure_condition: "No executable function in repair_rule_dictionary OR no explicit policy"

    - state: QUARANTINE
      entry_condition: "q_code in [Q01..Q16, Q18, Q19] (Q15 must be Q15A/B/C/D, Q17 forbidden)"
      ...
      failure_condition: "q_code missing OR q_code = Q15 standalone OR q_code = Q17"

    - state: UNSUPPORTED
      ...

    - state: INVALID
      ...

OUTPUT: YAML only. Header comment with v5.1 timestamp.
```

---

### P10 — Q-code Dictionary v4.2 (Q01-Q19, Q17 제외)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P9 완료
🔹 **첨부 파일:** P7 summary, P8 axis_dictionary.yaml
🔹 **산출물:** `config/quarantine_reason_codes.yaml`
🔹 **다음 액션:** P11 진행

```
ROLE: PMX Grandmaster.

INPUT: reports/frozen_universe_v4_2_summary.md, config/axis_dictionary.yaml.

TASK: Produce config/quarantine_reason_codes.yaml with EXACTLY 21 codes.

CODES:
  Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q12, Q13, Q14,
  Q15A, Q15B, Q15C, Q15D,
  Q16, Q18, Q19
  (Q15 STANDALONE FORBIDDEN, Q17 FORBIDDEN)

EACH CODE STRUCTURE:
- code: Q16
  short_name: ANALYTE_ROLE_POLICY_MISSING
  definition: "Modality-specific analyte role policy missing for ADC/CAR-T/bispecific/gene-therapy multi-analyte data"
  detection_rule: "A8 in [MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED] AND modality_class in [ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY] AND analyte_role NOT declared"
  linked_axis: [A8]
  linked_node: [N4]
  required_human_decision: "Bioanalyst declares analyte role per CMT"
  required_input_to_clear: "analyte_role declaration in AIC for each measured analyte"
  example: "ADC trial measures total Ab, conjugated ADC, free payload — analyte_role not declared per CMT"
  post_clear_action: "A8 → MULTI-CMT-DEFINED with analyte_role tags, recheck CMT assignment"
  difference_from_q09: "Q09 = no CMT number; Q16 = CMT exists but analyte role classification missing"

REQUIRED FOR v4.2:
- Q16 (analyte role missing) — full structure
- Q18 (maternal-infant dyad linkage ambiguous) — full structure
- Q19 (immunogenicity/DV adjudication missing) — full structure

# ══════════════════════════════════════════════════════════════
# [PATCH m-4 — CRITICAL, v5.1] Q15 sub-code 올바른 정의
# 이전 버전("컬럼/필드/표/파일 부재")으로 단순화된 설명은
# 실무 의미와 다릅니다. 아래 정의를 정확하게 사용하세요.
# ══════════════════════════════════════════════════════════════
REQUIRED Q15 SUB-CODES — MUST USE EXACTLY THESE DEFINITIONS:

- code: Q15A
  short_name: DATA_PACKAGE_INCOMPLETE_UPSTREAM_ADJUDICATION
  definition: "Data package incomplete — upstream adjudication decision 미제출.
               Bioanalytical/clinical final adjudication (e.g., sample acceptance/rejection,
               deviation resolution) has not yet been delivered to the wrangler.
               The raw data exist but the authoritative decision about which values to use is absent."
  example: "Bioanalytical report shows 2 reanalysis values for same sample; final adjudicated value
            not yet designated by bioanalytical scientist. Wrangler cannot pick without that decision."
  what_it_is_NOT: "NOT 'a column or file is missing from the data package'.
                   It is specifically an upstream decision that has not been communicated."

- code: Q15B
  short_name: LEGACY_FLAG_UNDOCUMENTED
  definition: "Legacy flag undocumented — 레거시 데이터의 플래그/필드 정의가 없어 해석 불가.
               A flag, code, or field present in the historical dataset has no documented
               meaning in any data specification, CRF, or data management document.
               The wrangler cannot determine the correct action without original documentation."
  example: "Legacy NONMEM-like dataset has column 'EVID2' with values 0/1/2/9;
            meaning of value 9 is not in any available dictionary or SAS format library."
  what_it_is_NOT: "NOT 'file not found'. The data is present but the interpretation key is absent."

- code: Q15C
  short_name: REALWORLD_ADHERENCE_HISTORY_UNRESOLVED
  definition: "Real-world adherence/administration history unresolved — RWD/TDM 투여 기록의
               실제 복용 이력 불명확. In real-world/TDM datasets, the patient-reported or
               pharmacy-dispensed dose history cannot be reliably reconciled with the
               observed concentration-time profile without additional source data or SAP guidance."
  example: "TDM dataset has pharmacy dispensing records (doses filled) but no information
            on actual patient adherence. Concentrations suggest partial adherence; without
            an SAP-level adherence imputation policy, EVID=1 rows cannot be reliably placed."
  what_it_is_NOT: "NOT 'dose data is missing'. The records exist but reconciliation is impossible."

- code: Q15D
  short_name: ASSAY_REANALYSIS_FINAL_ADJUDICATION_MISSING
  definition: "Assay reanalysis/final-result adjudication missing — 재분석 결과 중
               최종 선택 기준 미제시. Multiple assay results exist for the same sample
               (due to reanalysis, repeat analysis, or inter-laboratory comparison)
               and the rule for selecting the final DV has not been provided."
  example: "PC dataset contains both original and reanalysis DV values; the SOP or
            bioanalytical report does not specify whether to use original, reanalysis,
            or a specific priority rule. Cannot determine final DV without that rule."
  what_it_is_NOT: "NOT 'bioanalytical final flag column is missing' (that is Q15A).
                   Q15D = rule for choosing among multiple available values is absent."
# ══════════════════════════════════════════════════════════════
# END [PATCH m-4]
# ══════════════════════════════════════════════════════════════

ALSO INCLUDE:
- Q17: { code: "Q17", status: "REJECTED", reason: "Absorbed into Q13 (external covariate linkage). Use Q13 with log message 'product-level, lot-to-subject mapping absent'." }

VALIDATION:
- 21 entries (Q01..Q14 + Q15A..D + Q16,18,19) + Q17 as REJECTED entry
- Every entry has detection_rule using only valid axis state names
- Q15 standalone NOT a valid code
- Q15A, Q15B, Q15C, Q15D definitions must match [PATCH m-4] semantics exactly

OUTPUT: YAML only.
```

---

### P11 — Dependency Constraints YAML (v4.2 — 35개 이상)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P10 완료
🔹 **첨부 파일:** P8 axis_dictionary.yaml, P10 quarantine_reason_codes.yaml
🔹 **산출물:** `config/dependency_constraints.yaml`
🔹 **다음 액션:** P12 진행

```
ROLE: PMX Grandmaster.

INPUT: config/axis_dictionary.yaml, config/quarantine_reason_codes.yaml.

TASK: Produce config/dependency_constraints.yaml with MINIMUM 35 rules.

EACH RULE STRUCTURE:
- rule_id: DC001
  priority: 1
  if_conditions:
    - { axis: A0, state: AIC-MISSING }
  then_terminal: QUARANTINE
  then_q_code: Q11
  then_action_hint: "flag_quarantine(q_code=Q11)"
  rationale: "..."

REQUIRED RULES (must include all of the following):

[A0 / AIC]
DC001 A0=AIC-MISSING → Q11
DC002 A0 in {AIC-PKPD,AIC-ER,AIC-TTE,AIC-BIOMARKER} AND endpoint_data_type missing → Q11

[A0 / v4.2 endpoint_data_type new]
DC003 endpoint_data_type=CELLULAR_KINETICS AND cellular_LLOQ_derivation_policy absent → Q01 (cellular subtype)
DC004 endpoint_data_type=IMMUNOGENICITY AND positivity_adjudication_rule absent → Q19
DC005 endpoint_data_type=MATERNAL_INFANT_PK AND dyad_linkage_key absent → Q18
DC006 endpoint_data_type=MATERNAL_INFANT_PK AND delivery_anchor absent → Q12
DC007 endpoint_data_type=MILK_PK AND matrix_specific_LLOQ absent → Q01

[A3]
DC008 A3=AMBIGUOUS → Q02
DC009 A3=UNRECOVERABLE → INVALID
DC010 A3 has delivery_anchor_undefined for pregnancy/lactation studies → Q02

[A4]
DC011 A4=ADDL-ACTUAL-CONFLICT AND addl_actual_conflict_policy absent → Q14
DC012 A4=MISSING-NO-POLICY → Q08
DC013 A4=UNRECOVERABLE → INVALID
DC014 A4=TITRATION-ADAPTIVE AND dose_adaptation_policy absent → Q08
DC015 A4=LOADING-MAINTENANCE AND transition_point_undefined → Q08
DC016 A4=INFUSION-STOP-RESTART AND infusion_reconstruction_policy absent → Q04

[A5]
# [PATCH m-4 downstream — v5.1]
# Q15 sub-code 재정의 이후 A5 매핑 수정:
# DC017: BIOANALYTICAL-FINAL-FLAG-MISSING → Q15A (수정)
#   이유: "bioanalytical 최종 판정 플래그 부재"는 upstream adjudication decision이
#         wrangler에게 도달하지 않은 상태이므로 Q15A (data package incomplete)가 정확함.
#         Q15D는 "복수 결과 중 선택 기준 부재"로, 재분석(reanalysis) 케이스에 한정됨.
# DC028: REANALYSIS-FINAL-MISSING → Q15D (유지)
#   이유: "재분석 결과 중 최종 선택 기준 미제시"가 Q15D 정의와 정확히 일치함.
DC017 A5=BIOANALYTICAL-FINAL-FLAG-MISSING → Q15A  # [PATCH m-4] 수정: Q15D→Q15A
DC018 A5=BLQ-NO-POLICY → Q01
DC019 A5=LLOQ-MISSING → Q01
DC020 A5=ABSENT → INVALID

[A7 / v4.2]
DC021 A7=PRODUCT-LEVEL-COVARIATE AND lot_subject_linkage_key absent → Q13 (with note "product-level, lot-to-subject mapping absent")
DC022 A7=PRODUCT-LEVEL-COVARIATE AND product_attribute_absent_from_data_package → Q15A
DC023 A7=KEY-MISSING → Q13
DC024 A7=POLICY-MISSING → Q07

[A8 / v4.2]
DC025 A8=CMT-POLICY-MISSING → Q09
DC026 A8=DDI-VICTIM-PERPETRATOR AND dual_cmt_policy absent → Q09
DC027 A8 in {MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED} AND modality_class in {ADC,BISPECIFIC,CELL_THERAPY,GENE_THERAPY} AND analyte_role missing → Q16

[A9]
DC028 A9=REANALYSIS-FINAL-MISSING → Q15D
DC029 A9=IRRECONCILABLE → INVALID
DC030 A9=PROTOCOL-DEVIATION-NO-POLICY → Q06

[A10]
DC031 A10=NON-TABULAR → UNSUPPORTED
DC032 A10=CORRUPTED → INVALID
DC033 A10=SEMI-STRUCTURED AND source_parser_subtype=unknown → Q15A

[META]
DC034 Q-code-less QUARANTINE forbidden (validation rule)
DC035 Q15 standalone forbidden (validation rule)
DC036 Q17 forbidden (validation rule, with note "absorbed into Q13")

VALIDATION:
- ≥36 rules total
- All q_codes referenced exist in quarantine_reason_codes.yaml
- All axis/state references exist in axis_dictionary.yaml
- No rule produces Q15 alone
- No rule produces Q17

OUTPUT: YAML only.
```

---

### P12 — Family Assignment Rules v4.2 (F01~F29 op + F31~F34 out)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P11 완료
🔹 **첨부 파일:** P7 summary, P8 axis_dictionary.yaml
🔹 **산출물:** `config/family_assignment_rules.yaml`
🔹 **다음 액션:** P13 진행

```
ROLE: PMX Grandmaster.

INPUT: reports/frozen_universe_v4_2_summary.md, config/axis_dictionary.yaml.

TASK: Produce config/family_assignment_rules.yaml — F01..F29 (operational) + F31..F34 (out-of-scope).
# NOTE: F30 is intentionally not assigned (reserved as numbering buffer between ranges).
# Do NOT create an F30 entry. The gap is structural, not an error.

EACH FAMILY:
- family_id: F26
  family_name: CAR_T_Cellular_Kinetics
  operational_scope: true
  expected_terminal: REPAIR
  frequency_hint: LOW_TO_MEDIUM
  v4_2_new: true
  matching_axis_patterns:
    A0:
      modality_class: [CELL_THERAPY]
      endpoint_data_type: [CELLULAR_KINETICS]
    A8:
      analyte_role: [VECTOR_COPY, CAR_POSITIVE_CELL, TRANSGENE_EXPRESSION]
    A7:
      states_allowed: [PRODUCT-LEVEL-COVARIATE, BASELINE-CLEAN, TIME-VARYING]
  required_policies:
    - cellular_LLOQ_derivation_policy
    - lot_subject_linkage_key
  exclusion_conditions:
    - "A8=CMT-POLICY-MISSING"
    - "endpoint_data_type=CELLULAR_KINETICS AND cellular_LLOQ_derivation_policy absent"
  priority: 4
  examples: [...]
  notes: "v4.2 (C23): replaces silent CONTINUOUS_PD path that caused false REPAIR in v4.1"

REQUIRED FAMILIES (must all be present):

OPERATIONAL (F01-F29):
F01 Standard SDTM/ADaM popPK
F02 Multi-study pooled popPK
F03 EDC multi-table clinical PK
F04 CRO PK concentration + dosing
F05 Flat Excel/CSV PMX
F06 Legacy NONMEM-like
F07 SAD/MAD dose-escalation
F08 Crossover/BA-BE
F09 DDI victim-only          (v4.1 split kept)
F10 Food-effect
F11 Special population (renal/hepatic)
F12 Pediatric PK
F13 PK/PD continuous biomarker
F14 Exposure-response
F15 TTE/count/categorical
F16 External covariate linkage
F17 FACS-derived endpoint
F18 qPCR-derived endpoint
F19 Simple preclinical PK
F20 TDM/RWD
F21 Urine/interval collection PK
F22 DDI victim+perpetrator   (v4.1 split kept)
F23 Combination/concomitant therapy

v4.2 NEW operational:
F24 ADC PK/PKPD
F25 Bispecific / T-cell engager PKPD
F26 CAR-T / cell-therapy cellular kinetics
F27 mRNA / vaccine-like
F28 Pregnancy PK
F29 Lactation / mother-infant PK

OUT-OF-SCOPE (F31-F34, captured but operational_scope=false):
F31 raw FCS/qPCR without derivation (UNSUPPORTED)  [renumbered from old F24]
F32 omics/imaging/waveform raw (UNSUPPORTED)        [renumbered from old F25]
F33 unstructured notes only (UNSUPPORTED)           [renumbered from old F26]
F34 unrecoverable core missing (INVALID)             [renumbered from old F27]

VALIDATION:
- Multiple-match resolution: lower priority wins
- F26 must require cellular_LLOQ_derivation_policy
- F29 must require dyad_linkage_key + delivery_anchor
- F24 must require analyte_role (Q16 prevention)
- Old F24-F27 (operational/UNSUPPORTED in v4.1) must be renumbered to F31-F34
- F30 must NOT exist in the YAML (intentionally reserved, not assigned)

OUTPUT: YAML only.
```

---

### P13 — Action Sequence Standard v4.2 (controlled vocabulary)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P12 완료
🔹 **첨부 파일:** P8 axis_dictionary.yaml, P11 dependency_constraints.yaml
🔹 **산출물:**
  - `config/action_sequence_standard.yaml`
  - `config/action_function_library.yaml`
🔹 **다음 액션:** P14 진행

```
ROLE: PMX Grandmaster + NONMEM dataset engineer.

INPUT: config/axis_dictionary.yaml, config/dependency_constraints.yaml.

TASK: Produce 2 YAMLs.

FILE 1: config/action_sequence_standard.yaml

DEFINITION: action_sequence = ordered list of (function_name, parameter_policy) tuples.
Two scenarios are EP-equivalent iff function_name order, parameter_policy, terminal_state all match.

CONTROLLED VOCABULARY (function names, alphabetical):

# Parsing/preparation
parse_source
standardize_column_names
convert_units

# ID + linking
map_subject_id
attach_dyad_linkage         # v4.2 NEW (mother-infant)

# Time
derive_time_actual
derive_time_nominal
derive_time_elapsed
derive_time_interval
derive_time_postpartum_anchor   # v4.2 NEW

# Dose reconstruction
reconstruct_dose_weight
reconstruct_dose_bsa
reconstruct_dose_titration
reconstruct_loading_maintenance
reconstruct_infusion_stop_restart
expand_addl_ii
resolve_addl_actual_conflict

# Observation
canonicalize_blq                          # concentration BLQ
canonicalize_cellular_blq                 # v4.2 NEW (Poisson-LLOQ)
adjudicate_immunogenicity_positivity      # v4.2 NEW
resolve_reanalysis_final
assign_milk_matrix_lloq                   # v4.2 NEW

# Event
assign_evid

# CMT
assign_cmt_single
assign_cmt_multi
assign_cmt_ddi_victim_only
assign_cmt_ddi_victim_perpetrator
assign_cmt_with_analyte_role              # v4.2 NEW

# Covariate
attach_covariate_baseline
attach_covariate_time_varying
attach_covariate_external
attach_covariate_product_level            # v4.2 NEW (lot→subject)

# Cleanup
remove_exact_duplicates
sort_records

# Terminal flags
flag_quarantine
flag_invalid
flag_unsupported
export_nonmem_ready

TERMINAL PATTERNS:
- AUTO: parse_source ... assign_* ... export_nonmem_ready (no repair_*)
- REPAIR: AUTO pattern + ≥1 repair function (any function NOT in {parse_source, map_subject_id, assign_evid, assign_cmt_single, sort_records, export_nonmem_ready})
- QUARANTINE: [..., flag_quarantine(q_code=Q0XX)]   # NO export
- INVALID: [flag_invalid(reason=...)]
- UNSUPPORTED: [flag_unsupported(reason=...)]

FILE 2: config/action_function_library.yaml

For EACH function listed above:
- function_name
- required_parameters: [list]
- required_policy: [list of policy keys from AIC, or null]
- output_columns_added: [list]
- audit_log_fields: [list]
- failure_mode_q_code: Q-code if policy missing
- v4_2_new: true/false

OUTPUT: 2 YAML files. File header comments mark v5.1 + v4.2 basis.
```

---

### P14 — AIC Template v4.2

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P13 완료
🔹 **첨부 파일:** P8 axis_dictionary.yaml, P13 action_sequence_standard.yaml
🔹 **산출물:** `config/analysis_intent_contract_template.yaml`
🔹 **다음 액션:** P15 진행

```
ROLE: PMX Grandmaster.

INPUT: config/axis_dictionary.yaml (auxiliary_fields under A0/A8), config/action_sequence_standard.yaml.

TASK: Produce config/analysis_intent_contract_template.yaml — the AIC contract that every PMX project must satisfy before being routed through the decision tree.

REQUIRED FIELDS (each with: field_name, allowed_values, required_when, missing_q_code, example):

CORE:
- model_family
- analysis_objective
- modality_class                   # v4.2 [11 values]
- endpoint_data_type               # v4.2 [10 values, required when AIC type implies]
- analyte_role                     # v4.2 [12 values, conditional]

POLICIES:
- blq_handling_policy: [M1, M3, M4, exclude, project_specific]
- cellular_LLOQ_derivation_policy  # v4.2 [Poisson-derived, project_specific]
- positivity_adjudication_rule     # v4.2 (for IMMUNOGENICITY)
- time_policy: [actual, nominal, actual_preferred, nominal_preferred, elapsed, interval]
- elapsed_anchor_policy: [first_dose, last_dose, delivery_date, postpartum_day]   # v4.2
- occasion_policy: [dose, period, cycle, visit, model_defined, not_applicable]
- dose_reconstruction_policy: [actual, planned_fallback, addl_ii, weight_based, bsa_based, titration_adaptive, loading_maintenance]
- addl_actual_conflict_policy: [actual_priority, addl_priority, merge_policy_doc, not_applicable]
- infusion_reconstruction_policy: [rate_from_records, stop_restart_from_events, not_applicable]
- covariate_policy
- cmt_analyte_policy: [single, multi_with_rules, ddi_victim_only, ddi_dual_cmt, multi_analyte_role_tagged]
- external_linkage_policy
- product_level_covariate_linkage_policy   # v4.2
- bioanalytical_final_selection_policy
- reanalysis_final_selection_policy
- dyad_linkage_policy              # v4.2 (for MATERNAL_INFANT_PK)
- delivery_anchor_policy           # v4.2 (for pregnancy/lactation)
- milk_matrix_lloq_policy          # v4.2 (for MILK_PK)

OUTPUT REQUIREMENTS:
- nonmem_required_columns
- exclusion_policy
- audit_trail_requirement: [full, minimal]

VALIDATION:
- All 4 v4.2-new endpoint_data_types have associated required policy fields
- Q11 mapped to: model_family/analysis_objective/endpoint_data_type missing
- Q19 mapped to: positivity_adjudication_rule missing for IMMUNOGENICITY
- Q18 mapped to: dyad_linkage_policy missing for MATERNAL_INFANT_PK
- Q16 mapped to: analyte_role missing for required modalities

OUTPUT: YAML only.
```

---

### P15 — Repair/Quarantine Boundary Cases v4.2 (60개)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P14 완료
🔹 **첨부 파일:** P10 q-codes, P11 constraints, P13 action_sequence, P14 AIC
🔹 **산출물:** `reports/repair_quarantine_boundary_cases_v4_2.csv`
🔹 **다음 액션:** P16 진행

```
ROLE: PMX Grandmaster.

INPUT: All Phase 1 YAMLs.

TASK: Produce reports/repair_quarantine_boundary_cases_v4_2.csv with 60 cases.

DISTRIBUTION:
- REPAIR cases: 30
- QUARANTINE cases: 22
- AUTO cases: 4
- UNSUPPORTED cases: 2
- INVALID cases: 2

CSV COLUMNS:
case_id, scenario_description, A0_state, modality_class, endpoint_data_type,
A1_state, A2_state, A3_state, A4_state, A5_state, A6_state, A7_state,
A8_state, analyte_role, A9_state, A10_state,
required_policies, terminal_state, q_code, action_sequence_pattern, family_id_hint

REQUIRED v4.2 CASES (must all be present):

[REPAIR — v4.2 NEW]
- CAR-T cellular kinetics with cellular_LLOQ policy (F26)
- ADC measuring total Ab + conjugated + payload with analyte_role tagged (F24)
- Bispecific PK + soluble target with multi-CMT policy (F25)
- mRNA prime/boost (LOADING-MAINTENANCE) with positivity rule (F27)
- Pregnancy PK with delivery anchor declared (F28)
- Lactation dyad with linkage key + delivery anchor (F29)
- Milk PK with matrix-specific LLOQ (F29)
- Product-level covariate (lot transduction efficiency) with linkage key (PRODUCT-LEVEL-COVARIATE)
- Postpartum-anchored ELAPSED time

[QUARANTINE — v4.2 NEW]
- CELLULAR_KINETICS without cellular_LLOQ_policy → Q01 (cellular subtype)
- IMMUNOGENICITY without positivity_adjudication_rule → Q19
- MATERNAL_INFANT_PK without dyad_linkage_key → Q18
- MATERNAL_INFANT_PK without delivery_anchor → Q12
- ADC with multi-analyte but analyte_role missing → Q16
- CAR-T product-level covariate, lot-subject mapping absent → Q13 (with note)
- CAR-T product attribute absent from data package → Q15A
- MILK_PK without matrix-specific LLOQ → Q01

[Q15 standalone: 0 cases — all must be Q15A/B/C/D]
[Q17: 0 cases]

OUTPUT: CSV file.
```

---

### P16 — Config Schema Validator (Python 검증 코드)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P15 완료
🔹 **첨부 파일:** Phase 1 모든 config/*.yaml
🔹 **산출물:**
  - `scripts/config_validation/validate_config.py`
  - `tests/test_validate_config.py`
🔹 **다음 액션:** Cursor에서 `pytest tests/test_validate_config.py -v` PASS 확인 → P17

```
ROLE: Coding agent.

INPUT: config/{axis_dictionary, terminal_state_taxonomy, quarantine_reason_codes,
              dependency_constraints, family_assignment_rules,
              action_sequence_standard, action_function_library,
              analysis_intent_contract_template}.yaml

TASK: Implement scripts/config_validation/validate_config.py with EXACTLY 22 validators.

V01  axis_id uniqueness in axis_dictionary
V02  state_code uniqueness within each axis
V03  dependency_constraints axis references exist in axis_dictionary
V04  dependency_constraints state references exist in respective axis
V05  q_code references exist in quarantine_reason_codes
V06  Q15 standalone usage forbidden (anywhere)
V07  Q17 usage forbidden (except as REJECTED entry)
V08  family_assignment axis/state references valid
V09  terminal_state references match terminal_state_taxonomy
V10  AIC-{PKPD,ER,TTE,BIOMARKER} → endpoint_data_type rule exists in dependency_constraints
V11  A4=ADDL-ACTUAL-CONFLICT → Q14 rule exists
V12  A5=BIOANALYTICAL-FINAL-FLAG-MISSING → Q15D rule exists
V13  A9=REANALYSIS-FINAL-MISSING → Q15D rule exists
V14  A8 has DDI-VICTIM-ONLY and DDI-VICTIM-PERPETRATOR states
V15  F09 (DDI victim-only) and F22 (DDI victim+perpetrator) both exist as separate families
V16  Q01..Q19 (excluding Q17) exist (count = 21)
# v5.1 NEW (v4.2 patches):
V17  A0 auxiliary_fields contains modality_class with 11+ values
V18  A0 auxiliary_fields contains endpoint_data_type with 10 values including CELLULAR_KINETICS, IMMUNOGENICITY, MILK_PK, MATERNAL_INFANT_PK
V19  A8 auxiliary_fields contains analyte_role with 12+ values
V20  A7 contains PRODUCT-LEVEL-COVARIATE state
V21  Q16, Q18, Q19 all exist; Q17 marked REJECTED
V22  F24-F29 are operational; F31-F34 are out-of-scope (renumbered)

ERROR FORMAT (one line per error):
ERROR | validator_id | file | detail

CLI:
python scripts/config_validation/validate_config.py \
  --config-dir config \
  --out reports/config_schema_validation_report.md

OUTPUT FILE FORMAT (Markdown):
# Config Schema Validation Report
generated_at: ISO timestamp
total_validators: 22
total_errors: N
error_count_by_validator:
  V01: 0
  ...
errors:
  - { validator: V06, file: ..., detail: "..." }

TESTS (tests/test_validate_config.py):
- 1 fixture creating valid config dir → 0 errors expected
- 1 fixture with Q15 standalone → V06 fail expected
- 1 fixture with Q17 → V07 fail expected
- 1 fixture missing modality_class → V17 fail expected
- 1 fixture missing CELLULAR_KINETICS → V18 fail expected
- 1 fixture missing analyte_role → V19 fail expected
- 1 fixture missing PRODUCT-LEVEL-COVARIATE → V20 fail expected
- 1 fixture with old F24 numbering → V22 fail expected

OUTPUT: Both files. Run pytest after writing.
```

---

### P17 — Validator 실행 + 자동 수정 루프

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P16 PASS
🔹 **첨부 파일:** 모든 config/*.yaml
🔹 **산출물:**
  - 수정된 config/*.yaml
  - `reports/config_schema_validation_report.md` (error_count: 0)
  - (필요 시) `reports/llm_proxy/config_semantic_questions.md`
🔹 **다음 액션:** error_count=0이면 P18 (LP Panel CP1) 진행

```
ROLE: Coding agent.

PROCEDURE:
1. Run python scripts/config_validation/validate_config.py --config-dir config --out reports/config_schema_validation_report.md
2. If errors exist:
   a. Structural errors (missing keys, wrong types, broken references) — fix YAML directly
   b. PMX-semantic errors (e.g., "is this state really a REPAIR?") — write to reports/llm_proxy/config_semantic_questions.md (do NOT auto-decide)
3. Re-run validator. Loop until error_count = 0 OR only semantic questions remain (max 5 loops).
4. If max loops reached without success → output "ESCALATE: structural fixes exhausted, manual review needed".

OUTPUT:
- Final config/*.yaml (updated)
- reports/config_schema_validation_report.md with error_count=0 (or escalation flag)
- reports/llm_proxy/config_semantic_questions.md (only if semantic questions exist)

CONSTRAINT:
- Never auto-modify state codes or q-codes based on semantic intuition
- Only fix references, missing fields, structural typos
```

---

### P18~P20 — LP Panel CP1: Config Semantic Review (필요 시만)

> **🔹 조건부 실행:** P17에서 `reports/llm_proxy/config_semantic_questions.md`가 생성된 경우만 실행. 없으면 P21로 직행.

#### P18 (LP-A) — Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** config_semantic_questions.md, axis_dictionary, dependency_constraints
🔹 **산출물:** `reports/llm_proxy/config_semantic_review_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A).

INPUT (attached): reports/llm_proxy/config_semantic_questions.md
                  config/axis_dictionary.yaml
                  config/dependency_constraints.yaml
                  config/quarantine_reason_codes.yaml

TASK: For each semantic question, produce LP-A judgment per LP Panel template (P2 lp_panel_template.yaml).

OUTPUT FIELDS per question:
- recommended_decision (accept/reject/revise/split)
- rationale_pmx_evidence
- confidence (HIGH/MEDIUM/LOW)
- fatal_issues
- residual_risk
- must_escalate_to_human
- escalation_reason

OUTPUT: Markdown matching template.
File header: "# config_semantic_review_grandmaster.md (LP-A, Checkpoint: CP1)"
```

#### P19 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** P18 grandmaster.md + 원본 questions.md
🔹 **산출물:** `reports/llm_proxy/config_semantic_review_adversarial.md`

```
ROLE: Adversarial reviewer (LP-B). DIFFERENT model family from LP-A.

INPUT (attached): reports/llm_proxy/config_semantic_review_grandmaster.md
                  reports/llm_proxy/config_semantic_questions.md
                  config/axis_dictionary.yaml

ATTACK AXES:
1. REPAIR over-permissiveness in Grandmaster's accepts
2. Missed policy absence (Grandmaster accepted REPAIR but no policy specified)
3. Q-code mismatch with root cause
4. v4.2: Q15A-D classification error
5. v4.2: missing CELLULAR/IMMUNOGENICITY/MATERNAL_INFANT/MILK consideration
6. AIC endpoint_data_type omissions
7. Forced node violations (A0/A3/A4/A5/A8/A10/policy implicitly excluded)
8. Q17 sneaking in
9. PHI/legal/IRB risk overlooked

OUTPUT FIELDS:
- attack_list: [{question_id, issue, severity:fatal/major/minor, evidence, correction}]
- unresolved_fatal_count
- escalate_to_human_override (YES/NO)

OUTPUT: Markdown.
```

#### P20 (LP-C) — Judge + 자동 적용

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션, P18+P19 모두 첨부)
🔹 **첨부 파일:** P18 grandmaster + P19 adversarial
🔹 **산출물:**
  - `reports/llm_proxy/config_semantic_review_judge.md`
  - `reports/llm_proxy/config_semantic_review_decision.csv`
  - 자동 적용 시 수정된 config/*.yaml
🔹 **다음 액션:** validate_config.py 재실행 → error_count=0 확인 → P21

```
ROLE: Judge (LP-C).

INPUT (attached): grandmaster.md + adversarial.md (both Phase CP1 outputs).

ENFORCE Hard Rules from lp_panel_template.yaml:
- confidence=LOW → escalate=YES (forced)
- unresolved_fatal_count >= 1 → escalate=YES (forced)
- Cannot accept Q15 standalone, Q17, or QUARANTINE without q_code, or REPAIR without policy

OUTPUT FIELDS (per LP-C template):
- final_decision
- accepted_arguments_from_A
- accepted_attacks_from_B
- rejected_arguments_with_rationale
- required_patch (specific YAML edits)
- affected_artifacts
- required_rerun_steps
- confidence
- fatal_resolved
- escalate_to_human
- escalation_reason

AUTO-APPLY CONDITION:
If confidence=HIGH AND fatal_resolved=YES AND escalate=NO:
  Apply required_patch to config/*.yaml directly.
  Re-run validator.
  Confirm error_count=0.

OUTPUTS:
- judge.md (markdown)
- decision.csv (single-row machine-readable: checkpoint, lp_a_confidence, lp_b_fatal, judge_decision, escalated, auto_applied)
```

---

### P21 — AIC Schema Validator + 테스트

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P17 또는 P20 완료, error_count=0
🔹 **첨부 파일:** P14 AIC template
🔹 **산출물:**
  - `scripts/config_validation/validate_aic.py`
  - `tests/test_validate_aic.py`
🔹 **다음 액션:** pytest PASS → P22

```
ROLE: Coding agent.

TASK: Implement scripts/config_validation/validate_aic.py with these checks (8):

A01  required field presence (model_family, analysis_objective)
A02  AIC-PKPD/ER/TTE/BIOMARKER → endpoint_data_type required
A03  v4.2: CELLULAR_KINETICS → cellular_LLOQ_derivation_policy required
A04  v4.2: IMMUNOGENICITY → positivity_adjudication_rule required
A05  v4.2: MATERNAL_INFANT_PK → dyad_linkage_policy + delivery_anchor_policy required
A06  v4.2: MILK_PK → milk_matrix_lloq_policy required
A07  modality_class in {ADC,BISPECIFIC,CELL_THERAPY,GENE_THERAPY} + multi-analyte → analyte_role required
A08  Each missing-required maps to correct q_code per quarantine_reason_codes.yaml

CLI:
python scripts/config_validation/validate_aic.py --aic-file <path> --out <report>

TESTS: 8 cases, one per validator.
OUTPUT: Both files; run pytest.
```

---

### P22 — Phase 1 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델 — Claude Sonnet 계열 최신)
🔹 **진입 조건:** P21 PASS
🔹 **첨부 파일:** validation reports, frozen_universe_v4_2_summary.md
🔹 **산출물:** `reports/universe_yaml_completion_v4_2.md`
🔹 **다음 액션:** CHECK-1 실행

```
ROLE: Documentation writer.

INPUT (attached): reports/config_schema_validation_report.md
                  reports/frozen_universe_v4_2_summary.md
                  config/axis_dictionary.yaml
                  config/dependency_constraints.yaml
                  config/family_assignment_rules.yaml

TASK: Produce reports/universe_yaml_completion_v4_2.md.

CHECKLIST (all must be ✅ for completion):
[ ] schema_validation error_count = 0
[ ] V01-V22 all pass
[ ] A0-A10 axes defined
[ ] A0 has modality_class auxiliary field (11+ values)
[ ] A0 has endpoint_data_type auxiliary field (10 values, v4.2 NEW types present)
[ ] A7 has PRODUCT-LEVEL-COVARIATE state
[ ] A8 has analyte_role auxiliary field (12+ values)
[ ] F01-F29 operational + F31-F34 out-of-scope
[ ] F24, F25, F26, F27, F28, F29 v4.2-new operational families present
[ ] F31, F32, F33, F34 properly renumbered (formerly F24-F27)
[ ] Q01-Q19 except Q17 (count = 21 active codes)
[ ] Q15 standalone: 0
[ ] Q17 active: 0 (REJECTED entry only)
[ ] dependency_constraints ≥ 36 rules
[ ] DC003-DC007 (v4.2 endpoint constraints) present
[ ] DC021-DC022 (A7 PRODUCT-LEVEL-COVARIATE) present
[ ] DC027 (A8 analyte_role v4.2) present

If any unchecked → list as unresolved_items.

OUTPUT: Single markdown file.
```

---

### 🐍 CHECK-1 (Phase 1 검증)

`check_phase1.py`로 저장 후 `python check_phase1.py` 실행.

```python
# check_phase1.py
# Phase 1 (P7-P22) 완료 검증 — v4.2 universe 통합 확인
# 실행: python check_phase1.py

import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML 없음. pip install pyyaml")
    sys.exit(1)

# BASE 자동 탐색
BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("❌ pmx_universe_v5_1 폴더 없음")
    sys.exit(1)

print("=" * 60)
print("CHECK-1: Phase 1 (Universe YAML v4.2) 완료 검증")
print("=" * 60)

failures = []

# 1. 파일 존재
REQUIRED = [
    "config/axis_dictionary.yaml",
    "config/terminal_state_taxonomy.yaml",
    "config/quarantine_reason_codes.yaml",
    "config/dependency_constraints.yaml",
    "config/family_assignment_rules.yaml",
    "config/action_sequence_standard.yaml",
    "config/action_function_library.yaml",
    "config/analysis_intent_contract_template.yaml",
    "scripts/config_validation/validate_config.py",
    "scripts/config_validation/validate_aic.py",
    "reports/frozen_universe_v4_2_summary.md",
    "reports/config_schema_validation_report.md",
    "reports/universe_yaml_completion_v4_2.md",
    "reports/repair_quarantine_boundary_cases_v4_2.csv",
]
print("\n[파일 존재]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  ✅ {f.split('/')[-1]}")
    else:
        print(f"  ❌ {f}")
        failures.append(f"파일 없음: {f}")

# 2. axis_dictionary v4.2 검사
ax_path = BASE / "config/axis_dictionary.yaml"
if ax_path.is_file():
    print("\n[axis_dictionary v4.2 핵심 항목]")
    data = yaml.safe_load(ax_path.read_text(encoding="utf-8"))
    raw = ax_path.read_text(encoding="utf-8")

    # A0 modality_class
    if "modality_class" in raw and "CELL_THERAPY" in raw and "ADC" in raw:
        print("  ✅ A0 modality_class (ADC, CELL_THERAPY 등)")
    else:
        print("  ❌ A0 modality_class 누락 또는 불완전")
        failures.append("A0 modality_class")

    # A0 endpoint_data_type v4.2 4종
    v42_endpoints = ["CELLULAR_KINETICS", "IMMUNOGENICITY", "MILK_PK", "MATERNAL_INFANT_PK"]
    for ep in v42_endpoints:
        if ep in raw:
            print(f"  ✅ endpoint_data_type: {ep}")
        else:
            print(f"  ❌ endpoint_data_type {ep} 누락")
            failures.append(f"endpoint_data_type {ep}")

    # A7 PRODUCT-LEVEL-COVARIATE
    if "PRODUCT-LEVEL-COVARIATE" in raw:
        print("  ✅ A7 PRODUCT-LEVEL-COVARIATE")
    else:
        print("  ❌ A7 PRODUCT-LEVEL-COVARIATE 누락")
        failures.append("A7 PRODUCT-LEVEL-COVARIATE")

    # A8 analyte_role
    v42_roles = ["VECTOR_COPY", "CAR_POSITIVE_CELL", "TRANSGENE_EXPRESSION", "CONJUGATED_ADC"]
    for r in v42_roles:
        if r in raw:
            print(f"  ✅ analyte_role: {r}")
        else:
            print(f"  ❌ analyte_role {r} 누락")
            failures.append(f"analyte_role {r}")

# 3. Q-codes 21개 + Q17 rejected
qc_path = BASE / "config/quarantine_reason_codes.yaml"
if qc_path.is_file():
    print("\n[Q-code 검사]")
    txt = qc_path.read_text(encoding="utf-8")
    for q in ["Q01","Q02","Q03","Q04","Q05","Q06","Q07","Q08","Q09","Q10","Q11","Q12","Q13","Q14","Q15A","Q15B","Q15C","Q15D","Q16","Q18","Q19"]:
        if q in txt:
            pass
        else:
            print(f"  ❌ {q} 누락")
            failures.append(f"Q-code {q}")
    # Q17 처리
    if "Q17" in txt and ("REJECTED" in txt.upper() or "rejected" in txt):
        print("  ✅ Q17 = REJECTED 처리됨")
    else:
        if "Q17" not in txt:
            print("  ⚠️  Q17 항목 자체가 없음 (REJECTED 명시 권장)")
        else:
            print("  ❌ Q17이 활성 코드로 사용됨")
            failures.append("Q17 활성 사용")
    # Q15 단독
    import re
    standalone_q15 = re.findall(r'\bQ15\b(?!A|B|C|D)', txt)
    if not standalone_q15:
        print("  ✅ Q15 단독 사용 0건")
    else:
        print(f"  ❌ Q15 단독 {len(standalone_q15)}건")
        failures.append("Q15 단독")

    # [PATCH m-4 — v5.1 CRITICAL] Q15A-D 의미 정의 검증
    # 구버전 단순 정의("컬럼/필드/표/파일 부재")가 아닌 올바른 실무 정의 사용 여부 확인
    print("\n[PATCH m-4] Q15 sub-code 의미 검증")
    q15_semantic_checks = {
        "Q15A": {
            "required_keywords": ["adjudication", "upstream"],
            "forbidden_keywords": [],
            "description": "Q15A = upstream adjudication decision 미제출",
        },
        "Q15B": {
            "required_keywords": ["legacy", "undocumented"],
            "forbidden_keywords": [],
            "description": "Q15B = legacy flag/field 정의 없어 해석 불가",
        },
        "Q15C": {
            "required_keywords": ["adherence", "real-world"],
            "forbidden_keywords": [],
            "description": "Q15C = real-world adherence/administration history unresolved",
        },
        "Q15D": {
            "required_keywords": ["reanalysis", "adjudication"],
            "forbidden_keywords": [],
            "description": "Q15D = assay reanalysis/final-result adjudication missing",
        },
    }
    txt_lower = txt.lower()
    for code, spec in q15_semantic_checks.items():
        hit = all(kw.lower() in txt_lower for kw in spec["required_keywords"])
        if hit:
            print(f"  ✅ {code}: {spec['description']}")
        else:
            missing_kw = [kw for kw in spec["required_keywords"] if kw.lower() not in txt_lower]
            print(f"  ⚠️  {code}: 의미 키워드 누락 {missing_kw} — 구버전 단순 정의 사용 의심")
            print(f"       올바른 정의: {spec['description']}")
            print(f"       [PATCH m-4] Step 1 P10 프롬프트의 Q15 정의를 확인하세요.")
            # ⚠️ WARNING (not failure) — semantic content is hard to enforce automatically
            # 실제 운영 판단은 LP Panel CP1에서 수행

# 4. Family F24-F29 + F31-F34
fam_path = BASE / "config/family_assignment_rules.yaml"
if fam_path.is_file():
    print("\n[Family 검사]")
    txt = fam_path.read_text(encoding="utf-8")
    for f in ["F24","F25","F26","F27","F28","F29"]:
        if f in txt:
            print(f"  ✅ Operational {f}")
        else:
            print(f"  ❌ {f} 누락")
            failures.append(f"Family {f}")
    for f in ["F31","F32","F33","F34"]:
        if f in txt:
            print(f"  ✅ Out-of-scope {f}")
        else:
            print(f"  ❌ {f} 누락")
            failures.append(f"Family {f}")
    # F30 부재 검증 (intentionally reserved — must NOT be assigned)
    import re as _re
    f30_entries = _re.findall(r'\bF30\b', txt)
    if not f30_entries:
        print("  ✅ F30 미사용 (reserved, not assigned — 정상)")
    else:
        print(f"  ❌ F30가 {len(f30_entries)}회 사용됨 — F30는 예약 번호이며 할당 금지")
        failures.append("F30 잘못 할당")

# 5. dependency_constraints ≥ 36
dc_path = BASE / "config/dependency_constraints.yaml"
if dc_path.is_file():
    print("\n[Dependency Constraints]")
    data = yaml.safe_load(dc_path.read_text(encoding="utf-8"))
    rules = data.get("rules", data) if isinstance(data, dict) else data
    n = len(rules) if isinstance(rules, list) else 0
    print(f"  규칙 수: {n}")
    if n >= 36:
        print(f"  ✅ ≥36 (v4.2 기준)")
    else:
        print(f"  ❌ <36")
        failures.append(f"DC rules {n}/36")

# 6. validator 보고서
vr = BASE / "reports/config_schema_validation_report.md"
if vr.is_file():
    print("\n[Validator 보고서]")
    txt = vr.read_text(encoding="utf-8")
    if "total_errors: 0" in txt or "error_count: 0" in txt or "total_errors=0" in txt:
        print("  ✅ error_count = 0")
    else:
        print("  ⚠️  error_count 확인 필요")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 1 (Universe v4.2) 완료")
    print("→ 다음: Phase 2 (P23) 시작")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
```

---

## 🔄 Phase 2: Action Sequence + AIC Contract 고정 (P23~P28)

### 📌 이 단계 목적

P13~P14에서 만든 action_sequence + AIC를 검증하고 잠급니다. 이후 모든 EP 분류는 이 어휘를 사용합니다.

### 진입 조건
- [x] CHECK-1 PASS

---

### P23 — Boundary Case 의미 검증

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P15 boundary cases CSV, Phase 1 모든 YAML
🔹 **산출물:** `reports/boundary_case_semantic_review.md`
🔹 **다음 액션:** P24

```
ROLE: PMX Grandmaster.

INPUT (attached):
  reports/repair_quarantine_boundary_cases_v4_2.csv
  config/axis_dictionary.yaml
  config/quarantine_reason_codes.yaml
  config/action_sequence_standard.yaml

TASK: Review each of 60 boundary cases for semantic correctness.

FOR EACH CASE:
- Is terminal_state correct given the axis combination?
- Is q_code (if QUARANTINE) the most specific applicable code?
- Is action_sequence pattern consistent with terminal_state?
- v4.2: For new modality cases, are auxiliary fields (modality_class, analyte_role, endpoint_data_type) consistently set?

OUTPUT FIELDS per case (only flag if mismatch suspected):
- case_id
- issue_type: WRONG_TERMINAL / WRONG_QCODE / INCONSISTENT_SEQUENCE / V42_AUX_MISSING
- evidence
- recommended_correction

If 0 issues → output "ALL_CASES_PASS_SEMANTIC_REVIEW".

OUTPUT: Markdown.
```

---

### P24 — Boundary Case Q-code 자동 검증

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **첨부 파일:** P15 CSV, Phase 1 YAMLs
🔹 **산출물:**
  - `scripts/config_validation/validate_boundary_cases.py`
  - `reports/boundary_case_qcode_validation.md`
🔹 **다음 액션:** P25

```
ROLE: Coding agent.

TASK: Implement scripts/config_validation/validate_boundary_cases.py.

CHECKS:
1. Each row's q_code (if QUARANTINE) exists in quarantine_reason_codes.yaml
2. No row has q_code = "Q15" standalone
3. No row has q_code = "Q17"
4. action_sequence_pattern starts with "parse_source"
5. action_sequence_pattern ends with "export_nonmem_ready" (AUTO/REPAIR) or "flag_*" (others)
6. AUTO rows have no repair_* functions
7. v4.2 cases:
   - if endpoint_data_type=CELLULAR_KINETICS: action_sequence must contain canonicalize_cellular_blq if REPAIR
   - if endpoint_data_type=IMMUNOGENICITY: must contain adjudicate_immunogenicity_positivity if REPAIR
   - if endpoint_data_type=MATERNAL_INFANT_PK: must contain attach_dyad_linkage if REPAIR
   - if A8 has analyte_role declared: must use assign_cmt_with_analyte_role
8. Mismatch count by family
9. AUTO/REPAIR/QUARANTINE/UNSUPPORTED/INVALID distribution matches required (4/30/22/2/2)

CLI:
python scripts/config_validation/validate_boundary_cases.py \
  --csv reports/repair_quarantine_boundary_cases_v4_2.csv \
  --config-dir config \
  --out reports/boundary_case_qcode_validation.md

REPORT: Markdown with check results, distribution, mismatches.

OUTPUT: Both files. Run.
```

---

### P25 — Action Sequence Lock Decision

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P23 review, P24 validation report
🔹 **산출물:** `reports/action_sequence_lock_decision.md`
🔹 **다음 액션:** P26

```
ROLE: PMX Grandmaster.

INPUT: P23 semantic review + P24 automated validation.

TASK: Lock decision document.

CHECKLIST:
[ ] All 60 boundary cases semantic-review PASS
[ ] All 9 P24 automated checks PASS
[ ] action_sequence_standard contains v4.2 NEW functions:
    canonicalize_cellular_blq, adjudicate_immunogenicity_positivity,
    attach_dyad_linkage, derive_time_postpartum_anchor,
    assign_milk_matrix_lloq, assign_cmt_with_analyte_role,
    attach_covariate_product_level
[ ] AIC template covers all v4.2 conditional fields

If all checked → declare LOCKED v1.0 (action_sequence + AIC).
SHA256 hash of action_sequence_standard.yaml + analysis_intent_contract_template.yaml.

OUTPUT: Markdown with lock declaration + hashes (placeholder for C-LLM to fill).
```

---

### P26 — Action Sequence Hash 생성 (C-LLM)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **첨부 파일:** P25 lock decision draft
🔹 **산출물:**
  - `release/v1.0/action_sequence_lock_v1_0.md` (해시 채워진 최종본)
  - `release/v1.0/action_sequence_v1_0.sha256`
🔹 **다음 액션:** P27

```
ROLE: Coding agent.

TASK:
1. Compute SHA256 of:
   - config/action_sequence_standard.yaml
   - config/action_function_library.yaml
   - config/analysis_intent_contract_template.yaml
   Concatenated in this exact order, separated by single "\n".
2. Write release/v1.0/action_sequence_v1_0.sha256 with format:
   <hash>  config/action_sequence_standard.yaml
   <hash>  config/action_function_library.yaml
   <hash>  config/analysis_intent_contract_template.yaml
   <combined_hash>  COMBINED
3. Take P25's lock_decision draft and inject the hashes, save as release/v1.0/action_sequence_lock_v1_0.md

OUTPUT: Both files.
```

---

### P27 — Pilot Edge-Case Seed Pack 정의 (v5.1 NEW)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** Phase 1 YAMLs
🔹 **산출물:** `reports/pilot_edge_case_seed_pack_v5_1.md`
🔹 **다음 액션:** P28

> **이 프롬프트는 v5.1 신규 추가입니다.** 검토 의견 PATCH-6에 따라 pilot 다양성을 강제합니다.

```
ROLE: PMX Grandmaster.

INPUT: Phase 1 YAMLs (attached).

TASK: Define MANDATORY pilot edge-case seed pack — 20 categories that pilot fingerprints
MUST cover before universe freeze.

REQUIRED 20 CATEGORIES (each must be represented by ≥1 real or synthetic dataset):

ROUTINE (8):
1. Standard SDTM/ADaM popPK
2. Multi-study pooled popPK
3. SAD/MAD with ADDL/II
4. Crossover/BA-BE
5. DDI victim-only
6. Pediatric mg/kg/BSA
7. TDM/RWD irregular dosing
8. Simple preclinical PK

V4.1 EDGE (5):
9. Titration/adaptive dosing
10. Loading-maintenance regimen
11. Infusion stop-restart
12. ADDL vs actual dose conflict
13. Reanalysis duplicate with/without final flag

V4.2 NEW MODALITY (5):
14. ADC multi-analyte (total Ab + conjugated + payload)
15. Bispecific PK + soluble target
16. CAR-T cellular kinetics (qPCR or FACS)
17. mRNA prime/boost with immunogenicity
18. DDI victim+perpetrator (dual CMT)

V4.2 SPECIAL POPULATION (2):
19. Pregnancy PK with delivery-anchored time
20. Lactation/mother-infant dyad PK with milk matrix

FOR EACH CATEGORY, document:
- description
- expected family_id (F-code)
- expected modality_class
- expected endpoint_data_type
- key axis states (A0..A10) representative pattern
- minimum required AIC fields
- expected terminal_state
- expected q_code (if QUARANTINE) — provide both "policy present" and "policy absent" subcases

VALIDATION RULE FOR PILOT COMPLETENESS:
"Universe freeze (Phase 5) cannot proceed unless ALL 20 categories appear in
data/pilot_fingerprints/empirical_fingerprints_pilot.csv with at least one row each."

OUTPUT: Markdown with 20-row table + per-category detail sections.
```

---

### P28 — Phase 2 Hash + 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델 — Claude Sonnet 계열 최신)
🔹 **첨부 파일:** P25 lock, P26 hash file, P27 seed pack
🔹 **산출물:** `reports/phase2_completion_declaration.md`
🔹 **다음 액션:** CHECK-2 실행

```
ROLE: Documentation writer.

TASK: Produce reports/phase2_completion_declaration.md.

CHECKLIST:
[ ] action_sequence_standard.yaml LOCKED (hash exists)
[ ] AIC template LOCKED (hash exists)
[ ] 60 boundary cases semantic-reviewed PASS
[ ] 60 boundary cases automated-validated PASS
[ ] v4.2 new functions in action vocabulary
[ ] v4.2 conditional AIC fields covered
[ ] pilot edge-case seed pack (20 categories) documented

OUTPUT: Markdown.
```

---

### 🐍 CHECK-2 (Phase 2 검증)

```python
# check_phase2.py
# Phase 2 (P23-P28) 완료 검증
import os, sys, hashlib
from pathlib import Path

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("❌ pmx_universe_v5_1 폴더 없음")
    sys.exit(1)

print("=" * 60)
print("CHECK-2: Phase 2 (Action Sequence + AIC Lock) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "config/action_sequence_standard.yaml",
    "config/action_function_library.yaml",
    "config/analysis_intent_contract_template.yaml",
    "scripts/config_validation/validate_aic.py",
    "scripts/config_validation/validate_boundary_cases.py",
    "reports/repair_quarantine_boundary_cases_v4_2.csv",
    "reports/boundary_case_semantic_review.md",
    "reports/boundary_case_qcode_validation.md",
    "reports/pilot_edge_case_seed_pack_v5_1.md",
    "reports/phase2_completion_declaration.md",
    "release/v1.0/action_sequence_lock_v1_0.md",
    "release/v1.0/action_sequence_v1_0.sha256",
]
print("\n[파일 존재]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  ✅ {f.split('/')[-1]}")
    else:
        print(f"  ❌ {f}")
        failures.append(f)

# v4.2 신규 함수 7개 확인
print("\n[Action Sequence v4.2 신규 함수]")
asf = BASE / "config/action_sequence_standard.yaml"
if asf.is_file():
    txt = asf.read_text(encoding="utf-8")
    for fn in [
        "canonicalize_cellular_blq",
        "adjudicate_immunogenicity_positivity",
        "attach_dyad_linkage",
        "derive_time_postpartum_anchor",
        "assign_milk_matrix_lloq",
        "assign_cmt_with_analyte_role",
        "attach_covariate_product_level",
    ]:
        if fn in txt:
            print(f"  ✅ {fn}")
        else:
            print(f"  ❌ {fn} 누락")
            failures.append(fn)

# Pilot seed pack 20 카테고리 확인
print("\n[Pilot edge-case seed pack 20 카테고리]")
sp = BASE / "reports/pilot_edge_case_seed_pack_v5_1.md"
if sp.is_file():
    txt = sp.read_text(encoding="utf-8")
    keywords = [
        "SDTM", "Multi-study", "SAD/MAD", "Crossover", "DDI victim-only",
        "Pediatric", "TDM", "preclinical",
        "Titration", "Loading-maintenance", "Infusion stop", "ADDL", "Reanalysis",
        "ADC", "Bispecific", "CAR-T", "mRNA", "DDI victim+perpetrator",
        "Pregnancy", "Lactation",
    ]
    found = sum(1 for k in keywords if k.lower() in txt.lower())
    print(f"  카테고리 키워드 매칭: {found}/20")
    if found >= 18:  # 대소문자/표기 차이 감안
        print("  ✅ 20 카테고리 충족")
    else:
        print("  ❌ 일부 누락")
        failures.append("seed pack 카테고리")

# SHA256 해시 형식 확인
print("\n[SHA256 해시]")
hf = BASE / "release/v1.0/action_sequence_v1_0.sha256"
if hf.is_file():
    txt = hf.read_text(encoding="utf-8")
    import re
    hashes = re.findall(r'\b[a-f0-9]{64}\b', txt)
    if len(hashes) >= 4:
        print(f"  ✅ {len(hashes)}개 해시 (3 individual + 1 combined 이상)")
    else:
        print(f"  ❌ 해시 수 부족: {len(hashes)}")
        failures.append("해시 수")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 2 완료")
    print("→ 다음: Phase 3 (P29) 시작 — 실제 데이터 + H1, H2")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
```

---

## 📊 Step 1 종료 — 진행 상황 요약

```
✅ 환경 세팅 완료
✅ Phase 0 (P1-P6) — 헌장, LP Panel 템플릿, 폴더 구조, 로깅 유틸리티
✅ Phase 1 (P7-P22) — Frozen Universe v4.2 YAML 8개 + validator + LP Panel CP1 (조건부)
✅ Phase 2 (P23-P28) — Action Sequence + AIC Lock + Pilot seed pack
✅ CHECK-0, CHECK-1, CHECK-2 — Python 검증 스크립트 3개

이 시점까지 생성된 핵심 파일 (35개+)
- config/ 8개 YAML (axis, terminal, qcode, dependency, family, action, function, AIC)
- scripts/ 6개 (logging, lp_runner, validate_config, validate_aic, validate_boundary, conftest)
- reports/ 8개 (charter, dag, success, summary, validation, completion, semantic_review, edge_case_seed)
- release/v1.0/ 2개 (lock, sha256)
- tests/ 3개 (logging, lp_runner, validate_config)
- 루트 문서 5개 (README, CHANGELOG, .gitignore, requirements, pyproject)

다음 단계 (Step 2)에서 다룰 내용:
- Phase 3 (P29-P40): Pilot 데이터 수집 + Golden 1차 + H1, H2 (실제 데이터 투입)
- Phase 4 (P41-P52): Repair Executor 구현 + pytest + LP Panel CP3
- Phase 5 (P53-P65): Scenario Generator + Universe Freeze + LP Panel CP2
- Phase 6 (P66-P70): Decision Nodes (N0-N8, N8 forced 명시) + Cost Function (LP Panel 제거, 단일 R-LLM)
- Phase 7 (P71-P85): Action Label + LP Panel CP4 + EP Split + LP Panel CP5 + LOCK

> ⚠️ **[PATCH F-1 — Phase 번호 기준표]** Step 3의 Phase 범위는 다음으로 확정합니다.
> Step 3 파일과 충돌 시 이 기준이 우선합니다:
>
> | Phase | P 범위 | 내용 | CHECK |
> |---|---|---|---|
> | Phase 8 | P86–P100 | Decision Table + ILP + LP Panel CP6 | CHECK-8 |
> | Phase 9 | P101–P105 | Operational Decision Tree + NONMEM QC + Lock | CHECK-9 |
> | Phase 10 | P106–P115 | Golden Validation + H3 + H4 + H5 + LP Panel CP7 + Release Tag | CHECK-10 |
> | Phase 11 | P116–P140 | Change Control + 100-case Validation + SOP + Final Completion | CHECK-11 |

CHECK-3, CHECK-4, CHECK-5, CHECK-6, CHECK-7
```

> **민구 씨가 지금 해야 할 일:**
>
> 1. 이 v5.1_step1.md 문서를 처음부터 끝까지 한 번 읽고, 모르는 용어/단계가 있으면 표시
> 2. 환경 세팅(Python, Cursor, 폴더) 먼저 완료 → CHECK-0 자체는 P6 끝나고 실행
> 3. 시간 여유가 있을 때 P1부터 차근차근 시작
> 4. 각 P마다 "🔹 LLM 라우팅"에 명시된 모델로 입력
> 5. 산출물은 "🔹 산출물" 경로에 정확히 저장
> 6. CHECK 스크립트 PASS 후 다음 P로 진행
>
> **막히면 어디서 막혔는지 (P 번호 + 에러 메시지) 알려주세요.**
>
> Step 1이 정상적으로 잘 설계되었는지 확인해보시고,
> **"계속"** 입력하시면 Step 2 (Phase 3~7)를 작성하겠습니다.

---

*PMX-to-NONMEM Scenario Universe v5.1 — Step 1 / 3*
*Frozen Universe v4.2 통합 | LP Panel 7개 압축 | Forced Node 명시 | Pilot Seed Pack 강제*

---

### 📋 v5.1 Step 1 패치 이력 (patched_v3)

| 패치 ID | 대상 | 내용 | 심각도 |
|---|---|---|---|
| PATCH-m4-P10 | P10 quarantine_reason_codes.yaml | Q15A-D 올바른 실무 정의 4개 삽입 (upstream adjudication / legacy flag / adherence / reanalysis 기준) | CRITICAL |
| PATCH-m4-P11 | P11 DC017 | A5=BIOANALYTICAL-FINAL-FLAG-MISSING → Q15A로 수정 (Q15D는 reanalysis 선택 기준 부재에 한정) | CRITICAL |
| PATCH-m4-CHECK1 | CHECK-1 | Q15A-D semantic keyword 검증 블록 추가 (warning 수준, auto-catch) | IMPORTANT |
| PATCH-F30-header | Step 1 헤더 표 | F30 번호 공백에 "번호 예약" 주석 추가 | MINOR |
| PATCH-F30-P7 | P7 FAMILIES 태스크 | F30 NOT생성 지시 추가 | MINOR |
| PATCH-F30-P12 | P12 TASK + VALIDATION | F30 할당 금지 명시 및 검증 규칙 추가 | MINOR |
| PATCH-F30-CHECK1 | CHECK-1 | F30 부재 자동 검증 추가 (failures 등록) | MINOR |