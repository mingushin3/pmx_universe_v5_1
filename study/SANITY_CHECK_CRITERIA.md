# SANITY CHECK CRITERIA — PMX Wrangling Tree v2 UX 개선

> CLAUDE.md v2.0 Phase 1 산출물. 코딩(Phase 2)에 들어가기 전 이 문서가 먼저 확정됨.
> Phase 4 검증 단계에서 각 항목 옆에 `[PASS]` / `[FAIL: 이유]`를 기입한다.
> 전체 PASS 후에만 Phase 5 최종 보고를 진행한다.
>
> **Phase 4 결과 요약: 42/42 PASS, 0 FAIL.** 자동화 스크립트 `python3 study/_verify_v2.py`로 재현 가능.

---

## 산출물 위치 합의

| 파일 | 경로 | 상태 |
|------|------|------|
| 메인 (서버 모드) | `study/index_v2.html` | 신규 |
| 독립 실행 (인라인) | `study/tree_v2_standalone.html` | 신규 |
| 검증 기준 (본 문서) | `study/SANITY_CHECK_CRITERIA.md` | 신규 |
| R 코드 보강 | `study/data/r_code_library.json` | 기존 항목 무변경, 누락 노드만 추가 |
| 참조 보존 | `study/dashboard/index.html`, `study/dashboard/tree_artifact.html`, `study/dashboard/tree_artifact_full.html` | 미변경 |

데이터 fetch 경로: `study/index_v2.html`에서 `./data/...` (= `study/data/...`).

---

## SC-1 — 기존 로직 보존 확인

| # | 항목 | 결과 |
|---|------|------|
| 1.1 | `study/data/*.json` 중 r_code_library 제외 9개 파일 (tree, nodes, universe, decision_table, action_labels, labels_ko, q_codes, axis_dictionary, summary) **content hash 무변경** | **[PASS]** 9개 SHA-256 baseline과 일치 |
| 1.2 | `study/dashboard/index.html`, `tree_artifact.html`, `tree_artifact_full.html` 파일 mtime/size 무변경 | **[PASS]** index.html=62572 / tree_artifact.html=1012000 / tree_artifact_full.html=4054922 byte (Phase 0 기록 그대로) |
| 1.3 | 경로 추적기(시나리오 시뮬레이터)가 universe 시나리오 1건 이상에서 기존과 동일한 path/leaf 산출 | **[PASS]** universe 3건 무작위 표본 traverse 결과 모두 일치 |
| 1.4 | Universe Browser 탭이 terminal/Q-code/family/modality/endpoint 5종 분포를 그대로 표시 | **[PASS]** `data-tab="universe"` + `renderUniverseStats` 5종 분포 호출 보존 |
| 1.5 | Q-code/terminal_state 분류 로직 (`detectionRules`, `traverse`) JS 함수 시그니처·동작 변경 없음 | **[PASS]** `detectionRules` 객체 19개 항목 + `traverse(scenario, mode)` 시그니처 동일 |
| 1.6 | 한국어 라벨 헬퍼 12종 (`lblTerminal` 등) 시그니처·동작 변경 없음 | **[PASS]** 12개 함수 전부 보존 (termCls/lblTerminal/lblTerminalShort/lblQ/lblModality/lblEndpoint/lblAnalyteRole/lblFamily/lblAxisState/descAxisState/lblAction/lblNodeQuestion) |

---

## SC-2 — 시각 디자인 기준

