# Backward Artifact DAG — PMX-to-NONMEM Scenario Universe v5.1

> **Project Goal (immutable):**
> 실무적으로 현실성 있는 임의의 데이터셋 조합으로부터 NONMEM-ready dataset까지 발생 가능한
> 모든 시나리오 universe를 포착하고, 안전상 필수 forced gates(N0, N1, N2, N3, N4, N5, N8)를
> 고정한 상태에서 남은 optional nodes 중 강화된 distinguishability 제약을 만족하는
> 최소 추가 노드 집합을 ILP로 추출한다.
>
> **[PATCH MINOR-N3] ILP claim 정확화**
> - Forced nodes (7개): N0, N1, N2, N3, N4, N5, N8 — ILP 이전에 결정됨
> - Optional nodes (ILP 최적화 대상): N6, N7
> - "최소 의사결정 노드" = forced(7) ∪ ILP-selected(0~2)
> - distinguishability 제약 = (terminal_state, action_sequence, q_code, required_policy) 중
>   하나라도 다른 시나리오 쌍은 반드시 distinguish 가능해야 함

---

## 0. Backward Dependency DAG (visual)

```
D9 (coverage_claim_statement.md)
 └── D8 (golden_validation_report.md)
      ├── D6 (operational_decision_tree.yaml)
      │    └── D5 (final_minimal_node_set.csv)
      │         └── D4 (pairwise_distinguishability_matrix.npz)
      │              └── D3 (reduced_decision_table_v1.0.csv)
      │                   └── D2 (scenario_action_table_locked.csv)  ← LOCKED at H3
      │                        ├── D1 (scenario_universe_v1.0.csv)   ← FROZEN at H2
      │                        │    └── config/*.yaml (v4.2)
      │                        └── D7 (repair_executor.py)           ← LOCKED at H3
      └── D7 (repair_executor.py)
```

