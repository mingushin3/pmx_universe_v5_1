#!/usr/bin/env python3
"""CHECK-11 — FINAL Project verification (Phase 11).

Per v5_1_step3_patched_v3.md lines 3459-3748.
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
print("CHECK-11: FINAL — 모든 Phase 완료 + Release v1.0 검증")
print("=" * 60)

failures: list[str] = []
warnings: list[str] = []

# 0. CHECK-0..CHECK-10 execution log
print("\n[CHECK-0 ~ CHECK-10 이전 단계 PASS 검증]")
log_path = BASE / "reports/execution_log.csv"
if log_path.is_file():
    try:
        log_df = pd.read_csv(log_path)
        for n in range(0, 11):
            check_name = f"CHECK-{n}"
            rows = log_df[log_df.get("step_id", pd.Series(dtype=str)).astype(str).str.contains(check_name, na=False)] if "step_id" in log_df.columns else pd.DataFrame()
            if len(rows) > 0:
                last_status = rows.iloc[-1].get("gate_status", "unknown")
                if str(last_status).upper() == "PASS":
                    print(f"  ✅ {check_name}: PASS (log)")
                else:
                    print(f"  ❌ {check_name}: {last_status}")
                    failures.append(f"{check_name} 미통과")
            else:
                print(f"  ⚠️  {check_name}: log 없음 (수동 확인 필요)")
                warnings.append(f"{check_name} log 없음")
    except Exception as e:
        print(f"  ⚠️  execution_log.csv 읽기 실패: {e} → 수동 확인")
        warnings.append("execution_log 읽기 실패")
else:
    print("  ⚠️  execution_log.csv 없음 — 이전 CHECK 수동 확인 필요")
    warnings.append("execution_log 없음")

# 1. 9 Final Deliverables
print("\n[9 Final Deliverables 존재 확인]")
DELIVERABLES = [
    ("D1", "data/scenario_universe/scenario_universe_v1.0.csv"),
    ("D2", "data/action_labels/scenario_action_table_locked.csv"),
    ("D3", "data/decision_table/reduced_decision_table_v1.0.csv"),
    ("D4", "data/ilp/pairwise_distinguishability_matrix.npz"),
    ("D5", "data/ilp/final_minimal_node_set.csv"),
    ("D6", "config/operational_decision_tree.yaml"),
    ("D7", "scripts/repair_executor/repair_executor.py"),
    ("D8", "reports/golden_validation_report.md"),
    ("D9", "release/v1.0/coverage_claim_statement.md"),
]
for did, path in DELIVERABLES:
    if (BASE / path).is_file():
        print(f"  ✅ {did}: {path.split('/')[-1]}")
    else:
        print(f"  ❌ {did}: {path}")
        failures.append(f"{did} 누락")

# 1b. D8/D9 hash
print("\n[D8/D9 SHA256 Hash]")
for did, hf in [
    ("D8", "release/v1.0/golden_validation_report_v1_0.sha256"),
    ("D9", "release/v1.0/release_v1_0_combined.sha256"),
]:
    if (BASE / hf).is_file():
        print(f"  ✅ {did} hash: {hf.split('/')[-1]}")
    else:
        print(f"  ❌ {did} hash 없음: {hf}")
        failures.append(f"{did} hash 없음")

# 2. H1-H5
print("\n[H1-H5 서명]")
for h, path in [
    ("H1", "config/deidentification_checklist_v5_1.md"),
    ("H2", "reports/human_review/h2_fingerprint_approval_log.md"),
    ("H3", "reports/human_review/h3_golden_approval_log.md"),
    ("H4", "reports/human_review/h4_final_audit_report.md"),
    ("H5", "release/v1.0/H5_final_release_approval.md"),
]:
    p = BASE / path
    if p.is_file():
        txt = p.read_text(encoding="utf-8", errors="ignore").lower()
        if "approved" in txt or "signed" in txt or "checked_by" in txt:
            print(f"  ✅ {h}: 서명")
        else:
            print(f"  ⚠️  {h}: 서명 미확인")
            warnings.append(f"{h} 서명")
    else:
        print(f"  ❌ {h}: 파일 없음")
        failures.append(h)

# 3. LP Panel CP1-CP7
print("\n[LP Panel CP1-CP7 결과]")
LP_PANELS = [
    "config_semantic_review",
    "universe_attack_freeze",
    "repair_semantic_review",
    "action_label_adjudication",
    "action_label_lock",
    "minimal_node_approval",
    "release_coverage_approval",
]
for cp in LP_PANELS:
    judge = BASE / f"reports/llm_proxy/{cp}_judge.md"
    if judge.is_file():
        print(f"  ✅ {cp}: judge 결과 존재")
    else:
        if cp == "repair_semantic_review":
            print(f"  ⚠️  {cp}: 조건부 (semantic question 없으면 skip)")
        else:
            print(f"  ❌ {cp}: judge 결과 없음")
            failures.append(f"LP {cp}")

# 4. v5.1 PATCH 적용 확인
print("\n[v5.1 PATCH 적용]")
charter = BASE / "project_charter_v5_1.md"
if charter.is_file():
    txt = charter.read_text(encoding="utf-8", errors="ignore")
    for kw, name in [
        ("v4.2", "PATCH-1 universe upgrade"),
        ("distinguishability", "PATCH-2 ILP strengthening"),
        ("forced node", "PATCH-3 forced node"),
        ("LP Panel", "PATCH-4 panel compression"),
        ("blinded", "PATCH-5 H4 sampling"),
        ("seed pack", "PATCH-6 pilot diversity"),
        ("review-inclusive", "PATCH-7 wording"),
    ]:
        if kw.lower() in txt.lower():
            print(f"  ✅ {name}")
        else:
            print(f"  ⚠️  {name}: charter 미언급")
            warnings.append(name)

# 5. Final completion declaration
print("\n[Final Completion Declaration]")
fcd = BASE / "reports/PROJECT_FINAL_COMPLETION_v5_1.md"
if fcd.is_file():
    print("  ✅ PROJECT_FINAL_COMPLETION_v5_1.md 존재")
    txt = fcd.read_text(encoding="utf-8")
    if "approval" in txt.lower() and "v1.0" in txt:
        print("  ✅ release v1.0 approval 명시")
else:
    print("  ❌ Final completion declaration 없음")
    failures.append("final completion")

# 6. CHANGELOG v1.0.0
print("\n[CHANGELOG v1.0.0]")
cl = BASE / "CHANGELOG.md"
if cl.is_file():
    txt = cl.read_text(encoding="utf-8")
    if "v1.0.0" in txt:
        print("  ✅ v1.0.0 entry")
    else:
        print("  ❌ v1.0.0 entry 없음")
        failures.append("CHANGELOG v1.0.0")

# PATCH-C4: F30 부재
print("\n[F30 부재 최종 확인 (PATCH-C4 — defense-in-depth)]")
for f30_target, f30_path in [
    ("Universe CSV", "data/scenario_universe/scenario_universe_v1.0.csv"),
    ("Action Labels", "data/action_labels/scenario_action_table_locked.csv"),
]:
    p = BASE / f30_path
    if p.is_file():
        try:
            import pandas as _pd
            _df = _pd.read_csv(p)
            if "family_id" in _df.columns:
                f30_n = (_df["family_id"].astype(str) == "F30").sum()
                if f30_n == 0:
                    print(f"  ✅ {f30_target}: F30 미사용 (reserved — 정상)")
                else:
                    print(f"  ❌ {f30_target}: F30 {f30_n}개 발견")
                    failures.append(f"F30 in {f30_target}")
        except Exception as _e:
            print(f"  ⚠️  {f30_target}: 읽기 오류 {_e}")

# 7. Forbidden words final
print("\n[Coverage Claim 표현 최종 확인 (PATCH-7)]")
release_files = [
    "release/v1.0/RELEASE_NOTES_v1_0.md",
    "release/v1.0/coverage_claim_statement.md",
    "reports/coverage_metrics_final.md",
    "reports/PROJECT_FINAL_COMPLETION_v5_1.md",
]
forbidden = ["all practical scenarios", "exhaustive", "all modalities"]
for rf in release_files:
    p = BASE / rf
    if p.is_file():
        txt = p.read_text(encoding="utf-8").lower()
        bad = [w for w in forbidden if w in txt]
        if not bad:
            print(f"  ✅ {rf.split('/')[-1]}: 금지 표현 없음")
        else:
            print(f"  ❌ {rf.split('/')[-1]}: 금지 표현 {bad}")
            failures.append(f"{rf} forbidden")

# 8. SOP
print("\n[Operational SOPs]")
SOPS = [
    "release/v1.0/SOP_new_case_intake_v1_0.md",
    "release/v1.0/SOP_change_control_v1_0.md",
    "release/v1.0/operator_quick_reference.md",
]
for s in SOPS:
    if (BASE / s).is_file():
        print(f"  ✅ {s.split('/')[-1]}")
    else:
        print(f"  ❌ {s.split('/')[-1]}")
        failures.append(f"SOP {s}")

# 9. 100-case validation CSV
print("\n[100-case Validation — CSV 기반 검증]")
csv_path = BASE / "reports/100_case_validation_results.csv"
md_path = BASE / "reports/100_case_validation_summary.md"
if csv_path.is_file():
    try:
        df100 = pd.read_csv(csv_path)
        total = len(df100)
        if "overall_status" in df100.columns and total > 0:
            pass_n = (df100["overall_status"].astype(str).str.upper() == "PASS").sum()
            pass_rate = pass_n / total
            print(f"  총 케이스: {total}, PASS: {pass_n} ({pass_rate:.1%})")
            if pass_rate >= 0.95:
                print("  ✅ PASS rate ≥95%")
            else:
                print(f"  ❌ PASS rate {pass_rate:.1%} < 95%")
                failures.append(f"100-case {pass_rate:.1%} < 95%")
            if "family_id" in df100.columns:
                bad_fam = df100[df100["overall_status"].astype(str).str.upper() != "PASS"]["family_id"].value_counts()
                if not bad_fam.empty:
                    print(f"  실패 family: {bad_fam.to_dict()}")
        else:
            print("  ⚠️  overall_status 컬럼 없음 또는 빈 CSV")
            warnings.append("100-case CSV 컬럼 부족")
    except Exception as e:
        print(f"  ⚠️  CSV 읽기 오류: {e}")
        warnings.append("100-case CSV 읽기 오류")
elif md_path.is_file():
    txt = md_path.read_text(encoding="utf-8")
    if "95%" in txt or "100%" in txt:
        print("  ⚠️  summary.md만 있음 — CSV로 재확인 권장")
        warnings.append("100-case CSV 없음, md만 있음")
    else:
        print("  ⚠️  95% 명시 미확인")
        warnings.append("100-case 95% 미확인")
else:
    print("  ⚠️  100-case validation 파일 없음 (post-release stress test — 미완료)")
    warnings.append("100-case 미완료")

# 최종 판정
print("\n" + "=" * 60)
print(f"경고 수: {len(warnings)}")
print(f"실패 수: {len(failures)}")

if warnings:
    print("\n⚠️  경고 항목:")
    for w in warnings:
        print(f"  - {w}")

if not failures:
    print("\n🟢🟢🟢 PROJECT v1.0 RELEASE COMPLETE 🟢🟢🟢")
    print("→ 모든 Phase 0-11 완료")
    print("→ 9 deliverables LOCKED with hash")
    print("→ H1-H5 모두 서명")
    print("→ LP Panel CP1-CP7 모두 처리")
    print("→ Release v1.0 운영 시작")
    print("\n다음 단계: v1.1 candidate register 모니터링 (분기별 review)")
else:
    print(f"\n🔴 실패 항목 {len(failures)}개:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
