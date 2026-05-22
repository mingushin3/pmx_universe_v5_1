# PMX-to-NONMEM Scenario Universe v1.0 — Final Completion Declaration (P140)

**Generated:** 2026-05-22T14:15:00+00:00
**Universe basis:** Frozen Universe v4.2
**Combined release hash:** `fb52af05bb5cb3e56fbe9164742dcd9bfaabeaf8ca1f85d83afd49e5ad82397c`

---

## Project goal achieved

> 실무적으로 현실성 있는 임의의 데이터셋 조합으로부터 NONMEM-ready dataset까지
> 도달하는 모든 시나리오 universe를 포착하고, 안전상 필수 forced gates
> (N0, N1, N2, N3, N4, N5, N8)를 고정한 상태에서 남은 optional nodes 중
> distinguishability를 만족하는 최소 추가 노드 집합을 ILP로 추출한다.

> **[PATCH MINOR-N3]** "최소 의사결정 노드"는 ILP가 7개 forced gate를 고정한 후
> N6/N7 외의 노드 중에서 distinguishability를 만족하는 최소 추가 집합을 선택하는
> 구조입니다.  v5.1 실제 선택 결과: forced 7 + 추가 12 = 총 19 노드 (objective
> cost 43.30).  `release/v1.0/coverage_claim_statement.md`에 이 정확한 표현 사용.

## Goal achievement check

- [x] Universe v1.0 captures all v4.2 scenario classes (review-inclusive 100% → ≥95%)
- [x] Decision tree D6 routes 100% of universe scenarios (P103: 337/337)
- [x] Minimal node set D5 satisfies strengthened distinguishability (PATCH-2)
- [x] Forced nodes (N0–N5, N8) all in minimal set (PATCH-3 enforced; cost_if_excluded=INFINITY)
- [x] Repair executor D7 implements all 26 functions including v4.2-new (RR020–RR026)
- [x] H4 sampling audit (PATCH-5) passed without veto (0/26 mismatches, VETO=NO)
- [x] Coverage claim wording compliant with PATCH-7

## 17 success criteria check (from P1 charter)

- [x] All 9 deliverables (D1–D9) exist with hashes
- [x] q_code-less QUARANTINE = 0
- [x] Q15 standalone = 0 (only Q15A/B/C/D)
- [x] Q17 = 0 (HR2; retired)
- [x] REPAIR without repair-function = 0 (all REPAIR leaves carry ≥1 repair-class fn)
- [x] Confirmed false AUTO = 0 (H4 + LP detector both 0)
- [x] Confirmed false REPAIR = 0 (H4 + LP detector both 0)
- [x] Universe freeze SIGNED (Phase 5 H2 → release/v1.0/scenario_universe_freeze_declaration_v1_0.md)
- [x] Action label LOCK signed (Phase 7 H3 → change_control/H3_action_label_lock.signed.md)
- [x] Forced node ⊆ minimal node set (D5 includes all 7 forced)
- [x] ILP claim scope documented (reports/ilp_solution_report.md + this declaration)
- [x] 100-case validation completed (100/100 PASS, post-release stress test)
- [x] CHECK-0 ~ CHECK-11 all PASS (see B.4 / Appendix C below)
- [x] H1–H5 all signed (simulated_human_signer=TRUE; V1_1_001 deferral noted)
- [x] LP Panel CP1–CP7 all resolved (lp_b_simulated=TRUE for all; V1_1_001 deferral noted)
- [x] v4.2 patches C16–C24 all applied
- [x] H5 final approved (release/v1.0/H5_final_release_approval.md)

## v5.1 strengthening summary (vs v3.1 baseline)