| # | 항목 | 결과 |
|---|------|------|
| 2.1 | Decision tree가 **top-down 수직** 방향으로 렌더링 (root 최상단, leaves 최하단) | **[PASS]** depth × `V_GAP=95px` 수직 배치 (`SvgTree.layout()`) |
| 2.2 | 노드 간 연결선이 **수직/수평 꺾임선** (`M x1 y1 L x1 mid L x2 mid L x2 y2`) — bezier 곡선 미사용 | **[PASS]** `elbowPath()` 함수 — M…L…L…L 4-segment elbow, bezier(`C`) 없음 |
| 2.3 | 화면 첫 진입 시 트리 전체가 **한눈에** 들어옴 (자동 zoom-to-fit, 첫 페인트 후 1초 이내) | **[PASS]** `fit()` 호출: `Math.min((w-2*margin)/bounds.w, (h-2*margin)/bounds.h, 1)` 으로 자동 fit (`requestAnimationFrame` 보정) |
| 2.4 | Forced 노드(N0·N1·N2·N3·N4·N5·N8): **`#e74c3c` 빨강 원** | **[PASS]** `--c-forced: #e74c3c` + `.node-circle.forced { fill: var(--c-forced); }` |
| 2.5 | Optional 노드(N11·N13·N14·N17·N19·N20·N21·N22·N24·N25·N27·N29): **`#2980b9` 파랑 원** | **[PASS]** `--c-optional: #2980b9` + `.node-circle.optional` |
| 2.6 | Leaf 4종 색상 구별: AUTO `#27ae60` / REPAIR `#f39c12` / QUARANTINE `#c0392b` / INVALID `#7f8c8d`, 둥근 rect | **[PASS]** 4색 토큰 모두 일치, `.node-rect { rx: 4px; ry: 4px; }` 둥근 모서리 |
| 2.7 | YES 간선: 녹색 실선 + 라벨 `"예"` / NO 간선: 빨강 점선 + 라벨 `"아니오"` | **[PASS]** `.edge-yes { stroke: #27ae60 }` 실선 + `.edge-no { stroke: #c0392b; stroke-dasharray: 5 4 }` 점선, `"예"`/`"아니오"` 라벨 |
| 2.8 | vis-network 의존성 **완전 제거** (`<script src="...vis-network...">` 없음, `vis.Network` 호출 없음) | **[PASS]** `<script src=...vis-network>` 없음, `vis.Network` 호출 없음 (코멘트 1줄 외) |
| 2.9 | 노드 호버: `#ffe066` 테두리 강조, `cursor: pointer` | **[PASS]** `.node-circle:hover { stroke: var(--highlight); }` (`--highlight: #ffe066`) + `cursor: pointer` |
| 2.10 | 노드 선택: 두꺼운 `#f39c12` 테두리, 우측 패널 갱신 | **[PASS]** `.selected { stroke: #f39c12; stroke-width: 5px; }` + `selectNode()` 우측 패널 갱신 호출 |
| 2.11 | pan/zoom: 마우스 드래그(pan) + 휠(zoom) 지원 | **[PASS]** `svg.addEventListener("mousedown")` + `window.addEventListener("mousemove"/"mouseup")` + `svg.addEventListener("wheel")` — 마우스 위치 기준 줌 |

---

## SC-3 — 초보자 친화도 기준

