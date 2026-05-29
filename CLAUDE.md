# PMX Wrangling Tree — UX 개선 지시서
## Claude Code 전용 | v2.0
## 작업 위치: `/Users/min9/Documents/GitHub/pmx_universe_v5_1`

---

## ⚠️ 이 작업의 성격 — 반드시 먼저 읽어라

이 작업은 **처음부터 다시 만드는 것이 아니다.**

기존 HTML 3개(`study/index.html`, `study/tree_artifact.html`,
`study/tree_artifact_full.html`)는 **데이터와 로직이 이미 올바르게 구현**되어 있다.
시나리오 universe, 노드 구조, Q-code, terminal_state, 경로 추적 — 전부 정상 동작한다.

**이 작업의 목표는 단 하나:**
> 초보자가 처음 열었을 때 "어리둥절"하지 않도록
> UX·시각화·교육적 설명을 개선하는 것.

---

## FROZEN — 절대 건드리지 말 것

아래는 이미 검증된 산출물이다. **내용 변경 금지.**

```
data/tree.json
data/nodes.json
data/universe.json
data/decision_table.json
data/action_labels.json
data/labels_ko.json
data/q_codes.json
data/axis_dictionary.json
data/summary.json
```

> `data/r_code_library.json`만 예외: R 코드가 부재하거나 미흡한 노드에
> 내용을 **추가**할 수 있다. 기존 항목 수정은 금지.

---

## PHASE 0: 시작 전 현황 파악 (필수, 단 20분 이내)

아래 파일만 읽어라. md 원본 3개는 읽지 않아도 된다.
데이터는 이미 `data/*.json`에 인코딩되어 있다.

### 읽을 파일 (우선순위 순)

| 순서 | 파일 | 목적 |
|------|------|------|
| 1 | `study/index.html` | 기존 JS 로직, 탭 구조, 데이터 로딩 방식 파악 |
| 2 | `data/tree.json` | 트리 내부 노드 구조, yes_branch/no_branch 확인 |
| 3 | `data/nodes.json` | 노드별 detection_rule, rationale, q_code_if_fail |
| 4 | `data/r_code_library.json` | 기존 R 코드 라이브러리 보강 필요 여부 확인 |
| 5 | `data/labels_ko.json` | 한국어 라벨 및 node_question_ko 확인 |

파악 완료 후 아래 형식으로 보고하라:

```
[현황 파악 완료]
- 트리 내부 노드 수: N개
- Forced 노드: {N0, N1, ...}
- r_code_library.json 보강 필요 노드: [목록]
- 기존 HTML에서 재사용할 JS 함수: [목록]
- 기존 HTML에서 교체할 부분: [목록]
```

---

## PHASE 1: 검증 기준 확립

> ⛔ 코딩 전 반드시 먼저 수행.
> 파일명: `study/SANITY_CHECK_CRITERIA.md`
> 작성 후 보고. **코딩은 그 다음이다.**

---

### [SC-1] 기존 로직 보존 확인

- [ ] `data/*.json` (r_code_library 제외) 파일 내용 변경 없음
- [ ] 기존 경로 추적(시나리오 시뮬레이터) 기능 정상 동작
- [ ] 기존 Universe Browser 탭 정상 동작
- [ ] 기존 Q-code/terminal_state 분류 로직 변경 없음

### [SC-2] 시각 디자인 기준

- [ ] Decision tree가 **top-down 수직** 방향으로 렌더링됨
- [ ] 노드 간 연결선이 **수직/수평 꺾임선(elbow connector)** — bezier 곡선 금지
- [ ] 화면 첫 진입 시 트리 전체가 **한눈에** 들어옴 (zoom-to-fit)
- [ ] Forced 노드(N0·N1·N2·N3·N4·N5·N8): **빨강**, 즉시 구별
- [ ] Optional 노드: **파랑**, 즉시 구별
- [ ] Leaf 4종 색상 구별: AUTO(녹색) / REPAIR(주황) / QUARANTINE(진빨강) / INVALID(회색)
- [ ] vis-network 의존성 완전 제거됨

### [SC-3] 초보자 친화도 기준