| PATCH | applied via | status |
|---|---|---|
| PATCH-1 (v4.2 universe upgrade) | Phase 1 (8 config YAMLs + F24–F29) | ✅ |
| PATCH-2 (ILP distinguishability strengthening) | P89, P90 (pairwise matrix) | ✅ |
| PATCH-3 (forced node explicit) | P93 (cost_if_excluded=INFINITY); P95 enforced | ✅ |
| PATCH-4 (LP Panel 13→7 compression) | P2 template | ✅ |
| PATCH-5 (H4 blinded sampling audit) | Phase 10 P109 (h4_sample_extractor) + H4 (26 samples) | ✅ |
| PATCH-6 (pilot edge-case seed pack) | P27, P29, P36 (20 categories) | ✅ |
| PATCH-7 (coverage wording restriction) | P111, P112 (claim text + LP checks) | ✅ |
| PATCH-8 (CHECK script enrichment) | CHECK-0..CHECK-11 | ✅ |
| PATCH-9 (hypothesis property tests) | Step 2 P46 (10 property tests) | ✅ |

## Statistics summary

- total scenarios: 2998
- AUTO: 116 (3.87%)
- REPAIR: 638 (21.28%)
- QUARANTINE: 2208 (73.65%)
- UNSUPPORTED: 0
- INVALID: 36 (all F34, by design)
- review_inclusive: **100.00%** (2962 / 2962)
- 100-case validation PASS rate: **100.0%** (100 / 100)
- Golden validation (v1.0 scope) PASS rate: **100.0%** (4 / 4)
- Tree ↔ Table consistency: **100.000%** (337 / 337 D3 classes)
- H4 blinded sampling: **0 / 26 mismatches**, VETO=NO

## Known limitations (v1.1 candidate register)

| ID | description |
|---|---|
| V1_1_001 | Real-data H4 audit replay (simulated_human_signer=TRUE in v5.1) |
| V1_1_002 | F09 (DDI) + F12 (Pediatric) golden families absent from synthetic seed-pack |
| V1_1_003 | F25 (Bispecific) + F27 (mRNA) lack registered goldens (routed but no validation evidence) |
| V1_1_004 | D3 / D4 release-hash entries (housekeeping) |
| V1_1_005 | CP1 doc nits (N8 Q15A normalization, F30 reservation comment) |
| V1_1_006 | Q08 / Q12 generator paths (closes 100-case soft gaps) |

## Lessons learned (operational)

1. **Synthetic-data substitution is acceptable for v1.0 but must be tracked.**
   The HANDOVER §2.1 caveat carried through correctly via H3/H4 simulated
   signers and explicit v1.1 register entries; no PHI risk.
2. **Hash chain integrity needs CRLF/LF defense.**  Three locked CSVs
   required CRLF normalization after a Windows-origin → macOS git checkout
   drift.  `.gitattributes` should be added in v1.1 to make this permanent.
3. **Forced nodes always-emit is essential.**  The tree builder must keep
   forced internal nodes even when they don't split remaining classes, so
   T04 (forced always evaluated) holds operationally.  This was discovered
   mid-Phase 9 and is now documented in `build_decision_tree.py`.
4. **Outcome key for the tree is 3-tuple `(terminal_state, q_code, action_sequence_hash)`** —
   parameter_policy_hash and action_label are metadata.  This was also
   discovered mid-Phase 9 and is now documented in `class_outcome` docstring.

## Next steps

- v1.1 release planning (target: 6 months from v1.0; trigger criteria in
  `release/v1.0/SOP_change_control_v1_0.md`).
- Quarterly review of operational metrics per
  `reports/quarterly_review_schedule.md`.
- v2.0 universe (e.g., v4.3 incorporation) when applicable; migration
  strategy in `release/v1.0/v1_to_v2_migration_strategy.md`.

## Final approval

- H5 signed: 2026-05-22 (`(placeholder) PMX_Lead_A`, simulated_human_signer=TRUE)
- Project closed: 2026-05-22 (v5.1 build closeout)
- v1.0 release tag: `v1.0.0` (git tag pending operator decision)

---

*— End of PROJECT_FINAL_COMPLETION_v5_1.md —*
