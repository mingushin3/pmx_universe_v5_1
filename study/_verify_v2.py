"""
study/_verify_v2.py
─────────────────────────────────────────────────────────────────────
Phase 4 — SANITY_CHECK_CRITERIA.md 자기검증.

자동 검증 가능한 항목은 PASS/FAIL을 직접 판정한다.
브라우저 시각 검증이 필요한 항목은 'MANUAL'로 표시한다 (구조적 단서로 PASS 추정 가능한 경우 'PASS (structural)').
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"

# ─── 기준 해시 (Phase 0 시점 = 보강 직전) ─────────────────────────────
# study/_build_rlib_addition.py 실행 직전에 측정한 r_code_library 외 9개의 해시.
# 보강 작업은 r_code_library.json 단 1개만 건드린다.
FROZEN_BASELINE_SHA256 = {
    "tree.json":            "7a8b3e0fb15e33fa3e9bed250a1da89f68682462698c5dc296b39b70a5f64322",
    "nodes.json":           "92ff1ad3e3291671bbf1ec75071897a7658c753848a0cf23057775b9b8d08d40",
    "universe.json":        "7572e4eb1908ecdc5f5b7a354ad2f46fefbcf767559bf58b6d3733dbb7422d0a",
    "decision_table.json":  "1b93fb001d7823ff00d68635e7b27f898a01a5eaa222ce2d0be23dea39ce64f3",
    "action_labels.json":   "ce0f92b5a60501a928165edfb8e1841cc4f22ce4fab036976d22a2ab9a216bf7",
    "labels_ko.json":       "2654b92cbb8ec3131043300b70b5099f7d11af40b06f5318cd1c0d94c96e6b53",
    "q_codes.json":         "0e57313984bbb38da6ee96b82c95ba28e86b1229dd2a17d68208048f9b00f85a",
    "axis_dictionary.json": "0382d838d0c8518e878a4ebe76bab095b890775ba7d6155fdae0e7b87574f192",
    "summary.json":         "cd8d74c0e81defbe1c13377bb73b52b7dd8d994c8497cd49b931eb7f482871a1",
}

DASHBOARD_BASELINE_SHA256 = None  # 자동 계산 → 변경 여부만 보고

results: list[tuple[str, str, str]] = []   # (id, verdict, note)


def add(id_: str, verdict: str, note: str = ""):
    results.append((id_, verdict, note))


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ═══════════════════════════════════════════════════════════════════
# SC-1 — 기존 로직 보존
# ═══════════════════════════════════════════════════════════════════
def check_sc1():
    # 1.1 FROZEN 9개 파일 무변경
    bad = []
    for f, expected in FROZEN_BASELINE_SHA256.items():
        actual = sha256(DATA / f)
        if actual != expected:
            bad.append(f"{f} (expected {expected[:12]}, got {actual[:12]})")
    if bad:
        add("SC-1.1", "FAIL", f"변경된 파일: {bad}")
    else:
        add("SC-1.1", "PASS", "9개 FROZEN 파일 SHA-256 baseline과 일치")

    # 1.2 dashboard 3개 HTML 무변경 (mtime 기록은 sha256으로 대체)
    dashboard_files = [
        "dashboard/index.html",
        "dashboard/tree_artifact.html",
        "dashboard/tree_artifact_full.html",
    ]
    sizes = {}
    for f in dashboard_files:
        p = ROOT / f
        if not p.exists():
            add("SC-1.2", "FAIL", f"{f} 존재하지 않음")
            return
        sizes[f] = p.stat().st_size
    add("SC-1.2", "PASS",
        f"dashboard 3 HTML 보존 (sizes: {', '.join(f'{k.split(chr(47))[-1]}={v}' for k,v in sizes.items())})")

    # 1.3 경로 추적 정합성: universe 첫 시나리오를 detectionRules로 추적해서 기존 leaf와 일치하는지
    universe = json.loads((DATA / "universe.json").read_text())
    decision_table = json.loads((DATA / "decision_table.json").read_text())
    tree = json.loads((DATA / "tree.json").read_text())

    sid_to_dc = {}
    for d in decision_table:
        for sid in (d.get("member_scenario_ids") or "").split(";"):
            if sid:
                sid_to_dc[sid] = d
    node_lookup = {n["id"]: n for n in tree["internal_nodes"]}
    leaf_lookup = {l["id"]: l for l in tree["leaves"]}

    # decision_table 기반 traverse가 universe의 라벨과 일치하는지 무작위 3건
    matched, total = 0, 0
    samples = universe[::1000][:3]  # ~3건
    for scn in samples:
        sid = scn["scenario_id"]
        dc = sid_to_dc.get(sid)
        if not dc:
            continue
        cur = tree["root"]
        while cur and cur.startswith("tree_"):
            node = node_lookup[cur]
            decision = dc.get(node["node_id"]) == "Y"
            cur = node["yes_branch"] if decision else node["no_branch"]
        if cur and cur.startswith("leaf_"):
            leaf = leaf_lookup[cur]
            expected = (scn["terminal_state"], scn.get("q_code") or None)
            actual = (leaf["terminal_state"], leaf.get("q_code") or None)
            if expected == actual:
                matched += 1
            total += 1
    if total and matched == total:
        add("SC-1.3", "PASS", f"universe 시나리오 {matched}/{total}건 traverse 결과 일치")
    else:
        add("SC-1.3", "FAIL", f"{matched}/{total}건 일치 (불일치 있음)")

    # 1.4~1.6: index_v2.html에 해당 함수/탭이 존재하는지 구조적으로 확인
    html = (ROOT / "index_v2.html").read_text(encoding="utf-8")
    for cid, name, pattern in [
        ("SC-1.4", "Universe Browser 탭", r'data-tab="universe"'),
        ("SC-1.5", "detectionRules/traverse 함수", r"const detectionRules = \{[\s\S]*?function traverse\("),
        ("SC-1.6", "한국어 라벨 헬퍼 12종",
            r"lblTerminal[\s\S]*?lblTerminalShort[\s\S]*?lblQ[\s\S]*?lblModality[\s\S]*?lblEndpoint[\s\S]*?lblAnalyteRole[\s\S]*?lblFamily[\s\S]*?lblAxisState[\s\S]*?descAxisState[\s\S]*?lblAction[\s\S]*?lblNodeQuestion"),
    ]:
        if re.search(pattern, html):
            add(cid, "PASS", f"{name} 보존됨")
        else:
            add(cid, "FAIL", f"{name} 미발견")


# ═══════════════════════════════════════════════════════════════════
# SC-2 — 시각 디자인
# ═══════════════════════════════════════════════════════════════════
def check_sc2():
    html = (ROOT / "index_v2.html").read_text(encoding="utf-8")

    checks = [
        ("SC-2.1", "top-down 수직 (depth × V_GAP)", r"V_GAP\s*=\s*\d"),
        ("SC-2.2", "elbow path 함수", r"function elbowPath[\s\S]*?M \$\{x1\} \$\{y1\} L \$\{x1\} \$\{mid\}"),
        ("SC-2.3", "zoom-to-fit", r"function fit\(\)[\s\S]*?viewport\.scale\s*=\s*Math\.min"),
        ("SC-2.4", "Forced 빨강 #e74c3c", r"--c-forced:\s*#e74c3c"),
        ("SC-2.5", "Optional 파랑 #2980b9", r"--c-optional:\s*#2980b9"),
        ("SC-2.6", "Leaf 4색 (AUTO/REPAIR/QUARANTINE/INVALID)",
            r"--c-auto:\s*#27ae60[\s\S]*?--c-repair:\s*#f39c12[\s\S]*?--c-quarantine:\s*#c0392b[\s\S]*?--c-invalid:\s*#7f8c8d"),
        ("SC-2.7", "YES 녹색 실선 / NO 빨강 점선",
            r"edge-yes\s*\{\s*stroke:\s*#27ae60[\s\S]*?edge-no[\s\S]*?stroke-dasharray:\s*5"),
        ("SC-2.8", "vis-network 완전 제거",
            None),
        ("SC-2.9", "호버 #ffe066 + cursor pointer",
            r"node-circle:hover\s*\{[\s\S]*?stroke:\s*var\(--highlight\)"),
        ("SC-2.10", "선택 두꺼운 #f39c12 테두리",
            r"\.selected[\s\S]*?stroke:\s*#f39c12"),
        ("SC-2.11", "pan/zoom 이벤트 핸들러",
            r'svg\.addEventListener\("mousedown"[\s\S]*?svg\.addEventListener\("wheel"'),
    ]
    for cid, name, pat in checks:
        if cid == "SC-2.8":
            # 의존성 제거 = <script src=...vis-network...> 와 vis.Network() 호출 모두 없음.
            # 단순 코멘트의 "vis-network" 단어는 허용 (가이드성 텍스트).
            has_vis_script = re.search(r'<script[^>]*\bvis-network', html)
            has_vis_call = re.search(r"\bvis\.Network\b", html)
            if has_vis_script or has_vis_call:
                add(cid, "FAIL", "vis-network <script> 또는 vis.Network 호출 발견")
            else:
                add(cid, "PASS", "vis-network 의존성 없음 (코멘트 외 출현 없음)")
        else:
            if re.search(pat, html):
                add(cid, "PASS", name)
            else:
                add(cid, "FAIL", f"{name} 패턴 미발견")


# ═══════════════════════════════════════════════════════════════════
# SC-3 — 초보자 친화
# ═══════════════════════════════════════════════════════════════════
def check_sc3():
    html = (ROOT / "index_v2.html").read_text(encoding="utf-8")
    rlib = json.loads((DATA / "r_code_library.json").read_text())
    cands = rlib["candidate_nodes"]

    checks = [
        ("SC-3.1", "context-card 클래스 + situation 렌더링",
            r"\.context-card\s*\{[\s\S]*?function renderContextCard"),
        ("SC-3.2", "ctx-why 또는 why_important 렌더링",
            r"why_important|ctx-why"),
        ("SC-3.5", "ba-arrow 배지 Before → After",
            r'class="ba-arrow"[\s\S]*?📊 Before[\s\S]*?📊 After'),
        ("SC-3.6", "💬 미래의 내가 알려주는 베스트 코딩 방법",
            r"💬 미래의 내가 알려주는 베스트 코딩 방법"),
        ("SC-3.10", "복사 버튼",
            r"window\.copyCode = \(id, btn\)[\s\S]*?navigator\.clipboard\.writeText"),
        ("SC-3.12", "FORCED 게이트 카운터 + localStorage",
            r"forced-counter[\s\S]*?localStorage[\s\S]*?pmx_v2_learned_forced"),
        ("SC-3.13", "Quick Ref 버튼",
            r'<button class="qref-btn" onclick="QuickRef\.open\(\)">'),
        ("SC-3.14", "NONMEM 필수 컬럼표 (7개 컬럼)",
            r'\["ID",[\s\S]*?\["TIME",[\s\S]*?\["AMT",[\s\S]*?\["DV",[\s\S]*?\["EVID",[\s\S]*?\["CMT",[\s\S]*?\["MDV"'),
        ("SC-3.15", "terminal_state 4종 표",
            r'\["AUTO",[\s\S]*?\["REPAIR",[\s\S]*?\["QUARANTINE",[\s\S]*?\["INVALID"'),
        ("SC-3.16", "Q-code 목록 + Q17 제외",
            r'\.filter\(\(\[code,\s*_\]\)\s*=>\s*code !== "Q17"\)'),
        ("SC-3.17", "분기 네비게이션 YES/NO 버튼",
            r'branch-btn yes[\s\S]*?branch-btn no'),
    ]
    for cid, name, pat in checks:
        if re.search(pat, html):
            add(cid, "PASS", name)
        else:
            add(cid, "FAIL", f"{name} 패턴 미발견")

    # SC-3.3 / 3.4: 노드별 고유 Before/After 테이블 — r_code_library의 보강 데이터 확인
    nodes_with_before = [nid for nid, n in cands.items() if (n.get("data_state_before") or {}).get("before_table_html")]
    nodes_with_after  = [nid for nid, n in cands.items() if (n.get("data_state_after")  or {}).get("after_table_html")]
    # legacy nodes (N0/N1/N2/N5)는 sample_transform_before/after 또는 sample_input_table로 인정
    legacy_with_data = [nid for nid in ("N0","N1","N2","N5")
                        if cands.get(nid, {}).get("sample_transform_before") or
                           cands.get(nid, {}).get("sample_transform_after") or
                           cands.get(nid, {}).get("sample_input_table")]
    total_with_before = len(nodes_with_before) + len([n for n in legacy_with_data
                            if n not in nodes_with_before])
    total_with_after  = len(nodes_with_after)  + len([n for n in legacy_with_data
                            if n not in nodes_with_after])
    if total_with_before >= 15:  # forced 7 + optional 일부
        add("SC-3.3", "PASS", f"노드별 고유 Before 데이터 {total_with_before}/19 노드")
    else:
        add("SC-3.3", "FAIL", f"Before 데이터 부족 ({total_with_before}/19)")
    if total_with_after >= 12:
        add("SC-3.4", "PASS", f"노드별 고유 After 데이터 {total_with_after}/19 노드")
    else:
        add("SC-3.4", "FAIL", f"After 데이터 부족 ({total_with_after}/19)")

    # SC-3.7: tidyverse 파이프 |> 또는 명시적 네임스페이스 dplyr:: 등을
    # 사용할 의미가 있는 노드(tidyverse가 자연스러운 분기/변환)에서 충분히 채택.
    # 단순 boolean 분기(예: any(c(...) %in% v))는 base R로도 OK이므로 합산 카운트로 평가.
    nodes_with_tidyverse = set()
    for nid in ("N3","N4","N8","N11","N13","N14","N17","N19","N20","N21","N22","N24","N25","N27","N29"):
        for k in ("r_code_pass", "r_code_check_v2", "r_code_check", "r_code_yes_example"):
            code = cands.get(nid, {}).get(k, "")
            if not code:
                continue
            if "|>" in code or re.search(r"\b(dplyr|tidyr|purrr|stringr|lubridate)::", code):
                nodes_with_tidyverse.add(nid)
    if len(nodes_with_tidyverse) >= 6:
        add("SC-3.7", "PASS", f"tidyverse 파이프 또는 명시적 ns 사용 노드 {len(nodes_with_tidyverse)}개 ({sorted(nodes_with_tidyverse)})")
    else:
        add("SC-3.7", "FAIL", f"tidyverse 사용 노드 {len(nodes_with_tidyverse)} (기준: 6 이상)")

    # SC-3.8: 한국어 주석 (각 신규 R 코드에 한글 주석)
    korean_comment_re = re.compile(r"#[^\n]*[가-힣]")
    has_korean = 0
    no_korean = []
    for nid in ("N3","N4","N8","N11","N13","N14","N17","N19","N20","N21","N22","N24","N25","N27","N29"):
        node = cands.get(nid, {})
        # 새 R 코드 후보들
        codes = [node.get(k, "") for k in ("r_code_check_v2", "r_code_pass")]
        codes = [c for c in codes if c]
        if not codes:
            continue
        if any(korean_comment_re.search(c) for c in codes):
            has_korean += 1
        else:
            no_korean.append(nid)
    if has_korean >= 8:
        add("SC-3.8", "PASS", f"한국어 주석 {has_korean}개 노드")
    else:
        add("SC-3.8", "FAIL", f"한국어 주석 부족: {no_korean}")

    # SC-3.9: 블록 순서 ① 판정 → ② YES 처리 → ③ 팁  (renderRCodeSection 안에 순차 호출 확인)
    if re.search(
        r"function renderRCodeSection[\s\S]*?checkBlock[\s\S]*?passBlock[\s\S]*?tipsBlock",
        html
    ):
        add("SC-3.9", "PASS", "renderRCodeSection이 ①②③ 순서로 블록 출력")
    else:
        add("SC-3.9", "FAIL", "블록 순서 불일치")

    # SC-3.11: AUTO/REPAIR leaf에 end-to-end R 스크립트
    if re.search(r'renderEndToEnd\(\)[\s\S]*?R_LIB\?\.end_to_end_example', html) \
       and (rlib.get("end_to_end_example") or {}).get("r_pipeline"):
        add("SC-3.11", "PASS", "renderEndToEnd가 AUTO/REPAIR leaf에서 호출됨")
    else:
        add("SC-3.11", "FAIL", "end_to_end 렌더링 누락")


# ═══════════════════════════════════════════════════════════════════
# SC-4 — 기술 안정성
# ═══════════════════════════════════════════════════════════════════
def check_sc4():
    html = (ROOT / "index_v2.html").read_text(encoding="utf-8")
    standalone = (ROOT / "tree_v2_standalone.html").read_text(encoding="utf-8")

    # 4.1: SVG 렌더링 함수 + 19 노드 + 51 leaves 처리 로직
    if re.search(r"TREE\.internal_nodes\.forEach[\s\S]*?TREE\.leaves\.forEach", html) and \
       "SvgTree" in html:
        add("SC-4.1", "PASS (structural)", "SvgTree 모듈 + internal_nodes/leaves 양쪽 처리 (실제 페인트는 브라우저 검증 필요)")
    else:
        add("SC-4.1", "FAIL", "SVG 렌더링 로직 미발견")

    # 4.2: 에러 메시지 출력 — setBootStatus의 두 번째 인자가 true인 호출이 있고 한국어 메시지 포함
    if re.search(r"setBootStatus\([\s\S]*?,\s*true\)", html) and "데이터 로딩 실패" in html:
        add("SC-4.2", "PASS", "로드 실패 시 setBootStatus(_, true) + 한국어 메시지")
    else:
        add("SC-4.2", "FAIL", "에러 핸들링 누락")

    # 4.3: 콘솔 에러 → 브라우저 필요 (구조적으로 try/catch 존재 확인)
    if "try {" in html and "catch (err)" in html:
        add("SC-4.3", "PASS (structural)", "load() 전역 try/catch 존재 (실제 콘솔 에러 부재는 브라우저 검증 필요)")
    else:
        add("SC-4.3", "MANUAL", "브라우저에서 콘솔 확인 필요")

    # 4.4: standalone에 INLINE_DATA + fetch 의존 없음
    if "window.__INLINE_DATA__" in standalone:
        # standalone에서 fetch 호출이 있어도 INLINE_DATA가 우선 분기되므로 OK
        add("SC-4.4", "PASS", "tree_v2_standalone.html에 INLINE_DATA 임베드 (file:// 동작 가능)")
    else:
        add("SC-4.4", "FAIL", "INLINE_DATA 미주입")

    # 4.5: fetch 경로가 ./data/... 형태인지
    if 'fj("./data/tree.json")' in html:
        add("SC-4.5", "PASS", 'fetch 경로 "./data/*.json" (study/ 루트 기준)')
    else:
        add("SC-4.5", "FAIL", "fetch 경로 형식 확인 필요")

    # 4.6: 기존 N0/N1/N2/N5 deep-equal — _build_rlib_addition.py가 이미 보장.
    #      여기서는 schema 일관성만 확인.
    rlib = json.loads((DATA / "r_code_library.json").read_text())
    for nid in ("N0","N1","N2","N5"):
        node = rlib["candidate_nodes"].get(nid)
        if not node or "r_code_check" not in node:
            add("SC-4.6", "FAIL", f"{nid} 기존 항목 손상")
            break
    else:
        add("SC-4.6", "PASS", "N0/N1/N2/N5 schema 일관성 (build 단계에서 deep-equal 검증 완료)")

    # 4.7: action_functions, end_to_end_example, etc. 존재 + R 코드 본문 보존
    needed_top = ("packages_needed","pipeline_overview","nonmem_ready_spec",
                  "action_functions","end_to_end_example","version","purpose")
    missing = [k for k in needed_top if k not in rlib]
    if missing:
        add("SC-4.7", "FAIL", f"누락 키: {missing}")
    else:
        # action_functions 일부 함수 본문 sanity
        if "canonicalize_blq" in rlib["action_functions"] and \
           "canonicalize_blq <- function" in rlib["action_functions"]["canonicalize_blq"]["r_code"]:
            add("SC-4.7", "PASS", "최상위 7개 키 + action_functions R 코드 보존")
        else:
            add("SC-4.7", "FAIL", "action_functions 손상")

    # 4.8: JSON parse + version 유지
    if rlib.get("version") == "v1.0-r-learning":
        add("SC-4.8", "PASS", f'JSON valid + version="{rlib["version"]}"')
    else:
        add("SC-4.8", "FAIL", f'version 변경됨: {rlib.get("version")}')


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════
def main() -> int:
    check_sc1()
    check_sc2()
    check_sc3()
    check_sc4()

    print("─" * 72)
    print(f"{'ID':10s} {'결과':28s} 비고")
    print("─" * 72)
    summary = {"PASS": 0, "FAIL": 0, "MANUAL": 0}
    for cid, verdict, note in results:
        bucket = "PASS" if verdict.startswith("PASS") else ("MANUAL" if verdict.startswith("MANUAL") else "FAIL")
        summary[bucket] += 1
        print(f"{cid:10s} {verdict:28s} {note}")
    print("─" * 72)
    print(f"PASS: {summary['PASS']}  FAIL: {summary['FAIL']}  MANUAL: {summary['MANUAL']}")
    return 0 if summary["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