- [ ] 각 노드 패널 상단에 **"지금 이 상황은?"** 실무 맥락 (1–2문장)
- [ ] 각 노드 패널에 **"이 판단이 중요한 이유"** (놓쳤을 때 어떤 오류가 나는지)
- [ ] 각 노드 패널에 **Before 테이블** (문제 셀: 빨간 배경, 노드별 고유 예시)
- [ ] 각 노드 패널에 **After 테이블** (변경 셀: 초록 배경, 노드별 고유 예시)
- [ ] R 코드 블록에 **"미래의 나" 페르소나** 헤더 및 한국어 주석
- [ ] R 코드: **tidyverse 파이프** (`|>`) + 명시적 네임스페이스(`dplyr::mutate` 등)
- [ ] 각 leaf 패널에 **end-to-end R 스크립트** (대표 시나리오 1개)
- [ ] **Forced 게이트 학습 카운터** ("7개 중 N개 학습 완료")

### [SC-4] 기술 안정성 기준

- [ ] vis-network CDN 제거, 대체 렌더러 정상 동작
- [ ] `data/*.json` 로드 실패 시 명확한 에러 메시지 출력
- [ ] 브라우저 콘솔 JS 에러 없음 (기본 탐색 흐름 기준)

---

## PHASE 2: UX 개선 구현

### 산출물 (기존 파일은 덮어쓰지 말 것)

| 파일 | 설명 |
|------|------|
| `study/index_v2.html` | 메인 개선 버전 (HTTP 서버 모드, `data/*.json` fetch) |
| `study/tree_v2_standalone.html` | 독립 실행 버전 (모든 데이터 인라인 embed) |

> 기존 `index.html`, `tree_artifact.html`, `tree_artifact_full.html`은
> **절대 덮어쓰지 말 것.** 참조용으로 보존한다.

---

### 2-A. 재사용할 것 vs 교체할 것

#### 재사용 (기존 index.html에서 가져올 것)

```
✅ 재사용
- 데이터 로딩 로직 (fetchJson, load() 함수)
- detectionRules 객체 (N0~N29 판정 함수)
- 경로 추적 탭 (시나리오 → 경로 하이라이트) — UX만 다듬기
- Universe Browser 탭 (통계 분포)
- 한국어 라벨 헬퍼 함수 (lblTerminal, lblQ 등)
- 탭 전환 로직
```

#### 교체 (새로 구현할 것)

```
❌ 교체
- vis-network → 순수 SVG top-down 트리
- 노드 클릭 → 상세 패널 (4섹션 구조로 전면 개편)
- 전체 CSS (초보자 친화 레이아웃으로)
```

---

### 2-B. Decision Tree 재구현 — SVG top-down

**핵심 요구사항:**

1. **레이아웃 알고리즘**
   - BFS로 각 노드 depth 계산
   - 같은 depth 노드들을 수평 균등 배치
   - 부모→자식: 부모 하단 중앙 → 자식 상단 중앙을 잇는 **L-shape elbow** (`M x1 y1 L x1 mid L x2 mid L x2 y2`)
   - YES 분기: 녹색 실선 + `"예"` 라벨
   - NO 분기: 빨간 점선 + `"아니오"` 라벨
   - 수직 간격: 최소 90px / 수평 간격: 최소 60px

2. **노드 스펙**

   | 유형 | 모양 | 색상 | 라벨 |
   |------|------|------|------|
   | FORCED 내부 노드 | 원, r=22px | `#e74c3c` | `"N0"` 등, 흰색 볼드 |
   | OPTIONAL 내부 노드 | 원, r=22px | `#2980b9` | `"N11"` 등, 흰색 |
   | Leaf AUTO | 둥근 rect | `#27ae60` | `"AUTO"` |
   | Leaf REPAIR | 둥근 rect | `#f39c12` | `"REPAIR"` |
   | Leaf QUARANTINE | 둥근 rect | `#c0392b` | Q-code, 흰색 |
   | Leaf INVALID | 둥근 rect | `#7f8c8d` | `"INVALID"` |

3. **인터랙션**
   - 호버: `#ffe066` 테두리, `cursor: pointer`
   - 선택: 두꺼운 `#f39c12` 테두리 → 우측 패널 갱신
   - pan/zoom: 마우스 드래그 + 휠 지원

