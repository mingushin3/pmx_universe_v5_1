# study/ — PMX Universe 학습/검증 작업 폴더

**원본 보존 원칙**: 이 폴더 외부의 파일(config/, data/, scripts/, reports/, release/, *.md)은 절대 수정하지 않습니다. 모든 추가 작업은 이 폴더 내부에서만 수행합니다.

## 목적

1. **시각화** — v1.0 LOCKED 된 19-node decision tree (126 internal + 51 leaf)를 한눈에 보기
2. **검증** — universe(2,998 시나리오)와 decision tree가 NONMEM-ready dataset wrangling을 실무 수준으로 캡쳐하는지 확인
3. **학습** — 각 노드에서 발생하는 데이터 변환을 R 코드로 학습

## 폴더 구조

```
study/
├── README.md                # 이 파일
├── build/                   # 빌드 스크립트
│   ├── export_to_json.py    # 원본 YAML/CSV → study/data/*.json 변환
│   └── build_artifact.py    # 단일 파일 HTML 아티팩트 빌드
├── data/                    # 브라우저가 fetch하는 JSON (원본 사본, 자동 생성)
│   ├── tree.json, nodes.json, axis_dictionary.json, q_codes.json
│   ├── universe.json, decision_table.json, action_labels.json, summary.json
│   ├── labels_ko.json       # 한국어 라벨 사전 (수기 작성)
│   └── r_code_library.json  # R 학습 콘텐츠 (수기 작성)
├── dashboard/               # 인터랙티브 시각화 + Trace 시뮬레이터
│   ├── index.html           # 풀 기능 (HTTP 서버 필요, fetch 모드)
│   ├── tree_artifact.html   # 단일 파일 아티팩트 라이트 (~235 KB, 더블클릭)
│   └── tree_artifact_full.html  # 단일 파일 아티팩트 풀 (~3.2 MB, universe 포함)
└── r_notebooks/             # R 학습 자료 (검증 후 생성)
    └── 00_overview.Rmd ...
```

## 사용법

### 옵션 A — 단일 파일 아티팩트 (가장 간편, 더블클릭으로 열림)

```bash
# 한 번만: 원본 데이터 → JSON 변환 + 아티팩트 빌드
python3 study/build/export_to_json.py
python3 study/build/build_artifact.py             # 라이트 (~235 KB)
# python3 study/build/build_artifact.py --with-universe   # 풀 (~3.2 MB)
```

생성된 `study/dashboard/tree_artifact.html`을 파일 탐색기에서 **더블클릭**하면 즉시 열립니다.
HTTP 서버 불필요. CDN 라이브러리(vis-network, highlight.js)만 인터넷 필요.

- **tree_artifact.html** (라이트, 235 KB) — 트리 시각화 + 노드 상세 + R 학습. 공유/저장에 최적
- **tree_artifact_full.html** (풀, 3.2 MB) — 위 + 2,998 universe 시나리오 + trace simulator universe 모드

### 옵션 B — HTTP 서버 모드 (개발/실시간 데이터 갱신)

```bash
# 한 번만: 원본 데이터 → JSON 변환
python3 study/build/export_to_json.py

# 서버 띄우기
cd study && python3 -m http.server 8765
# 브라우저에서 http://localhost:8765/dashboard/ 접속
```

### 검증 단계

대시보드에서 다음을 직접 확인:
- 전체 19-node tree 구조 시각화
- 각 노드의 detection_rule / question / axis 의존성
- Starting condition을 입력하면 트리를 따라가며 어느 leaf에 도달하는지 trace
- 각 단계에서 어떤 wrangling 함수가 트리거되는지

검증 PASS 시 R 노트북 작성 단계로 진행.

## 원본 데이터 참조

- 시나리오 universe (D1): `data/scenario_universe/scenario_universe_v1.0.csv` — 2,998 rows
- Decision table (D3): `data/decision_table/reduced_decision_table_v1.0.csv` — 337 DC classes
- Operational tree (D6, LOCKED): `config/operational_decision_tree.yaml` — 126 internal + 51 leaves
- Node dictionary: `config/candidate_node_dictionary_with_costs.csv` — 30 candidate nodes
- Axis dictionary: `config/axis_dictionary.yaml` — A0~A10
- Q-code reference: `config/quarantine_reason_codes.yaml` — Q01~Q19 (Q17 forbidden)
- Repair functions: `scripts/repair_executor/repair_executor.py` — 27 functions
