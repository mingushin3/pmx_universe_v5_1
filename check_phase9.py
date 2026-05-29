#!/usr/bin/env python3
"""CHECK-9 — Phase 9 (Decision Tree + NONMEM QC) verification.

Per v5_1_step3_patched_v3.md lines 1404–1510.
"""
import os
import sys
from pathlib import Path

try:
    import yaml
    import pandas as pd  # noqa: F401  (kept for parity with playbook)
except ImportError:
    print("⚠️  pandas/pyyaml 없음")
    sys.exit(1)

BASE_CANDIDATES = [
    Path("pmx_universe_v5_1"),
    Path("./pmx_universe_v5_1"),
    Path("../pmx_universe_v5_1"),
    Path("."),  # also try current working directory (project root invocation)
]
BASE = next((c for c in BASE_CANDIDATES if (c / "config").is_dir()), None)
if BASE is None:
    print("❌  project base directory not found")
    sys.exit(1)

print("=" * 60)
print("CHECK-9: Phase 9 (Decision Tree + NONMEM QC) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "scripts/decision_tree/build_decision_tree.py",
    "scripts/decision_tree/verify_tree_table_match.py",
    "scripts/validation/nonmem_ready_qc.py",
    "config/operational_decision_tree.yaml",
    "release/v1.0/decision_tree_v1_0.sha256",
    "release/v1.0/decision_tree_lock_declaration.md",
    "reports/decision_tree_construction_plan.md",
    "reports/tree_table_consistency.md",
    "reports/phase9_completion_declaration.md",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  ✅ {f.split('/')[-1]}")
    else:
        print(f"  ❌ {f}")
        failures.append(f)

# Decision Tree 구조 검증
print("\n[Decision Tree 구조]")
tp = BASE / "config/operational_decision_tree.yaml"
if tp.is_file():
    try:
        data = yaml.safe_load(tp.read_text(encoding="utf-8"))
        tree = data.get("operational_decision_tree", data)
        order = tree.get("node_order", [])
        forced = {"N0", "N1", "N2", "N3", "N4", "N5", "N8"}
        if forced.issubset(set(order)):
            print(f"  ✅ Forced nodes 모두 tree 순서에 포함: {order}")
        else:
            missing = forced - set(order)
            print(f"  ❌ Forced 누락: {missing}")
            failures.append(f"tree forced 누락 {missing}")

        leaves = tree.get("leaves", [])
        print(f"  leaf 수: {len(leaves)}")

        q15_solo = sum(1 for l in leaves if l.get("q_code") == "Q15")
        q17 = sum(1 for l in leaves if l.get("q_code") == "Q17")
        if q15_solo == 0:
            print("  ✅ Q15 단독 leaf 0")
        else:
            failures.append(f"Q15 solo {q15_solo}")
        if q17 == 0:
            print("  ✅ Q17 leaf 0")
        else:
            failures.append(f"Q17 {q17}")

        auto_leaves = [l for l in leaves if l.get("terminal_state") == "AUTO"]
        bad_auto = [l for l in auto_leaves
                    if "export_nonmem_ready" not in l.get("action_sequence", [])]
        if not bad_auto:
            print(f"  ✅ AUTO leaves ({len(auto_leaves)}개) 모두 export_nonmem_ready")
        else:
            print(f"  ❌ AUTO leaf 중 export 없는 것 {len(bad_auto)}")
            failures.append("AUTO export 누락")

        labels_blob = " ".join(
            str(l.get("action_label", "")) + " " +
            " ".join(l.get("action_label_set", []) or [])
            for l in leaves
        ).upper()
        for kw in ["CELLULAR", "IMMUNOGEN", "MATERNAL", "DYAD"]:
            if kw in labels_blob:
                print(f"  ✅ v4.2 leaf 패턴 {kw}")
            else:
                print(f"  ⚠️  v4.2 leaf 패턴 {kw} 누락")
    except Exception as e:
        print(f"  ⚠️  YAML 파싱 오류: {e}")
        failures.append("yaml 파싱")

# Tree-table consistency
print("\n[Tree-Table Consistency]")
ttc = BASE / "reports/tree_table_consistency.md"
if ttc.is_file():
    txt = ttc.read_text(encoding="utf-8")
    if "100%" in txt or "100.0" in txt or "PASS" in txt.upper():
        print("  ✅ 100% match")
    else:
        print("  ⚠️  100% match 미확인")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 9 완료")
    print("→ 다음: Phase 10 (P106) — Golden Validation + H3, H4, H5")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