---

### 2-C. 노드 상세 패널 — 4섹션 구조

노드를 클릭하면 우측 패널에 아래 4섹션이 순서대로 표시된다.

---

#### 섹션 1: 실무 맥락 카드

배경색: `#eaf4fb` (연파랑), 왼쪽 보더: 4px `#2980b9`

```
📍 지금 이 상황은?
[node.summary_ko 또는 r_code_library의 실무 맥락 1–2문장]

⚠️ 이 판단이 중요한 이유
[놓쳤을 때 어떤 오류가 나는지 2–3문장]
```

노드별 실무 맥락 예시 (이 수준의 구체성으로 작성할 것):

| 노드 | 실무 맥락 |
|------|-----------|
| N0 | "분석 의뢰서(AIC)가 있는지, endpoint 유형이 선언되었는지 확인합니다. 이게 없으면 이후 모든 처리 방향이 흔들립니다." |
| N1 | "피험자 ID가 유일하게 정의 가능한지 확인합니다. 여러 시험 데이터가 합쳐질 때 ID 충돌이 자주 생깁니다." |
| N2 | "TIME 컬럼이 NONMEM이 읽을 수 있는 형태인지 확인합니다. 실제 시각(clock time)과 투약 후 경과 시간(elapsed)이 섞여 있는 경우가 흔합니다." |
| N3 | "투약 정보(AMT, DOSE)가 복구 가능한지 확인합니다. 용량 정보가 없으면 PK 모델링 자체가 불가능합니다." |
| N4 | "관측값(DV) 컬럼이 사용 가능한 상태인지 확인합니다. BLQ 처리 정책과 LLOQ가 명시되어야 합니다." |
| N5 | "BLQ(정량 한계 미만) 데이터를 NONMEM 규칙에 맞게 DV=0, MDV=1로 변환합니다. 이걸 빠뜨리면 NONMEM이 경고 없이 틀린 결과를 냅니다." |
| N8 | "제안된 처리 방식에 필요한 모든 정책이 AIC에 선언되어 있는지 마지막으로 확인합니다." |

---

#### 섹션 2: Before → After 데이터 미리보기

**구현 규칙:**
- HTML `<table>`로 구현 (ASCII 아님)
- 문제 셀: `background: #fdecea; color: #922b21; font-weight: bold`
- 변경 셀: `background: #d5f5e3; color: #186a3b; font-weight: bold`
- 각 노드마다 **노드 고유 예시** — 모든 노드에 동일 테이블 금지
- 테이블 위에 화살표 배지: `📊 Before → 📊 After`

**노드별 Before/After 예시 (이 수준으로 작성):**

N5 (BLQ 표준화):
```
Before:                          After:
ID  TIME  DV     EVID           ID  TIME  DV   EVID  MDV
1   0     NA     1              1   0     NA   1     1
1   2     45.2   0              1   2     45.2 0     0
1   4     BQL    0   ← ⚠️       1   4     0    0     1   ← ✅변경
2   0     NA     1              2   0     NA   1     1
2   6     12.8   0              2   6     12.8 0     0
```

N1 (ID 중복 해소):
```
Before:                          After:
ID   STUDY  TIME  DV            ID      STUDY  TIME  DV
1    A      2     45.2          A_001   A      2     45.2
1    B      4     12.8  ← ⚠️   B_001   B      4     12.8  ← ✅변경
2    A      0     NA            A_002   A      0     NA
```

N2 (TIME 표준화):
```
Before:                          After:
ID  CLOCK_TIME  DV              ID  TIME   DV
1   08:00       NA              1   0      NA
1   10:30       45.2  ← ⚠️    1   2.5    45.2   ← ✅변경
1   14:00       12.8  ← ⚠️    1   6.0    12.8   ← ✅변경
```

---

#### 섹션 3: R 코드 블록

헤더 (항상 표시):

```
💬 미래의 내가 알려주는 베스트 코딩 방법
"이 상황에서 R은 이렇게 쓰는 게 가장 깔끔하고 효율적이야.
 이 순서로 습관 들여놓으면 나중에 진짜 편해."
```

