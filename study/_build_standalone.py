"""
study/_build_standalone.py
─────────────────────────────────────────────────────────────────────
study/index_v2.html → study/tree_v2_standalone.html 빌드.

  - 모든 study/data/*.json을 window.__INLINE_DATA__로 임베드
  - fetch() 분기는 INLINE_DATA가 있으면 건너뛰므로 file:// 동작 가능
  - 외부 의존성은 highlight.js CDN 하나 (R syntax highlight) — file://에서도
    CDN 접근 가능한 환경이면 정상 동작, 아니면 highlight 없이 plain text로 표시
"""

from __future__ import annotations
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC  = ROOT / "index_v2.html"
DST  = ROOT / "tree_v2_standalone.html"
DATA = ROOT / "data"

DATA_FILES = {
    "tree":             "tree.json",
    "nodes":            "nodes.json",
    "axis_dictionary":  "axis_dictionary.json",
    "q_codes":          "q_codes.json",
    "universe":         "universe.json",
    "decision_table":   "decision_table.json",
    "action_labels":    "action_labels.json",
    "summary":          "summary.json",
    "labels_ko":        "labels_ko.json",
    "r_code_library":   "r_code_library.json",
}


def main() -> int:
    if not SRC.exists():
        print(f"[ERROR] {SRC} not found", file=sys.stderr)
        return 1

    html = SRC.read_text(encoding="utf-8")

    # Load + serialize inline data
    inline_data = {}
    total_bytes = 0
    for key, fname in DATA_FILES.items():
        p = DATA / fname
        if not p.exists():
            print(f"[ERROR] {p} not found", file=sys.stderr)
            return 1
        inline_data[key] = json.loads(p.read_text(encoding="utf-8"))
        total_bytes += p.stat().st_size

    # JSON-encode. </script> escape는 안전을 위해 처리.
    payload = json.dumps(inline_data, ensure_ascii=False).replace("</", "<\\/")
    inline_block = (
        '<script>\n'
        '// ═══ INLINE DATA — embedded by _build_standalone.py ═══\n'
        f'window.__INLINE_DATA__ = {payload};\n'
        '</script>\n'
    )

    # 타이틀 + 인라인 데이터 주입
    out = html.replace(
        "<title>PMX Wrangling Tree v2 — 초보자 친화 대시보드</title>",
        "<title>PMX Wrangling Tree v2 — 독립 실행 (Standalone)</title>",
        1,
    )

    # 첫 번째 메인 <script> (load 로직) 직전에 INLINE_DATA 주입
    marker = "<script>\n// ════════════════════════════════════════════════════════════════════\n// PMX Wrangling Tree v2 — JS"
    if marker not in out:
        print("[ERROR] main <script> marker not found in source HTML", file=sys.stderr)
        return 2
    out = out.replace(marker, inline_block + marker, 1)

    DST.write_text(out, encoding="utf-8")

    out_kb = DST.stat().st_size / 1024
    print(f"✓ {DST.relative_to(ROOT.parent)} 빌드 완료")
    print(f"  소스 HTML:     {SRC.stat().st_size/1024:>9.1f} KB")
    print(f"  임베드 데이터: {total_bytes/1024:>9.1f} KB (10 files)")
    print(f"  결과:          {out_kb:>9.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
