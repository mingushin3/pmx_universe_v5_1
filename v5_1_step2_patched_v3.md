# PMX-to-NONMEM Scenario Universe v5.1
## Python-Integrated Prompt Sequence (LLM-Maximal Edition)
### Step 2 / 3 — Phase 3~7 (P29~P85)

> **Step 1에서 한 일:** 환경 세팅 + Hard Rules + LP Panel 템플릿 + Frozen Universe v4.2 YAML + Action Sequence Lock
>
> **Step 2에서 할 일:** 실제 데이터 투입(H1, H2) + Repair Executor 구현 + Scenario Universe Freeze + Action Label Lock
>
> **Step 3에서 할 일:** ILP Minimal Node + Decision Tree + Validation + Release(H3, H4, H5) + Change Control

---

## 🚦 진입 조건 점검

Step 2를 시작하기 전 다음이 모두 PASS여야 합니다:

```
✅ CHECK-0 PASS  (Phase 0 완료)
✅ CHECK-1 PASS  (Phase 1 — v4.2 universe YAML 완료)
✅ CHECK-2 PASS  (Phase 2 — action sequence lock 완료)
```

만약 하나라도 FAIL이면 Step 1로 돌아가서 해당 P 번호를 재실행하세요.

---

## 🗂️ Phase 3: Pilot 데이터 수집 + Golden 1차 + H1, H2 (P29~P40)

### 📌 이 단계 목적

**처음으로 실제 PMX 데이터를 투입하는 단계입니다.**
연구실에 있는 임상/전임상 데이터셋을 비식별화하고, 각 데이터셋의 "지문(Fingerprint)"을 A0~A10 축에 매핑합니다.
**v5.1 핵심 강화:** Step 1 P27에서 정의한 20-카테고리 edge-case seed pack을 모두 충족해야 universe freeze로 진행 가능합니다.

### 진입 조건
- [x] CHECK-2 PASS
- [x] 연구실 실제 데이터 또는 합성/공개 데이터 접근 가능 (최소 20개 권장 — seed pack 20카테고리 각 1개 이상)

---

### P29 — Pilot Sampling Plan v5.1 (20-카테고리 강제)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** CHECK-2 PASS
🔹 **첨부 파일:** Step 1 P27 산출물 `reports/pilot_edge_case_seed_pack_v5_1.md`, P12 `family_assignment_rules.yaml`
🔹 **산출물:** `reports/pilot_sampling_plan_v5_1.md`
🔹 **다음 액션:** P30 진행

```
ROLE: PMX Grandmaster.

INPUT (attached):
  reports/pilot_edge_case_seed_pack_v5_1.md
  config/family_assignment_rules.yaml

TASK: Produce reports/pilot_sampling_plan_v5_1.md — concrete sampling plan that
guarantees all 20 edge-case seed categories are covered before universe freeze.

PLAN STRUCTURE per category (×20):

category_id (1-20)
description
required_n: 1 (minimum) or 2-3 (preferred for routine)
acceptable_data_sources:
  - "real lab dataset (deidentified)"
  - "synthetic dataset built per AIC template"
  - "public dataset (e.g., nlmixr2 warfarin for F01)"
suggested_public_alternatives:
  # When real data unavailable
required_raw_file_types: [list]
required_policy_docs: [list]
golden_dataset_candidate: YES/NO/PREFERRED
privacy_risk: HIGH/MEDIUM/LOW
minimum_columns_to_inspect: [list]
v4_2_aux_fields_required:
  modality_class: [...]
  endpoint_data_type: [...]
  analyte_role: [...]
expected_terminal_state: AUTO/REPAIR/QUARANTINE
expected_q_code_if_quarantine: [...]
fallback_if_unavailable: "register as v1.1 candidate, mark category as DEFERRED"

OVERALL TABLE:
| category_id | family_id | min_n | golden_candidate | privacy | source_type |

PUBLIC ALTERNATIVES (suggest at least 6):
F01 → nlmixr2 warfarin / theophylline
F02 → public popPK pooled examples
F07 → SAD/MAD synthetic from AIC
F09 → public DDI examples (Simcyp)
F12 → pediatric public examples (where deidentified)
F19 → Tox21/preclinical public
F26 → CAR-T public CK examples (Cell journal supplementary)
... etc.

VALIDATION RULE:
"Pilot completeness = 20/20 categories. If <20, list missing categories and
register them in change_control/v1.1_candidate_register.csv before freeze."

OUTPUT: Markdown.
```

---

### P30 — 비식별화 체크리스트 v5.1

🔹 **LLM 라우팅:** R-LLM (효율 모델 — 단순 체크리스트)
🔹 **진입 조건:** P29 완료
🔹 **첨부 파일:** 없음
🔹 **산출물:** `config/deidentification_checklist_v5_1.md`
🔹 **다음 액션:** **H1 (사람이 직접 수행)**

```
ROLE: Privacy/PHI compliance officer.

TASK: Produce config/deidentification_checklist_v5_1.md.

REQUIRED CHECKLIST ITEMS (each with: how_to_check, tool, example, risk_level):

1. USUBJID, SUBJID, PATID, patient initials
2. Date/datetime fields (EXSTDTC, PCDTC, BRTHDTC) — replace with relative day or shifted date
3. Site/investigator names, SITEID
4. Free-text comment/narrative fields
5. Specimen/lab accession numbers
6. Excel file metadata (author, last modified, company)
7. Excel hidden sheets (very common in CRO files)
8. Excel track changes / comments
9. PDF embedded metadata
10. File path containing project name / patient name
11. Protocol number, ClinicalTrials.gov ID (if narrow study)
12. Rare disease / small subject population re-identification risk
13. v5.1 NEW — manufacturing lot ID linked to patient (CAR-T, gene therapy)
14. v5.1 NEW — pregnancy/lactation specific identifiers (delivery hospital, infant ID)
15. v5.1 NEW — geolocation in TDM/RWD datasets

EXCEL CHECK PROCEDURE:
File → Info → Check for Issues → Inspect Document
Then remove: hidden sheets, comments, track changes, document properties

UNIX METADATA:
exiftool filename → check creator, last_modified
or: mdls filename (Mac)

WINDOWS METADATA:
Right-click → Properties → Details → Remove Properties and Personal Information

SIGNATURE BLOCK at end:
- checked_by: [name]
- date: [YYYY-MM-DD]
- project_id: [internal ID, NOT clinical trial number]
- decision: APPROVED / NEEDS_REWORK
- notes:

OUTPUT: Markdown with checkboxes.
```

---

### 🧑 H1 — HUMAN: 파일 비식별화 + 폴더 복사 (필수, 대체 불가)

> **이 단계는 LLM이 절대 대체할 수 없습니다. PHI 유출 시 IRB/법적 책임이 사람에게만 부과됩니다.**

#### 수행 절차 (한 단계씩 따라하세요)

**1단계. 작업 환경 준비**

```
파일 1개씩 처리합니다. 한 번에 여러 개 동시 처리하지 마세요.
체크리스트는 "config/deidentification_checklist_v5_1.md"를 사용합니다.
```

**2단계. 각 파일에 대해 다음을 수행**

체크리스트의 15개 항목을 **눈으로 직접 확인**:

```
□ USUBJID 컬럼이 있는가? → 있다면 임의 ID로 치환
   (예: SUBJ-001, SUBJ-002 ... 또는 SHA256 해시 앞 8자리)

□ 날짜 컬럼 (EXSTDTC, PCDTC, BRTHDTC) → 상대 날짜로 변환
   (예: study day 1 = 0, study day 8 = 7)
   * 만약 절대 날짜가 PMX 분석에 필수이면 모든 환자에게 동일한 offset 적용 후
     "shifted by N days" 메모 첨부

□ Site/Investigator 이름 컬럼 → 임의 코드로 치환 (S01, S02...)

□ 자유기술 comment 컬럼 → 통째로 삭제하거나 PHI 검출 후 마스킹

□ Excel 파일이면:
   File → Info → Check for Issues → Inspect Document
   → Hidden Sheets, Comments, Track Changes, Document Properties 모두 Remove

□ 파일명에 환자명/프로젝트명 포함되어있으면 → 일반 파일명으로 변경
   (예: "John_Doe_MRI.xlsx" → "subject_S01_PK.xlsx")

□ 프로토콜 번호 / ClinicalTrials.gov ID 검색 → 좁은 연구 식별 가능하면 마스킹

□ CAR-T / gene therapy 데이터면:
   manufacturing lot ID와 patient ID의 매핑이 동일 파일에 있는지 확인
   → 분리하거나 lot ID도 임의 코드로 치환

□ Pregnancy/lactation 데이터면:
   delivery hospital, infant medical record number 모두 마스킹

□ Mac/Linux에서 metadata 제거:
   exiftool -all= filename.xlsx

   Windows에서 metadata 제거:
   파일 우클릭 → Properties → Details → "Remove Properties and Personal Information"
   → "Create a copy with all possible properties removed" 선택
```

**3단계. 비식별화 완료된 파일을 정해진 폴더로 복사**

```
경로 구조:
pmx_universe_v5_1/data/raw_examples/{family_id}/{project_id}/raw_files/

예시:
data/raw_examples/F01/PROJ_S01_001/raw_files/dataset_deidentified.csv
data/raw_examples/F26/PROJ_CART_002/raw_files/cellular_kinetics_qpcr.csv
data/raw_examples/F29/PROJ_LAC_003/raw_files/maternal_milk_pk.csv
```

**4단계. 수작업 reference output이 있는 경우 (golden dataset 후보)**

```
경로:
pmx_universe_v5_1/data/golden_datasets/{project_id}/reference_output/

예시:
data/golden_datasets/PROJ_S01_001/reference_output/nonmem_ready.csv
```

**5단계. 인벤토리 작성**

`data/pilot_fingerprints/pilot_file_inventory.csv` 생성:

```csv
project_id,family_candidate,raw_file_path,ref_output_path,golden_candidate,deidentification_date,deidentified_by
PROJ_S01_001,F01,data/raw_examples/F01/PROJ_S01_001/raw_files/dataset.csv,data/golden_datasets/PROJ_S01_001/reference_output/nonmem_ready.csv,YES,[YYYY-MM-DD],[담당자 실명]
PROJ_CART_002,F26,data/raw_examples/F26/PROJ_CART_002/raw_files/cellular_kinetics.csv,,NO,[YYYY-MM-DD],[담당자 실명]
...
```

**6단계. 체크리스트 서명**

`config/deidentification_checklist_v5_1.md` 맨 아래에 직접 서명:
```
checked_by: [담당자 실명]
date: [YYYY-MM-DD]
project_count_processed: 20
decision: APPROVED
notes: [비식별화 결과 요약 — 예: "20-카테고리 seed pack 모두 커버. CAR-T 데이터(F26)는 lot ID 별도 분리."]
```

**7단계. 완료 조건 확인**

```
✅ data/raw_examples/ 아래 최소 20개 파일 존재 (20-카테고리 각 1개 이상)
✅ data/pilot_fingerprints/pilot_file_inventory.csv 생성됨
✅ config/deidentification_checklist_v5_1.md 서명됨
```

> **주의:** 만약 시간이 부족하거나 실제 데이터가 부족하면, P29의 "synthetic dataset" 또는 "public alternative" 옵션을 사용하세요. **20카테고리 미충족 상태로 다음 단계 진행 금지.** 미충족 카테고리는 `change_control/v1.1_candidate_register.csv`에 등록해서 v1.1로 미루세요.

---

### P31 — Fingerprint Template + Coding Guide v5.1

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** H1 완료 (raw_examples에 20개 이상 파일, 인벤토리, 서명)
🔹 **첨부 파일:** Phase 1 모든 YAML, P29 sampling plan
🔹 **산출물:**
  - `data/pilot_fingerprints/fingerprint_template.csv` (헤더만)
  - `reports/fingerprint_coding_guide_v5_1.md`
🔹 **다음 액션:** P32 진행

```
ROLE: PMX Grandmaster + bioinformatician.

INPUT (attached):
  config/axis_dictionary.yaml
  config/analysis_intent_contract_template.yaml
  config/action_sequence_standard.yaml
  reports/pilot_sampling_plan_v5_1.md

TASK 1: data/pilot_fingerprints/fingerprint_template.csv (header only)

COLUMNS (43개):
project_id
family_candidate
source_format
source_parser_subtype
study_design
aic_summary
modality_class                      # v5.1 NEW
endpoint_data_type                  # v5.1 NEW (10 values)
A0_state, A1_state, A2_state, A3_state, A4_state, A5_state,
A6_state, A7_state, A8_state, A9_state, A10_state
analyte_role                        # v5.1 NEW
input_tables
key_columns
time_columns
dose_columns
observation_columns
covariate_columns
known_policies
missing_policies
manual_steps_required
expected_terminal_state
expected_q_code
expected_action_sequence
golden_dataset_available
raw_input_path
reference_output_path
seed_category_id                    # v5.1 NEW (1-20 from edge-case seed pack)
v4_2_relevant_axes                  # comma-separated; e.g., "A0,A7,A8" if v4.2-specific
fingerprint_confidence              # HIGH/MEDIUM/LOW (LLM self-rating)
unknown_field_count
notes

OUTPUT: CSV with header row only (no data rows).

TASK 2: reports/fingerprint_coding_guide_v5_1.md

CONTENTS:
- How to fill each of 43 columns
- 5 example fingerprints (one each for: F01 routine, F09 DDI, F26 CAR-T, F29 lactation, F22 DDI dual)
- UNKNOWN coding rule: "If you cannot determine from the data + AIC, write UNKNOWN.
  Never guess. UNKNOWN >40% rate triggers H2 review escalation."
- Forbidden patterns: Q15 standalone, Q17, contradictions
- v5.1 specific guidance:
  - For modality_class: see Step 1 P8 axis_dictionary 11 values
  - For endpoint_data_type: 10 values, see P8
  - For analyte_role: 12 values, see P8 (only for ADC/BISPECIFIC/CELL/GENE multi-analyte)
  - seed_category_id: 1-20, must match P27 seed pack

OUTPUT: 2 files.
```

---

### P32 — 개별 Pilot Fingerprint 초안 (반복 프롬프트)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P31 완료, raw_examples에 파일 존재
🔹 **첨부 파일 (각 프로젝트마다):**
  - `config/axis_dictionary.yaml`
  - `reports/fingerprint_coding_guide_v5_1.md`
  - 해당 프로젝트의 raw 파일 컬럼 스냅샷 + 처음 3행 (비식별화 후)
  - 해당 프로젝트의 SAP/AIC 요약 (있으면)
🔹 **산출물:** `data/pilot_fingerprints/{PROJECT_ID}_fingerprint_draft.md` (각 프로젝트당 1개)
🔹 **다음 액션:** 모든 프로젝트 처리 후 H2

> **중요:** 이 프롬프트를 **각 project_id마다 반복 실행**합니다. 20개 프로젝트면 20번 실행. 같은 채팅창에서 반복해도 되지만, 5개 이상 누적되면 새 채팅창 권장 (context 오염 방지).

```
ROLE: PMX Grandmaster.

CONTEXT: I will provide one project's deidentified data snapshot. You produce a single
fingerprint draft.

INPUTS (attached):
  PROJECT_ID: {PROJECT_ID}
  FAMILY_CANDIDATE: {family_id}
  SEED_CATEGORY_ID: {1-20}
  COLUMN_SNAPSHOT: {column names + first 3 deidentified rows}
  AIC_SUMMARY: {SAP/AIC summary, or "NONE"}
  CODING_GUIDE: (attached)
  AXIS_DICTIONARY: (attached)

RULES:
1. Do not guess. UNKNOWN if uncertain.
2. REPAIR requires explicit policy in AIC_SUMMARY. If policy not visible → QUARANTINE
   with appropriate q_code.
3. If modality is ADC/BISPECIFIC/CELL_THERAPY/GENE_THERAPY and multi-analyte data
   → analyte_role REQUIRED for each measured analyte.
4. If endpoint_data_type=CELLULAR_KINETICS → cellular_LLOQ_derivation_policy must be
   visible in AIC; if absent → expected_q_code=Q01 with note "cellular subtype".
5. If endpoint_data_type=IMMUNOGENICITY → positivity_adjudication_rule required;
   absent → expected_q_code=Q19.
6. If endpoint_data_type=MATERNAL_INFANT_PK → dyad_linkage_key + delivery_anchor required;
   either absent → expected_q_code=Q18 or Q12.
7. expected_action_sequence uses only function names from action_sequence_standard.yaml.
8. q_code MUST NOT be Q15 standalone or Q17.
9. If you cannot determine seed_category_id, write "UNCERTAIN_n" where n is your best guess.

OUTPUT: data/pilot_fingerprints/{PROJECT_ID}_fingerprint_draft.md

FORMAT (markdown):
# Fingerprint Draft: {PROJECT_ID}

## Inventory
- family_candidate: {F-code}
- seed_category_id: {1-20}
- raw_input_path: {path}
- modality_class: {value or UNKNOWN}
- endpoint_data_type: {value or UNKNOWN}

## Axis States
- A0_state: ...
- A1_state: ...
... A10_state

## v4.2 Auxiliary
- analyte_role: ... (if applicable, else N/A)

## Detected Policies
- known_policies: [list]
- missing_policies: [list]

## Expected Classification
- expected_terminal_state: ...
- expected_q_code: ... (or N/A)
- expected_action_sequence: [function1, function2, ...]
- fingerprint_confidence: HIGH/MEDIUM/LOW
- unknown_field_count: N

## Notes
{free-form observations}
```

