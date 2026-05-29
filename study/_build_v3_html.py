"""
study/_build_v3_html.py
─────────────────────────────────────────────────────────────────────
_v3_template.html → study/index_v3.html 빌드.
  - 학습 중심 데이터 7종만 인라인 (universe / action_labels / decision_table 제외)
  - 외부 의존성 0 — file:// 더블클릭 동작 보장
  - INLINE_DATA_START / INLINE_DATA_END marker 사이에 데이터 주입
"""

from __future__ import annotations
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATE = ROOT / "_v3_template.html"
OUTPUT   = ROOT / "index_v3.html"
DATA     = ROOT / "data"

# 학습 중심 데이터만 인라인 (총 ~260KB)
ESSENTIAL = {
    "tree":             "tree.json",
    "nodes":            "nodes.json",
    "axis_dictionary":  "axis_dictionary.json",
    "q_codes":          "q_codes.json",
    "summary":          "summary.json",
    "labels_ko":        "labels_ko.json",
    "r_code_library":   "r_code_library.json",
}

MARKER_START = "<!-- INLINE_DATA_START -->"
MARKER_END = "<!-- INLINE_DATA_END -->"


def main() -> int:
    if not TEMPLATE.exists():
        print(f"[ERROR] {TEMPLATE} not found", file=sys.stderr)
        return 1

    html = TEMPLATE.read_text(encoding="utf-8")

    inline = {}
    total_bytes = 0
    for key, fname in ESSENTIAL.items():
        p = DATA / fname
        if not p.exists():
            print(f"[ERROR] {p} not found", file=sys.stderr)
            return 1
        inline[key] = json.loads(p.read_text(encoding="utf-8"))
        total_bytes += p.stat().st_size

    payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    injection = (
        MARKER_START + "\n"
        '<script>\n'
        '// ═══ Inline data — embedded by _build_v3_html.py ═══\n'
        f'window.__INLINE_DATA__ = {payload};\n'
        '</script>\n'
        + MARKER_END
    )

    if MARKER_START not in html or MARKER_END not in html:
        print(f"[ERROR] markers not found in template", file=sys.stderr)
        return 2

    pre, _, rest = html.partition(MARKER_START)
    _, _, post = rest.partition(MARKER_END)
    out = pre + injection + post

    OUTPUT.write_text(out, encoding="utf-8")
    out_kb = OUTPUT.stat().st_size / 1024
    print(f"✓ {OUTPUT.relative_to(ROOT.parent)} 빌드 완료")
    print(f"  template:   {TEMPLATE.stat().st_size/1024:>8.1f} KB")
    print(f"  inline 데이터: {total_bytes/1024:>8.1f} KB (7 files, 학습 중심)")
    print(f"  결과:        {out_kb:>8.1f} KB")
    print(f"\n  실행: open {OUTPUT.relative_to(ROOT.parent)}  (더블클릭으로 열림)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