**코드 표시 규칙:**
- highlight.js R 언어 syntax highlight
- 우측 상단 복사 버튼
- 코드 앞 3–5줄 한국어 주석 필수
- tidyverse 파이프 `|>` 우선
- 명시적 네임스페이스 (`dplyr::`, `tidyr::` 등)
- 변수명 `snake_case`

**코드 블록 순서 (노드마다):**

```
① 판정 코드 — "이 데이터가 이 노드를 통과할 수 있는지 확인"
② YES 처리 코드 — "통과하면 이렇게 변환"
③ 왜 이렇게 쓰는지 팁 — ✅ 주석으로
```

**강제 노드 7개 R 코드 템플릿 (이 수준으로 구현):**

```r
# ── [N5] BLQ 표준화 ───────────────────────────────────────────────
# BLQ 행은 NONMEM 규칙상 DV=0, MDV=1로 바꿔줘야 해.
# 그냥 NA나 문자열 "BQL"로 두면 NONMEM이 읽다가 에러 내거나
# 조용히 무시해버려서 결과가 완전히 틀어질 수 있어.

canonicalize_blq <- function(df) {
  df |>
    dplyr::mutate(
      MDV = dplyr::case_when(
        DV %in% c("BQL", "BLQ", "blq") ~ 1L,  # BLQ → 무시 플래그
        EVID == 1L                      ~ 1L,  # 투약행도 MDV=1
        .default                        = 0L
      ),
      DV = dplyr::case_when(
        MDV == 1L & EVID == 0L ~ 0,           # BLQ만 DV=0
        .default               = as.numeric(DV)
      )
    )
}

pk_ready <- pk_raw |> canonicalize_blq()

# ✅ case_when vs ifelse: 조건이 3개 이상이면 case_when이 훨씬 안전해.
# ifelse 중첩은 나중에 조건 추가할 때 버그 유입 위험이 커.
```

---

#### 섹션 4: 다음 분기 네비게이션

```
이 노드의 판정 결과:
  ✅ YES → [다음 노드 이름 + 클릭 가능 버튼]  "→ 무슨 확인으로"
  ❌  NO → [결과 이름 + 클릭 가능 버튼]       "→ 어떤 처리로"
```

버튼 클릭 시 해당 노드를 트리에서 선택 상태로 전환 + 패널 갱신.

---

### 2-D. 상단 고정 바

화면 최상단에 항상 표시:

```
[PMX Wrangling Tree v5.1]  |  FORCED 게이트: ●●●○○○○ (3/7 학습)  |  [Quick Ref 📋]
```

- **FORCED 게이트 카운터**: 빨간 원 7개, 클릭했던 강제 노드는 채워짐 (localStorage)
- **Quick Ref 버튼**: 클릭 시 슬라이드 패널 오픈

---

### 2-E. Quick Reference 패널 (슬라이드형)

오른쪽에서 슬라이드 인. 항상 접근 가능.

**포함 내용:**

**① NONMEM 필수 컬럼**

| 컬럼 | 의미 | 없으면? |
|------|------|---------|
| `ID` | 피험자 고유 번호 | 개체 구분 불가 |
| `TIME` | 투약 후 경과 시간(h) | 시간 축 없음 |
| `DV` | 농도 관측값 | 모델링 불가 |
| `EVID` | 이벤트 종류 (0=관측, 1=투약) | 투약/관측 구분 불가 |
| `MDV` | 누락 플래그 (BLQ·투약행=1) | BLQ 처리 오류 |
| `AMT` | 투약량 | 용량-반응 관계 없음 |
| `CMT` | 구획 번호 | 다구획 모델 불가 |

**② terminal_state 4종**

| 상태 | 색 | 의미 | 다음 행동 |
|------|-----|------|-----------|
| AUTO | 녹색 | 정책 없이 자동 처리 가능 | R 코드 바로 실행 |
| REPAIR | 주황 | AIC 정책 선언 후 수리 가능 | 분석자에게 정책 확인 |
| QUARANTINE | 진빨강 | 처리 보류, 사유 기록 | Q-code 확인 후 의뢰자 문의 |
| INVALID | 회색 | 처리 불가 | 데이터 재수령 필요 |

**③ Q-code 목록** (Q01–Q19, Q17 제외 — v4.2 기각)

---

