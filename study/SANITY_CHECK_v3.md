# SANITY CHECK v3 — UX 재정비 (디자인 + 음슴체 + 일타강사 핵심)

> v2 작업물의 디자인·서술·배포 방식을 한 단계 끌어올리기 위한 검증 기준.
> 각 항목 옆에 `[PASS]` / `[FAIL: 이유]` 기입. 전체 PASS 후에만 산출물 출력.
>
> **결과: 18/18 PASS, 0 FAIL.** v2 회귀도 42/42 PASS 유지. `python3 study/_verify_v3.py`로 재현 가능.

---

## 산출물 (v3)

| 파일 | 경로 | 상태 |
|------|------|------|
| 메인 단일 파일 (file:// 동작) | `study/index_v3.html` (306 KB) | **[신규]** 데이터 인라인, 더블클릭으로 열림, 외부 의존성 0 |
| 검증 기준 (본 문서) | `study/SANITY_CHECK_v3.md` | **[신규]** |
| 디자인 템플릿 | `study/_v3_template.html` | **[신규]** HTML/CSS/JS 원본 (data placeholder만 비어있음) |
| HTML 빌드 스크립트 | `study/_build_v3_html.py` | **[신규]** template + data → index_v3.html |
| R 코드 보강 빌드 | `study/_build_v3.py` | **[신규]** v3_* prefix 키 추가 (기존 키 무변경 보장) |
| 검증 스크립트 | `study/_verify_v3.py` | **[신규]** |
| R 코드 보강 (v3 키 추가) | `study/data/r_code_library.json` | **[갱신]** 12개 노드 × 4개 v3_* 키 = 48 신규 키 추가. 기존 키 무변경 |
| **참조 보존** | `study/index_v2.html`, `study/tree_v2_standalone.html`, `study/dashboard/*.html`, FROZEN 9개 데이터 | **[미변경]** SHA·size 동일 |

---

## D — 디자인 (Design) — 7/7 PASS

| # | 항목 | 결과 |
|---|------|------|
| D-1 | 트리 SVG가 **항상 viewport에 fit** — viewBox + `preserveAspectRatio="xMidYMid meet"` 사용, CSS `width:100%; height:100%`로 창 크기 변경 시 자동 재조정 | **[PASS]** viewBox + preserveAspectRatio meet + CSS 100% — 자동 fit |
| D-2 | 기본 상태에서 **pan/zoom 비활성화** — 사용자가 명시적으로 "탐색 모드 🔍" 토글을 켜야만 드래그/휠 동작. 그 외에는 트리가 자기 자리 지킴 | **[PASS]** `viewport.exploring = false` 기본 + `if (!exploring) return` 가드 + 토글 버튼 |
| D-3 | 노드가 **클릭 가능한 충분한 크기** — 내부 노드 원 반지름 viewBox 단위 ≥ 28, leaf 사각형 가로 ≥ 70px | **[PASS]** NODE_R=28, LEAF_W=70 |
| D-4 | **현재 위치 강조** — 선택한 노드가 (a) 외곽선 두께 5px 이상, (b) 펄스/글로우 애니메이션, (c) 패널 상단 breadcrumb에 노드 ID + 한국어 제목, 세 가지 모두 표시 | **[PASS]** `@keyframes pulse-glow` + `stroke-width: 7` + `<div class="tree-breadcrumb">` + `updateBreadcrumb()` 셋 모두 |
| D-5 | **색 팔레트 일관성** — 한 화면 안에서 5색 토큰(forced/optional/auto/repair/quar/invalid) 외 추가 색 사용 최소화. 카드 배경·강조색 모두 토큰 기반 | **[PASS]** 6개 노드 색 토큰 정의 (5색 + invalid 회색), 보조 색은 토큰 변형(linear-gradient)만 사용 |
| D-6 | **여백/위계 정돈** — 모든 카드 16px+ padding, 헤더 폰트 ≥ 14px, 본문 ≥ 12px, 라벨 ≥ 11px. 카드 간 12~16px gap, 섹션 간 24px+ | **[PASS]** `--pad: 16px`, `h2 17px`, `body 13px`, h3 margin 24px |
| D-7 | **고정 헤더** — 상단 헤더는 스크롤해도 사라지지 않음 (FORCED 카운터·Quick Ref 항상 접근) | **[PASS]** `header { flex: 0 0 auto }` + `body { display: flex; flex-direction: column; height: 100vh }` |

---

## E — 서술 (Editorial) — 6/6 PASS

| # | 항목 | 결과 |
|---|------|------|
| E-1 | **음슴체 통일** — 사용자에게 보이는 모든 한국어 텍스트가 `~음/함/임/됨` 형태로 통일 (모달, 패널, 헤더, 카드 모두). "~합니다", "~해주세요" 같은 정중체 제거 | **[PASS]** HTML/JS 영역에서 합니다/입니다/주세요/하세요/십시오/십니다 패턴 0건 |
| E-2 | **실무 비율 명시** — 각 forced 노드(N0~N5, N8)의 v3 context에 "실무에서 약 X%는 …" 같은 구체 수치 또는 분포 표현 1개 이상 포함 | **[PASS]** forced 7개 모두 `practical_distribution`에 % 또는 "약 X" 표현 포함 |
| E-3 | **raw 데이터 형태 명시** — 각 forced 노드의 v3 context에 "raw 데이터에서는 보통 `<컬럼명>` 같은 형태로 옴" 같이 입력 데이터 모양을 한 줄 예시로 보여줌 | **[PASS]** forced 7개 모두 `raw_data_shape`에 백틱(`)으로 묶인 코드 예시 포함 |
| E-4 | **NONMEM 잘 돌아가는 조건** — 각 forced 노드의 v3 context에 "이렇게 처리되어야 NONMEM이 잘 돌아감" 같이 결과 조건을 명시 | **[PASS]** forced 7개 모두 `nonmem_condition`에 'NONMEM' 언급 + 조건 서술 |
| E-5 | **어려운 용어 풀이** — 각 forced 노드의 v3 context에 도메인 약어 1개 이상을 평이한 말로 풀어씀 (예: "AIC(분석 의도 계약)") | **[PASS]** forced 7개 모두 `glossary`에 '용어 = 풀이' 형태 포함 |
| E-6 | **R 코드 일타강사 핵심** — 각 forced 노드의 보강된 R 블록(check/pass) 옆에 "✨ 일타강사의 핵심" 한 줄 (왜 이 패턴인지, 흔한 함정, 좋은 습관 형성 이유) | **[PASS]** forced 7개 모두 `v3_r_code_kpoint`에 '✨ 일타강사의 핵심' 표현 포함 |

---

## T — 기술/배포 (Technical) — 5/5 PASS

| # | 항목 | 결과 |
|---|------|------|
| T-1 | **file:// 더블클릭 동작** — `index_v3.html`을 macOS Finder에서 더블클릭 열거나 `open file:///…/index_v3.html` 실행 시 모든 기능 정상 작동 | **[PASS]** `window.__INLINE_DATA__` 인라인 + `if (window.__INLINE_DATA__)` 분기 가드 — fetch 호출 자체가 일어나지 않음 |
| T-2 | **외부 의존성 0** — `<script src="https://…">`, `<link href="https://…">` 등 외부 CDN 의존성 없음. highlight.js 인라인 또는 graceful fallback | **[PASS]** 외부 https 의존성 0건. R 코드는 monospace pre 태그로 plain text 표시 (highlight 없이도 가독성 OK) |
| T-3 | **FROZEN 9개 데이터 무변경** — Phase 0 baseline SHA-256 일치 | **[PASS]** tree/nodes/universe/decision_table/action_labels/labels_ko/q_codes/axis_dictionary/summary 9개 모두 baseline 일치 |
| T-4 | **r_code_library 기존 키 무변경** — v3 보강은 신규 키(`v3_*` prefix)만 추가 | **[PASS]** `v3_*` 제외한 모든 키가 v2 시점 r_code_library와 deep-equal. `_build_v3.py`의 자체 검증으로도 보장 |
| T-5 | **v2 산출물 보존** — `study/index_v2.html`, `study/tree_v2_standalone.html` 미변경 + v2 검증 회귀 없음 | **[PASS]** v2 산출물 size 동일 (74,488 byte / 3,539,231 byte). v2 자기검증 `_verify_v2.py` 42/42 PASS 유지 |

---

## 검증 절차

1. **자동 검증** (재현):
   ```bash
   cd /Users/min9/Documents/GitHub/pmx_universe_v5_1
   python3 study/_verify_v3.py    # 결과: 18/18 PASS
   python3 study/_verify_v2.py    # 결과: 42/42 PASS (v2 무회귀)
   ```
2. **수동 file:// 검증**: `open study/index_v3.html` (macOS Finder 더블클릭과 동일)
   - 트리가 화면에 한눈에 들어오는지
   - 노드 클릭 시 펄스 강조 + 상단 breadcrumb 갱신
   - "🔍 자유 탐색" 토글 켜야만 드래그/줌 동작
   - Quick Ref 📋 슬라이드, FORCED 카운터 동작

---

## 통과 조건

D 7개 + E 6개 + T 5개 = **총 18개 모두 PASS**.
**최종 결과: 18/18 PASS, 0 FAIL, 0 MANUAL-필수.**