---

### 🧑 H2 — HUMAN: Fingerprint 사실관계 검토 (필수, LLM hallucination 방지)

> **이 단계 목적:** LLM이 만든 fingerprint 초안이 실제 데이터와 일치하는지 사람이 확인합니다. LLM은 "그럴듯해 보이는 거짓말"을 할 수 있고, 실제 column 이름을 잘못 기억하거나 axis state를 잘못 추정할 수 있습니다.

#### 수행 절차

**1단계. 한 프로젝트씩 처리** (20개라면 20번 반복)

각 `{PROJECT_ID}_fingerprint_draft.md`에 대해:

**2단계. 두 창 띄우기**

- 창 A: `data/pilot_fingerprints/{PROJECT_ID}_fingerprint_draft.md`
- 창 B: `data/raw_examples/{family_id}/{PROJECT_ID}/raw_files/` 안의 실제 파일

**3단계. 11개 항목을 직접 검증**

```
□ 1. source_format / source_parser_subtype이 실제 파일 구조와 일치?
   (CSV vs Excel vs SAS XPT vs JSON 등)

□ 2. time_columns 목록이 실제 컬럼명과 일치?
   (LLM이 종종 EXSTDTC를 EXDTC로 잘못 적음)

□ 3. dose_columns 목록이 실제 컬럼명과 일치?

□ 4. A4_state가 실제와 일치?
   - TITRATION-ADAPTIVE라고 코딩됐다면, 실제로 dose가 변하는가?
   - LOADING-MAINTENANCE라고 코딩됐다면, 두 phase가 실제로 있는가?
   - INFUSION-STOP-RESTART라고 코딩됐다면, RATE=0 이벤트가 있는가?
   - ADDL-ACTUAL-CONFLICT라고 코딩됐다면, ADDL과 실제 record가 동시에 있는가?

□ 5. A5_state가 실제와 일치?
   - BLQ flag가 실제 데이터에 있는가?
   - LLOQ가 명시되어있는가?
   - REANALYSIS-FINAL-MISSING이면, 실제로 duplicate DV가 있고 final flag가 없는가?

□ 6. v4.2 항목 — modality_class가 실제 약물/모달리티와 일치?
   (CAR-T인데 SMALL_MOLECULE로 적혀있으면 큰 오류)

□ 7. v4.2 항목 — endpoint_data_type이 실제 측정 유형과 일치?
   (qPCR copy 수가 PK_CONCENTRATION으로 적혀있으면 silent error 위험)

□ 8. v4.2 항목 — analyte_role이 실제 측정 analyte와 일치?
   (ADC trial인데 PARENT 하나만 있고 TOTAL_ANTIBODY/CONJUGATED_ADC가 누락됐다면 오류)

□ 9. known_policies가 실제 SAP/프로토콜과 일치?
   (LLM이 SAP에 없는 정책을 "있다고" 적은 게 가장 위험한 hallucination)

□ 10. expected_terminal_state + q_code가 위 axis 상태로부터 자동 도출 가능?
    (논리적으로 맞는지 점검)

□ 11. seed_category_id가 P27 seed pack과 일치?
    (예: F26 CAR-T cellular kinetics는 카테고리 16)
```

**4단계. 수정 또는 승인**

- 틀린 항목은 직접 수정
- 불확실한 항목은 UNKNOWN 유지
- 수정 완료된 파일을 `{PROJECT_ID}_fingerprint_approved.md`로 별도 저장
  (원본 `_draft.md`는 보존)

**5단계. 승인 로그 기록**

`reports/human_review/h2_fingerprint_approval_log.md`:

```markdown
# H2 Fingerprint Approval Log

| project_id | reviewed_by | date | status | corrections_count | notes |
|---|---|---|---|---|---|
| PROJ_S01_001 | [검토자 실명] | [YYYY-MM-DD] | APPROVED | 2 | A4 state corrected from PARTIAL to COMPLETE |
| PROJ_CART_002 | [검토자 실명] | [YYYY-MM-DD] | APPROVED | 5 | endpoint_data_type was PK_CONCENTRATION, corrected to CELLULAR_KINETICS. analyte_role added. |
...

Total processed: 20
Total approved: 20
Total UNKNOWN-flagged for follow-up: 3
Seed categories covered: 20/20

Reviewed_by: [검토자 실명]
Date: [YYYY-MM-DD]
```

**6단계. 완료 조건**

```
✅ 모든 project_id의 _approved.md 파일 존재
✅ approval_log.md 작성 완료
✅ seed categories 20/20 (또는 미충족분은 v1.1 register 등록)
```

---

### P33 — Fingerprint 통합 + 자동 검증

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** H2 완료 (모든 _approved.md 존재)
🔹 **첨부 파일:** approved fingerprint 파일들의 폴더 경로
🔹 **산출물:**
  - `data/pilot_fingerprints/empirical_fingerprints_pilot.csv`
  - `reports/pilot_fingerprint_integration_report.md`
🔹 **다음 액션:** P34 진행

```
ROLE: Coding agent.

TASK: Implement scripts/validation/integrate_pilot_fingerprints.py and run it.

PROCEDURE:
1. Read all data/pilot_fingerprints/*_fingerprint_approved.md
2. Parse each markdown file (sections: Inventory, Axis States, v4.2 Auxiliary,
   Detected Policies, Expected Classification, Notes) into a row of CSV
   # seed_category_id 파싱 규칙 (v5.1 PATCH m-2):
   # - Inventory 섹션의 "seed_category_id:" 라인에서 값을 읽음
   # - 값이 없거나 "UNCERTAIN_*" 형식이면 그대로 보존 (1-20 정수 또는 UNCERTAIN_n)
   # - 이 컬럼이 누락된 approved.md 파일은 integration FAIL로 처리 (V09로 검증)
3. Write data/pilot_fingerprints/empirical_fingerprints_pilot.csv with the 43 columns
   from P31 template

VALIDATION CHECKS during integration:
V01  project_id uniqueness
V02  A0_state ∈ axis_dictionary[A0].states
V03  A1_state ... A10_state ∈ respective axis states
V04  modality_class ∈ {SMALL_MOLECULE, PEPTIDE, MAB, ADC, BISPECIFIC, CELL_THERAPY,
                      GENE_THERAPY, MRNA, VACCINE, OLIGO_ASO_SIRNA,
                      RADIOPHARMACEUTICAL, OTHER_CUSTOM, UNKNOWN}
V05  endpoint_data_type ∈ {10 values, UNKNOWN}
V06  expected_terminal_state ∈ {AUTO, REPAIR, QUARANTINE, UNSUPPORTED, INVALID, UNKNOWN}
V07  if expected_terminal_state == QUARANTINE, expected_q_code in Q01..Q19 (no Q15 standalone, no Q17)
V08  family_candidate ∈ F01..F29 ∪ F31..F34
V09  seed_category_id ∈ 1..20 (or "UNCERTAIN_*")
V10  UNKNOWN_count per row < (43 * 0.40) (60% rule)
V11  v4.2 conditional fields:
     if modality_class in {ADC,BISPECIFIC,CELL_THERAPY,GENE_THERAPY} → analyte_role NOT empty
     if endpoint_data_type=CELLULAR_KINETICS → "cellular_LLOQ" mentioned in known_policies or missing_policies
V12  Each of 20 seed_category_id covered by ≥1 fingerprint

REPORT (Markdown): reports/pilot_fingerprint_integration_report.md
- total_fingerprints
- v4.2 modality distribution
- terminal_state distribution
- seed_category coverage (20/20 expected)
- UNKNOWN rate per axis
- validation_errors

OUTPUT: 2 files. Run script after writing.
EXIT NONZERO if any validator fails.
```

---

### P34 — Golden Dataset Registry 1차 (자동)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P33 PASS
🔹 **첨부 파일:** `empirical_fingerprints_pilot.csv`
🔹 **산출물:**
  - `data/golden_datasets/golden_dataset_registry_draft.csv`
  - `reports/golden_registry_initial_report.md`
🔹 **다음 액션:** P35 진행

```
ROLE: Coding agent.

INPUT: data/pilot_fingerprints/empirical_fingerprints_pilot.csv

TASK: Create golden_dataset_registry_draft.csv from rows where golden_dataset_available=YES.

COLUMNS:
golden_id  (G001, G002, ...)
project_id
family_id
seed_category_id
raw_input_path
reference_output_path
expected_terminal_state
expected_action_label
expected_q_code (if QUARANTINE)
modality_class
endpoint_data_type
nonmem_required_cols_present (auto-check by reading reference_output)
validation_status  (initial: "pending_human_h3_approval")
priority  (HIGH if v4.2-new modality, MEDIUM if v4.1-edge, LOW otherwise)

REPORT contents:
- total_golden_candidates
- coverage by family
- coverage by seed_category
- HIGH-priority count (v4.2-new modalities require golden)
- MISSING families: which F-codes have 0 golden candidates
- MISSING seed_categories: which 1-20 have 0 golden candidates

GATE for Phase 5 freeze:
"At least 3 golden datasets total, AND at least 1 golden for each of these critical:
F01, F09 or F22 (DDI), F12 (pediatric), F26 (CAR-T) or F24 (ADC) [v4.2 representative]"

OUTPUT: 2 files.
```

---

### P35 — Empirical Gap Analysis

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P34 완료
🔹 **첨부 파일:** P33 fingerprints CSV, Phase 1 YAMLs
🔹 **산출물:**
  - `reports/empirical_gap_analysis.md`
  - `reports/universe_patch_candidates.csv`
🔹 **다음 액션:** P36 진행

```
ROLE: PMX Grandmaster.

INPUT (attached):
  data/pilot_fingerprints/empirical_fingerprints_pilot.csv
  config/axis_dictionary.yaml
  config/family_assignment_rules.yaml

TASK: Find gaps where Frozen Universe v4.2 fails to capture an actual fingerprint.

FOR EACH FINGERPRINT, check:
1. Can A0..A10 states from this fingerprint be reproduced by current axis_dictionary?
   (i.e., is there a state_code that matches the observed pattern?)
2. Does the family_candidate match a defined F-code?
3. Are required policies covered by AIC template fields?
4. Is the expected q_code coverable by current Q-codes (Q01..Q19, no Q15, no Q17)?

GAP CLASSIFICATION:
UNIVERSE_PATCH_NEEDED  — Code path differs, current universe cannot represent
FAMILY_PATCH_NEEDED    — F-code missing for this study type
FALSE_GAP              — Already representable, fingerprint coding error (route to H2 rework)
INTENTIONAL_EXCLUSION  — Belongs to F31-F34 (out-of-scope)
AIC_INSUFFICIENT       — Need more AIC template fields

universe_patch_candidates.csv columns:
project_id, axis, observed_issue, why_fails_or_not,
gap_type, proposed_patch, severity, defer_to_v1_1

GUIDANCE:
- If gap is in v4.2 territory (modality, dyad, cellular), most should already be covered.
  If still missing, propose specific axis state addition.
- If gap is exotic (e.g., new endpoint type, new study design), defer to v1.1.

OUTPUT: 2 files.
```

---

### P36 — Seed Pack 20-카테고리 커버리지 검증 (v5.1 NEW)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P35 완료
🔹 **첨부 파일:** fingerprints CSV, seed pack md
🔹 **산출물:** `reports/seed_pack_coverage_report.md`
🔹 **다음 액션:** P37 진행

> **이 단계는 v5.1 신규.** Universe freeze 전 강제 게이트.

```
ROLE: Coding agent.

INPUT:
  data/pilot_fingerprints/empirical_fingerprints_pilot.csv
  reports/pilot_edge_case_seed_pack_v5_1.md

TASK: Verify all 20 seed categories are covered.

PROCEDURE:
1. For each seed_category_id in 1..20:
   - Count fingerprints with that ID
   - Check expected_terminal_state distribution
   - Check expected_q_code distribution if QUARANTINE
2. Output coverage matrix:
   | category_id | description | n_fingerprints | terminal_distribution | golden_present | status |
3. If any category has n=0, mark status=MISSING and emit recommendation:
   - Add synthetic fingerprint OR defer to v1.1 register

REPORT structure:
# Seed Pack Coverage v5.1
| Category | Family | n | Terminals | Golden | Status |
|---|---|---|---|---|---|
| 1. Standard SDTM popPK | F01 | 3 | AUTO=2 REPAIR=1 | YES | ✅ COVERED |
| 16. CAR-T cellular kinetics | F26 | 1 | REPAIR=1 | NO | ⚠️ COVERED_NO_GOLDEN |
| 19. Pregnancy PK | F28 | 0 | - | - | ❌ MISSING |
...

GATE OUTPUT:
- "PASS" if all 20 covered (golden optional but recommended)
- "FAIL_MISSING" if any 0-coverage
- "CONDITIONAL_DEFER" if user explicitly opts to defer to v1.1

If FAIL_MISSING, output explicit instruction:
"Cannot proceed to Phase 5 universe freeze. Either add fingerprints OR
register missing categories in change_control/v1.1_candidate_register.csv with
justification."

OUTPUT: Markdown.
EXIT 1 if FAIL_MISSING (caller must respond).
```

---

### P37 — Universe Patch 후보 분석 (조건부)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P36 완료, universe_patch_candidates.csv에 entry 있음
🔹 **첨부 파일:** P35 patch candidates, Phase 1 YAMLs
🔹 **산출물:** `reports/universe_patch_decision_v5_1.md`
🔹 **다음 액션:** patch가 필요하면 v1.1 register 등록 후 P38, 아니면 직접 P38

> **참고:** v5.1에서는 별도 LP Panel(이전 P31-P33 universe_patch_approval)을 제거했습니다. PATCH-4에 따라 LP Panel 13→7개 압축의 일환. universe patch는 단순 R-LLM 판정 + change_control 기록으로 처리.

```
ROLE: PMX Grandmaster.

INPUT (attached):
  reports/universe_patch_candidates.csv
  config/axis_dictionary.yaml

DECISION RULE per candidate:
- If gap_type=FALSE_GAP → route to H2 rework, no universe change
- If gap_type=INTENTIONAL_EXCLUSION → mark as F31-F34, no change
- If gap_type=UNIVERSE_PATCH_NEEDED:
  - If v1.0 freeze blocking impact → propose immediate axis_dictionary patch
  - Else → register in change_control/v1.1_candidate_register.csv
- If gap_type=FAMILY_PATCH_NEEDED:
  - If covers a v4.2 family already (F24-F29) → likely FALSE_GAP, recheck
  - Else → register in v1.1
- If gap_type=AIC_INSUFFICIENT:
  - If a single field addition unblocks → propose AIC template patch
  - Else → register in v1.1

OUTPUT (Markdown):
# Universe Patch Decision v5.1
## Immediate patches (block freeze if not applied)
- patch_id, target_file, change_summary
## Deferred to v1.1 (register entries)
- candidate_id, justification
## False gaps (return to H2)
- project_id, recheck_axis

If "Immediate patches" is non-empty, list exact YAML edits needed.
```

---