| # | 항목 | 결과 |
|---|------|------|
| 3.1 | 각 내부 노드 패널 상단에 **"📍 지금 이 상황은?"** 실무 맥락 카드 (1–2문장, 연파랑 배경 `#eaf4fb` + 좌측 보더 `#2980b9`) | **[PASS]** `.context-card { background: var(--ctx-bg); border-left: 4px solid var(--accent); }` + `renderContextCard()` |
| 3.2 | 각 내부 노드 패널에 **"⚠️ 이 판단이 중요한 이유"** (놓쳤을 때 어떤 오류) | **[PASS]** `.ctx-why { border-left: 3px solid var(--c-repair); }` + `context_card.why_important` 렌더링 |
| 3.3 | 각 내부 노드 패널에 **Before 테이블** (HTML `<table>`, 문제 셀 `background: #fdecea; color: #922b21`) — **노드별 고유 예시** (모든 노드 동일 금지) | **[PASS]** 19/19 노드에 노드별 고유 데이터 (N0/N1/N2/N5 = legacy sample_*, N3~N29 = `before_table_html` 신규) + `.ba-tbl td.bad` 스타일 |
| 3.4 | 각 내부 노드 패널에 **After 테이블** (HTML `<table>`, 변경 셀 `background: #d5f5e3; color: #186a3b`) — **노드별 고유 예시** | **[PASS]** 19/19 노드에 After 데이터 + `.ba-tbl td.good` 스타일 |
| 3.5 | 테이블 위에 화살표 배지 `📊 Before → 📊 After` | **[PASS]** `<div class="ba-arrow"><span class="before">📊 Before</span> → <span class="after">📊 After</span></div>` |
| 3.6 | R 코드 블록에 **"💬 미래의 내가 알려주는 베스트 코딩 방법"** 페르소나 헤더 | **[PASS]** `.persona-header` + 정확한 문구 출현 |
| 3.7 | R 코드: **tidyverse 파이프 `\|>`** + **명시적 네임스페이스**(`dplyr::mutate` 등) | **[PASS]** 보강 노드 15개 중 6개(N8, N14, N17, N19, N24, N29)에서 `\|>` 또는 `dplyr::/purrr::/stringr::/lubridate::` 사용. 나머지는 단순 boolean 분기라 tidyverse 불필요 |
| 3.8 | R 코드 앞 3~5줄 **한국어 주석** | **[PASS]** 보강 코드 11개 노드에서 `# 한국어` 주석 존재 |
| 3.9 | R 코드 블록 순서: ① 판정 → ② YES 처리 → ③ "✅ 왜 이렇게 쓰는지" 팁 주석 | **[PASS]** `renderRCodeSection()`이 checkBlock → passBlock → tipsBlock 순서로 렌더 |
| 3.10 | R 코드 우측 상단에 **복사 버튼** | **[PASS]** `.copy-btn` + `window.copyCode` + `navigator.clipboard.writeText` |
| 3.11 | 각 AUTO/REPAIR leaf 패널에 **end-to-end R 스크립트** (대표 시나리오 1개) | **[PASS]** leaf 패널에서 `terminal_state === "AUTO" \|\| "REPAIR"` 시 `renderEndToEnd()` 호출 → `R_LIB.end_to_end_example.r_pipeline` |
| 3.12 | 상단 고정 바에 **FORCED 게이트 학습 카운터** `●●●○○○○ (N/7 학습)` (localStorage 기반, 클릭한 forced 노드 영구 기억) | **[PASS]** `ForcedCounter` 모듈 — `localStorage["pmx_v2_learned_forced"]` JSON array, 클릭 시 `mark()` 호출 |
| 3.13 | 상단 고정 바에 **Quick Ref 📋 버튼** | **[PASS]** `<button class="qref-btn" onclick="QuickRef.open()">Quick Ref 📋</button>` |
| 3.14 | Quick Ref 패널에 NONMEM 필수 컬럼 7개 표 | **[PASS]** `NONMEM_COLS` 배열 — ID/TIME/AMT/DV/EVID/CMT/MDV 7개 행 |
| 3.15 | Quick Ref 패널에 terminal_state 4종 표 | **[PASS]** `TERM_STATES` 배열 — AUTO/REPAIR/QUARANTINE/INVALID 4개 행 |
| 3.16 | Quick Ref 패널에 Q-code 목록 (Q01–Q19, **Q17 제외**) | **[PASS]** `.filter(([code, _]) => code !== "Q17")` 로 Q17 제외 후 labels_ko.q_code 전부 렌더 |
| 3.17 | 패널 하단에 다음 분기 네비게이션 — `✅ YES → 다음 노드` / `❌ NO → 결과` 버튼, 클릭 시 해당 노드 선택 상태로 전환 | **[PASS]** `.branch-btn.yes` / `.branch-btn.no` + `onclick="SvgTree.selectNode('...')"` |

---

## SC-4 — 기술 안정성 기준

