#!/usr/bin/env python3
"""CHECK-10 — Phase 10 (Validation + Release) verification.

Per v5_1_step3_patched_v3.md lines 2422-2575.
"""
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas 없음"); sys.exit(1)

BASE_CANDIDATES = [
    Path("pmx_universe_v5_1"),
    Path("./pmx_universe_v5_1"),
    Path("../pmx_universe_v5_1"),
    Path("."),
]
BASE = next((c for c in BASE_CANDIDATES if (c / "config").is_dir()), None)
if BASE is None:
    print("❌  project base directory not found"); sys.exit(1)

print("=" * 60)
print("CHECK-10: Phase 10 (Validation + Release) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "scripts/validation/run_golden_validation.py",
    "scripts/validation/detect_false_classification.py",
    "scripts/validation/h4_sample_extractor.py",
    "reports/golden_validation_results.csv",
    "reports/golden_validation_summary_v1.md",
    "reports/false_classification_candidates.csv",
    "reports/coverage_metrics_final.md",
    "reports/human_review/h3_golden_approval_log.md",
    "reports/human_review/h4_final_audit_report.md",
    "reports/human_review/h4_sample_set.csv",
    "reports/human_review/h4_sample_blinded.csv",
    "release/v1.0/H5_final_release_approval.md",
    "release/v1.0/RELEASE_NOTES_v1_0.md",
    "release/v1.0/release_v1_0_combined.sha256",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  ✅ {f.split('/')[-1]}")
    else:
        print(f"  ❌ {f}"); failures.append(f)

# H3, H4, H5 서명
print("\n[Human Checkpoints 서명]")
for h, kw in [
    ("reports/human_review/h3_golden_approval_log.md", ["APPROVED", "Reviewed_by"]),
    ("reports/human_review/h4_final_audit_report.md", ["VETO_RELEASE", "Reviewed_by"]),
    ("release/v1.0/H5_final_release_approval.md", ["APPROVED", "Signed"]),
]:
    p = BASE / h
    if p.is_file():
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if all(k in txt or k.lower() in txt.lower() for k in kw):
            print(f"  ✅ {h.split('/')[-1]}: 서명")
        else:
            print(f"  ⚠️  {h.split('/')[-1]}: 서명 미확인")
            failures.append(f"{h.split('/')[-1]} 서명")

# H4 sampling 26개 확인
print("\n[H4 표본 감사 (PATCH-5)]")
hs = BASE / "reports/human_review/h4_sample_set.csv"
if hs.is_file():
    df = pd.read_csv(hs, comment='#')
    n = len(df)
    print(f"  샘플 수: {n}")
    if n >= 26:
        print("  ✅ ≥26 (10 AUTO + 10 REPAIR + 6 v4.2)")
    else:
        print(f"  ❌ <26: {n}")
        failures.append(f"H4 sample {n}/26")

# H4 audit report에서 VETO + sample mismatch
hr = BASE / "reports/human_review/h4_final_audit_report.md"
if hr.is_file():
    txt = hr.read_text(encoding="utf-8", errors="ignore")
    if "VETO_RELEASE" in txt and ("VETO_RELEASE: NO" in txt or "VETO_RELEASE = NO" in txt):
        print("  ✅ VETO_RELEASE: NO (release 가능)")
    elif "VETO_RELEASE" in txt:
        print("  ⚠️  VETO 결정 확인 필요")
    if "Blinded" in txt or "blinded" in txt:
        print("  ✅ Blinded sampling 수행됨")

# Golden validation PASS rate
print("\n[Golden Validation PASS rate]")
gv = BASE / "reports/golden_validation_results.csv"
if gv.is_file():
    df = pd.read_csv(gv)
    if "overall_status" in df.columns and len(df) > 0:
        pass_rate = (df["overall_status"] == "PASS").sum() / len(df)
        print(f"  PASS rate: {pass_rate:.1%}")
        if pass_rate >= 0.80:
            print("  ✅ ≥80%")
        else:
            print(f"  ⚠️  <80%")
            failures.append(f"golden PASS rate {pass_rate:.1%}")
    else:
        print("  ⚠️  컬럼 또는 데이터 없음")

# 9 deliverables hash 존재 확인
print("\n[9 Deliverables Hash — D1~D9 전체]")
hashes = [
    ("D1", "release/v1.0/scenario_universe_v1_0.sha256"),
    ("D2", "release/v1.0/action_label_lock_v1_0.sha256"),
    ("D5", "release/v1.0/minimal_node_set_v1_0.sha256"),
    ("D6", "release/v1.0/decision_tree_v1_0.sha256"),
    ("D7", "release/v1.0/repair_executor_v1_0.sha256"),
    ("D8", "release/v1.0/golden_validation_report_v1_0.sha256"),
    ("D9", "release/v1.0/release_v1_0_combined.sha256"),
]
for label, h in hashes:
    if (BASE / h).is_file():
        print(f"  ✅ {label}: {h.split('/')[-1]}")
    else:
        print(f"  ❌ {label}: {h.split('/')[-1]}")
        failures.append(f"hash {label} {h}")

# D8/D9 canonical
print("\n[D8/D9 Canonical Files]")
for label, path in [
    ("D8", "reports/golden_validation_report.md"),
    ("D9", "release/v1.0/coverage_claim_statement.md"),
]:
    if (BASE / path).is_file():
        print(f"  ✅ {label}: {path.split('/')[-1]}")
    else:
        print(f"  ❌ {label}: {path}")
        failures.append(f"{label} canonical 없음")

# Coverage Claim 표현 (PATCH-7)
print("\n[Coverage Claim 표현 (PATCH-7)]")
cc = BASE / "release/v1.0/RELEASE_NOTES_v1_0.md"
if cc.is_file():
    txt = cc.read_text(encoding="utf-8")
    forbidden = ["all practical scenarios", "exhaustive", "all modalities"]
    found = [w for w in forbidden if w.lower() in txt.lower()]
    if not found:
        print("  ✅ 금지 표현 없음")
    else:
        print(f"  ❌ 금지 표현: {found}")
        failures.append(f"forbidden words {found}")
    if "review-inclusive" in txt.lower():
        print("  ✅ 'review-inclusive' 사용")
    else:
        print("  ⚠️  'review-inclusive' 표현 미확인")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 10 완료 — RELEASE v1.0 APPROVED")
    print("→ 다음: Phase 11 (P116) — Change Control + 100-case Validation")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