### P38 — v1.1 Register 갱신 (자동) + 즉시 patch 적용 (있는 경우)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P37 완료
🔹 **첨부 파일:** P37 decision
🔹 **산출물:**
  - `change_control/v1.1_candidate_register.csv` (신규 또는 갱신)
  - 즉시 patch 있으면 수정된 config/*.yaml + validate_config.py 재실행
🔹 **다음 액션:** error_count=0 확인 후 P39

```
ROLE: Coding agent.

INPUT: reports/universe_patch_decision_v5_1.md

TASKS:
1. If "Deferred to v1.1" entries exist:
   - Append to change_control/v1.1_candidate_register.csv
   - Columns: candidate_id, source_p_number, issue_type, affected_axis,
              affected_label, affected_executor, required_patch,
              required_rerun_prompts, status, registered_date

2. If "Immediate patches" exist:
   - Apply YAML edits to config/*.yaml (per P37 spec)
   - Run python scripts/config_validation/validate_config.py --config-dir config
   - If error_count != 0, ROLLBACK and emit "ESCALATE: patch caused validation failure"
   - If error_count = 0, append to CHANGELOG.md as patch log

3. If "False gaps" exist:
   - Append to reports/human_review/h2_rework_queue.md
   - Note: requires re-running H2 for affected project_id

OUTPUT: Updated files. Confirm validate_config error_count=0 after any patches.
```

---

### P39 — Phase 3 Completion Declaration

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **진입 조건:** P38 완료
🔹 **첨부 파일:** P33 report, P34 registry, P36 seed coverage, P38 register update
🔹 **산출물:** `reports/phase3_completion_declaration.md`
🔹 **다음 액션:** CHECK-3

```
ROLE: Documentation writer.

CHECKLIST:
[ ] H1 deidentification signed
[ ] H2 fingerprint approval signed (all _approved.md exist)
[ ] empirical_fingerprints_pilot.csv generated, validation PASS
[ ] golden_dataset_registry_draft.csv has ≥3 candidates
[ ] golden has ≥1 each for: F01, F09 or F22, F12, F24 or F26 (v4.2)
[ ] Seed pack 20/20 categories covered (or deferred to v1.1 with justification)
[ ] universe_patch_candidates.csv processed
[ ] v1.1_candidate_register.csv updated if needed
[ ] schema_validation error_count = 0 after any patches

OUTPUT: Markdown.
```

---

### P40 — Seed Pack 미충족 처리 (조건부)

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **진입 조건:** P36에서 일부 카테고리가 0-coverage였던 경우만
🔹 **산출물:** `reports/seed_pack_deferral_log.md`
🔹 **다음 액션:** CHECK-3

```
ROLE: Documentation writer.

INPUT: reports/seed_pack_coverage_report.md

If any category has status=MISSING or DEFERRED:

OUTPUT (markdown):
# Seed Pack Deferral Log

For each missing category:
- category_id, family_id, description
- reason_for_deferral (no real data, no synthetic, low priority)
- registered_in_v1_1: YES/NO
- impact_on_coverage_claim: "Pilot-bound coverage claim must explicitly note
  category {N} ({description}) is not represented and is deferred to v1.1."
- target_resolution_version: v1.1 or later

Emit corresponding entries in change_control/v1.1_candidate_register.csv.
```

---

### 🐍 CHECK-3 (Phase 3 검증)

```python
# check_phase3.py
# Phase 3 (P29-P40) 완료 검증
import os, sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas 없음. pip install pandas")
    sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("❌ pmx_universe_v5_1 폴더 없음"); sys.exit(1)

print("=" * 60)
print("CHECK-3: Phase 3 (Pilot 데이터 + H1, H2) 완료 검증")
print("=" * 60)

failures = []

# 1. 핵심 파일
KEY = [
    "config/deidentification_checklist_v5_1.md",
    "reports/pilot_sampling_plan_v5_1.md",
    "data/pilot_fingerprints/fingerprint_template.csv",
    "data/pilot_fingerprints/pilot_file_inventory.csv",
    "data/pilot_fingerprints/empirical_fingerprints_pilot.csv",
    "data/golden_datasets/golden_dataset_registry_draft.csv",
    "reports/fingerprint_coding_guide_v5_1.md",
    "reports/pilot_fingerprint_integration_report.md",
    "reports/empirical_gap_analysis.md",
    "reports/seed_pack_coverage_report.md",
    "reports/phase3_completion_declaration.md",
    "reports/human_review/h2_fingerprint_approval_log.md",
]
print("\n[필수 파일]")
for f in KEY:
    if (BASE / f).is_file():
        print(f"  ✅ {f.split('/')[-1]}")
    else:
        print(f"  ❌ {f}")
        failures.append(f"파일 없음: {f}")

# 2. H1 비식별화 서명
print("\n[H1 비식별화 서명]")
deid = BASE / "config/deidentification_checklist_v5_1.md"
if deid.is_file():
    txt = deid.read_text(encoding="utf-8", errors="ignore")
    if "checked_by" in txt.lower() and "approved" in txt.lower():
        print("  ✅ checked_by + APPROVED 서명")
    else:
        print("  ⚠️  서명 미확인")
        failures.append("H1 서명")

# 3. raw_examples 파일 수
print("\n[raw_examples 파일 수]")
raw = BASE / "data/raw_examples"
if raw.is_dir():
    cnt = sum(1 for p in raw.rglob("*") if p.is_file() and not p.name.startswith("."))
    print(f"  파일 수: {cnt}")
    if cnt >= 20:
        print("  ✅ 20개 이상 (seed pack 충족 가능)")
    elif cnt >= 10:
        print("  ⚠️  10~19개 — 일부 seed 카테고리 deferred 가능")
    else:
        print("  ❌ 10개 미만")
        failures.append(f"raw 파일 수 {cnt}/10")

# 4. fingerprint CSV 검사
print("\n[Fingerprint CSV]")
fp = BASE / "data/pilot_fingerprints/empirical_fingerprints_pilot.csv"
if fp.is_file():
    df = pd.read_csv(fp)
    print(f"  총 fingerprint: {len(df)}")
    # v4.2 필수 컬럼
    for col in ["modality_class", "endpoint_data_type", "analyte_role", "seed_category_id"]:
        if col in df.columns:
            print(f"  ✅ 컬럼 {col}")
        else:
            print(f"  ❌ 컬럼 {col} 누락")
            failures.append(f"v4.2 컬럼 {col}")

    # UNKNOWN 비율
    if len(df) > 0:
        total_cells = df.shape[0] * df.shape[1]
        unk = (df.astype(str).map(lambda x: x.upper().strip() == "UNKNOWN")).sum().sum()
        rate = unk / total_cells if total_cells else 0
        print(f"  UNKNOWN 비율: {rate:.1%}")
        if rate < 0.40:
            print("  ✅ <40%")
        else:
            print("  ❌ ≥40%")
            failures.append(f"UNKNOWN {rate:.0%}")

    # Q15 단독 / Q17 검사
    if "expected_q_code" in df.columns:
        q_series = df["expected_q_code"].astype(str).str.strip()
        q15_solo = (q_series == "Q15").sum()
        q17 = (q_series == "Q17").sum()
        if q15_solo == 0:
            print("  ✅ Q15 단독 0건")
        else:
            print(f"  ❌ Q15 단독 {q15_solo}건")
            failures.append(f"Q15 단독")
        if q17 == 0:
            print("  ✅ Q17 0건")
        else:
            print(f"  ❌ Q17 {q17}건")
            failures.append(f"Q17 사용")

    # Seed coverage
    # [PATCH-B1 — v5.1] 20/20 강제 정책 반영
    # 원칙: "Universe freeze 전 20개 카테고리 모두 커버 필수"
    # 예외: 미충족 카테고리에 대해 seed_pack_deferral_log.md + v1.1_register 등록 시 조건부 허용
    if "seed_category_id" in df.columns:
        covered = df["seed_category_id"].dropna().astype(str).unique()
        n = len([x for x in covered if x not in ("", "nan")])
        print(f"  Seed 카테고리 커버: {n}/20")
        deferral_log = BASE / "reports/seed_pack_deferral_log.md"
        v11_register = BASE / "change_control/v1.1_candidate_register.csv"
        if n == 20:
            print("  ✅ 20/20 전체 충족")
        elif n >= 18 and deferral_log.is_file() and v11_register.is_file():
            print(f"  ⚠️  {n}/20 — 미충족 {20-n}개: deferral log + v1.1 register 확인됨 (조건부 허용)")
            print("       Phase 5 freeze 전 deferral log가 명시적으로 작성되어야 합니다.")
        elif n >= 18 and (not deferral_log.is_file() or not v11_register.is_file()):
            print(f"  ❌ {n}/20 — deferral log 또는 v1.1_register 없음 → formal deferral 미완료")
            print("       P40 실행 후 seed_pack_deferral_log.md + v1.1_candidate_register.csv 작성 필요")
            failures.append(f"seed {n}/20 without formal deferral")
        else:
            print(f"  ❌ {n}/20 — 12개 미만 또는 deferral 처리 없음")
            failures.append(f"seed coverage {n}/20")

# 5. Golden registry
print("\n[Golden Registry]")
gr = BASE / "data/golden_datasets/golden_dataset_registry_draft.csv"
if gr.is_file():
    df = pd.read_csv(gr)
    print(f"  golden 후보 수: {len(df)}")
    if len(df) >= 3:
        print("  ✅ ≥3")
    else:
        print("  ❌ <3")
        failures.append(f"golden {len(df)}/3")

# 6. H2 승인 로그
print("\n[H2 승인 로그]")
h2 = BASE / "reports/human_review/h2_fingerprint_approval_log.md"
if h2.is_file():
    txt = h2.read_text(encoding="utf-8", errors="ignore")
    if "APPROVED" in txt.upper():
        print("  ✅ APPROVED 기록 있음")
    else:
        print("  ⚠️  APPROVED 기록 미확인")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 3 완료")
    print("→ 다음: Phase 4 (P41) — Repair Executor 구현")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## ⚙️ Phase 4: Repair Executor 구현 + LP Panel CP3 (P41~P52)

### 📌 이 단계 목적

실제로 데이터를 NONMEM-ready로 변환하는 **Python 코드(`repair_executor.py`)**를 만듭니다.
v4.2 신규 함수 7개를 포함해 총 26개 이상의 변환 함수를 구현합니다.
**v5.1 강화:** `hypothesis` 라이브러리로 property-based testing을 추가해 LLM이 만든 코드의 엣지 케이스를 자동 탐색합니다.

### 진입 조건
- [x] CHECK-3 PASS

---

### P41 — Repair Rule Dictionary v4.2

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** CHECK-3 PASS
🔹 **첨부 파일:** P13 action_function_library, P10 q-codes, P15 boundary cases
🔹 **산출물:** `config/repair_rule_dictionary.yaml`
🔹 **다음 액션:** P42

```
ROLE: PMX Grandmaster + dataset wrangling engineer.

INPUT (attached):
  config/action_function_library.yaml
  config/quarantine_reason_codes.yaml
  reports/repair_quarantine_boundary_cases_v4_2.csv

TASK: Produce config/repair_rule_dictionary.yaml with ≥26 repair rules.

EACH RULE STRUCTURE:
- repair_rule_id: RR020
  function_name: canonicalize_cellular_blq
  v4_2_new: true
  input_condition: "endpoint_data_type=CELLULAR_KINETICS, BLQ events present"
  required_columns: [ID, TIME, DV, MDV, CMT]
  required_policy: cellular_LLOQ_derivation_policy
  algorithm: |
    1. Read cellular_LLOQ from policy (Poisson-derived value)
    2. For each row with DV < cellular_LLOQ AND DV is observation (EVID=0):
       - Set MDV=1 if policy says exclude
       - Set DV to cellular_LLOQ/2 if policy says M3 (cellular subtype)
    3. Append audit_log entry
  output_columns: [DV, MDV, BLQ_FLAG]
  audit_log_fields: [rule_id, n_blq_rows, cellular_lloq_value, policy_used, timestamp]
  failure_mode: "cellular_LLOQ_derivation_policy missing or LLOQ value cannot be parsed"
  fallback_terminal: QUARANTINE
  fallback_q_code: Q01  # cellular subtype, with note in audit_log
  example_before: {ID:1, TIME:24, DV:0.5, MDV:0}
  example_after:  {ID:1, TIME:24, DV:0, MDV:1, BLQ_FLAG:"M1"}

REQUIRED RULES (must include all):

EXISTING (v4.1 + earlier) — 19 rules:
RR001 standardize_column_names
RR002 convert_units
RR003 map_subject_id
RR004 derive_time_actual
RR005 derive_time_nominal
RR006 derive_time_elapsed
RR007 derive_time_interval
RR008 reconstruct_dose_weight
RR009 reconstruct_dose_bsa
RR010 reconstruct_dose_titration
RR011 reconstruct_loading_maintenance
RR012 reconstruct_infusion_stop_restart
RR013 expand_addl_ii
RR014 resolve_addl_actual_conflict
RR015 canonicalize_blq                  # concentration BLQ
RR016 resolve_reanalysis_final
RR017 assign_cmt_ddi_victim_only
RR018 assign_cmt_ddi_victim_perpetrator
RR019 attach_covariate_baseline / time_varying / external

v4.2 NEW (must add) — 7 rules:
RR020 canonicalize_cellular_blq
RR021 adjudicate_immunogenicity_positivity
RR022 attach_dyad_linkage
RR023 derive_time_postpartum_anchor
RR024 assign_milk_matrix_lloq
RR025 assign_cmt_with_analyte_role
RR026 attach_covariate_product_level

VALIDATION CONSTRAINTS per rule:
- fallback_q_code MUST exist in quarantine_reason_codes.yaml
- fallback_q_code MUST NOT be Q15 standalone or Q17
- required_policy MUST be a field name from analysis_intent_contract_template.yaml
- algorithm MUST produce deterministic output given inputs + policy

# [PATCH m-4 downstream — v5.1 CRITICAL] Q15 sub-code 사용 기준
# repair_rule_dictionary.yaml에서 fallback_q_code를 Q15A/B/C/D로 지정할 때:
#
# Q15A 사용: "upstream adjudication decision 미제출"
#   - A5=BIOANALYTICAL-FINAL-FLAG-MISSING (bioanalytical 최종 판정이 아직 도달 안 한 상태)
#   - A7=PRODUCT-LEVEL-COVARIATE + product_attribute_absent_from_data_package
#   - A10=SEMI-STRUCTURED + source_parser_subtype=unknown
#
# Q15B 사용: "legacy flag/field 정의 없어 해석 불가"
#   - 레거시 NONMEM-like 데이터의 정의 없는 특수 플래그/컬럼
#
# Q15C 사용: "real-world adherence/administration history 불명확"
#   - TDM/RWD 투여 이력 reconciliation 불가 케이스
#
# Q15D 사용: "assay reanalysis/final-result adjudication missing"
#   - A9=REANALYSIS-FINAL-MISSING (재분석 결과 중 최종 선택 기준 부재)
#   - 복수 assay 결과가 존재하나 우선순위 rule이 없는 경우
#
# ❌ WRONG: BIOANALYTICAL-FINAL-FLAG-MISSING → Q15D  (구버전 잘못된 매핑)
# ✅ RIGHT:  BIOANALYTICAL-FINAL-FLAG-MISSING → Q15A  ([PATCH m-4] 수정값)

OUTPUT: YAML only.
```

---

### P42 — repair_executor.py 구현 (v4.2 통합)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE — Claude Sonnet 계열 최신 또는 Claude Code)
🔹 **진입 조건:** P41 완료
🔹 **첨부 파일:** P41 dictionary, P13 function_library
🔹 **산출물:** `scripts/repair_executor/repair_executor.py`
🔹 **다음 액션:** P43

```
ROLE: Coding agent.

INPUT (attached):
  config/repair_rule_dictionary.yaml
  config/action_function_library.yaml
  config/analysis_intent_contract_template.yaml
  config/quarantine_reason_codes.yaml

TASK: Implement scripts/repair_executor/repair_executor.py

REQUIREMENTS:
- Python 3.11, fully type-hinted, complete docstrings
- pandas-based, NEVER mutate input DataFrames in place (always copy)
- All 26 rules from repair_rule_dictionary.yaml implemented as functions

DATA CLASSES:

@dataclass
class RepairResult:
    df: pd.DataFrame
    terminal_state: str = "REPAIR"
    q_code: Optional[str] = None  # Always None for REPAIR
    audit_log: dict = field(default_factory=dict)
    applied_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    success: bool = True

@dataclass
class QuarantineResult:
    q_code: str
    reason: str
    audit_log: dict = field(default_factory=dict)
    success: bool = False
    terminal_state: str = "QUARANTINE"

    def __post_init__(self):
        if self.q_code == "Q15":
            raise ValueError("Q15 standalone forbidden — use Q15A/B/C/D")
        if self.q_code == "Q17":
            raise ValueError("Q17 forbidden — absorbed into Q13")

REQUIRED FUNCTIONS (signatures, complete bodies):

# v4.1 + earlier
def repair_column_synonym(df: pd.DataFrame, synonym_map: dict) -> RepairResult: ...
def repair_unit_conversion(df: pd.DataFrame, unit_dict: dict) -> RepairResult | QuarantineResult: ...
def repair_subject_id_mapping(df: pd.DataFrame, id_policy: dict) -> RepairResult: ...
def repair_time_derivation_actual(df: pd.DataFrame, anchor_col: str) -> RepairResult: ...
def repair_time_derivation_nominal(df: pd.DataFrame, schedule: dict) -> RepairResult: ...
def repair_time_elapsed(df: pd.DataFrame, anchor: str) -> RepairResult | QuarantineResult: ...
def repair_time_interval(df: pd.DataFrame) -> RepairResult: ...
def repair_dose_reconstruction_weight(df: pd.DataFrame, dose_per_kg: float) -> RepairResult | QuarantineResult: ...
def repair_dose_reconstruction_bsa(df: pd.DataFrame, dose_per_m2: float) -> RepairResult | QuarantineResult: ...
def reconstruct_dose_titration(df: pd.DataFrame, schedule: dict, policy: dict) -> RepairResult | QuarantineResult: ...
def reconstruct_loading_maintenance(df: pd.DataFrame, loading: dict, maintenance: dict, policy: dict) -> RepairResult | QuarantineResult: ...
def reconstruct_infusion_stop_restart(df: pd.DataFrame, infusion_policy: dict) -> RepairResult | QuarantineResult: ...
def expand_addl_ii(df: pd.DataFrame) -> RepairResult: ...
def resolve_addl_actual_conflict(df: pd.DataFrame, conflict_policy: dict) -> RepairResult | QuarantineResult: ...
def repair_blq_canonicalization(df: pd.DataFrame, blq_policy: str) -> RepairResult | QuarantineResult: ...
def resolve_reanalysis_final(df: pd.DataFrame, final_flag_col: str) -> RepairResult | QuarantineResult: ...
def assign_cmt_ddi_victim_only(df: pd.DataFrame, victim_cmt: int) -> RepairResult: ...
def assign_cmt_ddi_victim_perpetrator(df: pd.DataFrame, victim_cmt: int, perp_cmt: int, policy: dict) -> RepairResult | QuarantineResult: ...
def repair_covariate_attach(df: pd.DataFrame, cov_policy: dict, mode: str) -> RepairResult | QuarantineResult: ...

# v4.2 NEW
def canonicalize_cellular_blq(df: pd.DataFrame, cellular_lloq_policy: dict) -> RepairResult | QuarantineResult: ...
def adjudicate_immunogenicity_positivity(df: pd.DataFrame, positivity_rule: dict) -> RepairResult | QuarantineResult: ...
def attach_dyad_linkage(df: pd.DataFrame, dyad_key_policy: dict) -> RepairResult | QuarantineResult: ...
def derive_time_postpartum_anchor(df: pd.DataFrame, delivery_anchor_policy: dict) -> RepairResult | QuarantineResult: ...
def assign_milk_matrix_lloq(df: pd.DataFrame, milk_lloq_policy: dict) -> RepairResult | QuarantineResult: ...
def assign_cmt_with_analyte_role(df: pd.DataFrame, role_cmt_map: dict) -> RepairResult | QuarantineResult: ...
def attach_covariate_product_level(df: pd.DataFrame, lot_subject_map: dict, attribute_cols: list) -> RepairResult | QuarantineResult: ...

CONTRACT BEHAVIOR:
1. Every function: receive df + policy → return RepairResult OR QuarantineResult
2. If required policy is None or invalid → return QuarantineResult with correct q_code
3. audit_log MUST contain: rule_id, function_name, row_count_before, row_count_after,
   policy_used (deep copy), timestamp_iso, changes_summary
4. Q15 standalone return → MUST raise ValueError (caught by __post_init__)
5. Q17 return → MUST raise ValueError

ORCHESTRATOR:
def run_repair_pipeline(df: pd.DataFrame, action_sequence: List[Tuple[str, dict]],
                        aic: dict) -> RepairResult | QuarantineResult:
    """
    Executes ordered list of (function_name, parameter_policy) tuples.
    Returns first QuarantineResult encountered, or final RepairResult.
    Validates AIC against required_policy mapping for each function.
    """

OUTPUT: Single Python file. Must import successfully:
  python -c "from scripts.repair_executor.repair_executor import RepairResult, QuarantineResult"
```

---

### P43 — Unit Tests

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P42 완료
🔹 **첨부 파일:** P42 repair_executor.py
🔹 **산출물:** `tests/test_repair_executor_unit.py`
🔹 **다음 액션:** P44 진행 (pytest는 P47에서 통합 실행)

```
ROLE: Coding agent.

TASK: Implement tests/test_repair_executor_unit.py

REQUIREMENTS:
- Use pytest, fixtures from tests/conftest.py
- Each of 26 functions: ≥3 test cases
  Case 1: Normal input + valid policy → RepairResult success=True, audit_log populated
  Case 2: Policy=None or invalid → QuarantineResult with correct q_code
  Case 3: Edge case (empty df, NaN, single row, duplicate)

REQUIRED v4.2 TESTS (must include):

def test_canonicalize_cellular_blq_normal():
    df = pd.DataFrame({"ID":[1,1], "TIME":[0,24], "DV":[100, 0.05], "EVID":[0,0], "MDV":[0,0]})
    policy = {"cellular_lloq": 0.1, "method": "M1"}
    res = canonicalize_cellular_blq(df, policy)
    assert isinstance(res, RepairResult)
    assert res.success
    assert "rule_id" in res.audit_log

def test_canonicalize_cellular_blq_no_policy():
    df = ...
    res = canonicalize_cellular_blq(df, None)
    assert isinstance(res, QuarantineResult)
    assert res.q_code == "Q01"
    assert "cellular" in res.audit_log.get("note", "").lower()

def test_adjudicate_immunogenicity_no_rule():
    res = adjudicate_immunogenicity_positivity(df, None)
    assert res.q_code == "Q19"

def test_attach_dyad_linkage_no_key():
    res = attach_dyad_linkage(df, None)
    assert res.q_code == "Q18"

def test_q15_standalone_forbidden():
    with pytest.raises(ValueError, match="Q15 standalone forbidden"):
        QuarantineResult(q_code="Q15", reason="test", audit_log={})

def test_q17_forbidden():
    with pytest.raises(ValueError, match="Q17 forbidden"):
        QuarantineResult(q_code="Q17", reason="test", audit_log={})

OUTPUT: Single test file. Target ≥80 test cases total.
```

---

### P44 — Contract Tests

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P43 완료
🔹 **산출물:** `tests/test_repair_executor_contract.py`
🔹 **다음 액션:** P45

```
ROLE: Coding agent.

TASK: Implement tests/test_repair_executor_contract.py

CONTRACTS to verify (system-level invariants, not function-specific):

C01  Every QuarantineResult has q_code in {Q01..Q14, Q15A,Q15B,Q15C,Q15D, Q16, Q18, Q19}
C02  No function ever returns q_code="Q15" (standalone)
C03  No function ever returns q_code="Q17"
C04  Every RepairResult has non-empty audit_log
C05  Every RepairResult.df is not the same object as input df (copy-on-write)
C06  applied_rules in RepairResult is non-empty when at least one transformation occurred
C07  run_repair_pipeline: if any step returns QuarantineResult, pipeline halts
C08  run_repair_pipeline: if AIC missing required_policy for a function, that function
     returns QuarantineResult (not raises Exception)
C09  v4.2 specific:
     CELLULAR_KINETICS without cellular_lloq_policy → Q01
     IMMUNOGENICITY without positivity_rule → Q19
     MATERNAL_INFANT_PK without dyad_key → Q18
     MATERNAL_INFANT_PK without delivery_anchor → Q12
     MILK_PK without matrix_lloq → Q01
     ADC/BISPECIFIC/CELL/GENE multi-analyte without analyte_role → Q16

C10  audit_log timestamps are ISO 8601 strings
C11  All output DataFrames retain original ID column values (no silent reindexing)

Use parametrize where appropriate to cover multiple functions.

OUTPUT: Test file with ≥30 contract tests.
```

---

### P45 — Synthetic Fixtures (≥20 fixtures including v4.2)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P44 완료
🔹 **산출물:**
  - `tests/fixtures/*.csv` (20개 이상)
  - `tests/fixtures/*_expected.yaml` (각 fixture에 대응)
🔹 **다음 액션:** P46

```
ROLE: Coding agent.

TASK: Generate synthetic fixture datasets for testing repair functions.

EACH FIXTURE: One CSV + one expected YAML

REQUIRED FIXTURES (20+):

ROUTINE (5):
fixture_blq_policy_present.csv
fixture_blq_policy_missing.csv
fixture_time_actual.csv
fixture_time_policy_missing.csv
fixture_weight_based_dose.csv

V4.1 EDGE (8):
fixture_addl_actual_conflict.csv
fixture_addl_actual_conflict_policy_present.csv
fixture_reanalysis_final_flag_present.csv
fixture_reanalysis_final_flag_missing.csv
fixture_infusion_stop_restart.csv
fixture_loading_maintenance.csv
fixture_titration_adaptive.csv
fixture_ddi_victim_only.csv
fixture_ddi_victim_perpetrator.csv

V4.2 NEW (7):
fixture_cellular_kinetics_lloq_present.csv     # CAR-T qPCR
fixture_cellular_kinetics_lloq_missing.csv     # → Q01
fixture_immunogenicity_with_positivity_rule.csv
fixture_immunogenicity_no_positivity_rule.csv  # → Q19
fixture_maternal_infant_dyad.csv               # full dyad with linkage
fixture_maternal_infant_no_dyad_key.csv        # → Q18
fixture_milk_pk_matrix_lloq.csv

EXPECTED YAML structure (per fixture):
# tests/fixtures/fixture_xxx_expected.yaml
fixture_name: fixture_xxx
input_csv: fixture_xxx.csv
input_aic:
  blq_handling_policy: M1
  ...
expected_terminal: REPAIR  # or QUARANTINE
expected_q_code: null  # or Q01/Q19/etc
expected_action_sequence:
  - parse_source
  - canonicalize_cellular_blq
  - export_nonmem_ready
expected_row_count_after: N  # if known
expected_audit_keys: [rule_id, cellular_lloq_value, ...]

CSVs should be small (5-20 rows), realistic, and self-contained.

OUTPUT: All fixtures + expected YAMLs.
```

---

### P46 — Property-Based Tests (hypothesis library) — v5.1 NEW

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P45 완료
🔹 **산출물:** `tests/test_repair_executor_property.py`
🔹 **다음 액션:** P47

> **이 단계는 v5.1 신규 (PATCH-9).** hypothesis로 LLM이 미처 못 본 엣지 케이스를 자동 탐색합니다.

```
ROLE: Coding agent.

TASK: Implement tests/test_repair_executor_property.py using hypothesis library.

PROPERTIES TO TEST (each as @given decorator):

P01  for any valid AIC + valid input df:
     run_repair_pipeline returns either RepairResult or QuarantineResult
     (never raises uncaught exception, never returns None)

P02  for any AIC missing a required_policy:
     run_repair_pipeline returns QuarantineResult with correct q_code

P03  for any df with rows: idempotency property:
     running same pipeline twice on same input → same output

P04  audit_log always contains keys: {rule_id, function_name, timestamp_iso}

P05  for any QuarantineResult: q_code matches regex
     ^(Q0[1-9]|Q1[0-46]|Q15[ABCD]|Q1[89])$  # excludes Q15, Q17

P06  for any RepairResult: q_code is None

P07  v4.2: if endpoint_data_type=CELLULAR_KINETICS and cellular_lloq_policy is None:
     pipeline returns QuarantineResult(q_code="Q01")

P08  for any df where input is unchanged (df.equals comparison):
     output df is a different object but may equal input if no rules applied

USE hypothesis strategies:
- pandas DataFrames with bounded size (1-100 rows)
- AIC dicts built from possible field combinations
- modality_class strategies covering all 11 values
- endpoint_data_type strategies covering all 10 values

EXAMPLE:
from hypothesis import given, strategies as st
from hypothesis.extra.pandas import data_frames, column

@given(
    df=data_frames(
        columns=[
            column("ID", elements=st.integers(1, 100)),
            column("TIME", elements=st.floats(0, 168)),
            column("DV", elements=st.floats(0, 1000), unique=False),
            column("EVID", elements=st.sampled_from([0, 1, 2])),
            column("MDV", elements=st.sampled_from([0, 1])),
        ],
        rows=st.tuples(...).filter(...)
    ),
    cellular_lloq_policy=st.one_of(st.none(), st.fixed_dictionaries({"cellular_lloq": st.floats(0.001, 1.0), "method": st.sampled_from(["M1","M3"])}))
)
def test_cellular_blq_property(df, cellular_lloq_policy):
    res = canonicalize_cellular_blq(df, cellular_lloq_policy)
    if cellular_lloq_policy is None:
        assert isinstance(res, QuarantineResult)
        assert res.q_code == "Q01"
    else:
        assert isinstance(res, (RepairResult, QuarantineResult))
        if isinstance(res, RepairResult):
            assert "rule_id" in res.audit_log

USE @settings(max_examples=50) to cap runtime. Mark tests with pytest.mark.slow if >5s.

OUTPUT: Test file. Target ≥10 properties.
```

---

### P47 — 전체 pytest 실행

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P46 완료
🔹 **첨부 파일:** 모든 test/fixture 파일
🔹 **산출물:**
  - `reports/repair_executor_test_report.md` (pytest 결과 요약)
  - 코드 수정이 필요했다면 수정된 `repair_executor.py`
🔹 **다음 액션:** pytest 100% PASS 확인 → P48 (LP Panel CP3)

```
ROLE: Coding agent.

PROCEDURE:
1. Run: cd pmx_universe_v5_1 && python -m pytest tests/ -v --tb=short --cov=scripts/repair_executor
2. If failures occur:
   a. If test is wrong (incorrect expected value, fixture error) → fix test
   b. If repair_executor.py has bugs → fix executor
   c. If a property test (P46) reveals undefined behavior → write to
      reports/llm_proxy/repair_semantic_questions.md
3. Re-run until 100% PASS or only semantic questions remain (max 5 iterations)
4. Report coverage: target ≥85%

OUTPUT REPORT:
# Repair Executor Test Report (Phase 4)
- pytest summary: N passed, M failed
- coverage: X%
- semantic questions raised: list (if any)
- v4.2 specific test results: per function
- property-based test results: per property
# CP3 TRIGGER DECISION (v5.1 PATCH M-1 — 명시 필수):
# [ ] v4.2 신규 함수(RR020~RR026) 포함 여부: YES/NO
# [ ] semantic_questions.md 생성 여부: YES/NO
# → CP3 RUN: YES (둘 중 하나라도 YES) / SKIP: NO (둘 다 NO → P51 직행)

If semantic_questions exist OR v4.2 new functions present → trigger LP Panel CP3 (P48-P50).
If no semantic_questions AND all functions are RR001~RR019 range AND 100% PASS → skip to P51 (Lock).
```

---

### P48~P50 — LP Panel CP3: Repair Semantic Review (조건부)

> **조건부 실행:** P47이 semantic questions 없이 PASS면 P51로 직행. 있을 때만 P48-P50.
>
> ⚠️ **[PATCH M-1] CP3 명시적 트리거 규칙 (v5.1):**
>
> | 조건 | CP3 실행 여부 |
> |---|---|
> | P47 pytest 100% PASS + `repair_semantic_questions.md` 파일 없음 | **SKIP → P51 직행** |
> | P47에서 `repair_semantic_questions.md` 생성됨 (≥1 semantic question) | **필수 실행** |
> | **v4.2 신규 함수 (RR020~RR026) 중 하나라도 처음 도입된 경우** | **필수 실행** (semantic question 유무 무관) |
> | P46 property test에서 undefined behavior 발견 → `repair_semantic_questions.md` 자동 생성 | **필수 실행** |
>
> **판단 기준:** "기존 RR001~RR019만 사용한다면 semantic question 없이 SKIP 가능. RR020~RR026 (v4.2 신규) 중 하나라도 포함되면 CP3 필수." 이 규칙을 P47 output에 명시하여 사람이 Skip/Run을 명확히 판단하게 합니다.

#### P48 (LP-A) — Repair Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P47 semantic_questions, repair_rule_dictionary, action_sequence
🔹 **산출물:** `reports/llm_proxy/repair_semantic_review_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A) for Checkpoint CP3 (repair_semantic_review).

INPUT (attached):
  reports/llm_proxy/repair_semantic_questions.md
  config/repair_rule_dictionary.yaml
  config/action_function_library.yaml
  reports/repair_quarantine_boundary_cases_v4_2.csv

For each semantic question:
1. Is the proposed transformation deterministic given AIC + data?
2. Does AIC field cover the policy completely?
3. Is fallback q_code correct?
4. v4.2: Is cellular/immunogenicity/dyad/milk handling specifically right?
5. Does this require human escalation?

OUTPUT per LP-A template (P2 template).
File: reports/llm_proxy/repair_semantic_review_grandmaster.md
```

#### P49 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** P48 grandmaster, P47 semantic_questions
🔹 **산출물:** `reports/llm_proxy/repair_semantic_review_adversarial.md`

```
ROLE: Adversarial reviewer (LP-B) — DIFFERENT model family.

ATTACK AXES:
1. Functions claimed REPAIR but actually require analytical judgment
2. v4.2 cellular/immunogenicity policies inadequately scoped
3. dyad linkage edge cases (single mother → twins, single mother → multiple infants over time)
4. analyte_role partial specification (some analytes labeled, some not)
5. Q-code mismatch (e.g., cellular missing → Q01 vs Q15D vs new code)
6. Hidden state drift (function modifies df in unexpected columns)

OUTPUT per LP-B template.
```

#### P50 (LP-C) — Judge + 자동 적용

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션)
🔹 **첨부 파일:** P48 + P49
🔹 **산출물:**
  - `reports/llm_proxy/repair_semantic_review_judge.md`
  - `reports/llm_proxy/repair_semantic_review_decision.csv`
  - 자동 적용 시 수정된 repair_executor.py + repair_rule_dictionary.yaml
🔹 **다음 액션:** P47 pytest 재실행 PASS → P51

```
ROLE: Judge (LP-C).

ENFORCE Hard Rules from lp_panel_template.yaml.

If auto-apply condition met:
  Apply patches to repair_executor.py and/or repair_rule_dictionary.yaml.
  Re-run pytest to verify.
  Confirm 100% PASS.

If escalate_to_human=YES:
  Defer to H4 (false classification veto in Phase 10).
```

---

### P51 — Repair Executor Lock + Hash

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P47 (또는 P50) 완료, pytest 100% PASS
🔹 **첨부 파일:** repair_executor.py
🔹 **산출물:**
  - `release/v1.0/repair_executor_v1_0.sha256`
  - `release/v1.0/repair_executor_lock_v1_0.md`
🔹 **다음 액션:** P52

```
ROLE: Coding agent.

TASK:
1. Compute SHA256 of:
   - scripts/repair_executor/repair_executor.py
   - config/repair_rule_dictionary.yaml
   Save to release/v1.0/repair_executor_v1_0.sha256

2. Generate release/v1.0/repair_executor_lock_v1_0.md:
   - Lock declaration text
   - Functions implemented (list with v4_2_new flag)
   - pytest results summary
   - coverage %
   - hash values
   - "Locked at: {ISO timestamp}"
   - Modification policy: "Any change requires v1.1 candidate registration"

3. Update CHANGELOG.md with v0.5.0 entry: "Repair Executor v1.0 LOCKED"

OUTPUT: 2 files + updated CHANGELOG.
```

---

### P52 — Phase 4 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** P51 lock, P47 test report
🔹 **산출물:** `reports/phase4_completion_declaration.md`
🔹 **다음 액션:** CHECK-4

```
ROLE: Documentation writer.

CHECKLIST:
[ ] config/repair_rule_dictionary.yaml ≥26 rules
[ ] scripts/repair_executor/repair_executor.py implements all 26
[ ] tests/test_repair_executor_unit.py: ≥80 cases, all PASS
[ ] tests/test_repair_executor_contract.py: ≥30 cases, all PASS
[ ] tests/test_repair_executor_property.py: ≥10 properties, all PASS
[ ] tests/fixtures/: ≥20 CSV + expected YAML
[ ] coverage ≥85%
[ ] LP Panel CP3 (if triggered) resolved
[ ] release/v1.0/repair_executor_v1_0.sha256 generated
[ ] release/v1.0/repair_executor_lock_v1_0.md signed (auto-LLM)
[ ] CHANGELOG updated

OUTPUT: Markdown.
```

---

### 🐍 CHECK-4 (Phase 4 검증)

```python
# check_phase4.py
import os, sys, subprocess
from pathlib import Path

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("❌ pmx_universe_v5_1 폴더 없음"); sys.exit(1)

print("=" * 60)
print("CHECK-4: Phase 4 (Repair Executor) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "config/repair_rule_dictionary.yaml",
    "scripts/repair_executor/repair_executor.py",
    "tests/test_repair_executor_unit.py",
    "tests/test_repair_executor_contract.py",
    "tests/test_repair_executor_property.py",
    "release/v1.0/repair_executor_v1_0.sha256",
    "release/v1.0/repair_executor_lock_v1_0.md",
    "reports/repair_executor_test_report.md",
    "reports/phase4_completion_declaration.md",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file(): print(f"  ✅ {f.split('/')[-1]}")
    else: print(f"  ❌ {f}"); failures.append(f)

# v4.2 신규 함수 7개
print("\n[repair_executor.py v4.2 신규 함수 7개]")
ex = BASE / "scripts/repair_executor/repair_executor.py"
if ex.is_file():
    txt = ex.read_text(encoding="utf-8")
    v42_funcs = [
        "canonicalize_cellular_blq",
        "adjudicate_immunogenicity_positivity",
        "attach_dyad_linkage",
        "derive_time_postpartum_anchor",
        "assign_milk_matrix_lloq",
        "assign_cmt_with_analyte_role",
        "attach_covariate_product_level",
    ]
    for fn in v42_funcs:
        if f"def {fn}" in txt:
            print(f"  ✅ {fn}")
        else:
            print(f"  ❌ {fn}")
            failures.append(fn)

    # data class 검사
    for cls in ["class RepairResult", "class QuarantineResult"]:
        if cls in txt:
            print(f"  ✅ {cls}")
        else:
            print(f"  ❌ {cls}")
            failures.append(cls)

    # Q15 단독 / Q17 금지 강제
    if 'q_code="Q15"' in txt and "Q15A" not in txt[txt.find('q_code="Q15"'):txt.find('q_code="Q15"')+200]:
        # 단독 사용
        print("  ⚠️  Q15 사용 위치 점검 필요")
    if 'q_code="Q17"' in txt or "q_code='Q17'" in txt:
        print("  ❌ Q17 사용")
        failures.append("Q17 사용")
    else:
        print("  ✅ Q17 미사용")

# pytest 실행
if not failures:
    print("\n[pytest 전체 실행]")
    result = subprocess.run(
        ["python", "-m", "pytest", str(BASE / "tests"), "-v", "--tb=line", "-q",
         "--cov=" + str(BASE / "scripts/repair_executor"), "--cov-report=term-missing:skip-covered"],
        capture_output=True, text=True
    )
    out = result.stdout + result.stderr
    print("\n".join(out.splitlines()[-15:]))
    if result.returncode == 0:
        print("  ✅ pytest PASS")
    else:
        print("  ❌ pytest FAIL")
        failures.append("pytest")

# fixtures 수
fix = BASE / "tests/fixtures"
if fix.is_dir():
    csv_n = len([f for f in fix.iterdir() if f.suffix == ".csv"])
    yml_n = len([f for f in fix.iterdir() if f.suffix in (".yaml", ".yml")])
    print(f"\n[Fixtures: CSV={csv_n}, YAML={yml_n}]")
    if csv_n >= 20:
        print("  ✅ ≥20 CSV")
    else:
        print(f"  ❌ <20: {csv_n}")
        failures.append(f"fixtures {csv_n}/20")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 4 완료")
    print("→ 다음: Phase 5 (P53) — Scenario Generator + Universe Freeze")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## 🌐 Phase 5: Scenario Generator + Universe Freeze + LP Panel CP2 (P53~P65)

### 📌 이 단계 목적

A0~A10 모든 valid 조합을 생성해 **Scenario Universe v1.0**을 만들고 freeze합니다.
**v5.1 강화:** Pilot 20-카테고리가 universe에 모두 포함되었는지 강제 검증.
**LP Panel CP2** = universe attack + freeze approval (이전 두 LP Panel을 하나로 통합).

### 진입 조건
- [x] CHECK-4 PASS

---

### P53 — Scenario Generator 구현

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** CHECK-4 PASS
🔹 **첨부 파일:** Phase 1 모든 YAML
🔹 **산출물:**
  - `scripts/scenario_generator/generate_scenarios.py`
  - `data/scenario_universe/scenario_universe_raw.csv` (실행 결과)
  - `data/scenario_universe/scenario_universe_valid_candidate.csv`
  - `reports/invalid_scenario_log.csv`
🔹 **다음 액션:** P54

```
ROLE: Coding agent.

INPUT (attached):
  config/axis_dictionary.yaml
  config/dependency_constraints.yaml
  config/quarantine_reason_codes.yaml
  config/terminal_state_taxonomy.yaml

TASK: Implement scripts/scenario_generator/generate_scenarios.py

PROCEDURE:
1. Load axis_dictionary.yaml → states for A0..A10
2. Compute valid combinations (cartesian product), pruned by dependency_constraints
3. For each combination:
   - Apply rules in priority order
   - Determine terminal_state (AUTO/REPAIR/QUARANTINE/UNSUPPORTED/INVALID)
   - Determine q_code if QUARANTINE
   - scenario_id = SHA256(f"{A0}|{A1}|...|{A10}")[:12]
4. Handle auxiliary fields:
   - modality_class PROCESSING RULE (v5.1 명시):
     modality_class는 A0의 독립 축이 아닌 **auxiliary field**로 처리합니다.
     즉, 카르테시안 곱에 modality_class를 별도 축으로 추가하지 않습니다.
     대신, 다음 규칙을 따릅니다:
       * A0 state가 AIC-PKPD, AIC-ER, AIC-TTE, AIC-BIOMARKER, AIC-CELL_THERAPY,
         AIC-IMMUNOGEN, AIC-LACTATION 중 하나이고,
         동시에 modality_class가 {ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY}이면:
         → endpoint_data_type 및 analyte_role 의존 제약 (DC025~DC027) 추가 적용
         → analyte_role 미선언 시 Q16 할당
       * modality_class ∈ {SMALL_MOLECULE, PEPTIDE, MAB, MRNA, VACCINE,
                           OLIGO_ASO_SIRNA, RADIOPHARMACEUTICAL, OTHER_CUSTOM}은
         v4.2 신규 Q-code (Q16, Q18, Q19) 경로를 트리거하지 않음
     → 이 방식으로 universe 크기를 A0~A10 조합 × modality 복수 곱셈 없이 유지합니다.
     EXPECTED UNIVERSE SIZE RANGE: 1,000–5,000 (auxiliary field 방식 기준).
     만약 modality_class를 독립 축으로 처리하면 ×11 팽창 → 50,000+ → ILP 불능 위험.
   - When A10=SEMI-STRUCTURED → use source_parser_subtype as supplement
   - When A8 needs analyte_role → apply Q16 if missing
5. Output CSVs:
   - scenario_universe_raw.csv: all combinations
   - scenario_universe_valid_candidate.csv: terminal_state assigned
   - invalid_scenario_log.csv: combinations that failed (and why)

VALIDATION INSIDE GENERATOR:
- No row has q_code="Q15" standalone → if found, log to error log and skip
- No row has q_code="Q17" → if found, log and skip
- Every QUARANTINE has q_code → if not, log and skip
- Every AUTO has no repair function in implied action_sequence

EXPLICIT REASONING for v4.2:
- if endpoint_data_type=CELLULAR_KINETICS AND cellular_lloq_policy_proxy_state=PRESENT
  → AUTO/REPAIR
- if endpoint_data_type=CELLULAR_KINETICS AND cellular_lloq_policy_proxy_state=ABSENT
  → QUARANTINE Q01 (cellular subtype)
... etc for IMMUNOGENICITY (Q19), MATERNAL_INFANT (Q18, Q12), MILK_PK (Q01)

CLI:
python scripts/scenario_generator/generate_scenarios.py \
  --config-dir config \
  --out-dir data/scenario_universe

REPORT: reports/scenario_generation_report.md
- total_raw_combinations
- valid_count, invalid_count, unsupported_count
- terminal_state distribution
- q_code distribution
- v4.2 modality_class distribution
- v4.2 endpoint_data_type distribution
- Q15-standalone violations (must be 0)
- Q17 violations (must be 0)

EXPECT scenario count: 1000-5000 (depending on aux field expansion).
If <500 → likely under-expansion. If >50000 → over-expansion (need pruning).

OUTPUT: Python file + 3 CSVs + report.
```

---

### P54 — Family Assignment

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P53 완료
🔹 **첨부 파일:** family_assignment_rules.yaml, scenario_universe_valid_candidate.csv
🔹 **산출물:**
  - `scripts/scenario_generator/assign_family.py`
  - `data/scenario_universe/scenario_universe_with_family.csv`
  - `reports/family_coverage_summary.md`
🔹 **다음 액션:** P55

```
ROLE: Coding agent.

INPUT:
  config/family_assignment_rules.yaml
  data/scenario_universe/scenario_universe_valid_candidate.csv

TASK: Implement assign_family.py

PROCEDURE:
1. For each scenario:
   - Match against F01..F29 (operational) + F31..F34 (out-of-scope)
   - On multiple match: lower priority number wins
   - On no match: family_id = "FAMILY_UNASSIGNED"
2. Verify v4.2 specific assignments:
   - F26 (CAR-T) requires endpoint_data_type=CELLULAR_KINETICS
   - F29 (lactation dyad) requires endpoint_data_type=MATERNAL_INFANT_PK + dyad_linkage
   - F24 (ADC) requires modality_class=ADC + analyte_role declared

REPORT: reports/family_coverage_summary.md
- per-family scenario count
- F24-F29 (v4.2-new) representation: must be >0 each
- FAMILY_UNASSIGNED rate (operational scope only): target <5%

OUTPUT: Script + CSV + report.

GATE: F24-F29 each have ≥1 scenario; UNASSIGNED rate <5% in operational families.
```

---

### P55 — Pilot + Seed Pack Inclusion Check (강화)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P54 완료
🔹 **첨부 파일:** P54 universe with family, P33 fingerprints
🔹 **산출물:**
  - `scripts/scenario_generator/check_pilot_inclusion.py`
  - `reports/pilot_inclusion_check.md`
  - `reports/pilot_inclusion_failures.csv`
  - `reports/seed_pack_universe_coverage.md` (v5.1 NEW)
🔹 **다음 액션:** P56

```
ROLE: Coding agent.

TASK: Verify all pilot fingerprints AND all 20 seed-pack categories are
representable in the generated universe.

CHECKS:
1. For each fingerprint in empirical_fingerprints_pilot.csv:
   - Construct (A0..A10) tuple
   - Look up in scenario_universe_with_family.csv
   - if not found → record failure with cause classification
2. For each seed_category 1..20:
   - For each fingerprint with that seed_category_id:
     - Verify expected_terminal_state matches universe terminal
     - Verify expected_q_code matches universe q_code
3. Generate seed_pack_universe_coverage.md:
   - 20-row table: category | universe_representation | match_status

CAUSE CLASSIFICATION for failures:
- universe_gap: combination not in universe → patch needed
- fingerprint_error: H2 missed an axis state error → return to H2
- unknown_policy: missing AIC field → check AIC template
- f24_f27_intentional: legitimate UNSUPPORTED/INVALID, not a failure

GATE:
- Operational scope inclusion failure (after F31-F34 exclusion): MUST = 0
- Seed pack coverage: 20/20 in universe (or DEFERRED with v1.1 register entry)

If GATE fails → emit fallback steps (re-run P53 if universe_gap, H2 rework if fingerprint_error).

OUTPUT: Script + 3 reports.
```

---

### P56 — Pilot Inclusion Failure Analysis

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P55 완료
🔹 **첨부 파일:** P55 reports
🔹 **산출물:** `reports/pilot_inclusion_failure_analysis.md`
🔹 **다음 액션:** P57 (실패 있음) 또는 P58 (실패 없음으로 직행)

```
ROLE: PMX Grandmaster.

INPUT: reports/pilot_inclusion_failures.csv (and seed_pack_universe_coverage.md)

If failures.csv has 0 rows: output "PASS: all pilots representable" and stop.

Otherwise, for each failure:
- project_id, axes (A0..A10), failure_cause, suggested_fix

For seed pack misses:
- category_id, missing_combo, suggested_axis_patch_or_defer

OUTPUT: Markdown.
```

---

### P57 — A-LLM Universe Attack (12 typed queries v4.2)

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **진입 조건:** P56 완료
🔹 **첨부 파일:** P54 universe, P7 v4.2 summary
🔹 **산출물:** `reports/adversarial_reviews/universe_attack_v5_1.md`
🔹 **다음 액션:** P58 (LP Panel CP2 시작)

```
ROLE: Adversarial PMX dataset universe auditor (different model from R-LLM).

INPUT (attached):
  data/scenario_universe/scenario_universe_with_family.csv (head + summary)
  reports/frozen_universe_v4_2_summary.md

TASK: For each of 12 typed attack queries, provide concrete A0..A10 state
combination and assess universe coverage.

QUERIES:

Q01 multi-study ID conflict, no harmonization policy
   → Expect F02 with Q05
Q02 LLOQ changed mid-study + reanalysis without final flag
   → Expect Q15D
Q03 ADDL/II + actual mixed without resolution policy
   → Expect Q14
Q04 titration with variable AMT (no ADDL representation)
   → Expect F-routine + REPAIR via reconstruct_dose_titration
Q05 loading + maintenance with different RATE phases
   → Expect REPAIR via reconstruct_loading_maintenance
Q06 IV infusion stop/restart without RATE=0 events
   → Expect Q04 (no policy) or REPAIR (with infusion_reconstruction_policy)
Q07 DDI victim+perpetrator both measured, dual CMT
   → Expect F22 with assign_cmt_ddi_victim_perpetrator
Q08 Pediatric weight time-varying + mg/kg
   → Expect F12 with reconstruct_dose_weight + time_varying covariate

v4.2 SPECIFIC (must include):
Q09 CAR-T cellular kinetics, qPCR vector copy + FACS CAR+ cells, no cellular_LLOQ_policy
   → Expect F26 with Q01 (cellular subtype)
Q10 ADC measuring total Ab + conjugated + free payload, analyte_role NOT declared
   → Expect F24 with Q16
Q11 Maternal-infant pair PK, no dyad linkage key
   → Expect F29 with Q18
Q12 mRNA prime/boost, immunogenicity ADA detected, no positivity rule
   → Expect F27 with Q19

For EACH query (use this format):
- query_id
- concrete_axis_combo: A0=..., A1=..., ..., A10=..., aux={modality_class, endpoint_data_type, analyte_role}
- covered_by_current_universe: YES/NO
- universe_search_result: scenario_id if found, else "NOT FOUND"
- if NO: missing_axis_state_or_constraint, severity (CRITICAL/MAJOR/MINOR), recommended_patch
- if YES: terminal_state_match (Y/N), q_code_match (Y/N)

OUTPUT: Markdown with 12 query analyses + summary table at end.

CRITICAL CHECK: At least Q09-Q12 must have specific v4.2 axis states cited
(e.g., A8 analyte_role, A0 endpoint_data_type=CELLULAR_KINETICS, etc).
If A-LLM does not cite v4.2 fields specifically, retry with explicit reminder.
```

---

### P58~P60 — LP Panel CP2: Universe Attack + Freeze (병합)

> **v5.1 변경:** v3.1에서는 universe_attack과 universe_freeze 두 개 LP Panel이었지만, v5.1에서는 하나로 통합.

#### P58 (LP-A) — Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P57 attack, P54 universe, P56 failure analysis, P55 seed coverage
🔹 **산출물:** `reports/llm_proxy/universe_attack_freeze_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A) for Checkpoint CP2 (universe_attack_and_freeze).

INPUT (attached):
  reports/adversarial_reviews/universe_attack_v5_1.md
  reports/pilot_inclusion_failure_analysis.md
  reports/seed_pack_universe_coverage.md
  data/scenario_universe/scenario_universe_with_family.csv

TASKS (combined attack adjudication + freeze approval):

PART A: For each of 12 attack queries — accept or reject:
- If query reveals real universe gap → patch required
- If query reveals false gap (already covered) → reject
- If query is in F31-F34 territory → INTENTIONAL_EXCLUSION

PART B: Freeze approval checklist:
[ ] All 12 attack queries resolved (covered or rejected with rationale)
[ ] pilot inclusion operational failures = 0
[ ] seed pack 20/20 covered (or all misses deferred to v1.1 with justification)
[ ] Q15 standalone count = 0
[ ] Q17 count = 0
[ ] q_code_missing in QUARANTINE = 0
[ ] F24-F29 all populated
[ ] F31-F34 properly numbered

PART C: Required patches (if any) — list YAML edits.
PART D: confidence (HIGH/MEDIUM/LOW), fatal_issues, must_escalate_to_human.

OUTPUT per LP-A template.
```

#### P59 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** P58, P57, P54
🔹 **산출물:** `reports/llm_proxy/universe_attack_freeze_adversarial.md`

```
ROLE: Adversarial reviewer (LP-B) for CP2 freeze approval.

ATTACK Grandmaster's freeze approval:
1. Are coverage targets (capture ≥99%, review_inclusive ≥95%, etc.) met or just claimed?
2. Are v4.2 modality coverage claims defensible? (F24-F29 each have how many scenarios?)
3. Are seed-pack misses truly DEFERRED with valid reasoning, or hand-waved?
4. Did Grandmaster accept any patches that conflict with action_sequence_lock?
5. Q15-standalone or Q17 sneaking in via patches?
6. ILP downstream impact: would proposed patches change minimal node set later?

For each issue: severity (fatal/major/minor), evidence, correction.

OUTPUT per LP-B template.
```

#### P60 (LP-C) — Judge + 자동 Freeze

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션)
🔹 **첨부 파일:** P58 + P59
🔹 **산출물:**
  - `reports/llm_proxy/universe_attack_freeze_judge.md`
  - `reports/llm_proxy/universe_attack_freeze_decision.csv`
🔹 **다음 액션:** auto-apply 시 P61 (patches) → P62 (freeze) / 아니면 H1 또는 H4로 라우팅

```
ROLE: Judge (LP-C) for CP2.

ENFORCE Hard Rules from lp_panel_template.yaml.

If auto-apply: required_patch is non-empty → apply via C-LLM in next step (P61).
If no patches required AND fatal_resolved=YES AND escalate=NO → freeze can proceed (P62).
If escalate_to_human=YES → defer to H4 (release-stage human review).

OUTPUT per LP-C template.
```

---

### P61 — Universe Patches 자동 적용 (조건부)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P60 with required_patch non-empty
🔹 **첨부 파일:** P60 judge with patch list
🔹 **산출물:**
  - 수정된 config/*.yaml
  - re-generated `scenario_universe_with_family.csv`
  - re-run `check_pilot_inclusion.py` showing PASS
🔹 **다음 액션:** P62

```
ROLE: Coding agent.

PROCEDURE:
1. Apply each required_patch from P60 to corresponding config/*.yaml
2. Run validate_config.py — must PASS error_count=0
3. Re-run generate_scenarios.py
4. Re-run assign_family.py
5. Re-run check_pilot_inclusion.py — must PASS
6. Update CHANGELOG.md with patch entries

If any step fails → rollback all patches, escalate.

OUTPUT: Updated files. Confirm all gates PASS.
```

---

### P62 — Universe Freeze Declaration (R-LLM)

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** P60 judge, P55 seed coverage, P54 family summary
🔹 **산출물:** `release/v1.0/scenario_universe_freeze_declaration_v1_0.md`
🔹 **다음 액션:** P63

```
ROLE: Documentation writer.

TASK: Generate freeze declaration. Include:

# Scenario Universe v1.0 Freeze Declaration
**Frozen at:** {ISO timestamp - placeholder for C-LLM}
**Universe basis:** Frozen Universe v4.2

## Statistics
- total_valid_scenarios: N
- terminal_state_distribution
- family_distribution (F01-F29 op + F31-F34 out)
- modality_class_distribution
- endpoint_data_type_distribution
- q_code_distribution

## Hard Rule Compliance
- Q15 standalone count: 0 ✅
- Q17 count: 0 ✅
- q_code missing in QUARANTINE: 0 ✅
- F24-F29 each have N scenarios (list)

## Pilot Coverage
- pilot inclusion failures (operational): 0
- seed pack 20/20: list status per category (or DEFERRED with v1.1 register link)

## LP Panel CP2 Result
- LP-A confidence
- LP-B fatal count
- LP-C decision: APPROVED / CONDITIONAL / ESCALATED

## Hash placeholders
SHA256 (scenario_universe_v1.0.csv): {to be filled by C-LLM in P63}

## Signature
- approved_by_lp_panel: YES (auto, no escalation)
  OR
- escalated_to: H4 (release-stage human veto required)

OUTPUT: Markdown.
```

---

### P63 — Universe Freeze Hash + CSV 복사 (C-LLM)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **첨부 파일:** P62 declaration draft, scenario_universe_with_family.csv
🔹 **산출물:**
  - `data/scenario_universe/scenario_universe_v1.0.csv`
  - `release/v1.0/scenario_universe_v1_0.sha256`
  - `release/v1.0/scenario_universe_freeze_declaration_v1_0.md` (해시 채워진 최종본)
🔹 **다음 액션:** P64

```
ROLE: Coding agent.

TASKS:
1. cp data/scenario_universe/scenario_universe_with_family.csv → data/scenario_universe/scenario_universe_v1.0.csv
2. SHA256 of scenario_universe_v1.0.csv → release/v1.0/scenario_universe_v1_0.sha256
3. Inject hash into P62 declaration → save as final v1_0.md
4. Update CHANGELOG.md: "## v1.0.0 — Scenario Universe FROZEN, hash {hash}, count {N}"

OUTPUT: 3 files + CHANGELOG.
```

---

### P64 — Coverage Metrics Initial Report

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **첨부 파일:** scenario_universe_v1.0.csv
🔹 **산출물:**
  - `scripts/validation/calculate_coverage_metrics.py`
  - `reports/coverage_metrics_initial.md`
  > ⚠️ **[PATCH m-3]** P63에서 생성된 SHA256 파일명은 정확히 `release/v1.0/scenario_universe_v1_0.sha256`입니다.
  > CHECK-5와 CHECK-10 모두 이 파일명으로 검증하므로 C-LLM이 다른 이름으로 생성하지 않도록 주의하세요.
  > 파일명 패턴: `release/v1.0/{deliverable_name}_v1_0.sha256` (하이픈(-) 아닌 언더스코어(_) 사용)
🔹 **다음 액션:** P65

```
ROLE: Coding agent.

TASK: Implement scripts/validation/calculate_coverage_metrics.py

CALCULATE:
- total_scenarios = N
- capture_coverage = (AUTO + REPAIR + QUARANTINE + UNSUPPORTED + INVALID) / N
- review_inclusive = (AUTO + REPAIR + QUARANTINE) / (N - UNSUPPORTED - INVALID)
- operational = (AUTO + REPAIR) / (N - UNSUPPORTED - INVALID)
- auto_only = AUTO / (N - UNSUPPORTED - INVALID)
- unsupported_invalid_rate = (UNSUPPORTED + INVALID) / N

VALIDATE:
- capture_coverage ≥ 0.99
- review_inclusive ≥ 0.95
- unsupported_invalid_rate ≤ 0.05
- q_code_missing_count = 0
- q15_solo_count = 0
- q17_count = 0
- false_auto_count = 0 (estimated; actual count after golden validation)
- false_repair_count = 0 (estimated; actual after golden validation)

REPORT: reports/coverage_metrics_initial.md

CLI:
python scripts/validation/calculate_coverage_metrics.py \
  --universe data/scenario_universe/scenario_universe_v1.0.csv \
  --out reports/coverage_metrics_initial.md

OUTPUT: Script + report.
```

---

### P65 — Phase 5 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** P63, P64
🔹 **산출물:** `reports/phase5_completion_declaration.md`
🔹 **다음 액션:** CHECK-5

```
ROLE: Documentation writer.

CHECKLIST:
[ ] scenario_universe_v1.0.csv FROZEN (hash exists)
[ ] freeze_declaration signed (LLM/auto)
[ ] LP Panel CP2 APPROVED or ESCALATED with H4 routing
[ ] capture_coverage ≥99%
[ ] review_inclusive ≥95%
[ ] unsupported+invalid ≤5%
[ ] q15_solo=0, q17=0, q_missing=0
[ ] F24-F29 populated
[ ] seed pack 20/20 covered or deferred with v1.1 entries
[ ] CHANGELOG updated to v1.0.0

OUTPUT: Markdown.
```

---

### 🐍 CHECK-5 (Phase 5 검증)

```python
# check_phase5.py
import os, sys, hashlib
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas 없음"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("❌"); sys.exit(1)

print("=" * 60)
print("CHECK-5: Phase 5 (Scenario Universe Freeze) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "scripts/scenario_generator/generate_scenarios.py",
    "scripts/scenario_generator/assign_family.py",
    "scripts/scenario_generator/check_pilot_inclusion.py",
    "scripts/validation/calculate_coverage_metrics.py",
    "data/scenario_universe/scenario_universe_v1.0.csv",
    "release/v1.0/scenario_universe_v1_0.sha256",  # [PATCH m-3] 파일명 규칙: 언더스코어 사용
    "release/v1.0/scenario_universe_freeze_declaration_v1_0.md",
    "reports/coverage_metrics_initial.md",
    "reports/family_coverage_summary.md",
    "reports/pilot_inclusion_check.md",
    "reports/seed_pack_universe_coverage.md",
    "reports/phase5_completion_declaration.md",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file(): print(f"  ✅ {f.split('/')[-1]}")
    else: print(f"  ❌ {f}"); failures.append(f)

# Universe CSV 검사
uv = BASE / "data/scenario_universe/scenario_universe_v1.0.csv"
if uv.is_file():
    df = pd.read_csv(uv)
    print(f"\n[Universe CSV: {len(df):,} 시나리오]")

    # terminal 분포
    if "terminal_state" in df.columns:
        d = df["terminal_state"].value_counts()
        for s, n in d.items():
            print(f"  {s}: {n} ({n/len(df)*100:.1f}%)")

    # Q15 / Q17 / 누락
    if "q_code" in df.columns:
        q_str = df["q_code"].astype(str).str.strip()
        q15s = (q_str == "Q15").sum()
        q17 = (q_str == "Q17").sum()
        if q15s == 0: print("  ✅ Q15 단독 0")
        else: failures.append(f"Q15 단독 {q15s}"); print(f"  ❌ Q15 {q15s}")
        if q17 == 0: print("  ✅ Q17 0")
        else: failures.append("Q17"); print(f"  ❌ Q17 {q17}")

        if "terminal_state" in df.columns:
            qmask = df["terminal_state"] == "QUARANTINE"
            qmiss = (qmask & (df["q_code"].isna() | (q_str == ""))).sum()
            if qmiss == 0: print("  ✅ q_code 누락 QUARANTINE 0")
            else: failures.append(f"q_missing {qmiss}"); print(f"  ❌ {qmiss}")

    # F24-F29 v4.2 family
    if "family_id" in df.columns:
        for f in ["F24","F25","F26","F27","F28","F29"]:
            n = (df["family_id"] == f).sum()
            if n > 0: print(f"  ✅ {f}: {n} scenarios")
            else: print(f"  ❌ {f}: 0"); failures.append(f"family {f} 빈")
        # [PATCH-B2] F30 부재 검증 (Step 1 PATCH-F30 downstream defense)
        f30_n = (df["family_id"] == "F30").sum()
        if f30_n == 0:
            print("  ✅ F30 미사용 (reserved, not assigned — 정상)")
        else:
            print(f"  ❌ F30 {f30_n}개 발견 — F30는 예약 번호이며 universe에 존재해선 안 됨")
            failures.append("F30 잘못 할당됨")

# SHA256 hash 검증
print("\n[SHA256 hash]")
hf = BASE / "release/v1.0/scenario_universe_v1_0.sha256"
if hf.is_file() and uv.is_file():
    computed = hashlib.sha256(uv.read_bytes()).hexdigest()
    stored = hf.read_text().strip().split()[0]
    if computed == stored: print(f"  ✅ hash 일치: {computed[:16]}...")
    else: print(f"  ❌ hash 불일치"); failures.append("hash")

# Coverage metrics
cm = BASE / "reports/coverage_metrics_initial.md"
if cm.is_file():
    txt = cm.read_text(encoding="utf-8")
    print("\n[Coverage Metrics]")
    for kw in ["capture_coverage", "review_inclusive", "operational"]:
        if kw in txt: print(f"  ✅ {kw} 포함")
        else: print(f"  ⚠️  {kw} 누락"); failures.append(kw)

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 5 완료")
    print("→ 다음: Phase 6 (P66) — Decision Nodes + Cost")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## 🎯 Phase 6: Decision Nodes + Cost Function (P66~P70)

### 📌 이 단계 목적

N0~N7 (그리고 v5.1에서 추가되는 N8) **결정 노드**를 정의하고, ILP에 투입할 cost를 부여합니다.
**v5.1 핵심:** Forced node set 명시 (PATCH-3) — N0, N1, N2, N3, N4, N5, N8 7개는 minimal node에 반드시 포함.
**v5.1 압축:** cost function LP Panel 제거. 단일 R-LLM + Python validation으로 대체.

### 진입 조건
- [x] CHECK-5 PASS

---

### P66 — Candidate Node Dictionary v5.1 (Forced Nodes 명시)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** CHECK-5 PASS
🔹 **첨부 파일:** scenario_universe_v1.0.csv 통계, AIC template
🔹 **산출물:** `config/candidate_node_dictionary_v5_1.csv`
🔹 **다음 액션:** P67

```
ROLE: PMX Grandmaster.

INPUT (attached):
  data/scenario_universe/scenario_universe_v1.0.csv (head + terminal distribution)
  config/analysis_intent_contract_template.yaml
  config/family_assignment_rules.yaml

TASK: Define decision node dictionary with forced node set explicit.

NODES:
N0  AIC sufficient + endpoint_data_type declared (when required by AIC type)
    forced_inclusion: TRUE
    rationale: "Without AIC, no decision is meaningful."
N1  Subject ID + dyad_linkage (if maternal_infant) constructible
    forced_inclusion: TRUE
    rationale: "ID failure → INVALID; dyad-key failure → Q18."
N2  Time anchor recoverable (actual/nominal/elapsed/postpartum)
    forced_inclusion: TRUE
    rationale: "Time path determines all event ordering; v4.2 adds postpartum anchor."
N3  Dose record completeness (including titration/loading/infusion v4.1, no addl-conflict)
    forced_inclusion: TRUE
    rationale: "Dose path failure → false REPAIR risk highest."
N4  Observation completeness (BLQ for concentration AND cellular AND immunogenicity AND milk)
    forced_inclusion: TRUE
    rationale: "v4.2 cellular/immunogen/milk silent error mostly happens here."
N5  BLQ/MDV policy applied
    forced_inclusion: TRUE
    rationale: "BLQ policy mismatch → wrong DV values."
N6  Covariate attachment (including product-level for CAR-T)
    forced_inclusion: FALSE
    rationale: "Optional for some scenarios."
N7  Remaining ambiguity below threshold
    forced_inclusion: FALSE
    rationale: "Catch-all, may be redundant with prior nodes."
N8  Required policy availability check (v5.1 NEW)
    forced_inclusion: TRUE
    rationale: "Explicit gate ensuring REPAIR has all required policies before
               proceeding. Catches cases where multiple policies are individually
               possible but combined REPAIR pipeline is undefined."
    detection_rule: |
      N8 = Y  ← ALL required_policies for proposed action_sequence are declared
                   in the project's AIC (analysis_intent_contract_template.yaml fields).
                   "Declared" means the field is present AND non-null/non-empty.
      N8 = N  ← ANY single required_policy absent in AIC → terminal = QUARANTINE,
                   q_code = the specific Q-code corresponding to the missing policy
                   (e.g., Q01 for missing blq_handling_policy, Q19 for missing
                    positivity_adjudication_rule, Q18 for missing dyad_linkage_policy).
      N8 = NA ← No repair functions in proposed sequence (AUTO path) — skip.
    cost_if_excluded: INFINITY   # forced=TRUE, ILP constraint: x_N8 = 1 (mandatory)
    cost_components: failure_risk=5, downstream_impact=5, implementation_complexity=2,
                     audit_risk=5, manual_burden=3
    total_cost: 4.40  # 0.30*5 + 0.25*5 + 0.15*2 + 0.20*5 + 0.10*3
    placement_in_tree: "After N1 (ID check), before N2 (time anchor) — policy gate
                        must be resolved before any transform logic is attempted."
    v5_1_note: "Added per PATCH-3. N8 was implicit in v4.1 but caused silent REPAIR
                when policies were partially specified."

NODE STRUCTURE per row in CSV:
node_id, question, allowed_answers (Y/N/NA), yes_path, no_path,
q_code_if_fail, depends_on_axis, terminal_if_fail, forced_inclusion,
cost_if_excluded,   # INFINITY for forced nodes, numeric for optional
total_cost,         # weighted sum per cost_function_definition_v5_1.md
rationale, detection_rule, audit_risk, v5_1_note

# FORCED NODE COST POLICY (v5.1 PATCH-3):
# For N0, N1, N2, N3, N4, N5, N8: cost_if_excluded = INFINITY
# ILP implementation: add constraint x_Ni = 1 for each forced node
# This is equivalent to setting penalty >> max_total_cost_of_all_nodes

OUTPUT: CSV with 9 nodes (N0-N8) — N8 is v5.1 NEW.
# VALIDATION: all 7 forced nodes must have cost_if_excluded = INFINITY
# VALIDATION: all 9 rows must have non-null detection_rule
```

---

### P67 — Node Pilot Test (각 fingerprint에 노드 적용)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P66 완료
🔹 **첨부 파일:** P66 nodes, fingerprints CSV
🔹 **산출물:**
  - `scripts/decision_table/pilot_node_test.py`
  - `reports/pilot_node_test_report.md`
🔹 **다음 액션:** PASS rate 100% 확인 → P68

```
ROLE: Coding agent.

INPUT:
  config/candidate_node_dictionary_v5_1.csv
  data/pilot_fingerprints/empirical_fingerprints_pilot.csv

TASK: For each fingerprint, compute N0..N8 answers and predicted terminal_state.

PROCEDURE:
For each fingerprint row:
  N0_answer = (A0_state != AIC-MISSING) AND (endpoint_data_type declared if applicable)
  N1_answer = (A9_state != IRRECONCILABLE) AND (ID constructible) AND
              (if MATERNAL_INFANT_PK: dyad_linkage_key present)
  N2_answer = (A3_state not in {UNRECOVERABLE, AMBIGUOUS without policy}) AND
              (delivery_anchor present if pregnancy/lactation)
  N3_answer = (A4_state not in {UNRECOVERABLE, MISSING-NO-POLICY,
                                 ADDL-ACTUAL-CONFLICT without policy,
                                 TITRATION/LOADING/INFUSION without policy})
  N4_answer = (A5_state not in {ABSENT, BIOANALYTICAL-FINAL-FLAG-MISSING,
                                 BLQ-NO-POLICY (concentration), Cellular without policy})
              AND (A9_state != REANALYSIS-FINAL-MISSING)
              AND (if IMMUNOGENICITY: positivity_rule present)
  N5_answer = (A5_state not in {BLQ-NO-POLICY, LLOQ-MISSING})
              AND (cellular_LLOQ present if cellular endpoint)
  N6_answer = (A7_state not in {KEY-MISSING, POLICY-MISSING})
              AND (product_level_linkage present if PRODUCT-LEVEL-COVARIATE state)
  N7_answer = no unresolved q_code
  N8_answer = ALL required_policies for proposed action_sequence present in AIC

PREDICTED terminal_state:
- If any forced node = N → terminal = QUARANTINE/INVALID per node's q_code_if_fail
- If all forced nodes = Y AND any non-forced node = N → REPAIR (with caveat)
- If all = Y → AUTO

Compare predicted vs expected_terminal_state from fingerprint.

REPORT:
- match rate (target: 100%)
- mismatches by category: TREE_ERROR / FINGERPRINT_ERROR / NODE_DEFINITION_ERROR
- v4.2 specific cases: how do new modality fingerprints traverse N0-N8?

OUTPUT: Script + report.

GATE: match rate = 100% (mismatch → fix in P66 or escalate to H2).
```

---

### P68 — Cost Function 정의 + 자동 적용

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델) — **단일 R-LLM, LP Panel 없음 (PATCH-4)**
🔹 **진입 조건:** P67 PASS
🔹 **첨부 파일:** P66 nodes, P67 test report
🔹 **산출물:**
  - `reports/cost_function_definition_v5_1.md`
  - `config/candidate_node_dictionary_with_costs.csv`
🔹 **다음 액션:** P69

```
ROLE: PMX Grandmaster + ILP modeler.

INPUT (attached):
  config/candidate_node_dictionary_v5_1.csv
  reports/pilot_node_test_report.md

TASK: Define cost per node and inject into dictionary.

COST COMPONENTS (each 1-5 scale):
- failure_risk: NONMEM error probability if this node is wrong
- downstream_impact: number of subsequent decisions affected
- implementation_complexity: code complexity to detect this node's answer
- audit_risk: regulatory/audit consequence
- manual_burden: human review cost when node fails

Total cost = 0.30*failure_risk + 0.25*downstream_impact + 0.15*impl + 0.20*audit + 0.10*manual

PROPOSED COSTS (review and adjust):
N0: 5,5,1,5,3 → 4.20  forced
N1: 5,5,1,4,2 → 3.90  forced
N2: 5,4,3,4,4 → 4.10  forced
N3: 5,5,4,4,4 → 4.50  forced  (v5.1: bumped from 3.6 — v4.2 dose paths increase complexity)
N4: 5,4,3,4,4 → 4.10  forced  (v5.1: bumped from 3.2 — cellular/immunogen subtype)
N5: 4,3,2,3,3 → 3.10           forced  (v5.1: forced added per PATCH-3)
N6: 2,2,2,2,2 → 2.00           non-forced
N7: 3,1,1,2,3 → 2.10           non-forced
N8: 5,5,2,5,3 → 4.40  forced  (v5.1 NEW)

Forced nodes infinity cost penalty for exclusion:
ILP constraint: x_N0 = x_N1 = x_N2 = x_N3 = x_N4 = x_N5 = x_N8 = 1

IMMUTABILITY DECLARATION:
"These costs are LOCKED before ILP execution. Post-ILP cost changes forbidden."

OUTPUT:
- reports/cost_function_definition_v5_1.md (rationale)
- config/candidate_node_dictionary_with_costs.csv (updated dictionary)
```

---

### P69 — Action Sequence Standard Final Review

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** P13 action_sequence, P26 lock, P66 nodes
🔹 **산출물:** `config/action_sequence_standard_v1_final.yaml`
🔹 **다음 액션:** P70

```
ROLE: PMX Grandmaster.

INPUT (attached):
  config/action_sequence_standard.yaml (P13)
  release/v1.0/action_sequence_lock_v1_0.md (P26)
  config/candidate_node_dictionary_v5_1.csv (P66)

TASK: Verify P13 action_sequence_standard.yaml is consistent with node decisions.

ADDITIONAL VERIFICATION:
- titration/loading/infusion/addl-actual-conflict paths all linked to N3
- cellular_blq, immunogenicity, dyad_linkage paths linked to N4
- assign_cmt_with_analyte_role linked to N4 (analyte_role check)
- attach_covariate_product_level linked to N6
- N8 (policy_availability) gates entire pipeline before any repair function executes

If consistent: copy to action_sequence_standard_v1_final.yaml (no content change, version bump only)
If inconsistent: list discrepancies and emit "ESCALATE: action_sequence vs node mismatch"

OUTPUT: YAML.
```

---

### P70 — Phase 6 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `reports/phase6_completion_declaration.md`
🔹 **다음 액션:** CHECK-6

```
ROLE: Documentation writer.

CHECKLIST:
[ ] candidate_node_dictionary_v5_1.csv has 9 nodes (N0-N8)
[ ] forced_inclusion=TRUE for N0,N1,N2,N3,N4,N5,N8 (7 nodes)
[ ] forced_inclusion=FALSE for N6, N7
[ ] N8 (policy_availability, v5.1 NEW) defined
[ ] pilot node test PASS rate 100%
[ ] cost function defined and immutable
[ ] action_sequence_standard_v1_final.yaml consistent with nodes

OUTPUT: Markdown.
```

---

### 🐍 CHECK-6 (Phase 6 검증)

```python
# check_phase6.py
import os, sys
from pathlib import Path

try:
    import pandas as pd
except ImportError: sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("❌"); sys.exit(1)

print("=" * 60)
print("CHECK-6: Phase 6 (Decision Nodes + Cost) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "config/candidate_node_dictionary_v5_1.csv",
    "config/candidate_node_dictionary_with_costs.csv",
    "config/action_sequence_standard_v1_final.yaml",
    "scripts/decision_table/pilot_node_test.py",
    "reports/pilot_node_test_report.md",
    "reports/cost_function_definition_v5_1.md",
    "reports/phase6_completion_declaration.md",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file(): print(f"  ✅ {f.split('/')[-1]}")
    else: print(f"  ❌ {f}"); failures.append(f)

# Node 개수 + forced
print("\n[Node Dictionary]")
nd = BASE / "config/candidate_node_dictionary_with_costs.csv"
if nd.is_file():
    df = pd.read_csv(nd)
    print(f"  노드 수: {len(df)} (N0-N8 → 9 expected)")
    if len(df) >= 9:
        print("  ✅ 9 노드")
    else:
        failures.append(f"node {len(df)}/9")

    if "forced_inclusion" in df.columns:
        forced = df[df["forced_inclusion"].astype(str).str.upper().isin(["TRUE", "YES", "T"])]
        forced_ids = set(str(x).strip() for x in forced["node_id"]) if "node_id" in df.columns else set()
        expected = {"N0","N1","N2","N3","N4","N5","N8"}
        missing = expected - forced_ids
        if not missing:
            print(f"  ✅ Forced nodes 7개 모두 (N0,N1,N2,N3,N4,N5,N8)")
        else:
            print(f"  ❌ Forced 누락: {missing}")
            failures.append(f"forced 누락 {missing}")
    else:
        failures.append("forced_inclusion 컬럼")
        print("  ❌ forced_inclusion 컬럼 없음")

    # cost 컬럼
    if any("cost" in c.lower() for c in df.columns):
        print("  ✅ cost 컬럼 존재")
    else:
        failures.append("cost 컬럼")

# Pilot node test PASS rate
ptr = BASE / "reports/pilot_node_test_report.md"
if ptr.is_file():
    print("\n[Pilot Node Test]")
    txt = ptr.read_text(encoding="utf-8")
    if "100%" in txt or "match_rate: 1.0" in txt:
        print("  ✅ 100% match")
    else:
        print("  ⚠️  match_rate 확인 필요")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 6 완료")
    print("→ 다음: Phase 7 (P71) — Action Label + Lock")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## 🏷️ Phase 7: Action Label + Lock + LP Panel CP4, CP5 (P71~P85)

### 📌 이 단계 목적

각 시나리오에 구체적 **action_label** (예: `REPAIR_DOSE_TITRATION_WEIGHT_BASED`)을 부여하고 잠급니다.
**v5.1 변경:** EP-split LP Panel은 action_label_adjudication에 흡수 (PATCH-4).
**LP Panel CP4** = action_label adjudication (EP split 포함)
**LP Panel CP5** = action_label lock

### 진입 조건
- [x] CHECK-6 PASS

---

### P71 — Action Label 초안 생성

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** scenario_universe_v1.0.csv, action_sequence_standard, q-codes
🔹 **산출물:** `data/action_labels/scenario_action_table_draft.csv`
🔹 **다음 액션:** P72

```
ROLE: PMX Grandmaster.

INPUT (attached):
  data/scenario_universe/scenario_universe_v1.0.csv
  config/action_sequence_standard_v1_final.yaml
  config/quarantine_reason_codes.yaml
  config/repair_rule_dictionary.yaml

TASK: For each scenario in v1.0, assign:
- candidate_action_label
- action_sequence (ordered list of (function_name, parameter_policy))
- parameter_policy
- rationale
- confidence (HIGH/MEDIUM/LOW)
- label_status: "draft"

LABEL NAMING CONVENTION:
{TERMINAL}_{CATEGORY}_{DETAIL}

Examples:
AUTO_SDTM_STANDARD
AUTO_LEGACY_NM_CLEAN
REPAIR_DOSE_TITRATION_WEIGHT_BASED
REPAIR_BLQ_M3_CONCENTRATION
REPAIR_CELLULAR_BLQ_POISSON_LLOQ          # v4.2
REPAIR_DDI_VICTIM_PERPETRATOR_DUAL_CMT
REPAIR_MATERNAL_INFANT_DYAD_LINKAGE       # v4.2
REPAIR_ADC_MULTI_ANALYTE_TAGGED           # v4.2
REPAIR_IMMUNOGENICITY_POSITIVITY_RULE     # v4.2
QUARANTINE_BLQ_NO_POLICY_Q01
QUARANTINE_CELLULAR_NO_LLOQ_Q01_CELLULAR  # v4.2
QUARANTINE_IMMUNOGEN_NO_RULE_Q19          # v4.2
QUARANTINE_MATERNAL_NO_DYAD_Q18           # v4.2
QUARANTINE_ANALYTE_ROLE_MISSING_Q16       # v4.2
INVALID_TIME_UNRECOVERABLE
UNSUPPORTED_RAW_FCS_F31

HARD RULES:
- REPAIR label MUST have ≥1 repair function in action_sequence
- AUTO label MUST NOT have any repair function
- QUARANTINE label MUST end with q_code in name
- Q15 standalone, Q17 forbidden
- INVALID/UNSUPPORTED action_sequence MUST NOT contain export_nonmem_ready
- Same action_label → same action_sequence (EP equivalence)

OUTPUT: data/action_labels/scenario_action_table_draft.csv
Columns: scenario_id, family_id, terminal_state, q_code,
         candidate_action_label, action_sequence, parameter_policy,
         rationale, confidence, label_status

GATE: scenario_action_table_draft has same row count as scenario_universe_v1.0.
```

---

### P72 — Label Conflict Detection

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P71 완료
🔹 **첨부 파일:** P71 draft
🔹 **산출물:**
  - `scripts/label_workbench/detect_label_conflicts.py`
  - `reports/label_conflict_report.csv`
  - `reports/expert_review_queue.csv`
🔹 **다음 액션:** P73

```
ROLE: Coding agent.

TASK: detect_label_conflicts.py

CONFLICT TYPES (10):
C01  Same A0..A10 combination → different labels
C02  Same label → different action_sequence
C03  REPAIR label → policy missing in action_sequence parameter_policy
C04  QUARANTINE label → no q_code in name or wrong q_code in CSV column
C05  Q15 standalone in q_code
C06  Q17 in q_code
C07  AUTO label → repair_* function in action_sequence
C08  INVALID/UNSUPPORTED → export_nonmem_ready in action_sequence
C09  Different parameter_policy → same label
C10  v4.2: ADC/CAR-T multi-analyte → analyte_role missing in label name

OUTPUT:
- label_conflict_report.csv: scenario_id, conflict_type, severity, detail
- expert_review_queue.csv: sorted by severity DESC, then scenario_id

GATE: report generated. Conflict resolution happens in CP4 (P74-P76).
```

---

### P73 — Expert Review Packet

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P72 완료
🔹 **첨부 파일:** P72 conflict report + queue
🔹 **산출물:** `reports/human_review/action_label_adjudication_packet_v5_1.md`
🔹 **다음 액션:** P74 (LP Panel CP4)

```
ROLE: PMX Grandmaster.

INPUT: reports/label_conflict_report.csv, expert_review_queue.csv

For each conflict (or conflict cluster), produce review packet entry:
- conflict_cluster_id
- affected_scenario_ids
- conflict_type
- pmx_context (2-sentence explanation of why this matters)
- practical_risk (false AUTO / wrong REPAIR / regulatory issue)
- resolution_options:
    A. accept current label as-is (with rationale)
    B. split into multiple labels (specify split criteria)
    C. revise label name (specify new name)
    D. escalate to v1.1 (defer)
- recommended_resolution + rationale

OUTPUT: Markdown with cluster-by-cluster analysis.
```

---

### P74~P76 — LP Panel CP4: Action Label Adjudication (EP split 포함)

#### P74 (LP-A) — Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P73 packet, P71 draft, repair_rule_dictionary, q-codes
🔹 **산출물:** `reports/llm_proxy/action_label_adjudication_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A) for Checkpoint CP4 (action_label_adjudication).

INPUT (attached):
  reports/human_review/action_label_adjudication_packet_v5_1.md
  data/action_labels/scenario_action_table_draft.csv
  config/repair_rule_dictionary.yaml
  config/quarantine_reason_codes.yaml

For each conflict cluster:
1. Is REPAIR claim grounded in explicit policy?
2. BLQ M1/M3/M4 — do these need parameter_policy split?
3. v4.2: cellular vs concentration BLQ — different labels?
4. v4.2: dyad linkage variations — same or split labels?
5. v4.2: ADC analyte_role variations — same label?
6. EP equivalence check: function order + parameter + terminal must match

OUTPUT per LP-A template.
```

#### P75 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** `reports/llm_proxy/action_label_adjudication_grandmaster.md` (P74), `reports/human_review/action_label_adjudication_packet_v5_1.md` (P73), `data/action_labels/scenario_action_table_draft.csv` (P71)
  > ⚠️ **[PATCH m-7]** P74 산출물(`action_label_adjudication_grandmaster.md`)을 반드시 첨부하세요.
  > LP-B는 LP-A가 내린 판정을 공격하는 역할이므로, LP-A 결과가 없으면 공격 대상이 없습니다.
  > P73 패킷도 함께 첨부해 원본 conflict cluster 맥락을 유지하세요.
  > (이전에는 "P74, P73"으로만 표기되어 실제 파일명이 불명확했습니다.)
🔹 **산출물:** `reports/llm_proxy/action_label_adjudication_adversarial.md`

```
ROLE: Adversarial reviewer (LP-B) — DIFFERENT model.

ATTACK Grandmaster's adjudication:
1. REPAIR labels with hidden analytical judgment
2. AUTO labels that actually require policy
3. v4.2 splits incorrectly merged (e.g., conjugated_ADC vs total_antibody same label)
4. dyad linkage policies merged when they should split
5. cellular/concentration BLQ merged
6. immunogenicity adjudication labels missing positivity_rule reference
7. parameter_policy hidden differences (BLQ M1 vs M3)

For each issue: severity, evidence, correction.
```

#### P76 (LP-C) — Judge + 자동 적용

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션)
🔹 **첨부 파일:** P74 + P75
🔹 **산출물:**
  - `reports/llm_proxy/action_label_adjudication_judge.md`
  - `reports/llm_proxy/action_label_adjudication_decision.csv`
  - 자동 적용된 `data/action_labels/scenario_action_table_adjudicated.csv`
🔹 **다음 액션:** P77

```
ROLE: Judge (LP-C).

ENFORCE Hard Rules.

If auto-apply:
- Apply each accepted patch to scenario_action_table_draft.csv
- Update label, action_sequence, parameter_policy as instructed
- Save as scenario_action_table_adjudicated.csv

Re-run detect_label_conflicts.py — count must ≤ initial count - resolved_count.
```

---

### P77 — EP Validation + Auto Split (P78 흡수)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P76 완료
🔹 **첨부 파일:** P76 adjudicated CSV
🔹 **산출물:**
  - `scripts/label_workbench/validate_equivalence_partitioning.py`
  - `reports/equivalence_partition_report.md`
  - `data/action_labels/scenario_action_table_after_ep.csv`
🔹 **다음 액션:** P78

```
ROLE: Coding agent.

TASK: For each action_label group:
1. Verify all members have identical:
   - function_name sequence
   - parameter_policy
   - terminal_state
   - q_code (or both null)
2. Flag inconsistent groups:
   - High-risk groups requiring scrutiny:
     BLQ (M1/M3/M4), DDI (victim-only vs perpetrator),
     pediatric, LLOQ-changed/reanalysis, multi-study, TDM,
     infusion, titration, loading-maintenance,
     cellular_kinetics, immunogenicity, dyad_linkage, analyte_role variations
3. Auto-split groups where splits are unambiguous (e.g., terminal_state differs)
4. List ambiguous splits for P78 attack

OUTPUT:
- equivalence_partition_report.md
- scenario_action_table_after_ep.csv (auto-splits applied)
- ep_split_residual.csv (cases needing P78 attack review)
```

---

### P78 — A-LLM EP Split Attack (단일, LP Panel 없음)

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **진입 조건:** P77 완료
🔹 **첨부 파일:** P77 ep_split_residual.csv, equivalence_partition_report
🔹 **산출물:** `reports/adversarial_reviews/ep_split_attack_v5_1.md`
🔹 **다음 액션:** P79

> **v5.1 변경:** v3.1에서 별도 LP Panel이었던 EP split을 단일 A-LLM 공격 + R-LLM 판정으로 압축 (PATCH-4).

```
ROLE: Adversarial reviewer.

INPUT: reports/ep_split_residual.csv, equivalence_partition_report.md

For each residual case, attack the proposed equivalence:

ATTACK AXES (8):
1. BLQ M1/M3/M4 — parameter_policy difference creates control stream difference
2. DDI: victim_only single CMT vs victim+perp dual CMT — different functions
3. Pediatric: static weight vs time-varying — different covariate path
4. LLOQ-changed: with vs without date — different reconstruction
5. Multi-study: same vs different ID format — different prefix policy
6. Infusion: bolus vs RATE-based — different reconstruction function
7. Titration: ADDL vs variable — reconstruct_dose_titration vs expand_addl_ii
8. Reanalysis: final flag present vs missing → REPAIR vs QUARANTINE (totally different)
9. v4.2 cellular: with vs without LLOQ → REPAIR vs QUARANTINE
10. v4.2 immunogenicity: with vs without positivity rule → REPAIR vs QUARANTINE
11. v4.2 dyad: with vs without linkage key → REPAIR vs QUARANTINE
12. v4.2 analyte_role: with vs without role declaration → REPAIR vs Q16

For each: scenario_id, current_grouping, hidden_difference,
split_required (Y/N), recommended_split.

OUTPUT: Markdown.
```

---

### P79 — EP Split 판정 + 자동 적용

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델) — 단일 R-LLM, 별도 LP Panel 없음
🔹 **첨부 파일:** P78 attack
🔹 **산출물:**
  - `reports/ep_split_decision.md`
  - 자동 적용된 `data/action_labels/scenario_action_table_after_ep_split.csv`
🔹 **다음 액션:** P80

```
ROLE: PMX Grandmaster.

INPUT: reports/adversarial_reviews/ep_split_attack_v5_1.md

For each attack item:
1. Validate hidden_difference claim with NONMEM control stream argument
2. If valid AND no universe_patch needed → split label, update action_sequence
3. If valid BUT universe_patch needed → defer to v1.1 register
4. If invalid → reject with rationale

Apply accepted splits to scenario_action_table_after_ep.csv.
Save as scenario_action_table_after_ep_split.csv.

Re-run validate_equivalence_partitioning.py — must show 0 inconsistent groups.

OUTPUT: Decision markdown + updated CSV.
```

---

### P80 — A-LLM Label Lock 전 적대적 검토

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** P79 final CSV
🔹 **산출물:** `reports/adversarial_reviews/label_lock_attack_v5_1.md`
🔹 **다음 액션:** P81 (LP Panel CP5)

```
ROLE: Adversarial reviewer.

INPUT: data/action_labels/scenario_action_table_after_ep_split.csv

Find issues before lock:
1. REPAIR label with hidden policy
2. AUTO label with hidden analytical judgment
3. QUARANTINE label with wrong q_code
4. Q15 standalone or Q17 sneaking in
5. v4.2 label gaps (cellular/immunogenicity/dyad/analyte_role)
6. UNSUPPORTED/INVALID with export_nonmem_ready
7. DDI labels missing victim-only vs perpetrator separation

For each issue: scenario_id, label, severity (CRITICAL/MAJOR/MINOR), recommended_fix.

OUTPUT: Markdown.
GATE: 8 categories all reviewed.
```

---

### P81~P83 — LP Panel CP5: Action Label Lock

#### P81 (LP-A) — Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P79 CSV, P80 attack
🔹 **산출물:** `reports/llm_proxy/action_label_lock_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A) for Checkpoint CP5 (action_label_lock).

LOCK CONDITIONS (all must be ✅):
[ ] Every scenario has action_label (no NULL)
[ ] label_status = "adjudicated" or "ep_split_resolved", no draft/disputed/invalid
[ ] QUARANTINE q_code missing = 0
[ ] Q15 standalone = 0
[ ] Q17 = 0
[ ] EP inconsistent groups = 0
[ ] REPAIR without executor function = 0
[ ] adversarial attack (P80) all resolved
[ ] v4.2 specific labels present:
    REPAIR_CELLULAR_BLQ_*, REPAIR_IMMUNOGENICITY_*, REPAIR_MATERNAL_INFANT_*,
    QUARANTINE_*_Q19, QUARANTINE_*_Q18, QUARANTINE_*_Q16

If all checked: recommend AUTO LOCK.
If any unchecked: list and escalate.

OUTPUT per LP-A.
```

#### P82 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)

```
ROLE: Adversarial (LP-B).

Final attack before lock:
1. Grandmaster missed false AUTO?
2. Lock checklist verification incomplete?
3. v4.2 labels exist but content mismatched?
4. Any label that, after lock, would prevent v1.1 patches without major rework?

OUTPUT per LP-B.
```

#### P83 (LP-C) — Judge + 자동 Lock

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션)
🔹 **산출물:**
  - `reports/llm_proxy/action_label_lock_judge.md`
  - 자동 진행 시: `data/action_labels/scenario_action_table_locked.csv`
🔹 **다음 액션:** P84

```
ROLE: Judge (LP-C).

If auto-apply: copy scenario_action_table_after_ep_split.csv to scenario_action_table_locked.csv.
If escalate: route to H4 (release-stage, will be checked in Phase 10).

OUTPUT per LP-C template.
```

---

### P84 — Lock Hash + Dictionary

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P83 완료
🔹 **산출물:**
  - `release/v1.0/action_label_lock_v1_0.sha256`
  - `release/v1.0/action_label_lock_declaration.md`
  - `config/action_label_dictionary_v1_0.yaml`
🔹 **다음 액션:** P85

```
ROLE: Coding agent.

TASKS:
1. SHA256 of data/action_labels/scenario_action_table_locked.csv → .sha256 file
2. Generate config/action_label_dictionary_v1_0.yaml:
   - Each unique action_label → action_sequence + parameter_policy + terminal_state + q_code
   - Total unique label count expected: 80-200
3. Generate lock declaration with hash + LP Panel CP5 result + statistics
4. Update CHANGELOG: "## v0.7.0 — Action Label LOCKED"

OUTPUT: 3 files + CHANGELOG.
```

---

### P85 — Phase 7 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `reports/phase7_completion_declaration.md`
🔹 **다음 액션:** CHECK-7

```
ROLE: Documentation writer.

CHECKLIST:
[ ] scenario_action_table_locked.csv exists (hash file too)
[ ] action_label_dictionary_v1_0.yaml generated
[ ] Lock declaration signed (auto or escalated)
[ ] LP Panel CP4 (label_adjudication) resolved
[ ] LP Panel CP5 (label_lock) resolved
[ ] EP split resolved (P77-P79)
[ ] Q15 standalone = 0, Q17 = 0
[ ] q_code missing in QUARANTINE = 0
[ ] v4.2 specific labels present

OUTPUT: Markdown.
```

---

### 🐍 CHECK-7 (Phase 7 검증)

```python
# check_phase7.py
import os, sys, hashlib
from pathlib import Path

try:
    import pandas as pd
except ImportError: sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("❌"); sys.exit(1)

print("=" * 60)
print("CHECK-7: Phase 7 (Action Label Lock) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "data/action_labels/scenario_action_table_locked.csv",
    "config/action_label_dictionary_v1_0.yaml",
    "release/v1.0/action_label_lock_v1_0.sha256",
    "release/v1.0/action_label_lock_declaration.md",
    "scripts/label_workbench/detect_label_conflicts.py",
    "scripts/label_workbench/validate_equivalence_partitioning.py",
    "reports/equivalence_partition_report.md",
    "reports/phase7_completion_declaration.md",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file(): print(f"  ✅ {f.split('/')[-1]}")
    else: print(f"  ❌ {f}"); failures.append(f)

# Locked CSV 검사
loc = BASE / "data/action_labels/scenario_action_table_locked.csv"
if loc.is_file():
    df = pd.read_csv(loc)
    print(f"\n[Locked CSV: {len(df):,} 시나리오]")

    if "label_status" in df.columns:
        bad = df[~df["label_status"].astype(str).str.lower().isin(
            ["locked","adjudicated","ep_split_resolved","approved"])]
        if len(bad) == 0:
            print("  ✅ 모든 label 확정")
        else:
            print(f"  ❌ 미확정 {len(bad)}")
            failures.append(f"미확정 {len(bad)}")

    # q_code/Q15/Q17 검사
    if "q_code" in df.columns and "terminal_state" in df.columns:
        q_str = df["q_code"].astype(str).str.strip()
        qmask = df["terminal_state"] == "QUARANTINE"
        miss = (qmask & (df["q_code"].isna() | (q_str == ""))).sum()
        if miss == 0: print("  ✅ q_code 누락 0")
        else: failures.append(f"q_missing {miss}")

        if (q_str == "Q15").sum() == 0: print("  ✅ Q15 단독 0")
        else: failures.append("Q15 단독")

        if (q_str == "Q17").sum() == 0: print("  ✅ Q17 0")
        else: failures.append("Q17")

    # v4.2 라벨 패턴
    if "candidate_action_label" in df.columns or "action_label" in df.columns:
        col = "candidate_action_label" if "candidate_action_label" in df.columns else "action_label"
        labels_str = " ".join(df[col].dropna().astype(str).unique().tolist()).upper()
        v42_patterns = ["CELLULAR", "IMMUNOGEN", "MATERNAL", "ANALYTE_ROLE", "Q19", "Q18", "Q16"]
        for p in v42_patterns:
            if p in labels_str:
                print(f"  ✅ v4.2 라벨 패턴 {p}")
            else:
                print(f"  ⚠️  v4.2 라벨 패턴 {p} 누락")

    # [PATCH-B3] F30 부재 검증 (locked CSV family_id)
    if "family_id" in df.columns:
        f30_n = (df["family_id"].astype(str) == "F30").sum()
        if f30_n == 0:
            print("  ✅ F30 family_id 미사용 (reserved — 정상)")
        else:
            print(f"  ❌ F30 family_id {f30_n}개 발견 — 예약 번호 오사용")
            failures.append("F30 action label 오사용")

# Hash 검증
hf = BASE / "release/v1.0/action_label_lock_v1_0.sha256"
if hf.is_file() and loc.is_file():
    computed = hashlib.sha256(loc.read_bytes()).hexdigest()
    stored = hf.read_text().strip().split()[0]
    if computed == stored: print(f"\n  ✅ Hash 일치")
    else: print(f"  ❌ Hash 불일치"); failures.append("hash")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 7 완료")
    print("→ Step 3 (Phase 8~11) 진행 준비 완료")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## 📊 Step 2 종료 — 진행 상황 요약

```
✅ Phase 3 (P29-P40) — Pilot 데이터 + H1, H2 + Seed pack 20 카테고리 검증
✅ Phase 4 (P41-P52) — Repair Executor + 26 함수 + pytest + LP Panel CP3 (조건부)
✅ Phase 5 (P53-P65) — Scenario Generator + LP Panel CP2 + Universe FREEZE v1.0
✅ Phase 6 (P66-P70) — Decision Nodes (N0-N8) + Forced node 명시 + Cost Function
✅ Phase 7 (P71-P85) — Action Label + LP Panel CP4 + EP Split + LP Panel CP5 + LOCK

✅ CHECK-3, 4, 5, 6, 7 검증 스크립트

이 시점까지 추가된 핵심 산출물:
- D1 scenario_universe_v1.0.csv ✅ FROZEN with hash
- D2 scenario_action_table_locked.csv ✅ LOCKED with hash
- D7 repair_executor.py ✅ LOCKED with hash (26 functions, v4.2 7 new)
- pilot_fingerprints empirical_*.csv ✅ H2 approved
- golden_dataset_registry_draft.csv ✅ ≥3 candidates
- candidate_node_dictionary_with_costs.csv ✅ 9 nodes (N0-N8), 7 forced
- repair_rule_dictionary.yaml ✅ 26 rules
- LP Panel CP2, CP3, CP4, CP5 모두 처리 (CP3는 조건부)
  # LP Panel 실제 P번호 위치 (Step2 기준 확정값):
  # CP2 (universe_attack_and_freeze): P58~P60
  # CP3 (repair_semantic_review, 조건부): P48~P50
  # CP4 (action_label_adjudication): P74~P76
  # CP5 (action_label_lock): P81~P83

H-checkpoint 완료:
- H1 ✅ 비식별화
- H2 ✅ Fingerprint 사실 검토
- H3, H4, H5는 Step 3에서

다음 단계 (Step 3):
- Phase 8  (P86-P100):  Decision Table + ILP + LP Panel CP6
- Phase 9  (P101-P105): Operational Decision Tree + NONMEM QC + Lock
- Phase 10 (P106-P115): Golden Validation + H3 + H4 (강화, PATCH-5) + H5 + LP Panel CP7 + Release Tag
- Phase 11 (P116-P140): Change Control + 100-case Validation + SOP + Final Completion

> ⚠️ **[PATCH F-1]** 이 Phase 번호 범위는 Step 1 종료 요약의 기준표와 동기화된 확정값입니다.
> Step 3 파일의 진행 맵 헤더 및 체크리스트와 반드시 일치해야 합니다.
> 구버전 표기 `Phase 8 P86-P105`, `Phase 9 P106-P115`는 폐기합니다.

CHECK-8, CHECK-9, CHECK-10, CHECK-11 (최종)
```

> **Step 2 완주 후 실행자가 해야 할 일:**
>
> 1. Step 1을 정상적으로 완주 (CHECK-0, 1, 2 PASS)
> 2. Step 2를 시작하기 전 — 실제 데이터 또는 합성/공개 데이터 20개 이상 확보 (Pilot seed pack 20 카테고리 충족 위함)
> 3. P29부터 차례로 진행. 특히 H1 비식별화는 시간이 오래 걸리므로 여유롭게 잡으세요 (1-2일 권장)
> 4. H2는 LLM이 만든 fingerprint와 실제 파일을 한 줄씩 대조. 매우 중요한 단계입니다
> 5. P41-P52 Repair Executor는 Cursor에서 진행. pytest 통과 안 되면 에러 메시지를 그대로 LLM에 다시 붙여넣어 수정 요청
> 6. CHECK-7까지 PASS되면 Step 3로 넘어가도 됩니다
>
> **[PATCH Step2-3] D9 Option B 확정 선언 (Step1 v2와 동기화):**
> 이 플레이북은 100-case validation을 post-release operational stress test로 운용합니다 (Option B).
> D9(`coverage_claim_statement.md`)의 coverage claim 근거는 D8(golden validation) + H4(blinded audit) + pilot/seed-pack coverage이며,
> 100-case 결과는 v1.1 candidate register 트리거 용도입니다. Step 3 Phase 11에서 동일하게 확정됩니다.
>
> **Step 2 완료 후 "계속" 입력하시면 Step 3 (Phase 8~11, P86~P140)을 작성합니다.**
> Step 3는 ILP 최적화 + 결정 트리 + Golden 검증 + Release까지의 핵심 단계로,
> v5.1의 가장 중요한 PATCH-2 (ILP distinguishability 강화)와 PATCH-5 (H4 표본 감사)가 구현됩니다.

---

*PMX-to-NONMEM Scenario Universe v5.1 — Step 2 / 3*
*Phase 3-7 | Pilot + H1, H2 | Repair Executor v1.0 LOCK | Universe v1.0 FREEZE | Action Label LOCK*
*LP Panel CP2 (universe), CP3 (repair, conditional), CP4 (label adjudication), CP5 (label lock)*

---

### 📋 v5.1 Step 2 패치 이력 (patched_v3)

| 패치 ID | 대상 | 내용 | 심각도 |
|---|---|---|---|
| PATCH-B1 | CHECK-3 seed coverage | 18/20 → 20/20 정책 반영. 미충족 시 deferral_log + v1.1_register 존재 확인 후 조건부 허용. 그 외 failures 등록 | CRITICAL |
| PATCH-B2 | CHECK-5 family 검증 | F30 부재 검증 블록 추가 (F30 존재 시 failures 등록) | MINOR |
| PATCH-B3 | CHECK-7 locked CSV | F30 family_id 부재 검증 추가 | MINOR |
| PATCH-B4 | P41 repair rule dict | PATCH m-4 Q15A-D 사용 기준 명시 (BIOANALYTICAL-FINAL-FLAG → Q15A, REANALYSIS-FINAL → Q15D 등) | IMPORTANT |