## PHASE 3: R 코드 라이브러리 보강

`data/r_code_library.json`에서 아래 항목이 **없거나 미흡한 노드만** 추가하라.
기존 항목은 수정하지 말 것.

### 추가 대상 우선순위

1. **최우선**: Forced 노드 7개 — N0, N1, N2, N3, N4, N5, N8
2. **차순위**: Optional 노드 — N11, N13, N14, N17, N19, N20, N21, N22, N24, N25, N27, N29

### 추가할 필드 형식

```json
{
  "node_id": "N5",
  "summary_ko": "실무 맥락 1–2문장 (초보자 언어로)",
  "persona_intro": "미래의 나 페르소나 (친근한 말투, 1문장)",
  "context_card": {
    "situation": "지금 이 상황은? 설명",
    "why_important": "놓치면 어떤 오류가 나는지"
  },
  "data_state_before": {
    "stage": "이 노드 진입 전 단계명",
    "before_table_html": "<table>...</table>",
    "problem_cells": ["문제 셀 설명"]
  },
  "data_state_after": {
    "after_table_html": "<table>...</table>",
    "changed_cells": ["변경 내용 설명"]
  },
  "r_code_check": "# 판정 R 코드 (tidyverse, 한국어 주석)",
  "r_code_pass": "# YES 처리 R 코드",
  "r_code_fail": null,
  "best_practice_tips": [
    "왜 이 순서로 쓰는지",
    "초보가 흔히 하는 실수",
    "이 습관이 나중에 왜 편한지"
  ]
}
```

---

## PHASE 4: 검증 실행

산출물 완성 후 `study/SANITY_CHECK_CRITERIA.md`의 모든 항목을 직접 검토.
각 항목에 `[PASS]` 또는 `[FAIL: 이유]` 기입.

FAIL 있으면 즉시 수정 → 재검토. **전체 PASS 후에만 보고.**

---

## PHASE 5: 최종 보고 형식

```
## 산출물
- study/index_v2.html             [신규]
- study/tree_v2_standalone.html   [신규]
- study/SANITY_CHECK_CRITERIA.md  [신규]
- data/r_code_library.json        [보강, 기존 항목 무변경]

## 기존 파일 보존 확인
- study/index.html              ✅ 미변경
- study/tree_artifact.html      ✅ 미변경
- study/tree_artifact_full.html ✅ 미변경
- data/*.json (r_code_lib 제외) ✅ 미변경

## 검증 결과
- SC-1 기존 로직 보존: X/4 PASS
- SC-2 시각 디자인:    X/7 PASS
- SC-3 초보자 친화도:  X/8 PASS
- SC-4 기술 안정성:    X/3 PASS

## 알려진 제약
- [없으면 "없음"]
```

---

## 절대 금지 사항

| # | 금지 |
|---|------|
| 1 | 기존 `data/*.json` (r_code_library 제외) 내용 변경 |
| 2 | 기존 `study/index.html` 등 3개 파일 덮어쓰기 |
| 3 | vis-network 재사용 (완전 새 SVG 구현) |
| 4 | 모든 노드에 동일한 제네릭 Before/After 테이블 사용 |
| 5 | 영어만으로 된 R 주석 (한국어 병기 필수) |
| 6 | tidyverse 없이 base R 중첩 ifelse로 복잡한 변환 구현 |
| 7 | Q17 언급 (v4.2에서 기각된 코드) |
| 8 | SANITY_CHECK_CRITERIA.md 작성 전 코딩 시작 |

---

## 운용 팁

| 상황 | 대응 |
|------|------|
| Phase 0 보고 없이 코딩 시작 | "현황 파악 보고부터 해주세요" |
| Before/After 테이블이 모든 노드에 동일 | "노드별 고유 예시 데이터로 재작업" |
| vis-network 코드 등장 | "SVG 직접 구현으로 교체" |
| 기존 json 파일 변경 시도 | "FROZEN 파일입니다. 변경 불가" |
| 컨텍스트가 길어질 때 | Phase별 중간 보고 요청으로 집중 유지 |

---

*PMX Wrangling Tree — UX 개선 지시서 v2.0*
*목적: 기존 산출물 보완 (데이터·로직 보존, UX·교육성 개선)*