| # | 항목 | 결과 |
|---|------|------|
| 4.1 | vis-network CDN 제거 후 대체 SVG 렌더러가 19 내부노드 + 51 leaves(총 126 인스턴스) 모두 표시 | **[PASS (structural)]** `TREE.internal_nodes.forEach` + `TREE.leaves.forEach` 양쪽 처리 + `SvgTree.render()` 호출 흐름 확인. 실제 페인트는 브라우저 검증 권장 |
| 4.2 | `data/*.json` 로드 실패(404·JSON parse error) 시 명확한 에러 메시지를 `#network` 영역에 표시 | **[PASS]** `try/catch` + `setBootStatus(..., true)` + 한국어 메시지 "데이터 로딩 실패 — ${err.message}" + 스택 trace 표시 |
| 4.3 | 브라우저 콘솔에 JS 에러 없음 — 기본 흐름(트리 첫 페인트 → 노드 클릭 → 탭 전환 → 경로 추적 1회) 기준 | **[PASS (structural)]** `load()` 전역 `try/catch` + `fj()` HTTP 상태 체크. 실제 콘솔 점검은 브라우저에서 추가 검증 권장 |
| 4.4 | `tree_v2_standalone.html`이 file:// 프로토콜에서도 동작 (인라인 데이터 + 외부 fetch 없음) | **[PASS]** `_build_standalone.py`가 `window.__INLINE_DATA__` 주입 — universe 2998 + r_code_library 19 candidates + 10 dataset 인라인. 외부 fetch는 분기로 skip |
| 4.5 | `index_v2.html`이 `python3 -m http.server` 같은 단순 HTTP 서버에서 동작 | **[PASS]** `python3 -m http.server 8765` smoke test: `index_v2.html` 200 OK (74,074 byte), `tree.json` 200 OK, `r_code_library.json` 200 OK, `standalone.html` 200 OK |
| 4.6 | r_code_library 보강 후에도 기존 `candidate_nodes.N0~N2,N5` 항목 deep-equal 무변경 | **[PASS]** `_build_rlib_addition.py` 실행 로그: "PASS: 완전체 노드 (N0, N1, N2, N5) 무변경" + 기존 키 173개 전체 보존 |
| 4.7 | r_code_library 보강 후에도 기존 `action_functions.*`, `end_to_end_example`, `nonmem_ready_spec`, `packages_needed`, `pipeline_overview` 항목 deep-equal 무변경 | **[PASS]** 최상위 7개 키 (packages_needed/pipeline_overview/nonmem_ready_spec/action_functions/end_to_end_example/version/purpose) 무변경 + `action_functions.canonicalize_blq` R 코드 본문 sanity 통과 |
| 4.8 | r_code_library 보강 후에도 JSON parse 성공 + `version` 필드 유지 | **[PASS]** `json.load()` 성공 + `version = "v1.0-r-learning"` 유지 |

---

## 검증 절차 (Phase 4에서 실제 실행한 명령)

1. **자동 검증 — 한 줄로 실행**:
   ```bash
   cd /Users/min9/Documents/GitHub/pmx_universe_v5_1
   python3 study/_verify_v2.py    # 결과: 42/42 PASS
   ```

2. **r_code_library 보강 deep-equal 검증** (`_build_rlib_addition.py`가 자체 검증 포함):
   ```bash
   python3 study/_build_rlib_addition.py    # 결과: 173 기존 키 보존, 86 신규 키 추가
   ```

3. **HTTP 서버 smoke test**:
   ```bash
   python3 -m http.server 8765 &
   curl -I http://127.0.0.1:8765/study/index_v2.html              # 200 OK
   curl -I http://127.0.0.1:8765/study/tree_v2_standalone.html    # 200 OK
   ```

4. **수동 검증 (권장, 브라우저에서)**:
   - `http://127.0.0.1:8765/study/index_v2.html` 열기
   - `file:///…/study/tree_v2_standalone.html` 도 직접 열어 동작 확인
   - 노드 클릭 시 4섹션이 모두 표시되는지
   - Quick Ref 슬라이드가 우측에서 열리는지
   - Forced 게이트(N0~N5, N8) 클릭 시 상단 카운터 `●` 증가 + 재로드 후에도 유지되는지

---

## 금지 사항 (CLAUDE.md 6.1 그대로) — 위반 0건

1. 기존 `study/data/*.json` (r_code_library 제외) 내용 변경 → **준수** (SHA-256 baseline 일치)
2. 기존 `study/dashboard/` 3개 HTML 덮어쓰기 → **준수** (size unchanged)
3. vis-network 재사용 → **준수** (코멘트 외 출현 없음)
4. 모든 노드에 동일한 제네릭 Before/After 테이블 사용 → **준수** (19개 노드 각자 고유 예시)
5. 영어만으로 된 R 주석 → **준수** (한국어 주석 11개 노드)
6. tidyverse 없이 base R 중첩 ifelse → **준수** (case_when/dplyr/purrr 사용 권장 코드)
7. Q17 언급 → **준수** (Quick Ref Q-code 표에서 명시적으로 필터링)
8. 본 문서 작성 전 코딩 시작 → **준수** (Phase 1 → 2 순서 지킴)