**Forward execution order:** config/*.yaml → D1 → D7 → D2 → D3 → D4 → D5 → D6 → D8 → D9

---

## 1. Deliverable D1 — `data/scenario_universe/scenario_universe_v1.0.csv`

| Field | Value |
|---|---|
| **Purpose** | Frozen Universe v4.2의 A0~A10 모든 valid 상태 조합 (시나리오 공간) |
| **Upstream files** | `config/axis_dictionary.yaml`, `config/terminal_state_taxonomy.yaml`, `config/q_code_dictionary.yaml`, `config/family_taxonomy.yaml`, `config/aic_field_schema.yaml`, `config/cross_axis_constraints.yaml` |
| **Generating step** | P23–P28 (Phase 2: scenario generator) |
| **Validation gate** | CHECK-2 (Phase 2 closure) |
| **Failure fallback** | Constraint 위반 시 P25(generator) 재실행 → 위반이 axis_dictionary 정의 문제이면 P8(axis YAML) 재실행 |
| **Immutable** | true (CP2 universe_attack_and_freeze 통과 후 freeze) |
| **Human approval** | H2 (universe freeze 서명) |
| **Notes** | v4.2 신규 상태(modality_class, endpoint_data_type 확장, A7 PRODUCT-LEVEL-COVARIATE, A8 analyte_role) 모두 포함. Q15 단독 사용 = 0, Q17 사용 = 0 필수. |

---

## 2. Deliverable D2 — `data/action_labels/scenario_action_table_locked.csv`

| Field | Value |
|---|---|
| **Purpose** | 각 시나리오의 (terminal_state, q_code, action_label, action_sequence) 결정 매트릭스 |
| **Upstream files** | D1 (scenario_universe_v1.0.csv), D7 (repair_executor.py), `config/repair_rule_dictionary.yaml`, `config/action_label_grammar.yaml` |
| **Generating step** | P61–P79 (Phase 5: action labeling + adjudication + lock) |
| **Validation gate** | CHECK-5 (action label lock) |
| **Failure fallback** | LP_C가 false-AUTO/false-REPAIR 감지 시 → P67(label generator) 재실행 → root cause가 repair function이면 P45(repair_executor) 재실행 |
| **Immutable** | true (CP5 action_label_lock 통과 후 freeze) |
| **Human approval** | H3 (action label lock 서명) |
| **Notes** | HR1-HR14 전부 적용. REPAIR row는 반드시 required_policy + algorithm 명시. QUARANTINE row는 반드시 q_code (Q01~Q19, Q17 제외) 동반. |

---

## 3. Deliverable D3 — `data/decision_table/reduced_decision_table_v1.0.csv`

| Field | Value |
|---|---|
| **Purpose** | N0~N8 candidate node × scenario 답변 매트릭스 (DC reduction 적용) |
| **Upstream files** | D2 (scenario_action_table_locked.csv), `config/candidate_node_dictionary.yaml` |
| **Generating step** | P84–P87 (Phase 7: decision table construction) |
| **Validation gate** | CHECK-7 |
| **Failure fallback** | DC reduction 후에도 distinguishability 위반 시 → P85(node detection rule) 재정의 → 안 되면 P82(candidate_node_dictionary)에 새 node 추가 |
| **Immutable** | false (decision table은 D5 도출의 입력으로만 사용; 재생성 가능) |
| **Human approval** | 없음 (Python CHECK 만으로 통과) |
| **Notes** | N8 (policy_availability) 반드시 포함. Forced node set ⊆ table column. |

---

## 4. Deliverable D4 — `data/ilp/pairwise_distinguishability_matrix.npz`

| Field | Value |
|---|---|
| **Purpose** | scenario pair × node 행렬 — 두 시나리오를 distinguish 가능한 node들 표시 |
| **Upstream files** | D3 (reduced_decision_table_v1.0.csv) + 강화된 distinguishability 정의 (HR14) |
| **Generating step** | P88–P90 (Phase 8: pairwise matrix construction) |
| **Validation gate** | CHECK-8 |
| **Failure fallback** | 어떤 pair도 어떤 node로도 distinguish 불가능 시 → D3 재생성(P85) → 그래도 실패하면 P82에 새 candidate node 추가 |
| **Immutable** | false (D5 입력으로만 사용) |
| **Human approval** | 없음 |
| **Notes** | distinguish 조건: 두 시나리오의 (terminal_state OR action_sequence OR q_code OR required_policy) 중 하나라도 다르면 distinguish 가능한 node가 ≥1개 존재해야 함. |

---

## 5. Deliverable D5 — `data/ilp/final_minimal_node_set.csv`

| Field | Value |
|---|---|
| **Purpose** | ILP 최적해로 추출된 최소 결정 노드 집합 |
| **Upstream files** | D4 (pairwise_distinguishability_matrix.npz), `config/node_cost_function.yaml`, forced node set {N0,N1,N2,N3,N4,N5,N8} |
| **Generating step** | P91–P95 (Phase 9: ILP solve + minimal node approval) |
| **Validation gate** | CHECK-9 + CP6 (minimal_node_approval) |
| **Failure fallback** | ILP infeasible 시 → forced node 정의 점검(P82) → distinguishability 정의 완화는 금지(HR14) → cost function 조정(P56) |
| **Immutable** | true (CP6 통과 후 lock) |
| **Human approval** | H5 일부 (release approval에 포함) |
| **Notes** | forced node set ⊆ minimal_node_set 필수 (HR13). ILP가 실제로 선택하는 대상은 N6, N7. Tier A/B/C/D claim scope 문서화 필요. |

---

## 6. Deliverable D6 — `config/operational_decision_tree.yaml`

| Field | Value |
|---|---|
| **Purpose** | 실행 가능한 결정 트리 (node 순서 + Q-code mapping + 분기 조건) |
| **Upstream files** | D5 (final_minimal_node_set.csv), `config/q_code_dictionary.yaml`, `config/candidate_node_dictionary.yaml` |
| **Generating step** | P96–P100 (Phase 10: decision tree assembly) |
| **Validation gate** | CHECK-10 |
| **Failure fallback** | 트리 노드 순서 또는 Q-code mapping 불일치 시 → P96 재실행 → D5와 일치 안 하면 P91 재실행 |
| **Immutable** | true (release 후 변경은 change_control 경유) |
| **Human approval** | H5 (release approval에 포함) |
| **Notes** | N1 분기에서 MATERNAL_INFANT_PK dyad linkage 경로 포함. N5 분기에서 CELLULAR_KINETICS LLOQ policy 분기 포함. |

---

## 7. Deliverable D7 — `scripts/repair_executor/repair_executor.py`

| Field | Value |
|---|---|
| **Purpose** | 26+ REPAIR 변환 함수 (v4.2 신규 7개 포함). 각 함수는 정책 + 유일 출력 알고리즘 보장 |
| **Upstream files** | `config/repair_rule_dictionary.yaml`, `config/axis_dictionary.yaml`, `config/aic_field_schema.yaml` |
| **Generating step** | P41–P50 (Phase 4: repair executor implementation + semantic review) |
| **Validation gate** | CHECK-4 + CP3 (repair_semantic_review, CONDITIONAL) |
| **Failure fallback** | property-based test 실패 시 → 해당 함수 재구현(P43) → 정책 자체가 불완전하면 P42(repair_rule_dictionary) 재정의 |
| **Immutable** | true (CP3 통과 후 lock; v1.0 release까지) |
| **Human approval** | H3 일부 (action label lock 시 함께 서명) |
| **Notes** | HR4(REPAIR=정책+알고리즘), HR5(AUTO에 repair function 금지). property-based testing (hypothesis) 적용. v4.2 신규 7함수: ADC parent/total/conjugated split, bispecific binding, CAR-T cell count derivation, mRNA dose form, lactation dyad anchor, pregnancy time anchor, immunogenicity adjudication. |

---

## 8. Deliverable D8 — `reports/golden_validation_report.md`

| Field | Value |
|---|---|
| **Purpose** | golden datasets vs decision tree + repair_executor 출력 일치 보고서 |
| **Upstream files** | D6 (operational_decision_tree.yaml), D7 (repair_executor.py), `data/golden_datasets/*` |
| **Generating step** | P101–P110 (Phase 11: golden validation + H4 blinded audit) |
| **Validation gate** | CHECK-11 |
| **Failure fallback** | golden 불일치 시 → root cause 분석 → label 문제면 P67/P74 재실행, repair 문제면 P43 재실행, tree 문제면 P96 재실행. 모두 아니면 golden 자체 재검토(P102). |
| **Immutable** | false (각 golden case 추가 시 재생성) |
| **Human approval** | H4 (AUTO/REPAIR sample blinded audit) — v5.1 강화 |
| **Notes** | H4 강화: minimum 10 random AUTO + 10 random REPAIR scenarios blinded audit before veto. |

---

## 9. Deliverable D9 — `release/v1.0/coverage_claim_statement.md`

| Field | Value |
|---|---|
| **Purpose** | review-inclusive coverage 주장문 (v1.0 release 문서) |
| **Upstream files** | D8 (golden_validation_report.md), H4 blinded audit 결과, pilot/seed-pack coverage 보고서 |
| **Generating step** | P111–P118 (Phase 12: release coverage approval) |
| **Validation gate** | CHECK-12 + CP7 (release_coverage_approval) |
| **Failure fallback** | claim wording이 HR11/HR12 위반 시 → P115 재작성. coverage 수치 미달 시 → 결손 case 식별 후 D1 재freeze(H2 재서명). |
| **Immutable** | true (release lock) |
| **Human approval** | H5 (final release approval) |
| **Notes** | **[PATCH MINOR-N2 Option B]** D9 근거 = D8 + H4 + pilot/seed-pack coverage. 100-case validation은 post-release operational stress test (v1.1 candidate register 트리거 용도), release 전제 아님. Wording 제한: "review-inclusive coverage of scenario classes represented in v4.2 universe"만 허용; "all practical scenarios", "exhaustive", "all modalities" 금지. |

---

## 10. Cross-Cutting Validation Gates (CHECK-0 ~ CHECK-12 요약)

| Gate | Phase | 주요 검증 항목 |
|---|---|---|
| CHECK-0 | Phase 0 (P1-P6) | 폴더 트리, 헌장, 14 hard rules 키워드, pytest |
| CHECK-1 | Phase 1 (P7-P22) | config YAML 6종, modality_class/endpoint_data_type/analyte_role 존재, Q17 부재 |
| CHECK-2 | Phase 2 (P23-P28) | D1 생성, 모든 v4.2 신규 상태 표현, constraint 8개 모두 만족 |
| CHECK-3 | Phase 3 (P29-P40) | pilot fingerprints 20 seed pack, AIC schema 적용 |
| CHECK-4 | Phase 4 (P41-P50) | D7 구현, 26+ 함수, property-based tests |
| CHECK-5 | Phase 5 (P61-P79) | D2 lock, label LP_C 통과 |
| CHECK-6 | (reserved) | — |
| CHECK-7 | Phase 7 (P84-P87) | D3 생성, forced node 모두 column |
| CHECK-8 | Phase 8 (P88-P90) | D4 생성, distinguish 불가능 pair = 0 |
| CHECK-9 | Phase 9 (P91-P95) | D5 생성, forced ⊆ minimal, ILP feasible |
| CHECK-10 | Phase 10 (P96-P100) | D6 생성, decision tree path coverage |
| CHECK-11 | Phase 11 (P101-P110) | D8, golden mismatch = 0 또는 모두 분석됨 |
| CHECK-12 | Phase 12 (P111-P118) | D9, HR11/HR12 wording 검사 |

---

## 11. Human Approval Checkpoints (H1~H5)

| H# | 시점 | 책임 범위 |
|---|---|---|
| H1 | Phase 1 config freeze (pre-pilot) | PHI/legal/IRB risk가 포함된 config 검토 |
| H2 | Phase 2 universe freeze | D1 lock 서명 — CP2 통과 후 |
| H3 | Phase 4–5 action label lock | D7 + D2 lock 서명 — CP3/CP5 통과 후 |
| H4 | Phase 11 golden audit | AUTO/REPAIR blinded sample audit (v5.1 강화) |
| H5 | Phase 12 release approval | D5/D6/D9 final sign-off; v1.0 release |

---

*— End of backward_artifact_dag.md —*
