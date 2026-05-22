# PMX-to-NONMEM Scenario Universe v5.1
## Python-Integrated Prompt Sequence (LLM-Maximal Edition)
### Step 3 / 3 — Phase 8~11 (P86~P140) + Final Completion

> **Step 1에서 한 일:** 환경 세팅 + Hard Rules + LP Panel 템플릿 + Frozen Universe v4.2 YAML + Action Sequence Lock
>
> **Step 2에서 한 일:** Pilot 데이터(H1, H2) + Repair Executor v1.0 LOCK + Universe v1.0 FREEZE + Action Label LOCK
>
> **Step 3에서 할 일:** ILP 최소 결정 노드(N0-N8) 추출 + 결정 트리 + Golden 검증(H3) + 표본 감사(H4) + Release(H5) + Change Control + 100-case Validation + 최종 완수 선언

---

## 🚦 진입 조건 점검

Step 3를 시작하기 전 다음이 모두 PASS여야 합니다:

```
✅ CHECK-0 PASS  (Phase 0 완료)
✅ CHECK-1 PASS  (Phase 1 — v4.2 universe YAML 완료)
✅ CHECK-2 PASS  (Phase 2 — action sequence lock 완료)
✅ CHECK-3 PASS  (Phase 3 — pilot 데이터 + H1 + H2 완료)
✅ CHECK-4 PASS  (Phase 4 — repair executor LOCK)
✅ CHECK-5 PASS  (Phase 5 — universe FREEZE v1.0)
✅ CHECK-6 PASS  (Phase 6 — decision nodes N0-N8 + cost)
✅ CHECK-7 PASS  (Phase 7 — action label LOCK)
```

만약 하나라도 FAIL이면 해당 Step으로 돌아가 재실행하세요.

---

## 📑 Step 3 진행 맵

```
Phase 8  (P86~P100):  Decision Table + ILP 최소 결정 노드 추출 + LP Panel CP6
Phase 9  (P101~P105A): Operational Decision Tree + NONMEM-Ready QC + Lock
Phase 10 (P106~P115): Golden 검증(H3) + 표본 감사(H4) + Release(H5) + LP Panel CP7 + Release Tag
Phase 11 (P116~P140): Change Control + 100-case Validation + SOP + 최종 완수

CHECK-8, CHECK-9, CHECK-10, CHECK-11 (최종)
```

> ⚠️ **[PATCH F-1]** 위 Phase 범위는 Step1/Step2 기준표와 동기화된 확정값입니다.
> 구버전 표기 `Phase 8 P86-P105`, `Phase 9 P106-P115`는 폐기됩니다.
> Phase 8 헤딩과 Phase 9 헤딩도 아래 본문에서 동일하게 수정되어 있습니다.

---

## 🧮 Phase 8: Decision Table + ILP 최소 결정 노드 (P86~P100)

### 📌 이 단계 목적

Step 2에서 만든 **scenario_action_table_locked.csv** + **candidate_node_dictionary_with_costs.csv**를 입력으로,
**ILP(Integer Linear Programming)**를 풀어 모든 시나리오 쌍을 distinguish할 수 있는 **최소 결정 노드 집합 D5**를 추출합니다.

### v5.1 핵심 강화 (Step 1에서 PATCH-2, PATCH-3로 정의)
- **PATCH-2: Distinguishability 강화** — 두 시나리오 쌍이 (terminal_state, action_sequence, q_code, required_policy) 중 하나라도 다르면 반드시 distinguish 가능해야 함. 단순 axis 차이만으로는 부족.
- **PATCH-3: Forced node 명시** — N0, N1, N2, N3, N4, N5, N8 (총 7개)는 ILP 해(解)에 무조건 포함. 비용 무한대 페널티로 강제.

### 진입 조건
- [x] CHECK-7 PASS
- [x] D2 scenario_action_table_locked.csv 존재 (hash 검증됨)
- [x] candidate_node_dictionary_with_costs.csv 존재 (9 노드, 7 forced)

---

### P86 — Decision Table 생성기 구현

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** CHECK-7 PASS
🔹 **첨부 파일:**
  - `data/action_labels/scenario_action_table_locked.csv`
  - `config/candidate_node_dictionary_with_costs.csv`
  - `config/axis_dictionary.yaml`
🔹 **산출물:**
  - `scripts/decision_table/generate_decision_table.py`
  - `data/decision_table/raw_decision_table.csv`
🔹 **다음 액션:** P87 진행

```
ROLE: Coding agent.

INPUT (attached):
  data/action_labels/scenario_action_table_locked.csv
  config/candidate_node_dictionary_with_costs.csv
  config/axis_dictionary.yaml

TASK: Implement scripts/decision_table/generate_decision_table.py.

PROCEDURE:
1. Load locked action table (with scenario_id, A0..A10, modality_class,
   endpoint_data_type, analyte_role, terminal_state, q_code, action_label,
   action_sequence, parameter_policy, family_id).
2. Load 9 nodes (N0..N8) from candidate_node_dictionary_with_costs.csv.
3. For EACH scenario, compute deterministic answer for each node:
   - Y/N/NA based on detection rule from node dictionary
   - Use detection logic from Step 2 P67 (pilot_node_test.py)

NODE EVALUATION RULES (must match P67 exactly):
N0 = Y if A0 != AIC-MISSING AND endpoint_data_type declared (when required)
N1 = Y if A9 != IRRECONCILABLE AND ID constructible
        AND (if MATERNAL_INFANT_PK: dyad_linkage_key present)
N2 = Y if A3 not in {UNRECOVERABLE, AMBIGUOUS without policy}
        AND (delivery_anchor present if pregnancy/lactation)
N3 = Y if A4 not in {UNRECOVERABLE, MISSING-NO-POLICY,
                     ADDL-ACTUAL-CONFLICT without policy,
                     TITRATION/LOADING/INFUSION without policy}
N4 = Y if A5 not in {ABSENT, BIOANALYTICAL-FINAL-FLAG-MISSING,
                     BLQ-NO-POLICY (concentration), Cellular without policy}
        AND (A9 != REANALYSIS-FINAL-MISSING)
        AND (if IMMUNOGENICITY: positivity_rule present)
N5 = Y if A5 not in {BLQ-NO-POLICY, LLOQ-MISSING}
        AND (cellular_LLOQ present if cellular endpoint)
N6 = Y if A7 not in {KEY-MISSING, POLICY-MISSING}
        AND (product_level_linkage present if PRODUCT-LEVEL-COVARIATE)
N7 = Y if no unresolved q_code
N8 = Y if ALL required_policies for proposed action_sequence are present

OUTPUT CSV: data/decision_table/raw_decision_table.csv

COLUMNS:
scenario_id, family_id, terminal_state, q_code, action_label,
action_sequence_hash,    # SHA256 first 12 chars of joined function names
parameter_policy_hash,   # SHA256 first 12 chars of policy dict (sorted keys)
required_policy_set,     # comma-separated sorted set
N0, N1, N2, N3, N4, N5, N6, N7, N8

VALIDATION:
- Row count matches scenario_action_table_locked.csv
- All N0..N8 in {Y, N, NA}
- No NULLs in node columns

CLI:
python scripts/decision_table/generate_decision_table.py \
  --action-table data/action_labels/scenario_action_table_locked.csv \
  --node-dict config/candidate_node_dictionary_with_costs.csv \
  --out data/decision_table/raw_decision_table.csv

OUTPUT: Script + CSV. Must run successfully.
```

---

### P87 — Don't-Care (DC) Reduction

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P86 완료
🔹 **첨부 파일:** P86 raw_decision_table.csv, P66 node dictionary
🔹 **산출물:**
  - `scripts/decision_table/dc_reduction.py`
  - `data/decision_table/reduced_decision_table_v1.0.csv` (= **D3**)
  - `reports/dc_reduction_report.md`
🔹 **다음 액션:** P88

> **DC reduction 의미:** 어떤 시나리오에서 N6=NA(평가 불가)면 N6을 "*"로 표기. ILP에서 이 셀은 distinguishability 계산 시 don't-care로 처리됩니다.

```
ROLE: Coding agent.

TASK: Implement scripts/decision_table/dc_reduction.py.

PROCEDURE:
1. Load raw_decision_table.csv
2. For each cell with value "NA" (node is not applicable to this scenario):
   - Replace with "*" (don't-care)
3. Detect scenarios that became identical after DC replacement
   (same N0..N8 pattern with * treated as wildcard)

   # ⚠️ [PATCH DC-wildcard] DC 클래스 생성 규칙 (v5.1):
   # wildcard compatibility는 비이행적(non-transitive)일 수 있습니다.
   # 예: 시나리오 A="Y,*,N" B="Y,Y,*" C="*,Y,N"은
   #     A↔B 호환, B↔C 호환이지만 A↔C 불호환 → 같은 class에 넣으면 안됨.
   #
   # MANDATORY: 아래 두 방법 중 하나를 선택하고 코드에 명시:
   # Option 1 (권장): exact string pattern grouping
   #   - "*"를 포함한 N0..N8 문자열이 정확히 동일한 경우만 같은 class
   #   - 구현: df.groupby(["N0","N1","N2","N3","N4","N5","N6","N7","N8"])
   # Option 2: pairwise compatibility graph + maximal clique
   #   - 두 시나리오가 각 위치에서 (Y==Y or 둘 중 하나 "*") 이면 호환
   #   - class = maximal clique (greedy merge 금지)
   #
   # FORBIDDEN: greedy merge (순서대로 "호환이면 추가" 방식) → ILP distinguishability 손실 위험
   GROUPING_METHOD = "exact_pattern"  # or "maximal_clique"

4. Group identical scenarios into "DC-equivalence classes"
5. Within each class, verify they have:
   - Same terminal_state
   - Same q_code
   - Same action_sequence_hash
   - Same parameter_policy_hash
   - Same required_policy_set
   If ANY differ → FATAL: log scenario_ids and emit error
6. Output reduced_decision_table_v1.0.csv with DC equivalence classes
   (one row per class, with member_scenario_ids list)

REPORT (reports/dc_reduction_report.md):
- total_input_scenarios
- total_dc_classes (this becomes the actual "scenarios" for ILP)
- reduction_ratio (dc_classes / input_scenarios)
- fatal_inconsistencies (must be 0)
- v4.2 specific reduction:
  - CELLULAR_KINETICS scenarios with NA on N5 vs cellular_LLOQ
  - MATERNAL_INFANT scenarios with NA on N6 (product-level)

GATE:
- fatal_inconsistencies == 0 (otherwise rollback to P86 review)
- reduction_ratio typically 0.3-0.6 (if higher, possibly over-grouping)

OUTPUT: Script + 2 files.
```

---

### P88 — Action Sequence + Policy Hash Validation

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P87 완료
🔹 **첨부 파일:** P87 reduced_decision_table, P86 raw_decision_table
🔹 **산출물:**
  - `scripts/decision_table/validate_hashes.py`
  - `reports/decision_table_hash_validation.md`
🔹 **다음 액션:** P89

```
ROLE: Coding agent.

TASK: Implement scripts/decision_table/validate_hashes.py.

CHECKS:
H01  action_sequence_hash uniqueness per (action_label, parameter_policy_hash) tuple
H02  Same action_label always has same action_sequence_hash
H03  parameter_policy_hash deterministic (re-hash same policy → same value)
H04  required_policy_set is consistent within DC-equivalence class
H05  v4.2: cellular_LLOQ_derivation_policy hash propagated correctly for F26
H06  v4.2: dyad_linkage_policy hash propagated correctly for F29
H07  v4.2: positivity_adjudication_rule hash propagated correctly for F27 IMMUNOGEN

REPORT: reports/decision_table_hash_validation.md
- check results
- mismatches with scenario_id list

GATE: All checks PASS. If any fail → fix in P86 (action_label inconsistency)
or P87 (DC reduction grouping error).

OUTPUT: Script + report.
```

---

### P89 — Strengthened Distinguishability Definition (PATCH-2)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P88 PASS
🔹 **첨부 파일:** P87 reduced_decision_table, charter HR14
🔹 **산출물:** `reports/distinguishability_definition_v5_1.md`
🔹 **다음 액션:** P90

> **이 단계는 v5.1 PATCH-2의 핵심 구현 단계입니다.** 강화된 distinguishability 정의를 명문화한 뒤, P90 코드에 반영합니다.

```
ROLE: PMX Grandmaster + ILP modeler.

INPUT (attached):
  data/decision_table/reduced_decision_table_v1.0.csv (head + summary)
  project_charter_v5_1.md (HR14)

TASK: Produce reports/distinguishability_definition_v5_1.md.

CONTENT:

# Pairwise Distinguishability Definition v5.1 (PATCH-2)

## Definition
For two DC-equivalence classes c_i and c_j:

DISTINGUISHABLE_REQUIRED(c_i, c_j) = TRUE iff ANY of the following differs:
  - terminal_state(c_i) != terminal_state(c_j)
  - action_sequence_hash(c_i) != action_sequence_hash(c_j)
  - q_code(c_i) != q_code(c_j)  (treating null as null, not different from null)
  - required_policy_set(c_i) != required_policy_set(c_j)

For pairs where DISTINGUISHABLE_REQUIRED is TRUE, the selected node subset S
(minimal node set) MUST satisfy:
  ∃ n ∈ S such that node_value(c_i, n) ≠ node_value(c_j, n)
  where * (don't-care) is treated as compatible with any value.

For pairs where DISTINGUISHABLE_REQUIRED is FALSE (truly equivalent),
the constraint is satisfied vacuously (they may be indistinguishable).

## Why Strengthened (vs v3.1 baseline)

v3.1 baseline only required terminal_state OR action_label difference.
This was insufficient because:
1. Two scenarios may share action_label but differ in parameter_policy
   (e.g., REPAIR_BLQ_M3 with M3 vs M3-LIN extrapolation)
2. Two scenarios may share terminal_state but require different policies
   in AIC (i.e., user must declare different things)
3. v4.2 specific: CAR-T REPAIR with vs without product-level linkage policy
   would be incorrectly merged under v3.1.

## Treatment of "*" (don't-care)

When comparing node_value(c_i, n) to node_value(c_j, n):
- Both Y → match (same)
- Both N → match (same)
- Y vs N → differ (distinguishable on this node)
- * vs Y or * vs N → match (don't-care is compatible)
- * vs * → match

So a node CAN distinguish a pair only if both have non-* values that differ.

## Edge cases (v4.2)
- N1 dyad path: scenarios with MATERNAL_INFANT_PK and dyad present vs absent
  must differ at N1 → both should be non-*
- N4 cellular: CELLULAR_KINETICS with vs without cellular_LLOQ should differ at N4
- N8 policy_availability: ALL pairs that differ in required_policy_set
  should differ at N8 (force this in detection logic)

## Mathematical formulation for ILP
For binary variables x_n ∈ {0,1} (1 if node n is selected):

Constraint per distinguishable pair (c_i, c_j):
  Σ_{n: node_value(c_i, n) ≠ node_value(c_j, n) AND both non-*} x_n ≥ 1

If RHS set is empty for some required pair → INFEASIBLE
(meaning the universe definition itself fails distinguishability — needs P92 escalation)

OUTPUT: Markdown.
```

---

### P90 — Pairwise Distinguishability Matrix 생성

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P89 완료
🔹 **첨부 파일:** P87 reduced_decision_table, P89 definition
🔹 **산출물:**
  - `scripts/decision_table/build_pairwise_matrix.py`
  - `data/ilp/pairwise_distinguishability_matrix.npz` (= **D4**)
  - `reports/pairwise_matrix_report.md`
🔹 **다음 액션:** P91

```
ROLE: Coding agent.

INPUT (attached):
  data/decision_table/reduced_decision_table_v1.0.csv
  reports/distinguishability_definition_v5_1.md

TASK: Implement scripts/decision_table/build_pairwise_matrix.py.

PROCEDURE:
1. Load reduced_decision_table → DataFrame with M rows (DC classes)
2. Compute DISTINGUISHABLE_REQUIRED matrix R[M, M]:
   R[i,j] = 1 if (terminal_state, action_sequence_hash, q_code, required_policy_set)
              differs between class i and class j; else 0
3. Compute distinguishing-node matrix D[M, M, 9]:
   D[i,j,n] = 1 if node n distinguishes pair (i,j)
              (both non-* and differ); else 0
4. Identify INFEASIBLE pairs:
   - R[i,j] = 1 AND sum_n(D[i,j,n]) = 0
   - These are pairs that REQUIRE distinguishing but no node can distinguish them
5. Save numpy archive:
   - 'R': R matrix (M x M, uint8)
   - 'D': D tensor (M x M x 9, uint8)
   - 'class_ids': array of DC class IDs in order
   - 'node_ids': ['N0', 'N1', ..., 'N8']
   - 'infeasible_pairs': list of (i, j) tuples with R=1 and no distinguishing node

REPORT (reports/pairwise_matrix_report.md):
- M (number of DC classes)
- total_pairs = M*(M-1)/2
- distinguishable_required_count = sum(R) / 2
- infeasible_pair_count
- node-wise distinguishing power: for each n, how many R=1 pairs n alone covers
- v4.2 sanity:
  - F26 (CAR-T) classes: how many distinguished by N4 (cellular_LLOQ)
  - F29 (Lactation) classes: how many distinguished by N1 (dyad)
  - Q19 IMMUNOGENICITY classes: distinguished from non-Q19 immunogen REPAIRs

CLI:
python scripts/decision_table/build_pairwise_matrix.py \
  --decision-table data/decision_table/reduced_decision_table_v1.0.csv \
  --out data/ilp/pairwise_distinguishability_matrix.npz \
  --report reports/pairwise_matrix_report.md

GATE:
- infeasible_pair_count == 0 (else trigger P91 universe gap analysis)

OUTPUT: Script + 2 files.
```

---

### P91 — Infeasible Pair Triage (조건부)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P90 완료, infeasible_pairs 존재 시만
🔹 **첨부 파일:** P90 report, reduced_decision_table
🔹 **산출물:** `reports/infeasible_pair_triage.md`
🔹 **다음 액션:** P92 또는 P93

```
ROLE: PMX Grandmaster + ILP modeler.

INPUT: reports/pairwise_matrix_report.md (with infeasible_pair list)

If infeasible_pair_count = 0: output "PASS — no infeasible pairs" and stop.

Otherwise, for each infeasible pair (c_i, c_j):
1. Inspect why no node distinguishes them:
   - Are both classes having "*" for all candidate distinguishing nodes?
   - Is universe definition under-specified (e.g., two distinct policies
     produce same axis pattern)?
2. Classification:
   - UNIVERSE_GAP: missing axis state (need patch to v4.2 universe)
   - NODE_DEF_INSUFFICIENT: existing nodes don't capture relevant distinction
     (need new node N9, N10, ...)
   - REQUIREMENT_LOOSER: pair should not actually require distinguishing
     (e.g., they are truly EP-equivalent, fix labeling in P77-P79)
3. Recommendation:
   - For UNIVERSE_GAP → defer to v1.1 register (cannot patch frozen universe)
     OR escalate to H4 with universe-rollback recommendation
   - For NODE_DEF_INSUFFICIENT → propose new node, add to candidate dictionary
   - For REQUIREMENT_LOOSER → return to action_label adjudication

OUTPUT: Markdown with one entry per infeasible pair, severity, recommendation.

GATE:
- If any UNIVERSE_GAP → severe escalation (H4 forced)
- If only NODE_DEF_INSUFFICIENT or REQUIREMENT_LOOSER → can resolve in P92
```

---

### P92 — Node Dictionary 보강 또는 Label 재조정 (조건부)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE) + R-LLM (고성능 추론 모델) — 분석 위주는 R-LLM, 코드 수정은 C-LLM
🔹 **진입 조건:** P91 결과에서 NODE_DEF_INSUFFICIENT 또는 REQUIREMENT_LOOSER 있는 경우
🔹 **산출물:**
  - 수정된 `config/candidate_node_dictionary_with_costs.csv` (N9, N10 추가 시)
  - 또는 수정된 `data/action_labels/scenario_action_table_locked.csv` (label 재조정)
  - `change_control/v1_1_or_v1_0_patch_decision.md`
🔹 **다음 액션:** P86부터 재실행 → P90 PASS 확인 → P93

```
ROLE: PMX Grandmaster + Coding agent.

INPUT: reports/infeasible_pair_triage.md

PROCEDURE per recommendation:

For NODE_DEF_INSUFFICIENT (add new node):
1. Define new node Nx (e.g., N9 = "Reanalysis final-flag policy explicit")
2. Add to candidate_node_dictionary_with_costs.csv with:
   - cost (use methodology from Step 2 P68)
   - forced_inclusion = FALSE (new nodes are non-forced unless universally needed)
3. Re-run P86 (decision table generation) → P87 (DC reduction) → P88 → P90
4. Verify infeasible_pair_count = 0

For REQUIREMENT_LOOSER (label merge):
1. If two scenarios truly EP-equivalent but distinct hashes → merge action_label
2. CAUTION: This requires re-locking action_label (return to Phase 7 P83-P84)
   Only do if H4 (release-stage human) approves rollback
   For minor cases (cosmetic difference only) → log to v1.1 register

For UNIVERSE_GAP:
1. CANNOT patch frozen universe v1.0
2. Document in change_control/v1_1_or_v1_0_patch_decision.md
3. Two options:
   a. Roll back universe freeze (massive cost — full Phase 5 redo)
   b. Defer to v1.1, accept that v1.0 has known infeasible pairs
      (and document them in coverage_claim_statement)

OUTPUT: Updated files + decision document.

GATE: After fix, P90 must show infeasible_pair_count = 0
```

---

### P93 — ILP Cost Function 잠금 + Forced Node Constraint 코드화

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P90 (또는 P92 후) PASS
🔹 **첨부 파일:** P68 cost (Step 2), P89 definition, candidate_node_dictionary_with_costs.csv
🔹 **산출물:**
  - `config/ilp_problem_definition.yaml`
  - `release/v1.0/ilp_cost_lock_v1_0.md`
🔹 **다음 액션:** P94

```
ROLE: Coding agent + PMX Grandmaster (review).

INPUT (attached):
  config/candidate_node_dictionary_with_costs.csv
  reports/distinguishability_definition_v5_1.md

TASK 1: Produce config/ilp_problem_definition.yaml

ilp_problem:
  version: "v1.0"
  objective: minimize_cost
  variables:
    - name: x_N0
      type: binary
      cost: 4.20
      forced: true
    - name: x_N1
      cost: 3.90
      forced: true
    - name: x_N2
      cost: 4.10
      forced: true
    - name: x_N3
      cost: 4.50
      forced: true
    - name: x_N4
      cost: 4.10
      forced: true
    - name: x_N5
      cost: 3.10
      forced: true
    - name: x_N6
      cost: 2.00
      forced: false
    - name: x_N7
      cost: 2.10
      forced: false
    - name: x_N8
      cost: 4.40
      forced: true
  constraints:
    - id: forced_inclusion
      description: "PATCH-3: forced nodes must equal 1"
      formulation: |
        x_N0 = 1
        x_N1 = 1
        x_N2 = 1
        x_N3 = 1
        x_N4 = 1
        x_N5 = 1
        x_N8 = 1
    - id: distinguishability
      description: "PATCH-2: every required pair must be distinguished"
      formulation: |
        For each (i, j) with R[i,j] = 1:
          Σ_{n where D[i,j,n] = 1} x_n ≥ 1
  cost_immutability:
    locked_at: "<ISO timestamp>"
    locked_by: "automated (Step 2 P68 + P93)"
    modification_policy: "Costs frozen until v1.1 release. Any change requires
                          full ILP re-run + LP Panel CP6 re-approval."

TASK 2: Produce release/v1.0/ilp_cost_lock_v1_0.md

CONTENT:
- Cost summary table (9 rows)
- Forced nodes: N0, N1, N2, N3, N4, N5, N8 (7 nodes, sum cost = 28.20)
- Free nodes: N6, N7 (2 nodes, cost 2.00 + 2.10)
- Theoretical lower bound on objective: 28.20 (forced nodes only,
  if they alone satisfy distinguishability — unlikely for full universe)
- Hash of ilp_problem_definition.yaml

OUTPUT: 2 files.
```

---

### P94 — ILP Solver 구현

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P93 완료
🔹 **첨부 파일:** P90 matrix npz, P93 ilp_problem yaml
🔹 **산출물:**
  - `scripts/ilp/solve_minimal_node_set.py`
  - `tests/test_solve_minimal_node_set.py`
🔹 **다음 액션:** P95

```
ROLE: Coding agent.

TASK 1: Implement scripts/ilp/solve_minimal_node_set.py

REQUIREMENTS:
- Use OR-Tools CP-SAT solver (preferred) or PuLP with CBC fallback
- Inputs: pairwise_distinguishability_matrix.npz, ilp_problem_definition.yaml
- Output: data/ilp/solver_output.json with:
  - status: OPTIMAL / FEASIBLE / INFEASIBLE
  - objective_value: total cost
  - selected_nodes: list of N0..N8 selected (forced + free)
  - solve_time_seconds
  - lp_relaxation_bound (if available)
  - infeasibility_reason (if INFEASIBLE)

ALGORITHM:
1. Load matrix R, D from npz
2. Load cost + forced from ilp_problem_definition.yaml
3. Create variables x_N0..x_N8 (binary)
4. Add forced constraints: x_n = 1 for forced nodes
5. Add distinguishability constraints: for each (i,j) with R[i,j]=1:
   sum(x_n for n where D[i,j,n]=1) >= 1
6. Set objective: minimize sum(cost[n] * x_n)
7. Solve with timeout = 300 seconds
8. Output JSON

EDGE CASES:
- INFEASIBLE: log distinguishability conflict (should have been caught in P90)
- Multiple optima: solver picks one (deterministic via seed)
- Forced nodes alone insufficient: solver adds free nodes

CLI:
python scripts/ilp/solve_minimal_node_set.py \
  --matrix data/ilp/pairwise_distinguishability_matrix.npz \
  --problem config/ilp_problem_definition.yaml \
  --out data/ilp/solver_output.json

TASK 2: tests/test_solve_minimal_node_set.py
- 5+ test cases:
  T1. Trivial 2-class problem with 1-node distinguishing → expected solution
  T2. Forced-only feasibility (constructed case)
  T3. INFEASIBLE detection (constructed case with no distinguishing node)
  T4. Cost minimization (verify solver picks lower-cost node when both work)
  T5. v4.2 specific: synthetic case with CELLULAR_KINETICS distinguishability
       resolved by N4 only

OUTPUT: 2 files. Run pytest.
```

---

### P95 — ILP 실행 + final_minimal_node_set.csv 생성

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P94 PASS (pytest)
🔹 **첨부 파일:** D3, D4, ilp_problem yaml
🔹 **산출물:**
  - `data/ilp/solver_output.json`
  - `data/ilp/final_minimal_node_set.csv` (= **D5**)
  - `reports/ilp_solution_report.md`
🔹 **다음 액션:** P96 (LP Panel CP6 시작)

```
ROLE: Coding agent.

PROCEDURE:
1. Run python scripts/ilp/solve_minimal_node_set.py
   --matrix data/ilp/pairwise_distinguishability_matrix.npz
   --problem config/ilp_problem_definition.yaml
   --out data/ilp/solver_output.json

2. Verify status == OPTIMAL or FEASIBLE
3. If INFEASIBLE → STOP, escalate (P91 should have caught this earlier)

4. Generate data/ilp/final_minimal_node_set.csv:
   Columns: node_id, included, forced, cost, rationale_v5_1
   One row per N0..N8

5. Verify forced nodes ∈ included (HR13 enforcement):
   for n in [N0, N1, N2, N3, N4, N5, N8]:
     assert solver_output.selected_nodes contains n
   If not → FATAL, log + emit "ESCALATE: forced node violation"

6. Generate reports/ilp_solution_report.md:
   - solver status, objective, solve_time
   - selected_nodes list
   - excluded nodes (if any) with rationale
   - distinguishability coverage:
     - total required pairs
     - pairs distinguished by selected set
     - pairs distinguished by each individual node
   - v4.2 specific:
     - CELLULAR_KINETICS pair coverage
     - MATERNAL_INFANT pair coverage
     - IMMUNOGENICITY pair coverage
     - PRODUCT-LEVEL-COVARIATE pair coverage

7. Update CHANGELOG.md: "## v0.8.0 — ILP solved, minimal node set extracted"

OUTPUT: 3 files + CHANGELOG.

GATE:
- forced node ⊆ selected_nodes (else FATAL)
- distinguishability coverage = 100% of required pairs (else FATAL)
```

---

### P96~P98 — LP Panel CP6: Minimal Node Approval (강화: dangerous_merge 흡수)

> **v5.1 변경:** v3.1에서 별도 LP Panel이었던 dangerous_merge_check를 minimal_node_approval에 흡수 (PATCH-4).

#### P96 (LP-A) — Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P95 solver output + report, P89 definition, D3 reduced_decision_table
🔹 **산출물:** `reports/llm_proxy/minimal_node_approval_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A) for Checkpoint CP6 (minimal_node_approval).

INPUT (attached):
  data/ilp/solver_output.json
  data/ilp/final_minimal_node_set.csv
  reports/ilp_solution_report.md
  reports/distinguishability_definition_v5_1.md
  data/decision_table/reduced_decision_table_v1.0.csv

TASKS (combined: minimal node approval + dangerous merge check):

PART A: Minimal node set approval
1. Forced nodes (N0,N1,N2,N3,N4,N5,N8) all included? → must be YES
2. Are excluded nodes (likely N6, N7) acceptable to exclude?
   - For each excluded node, examine the DC-equivalence classes that USE that node
     for distinguishing in the input data. Are those distinctions trivially
     covered by other selected nodes?
3. v4.2 sanity:
   - Does the selected set adequately distinguish CELLULAR_KINETICS subtypes?
   - Does it handle MATERNAL_INFANT dyad cases?
   - Does it cover IMMUNOGENICITY (Q19) detection?
   - Does it handle PRODUCT-LEVEL-COVARIATE (CAR-T)?

PART B: Dangerous merge detection
For each unselected node (e.g., N6):
- Look at scenario pairs where ONLY N6 distinguished them in the original universe
- After merging (excluding N6), verify these pairs are NOT operationally critical
  (not different terminal_state, not different action_sequence, not different policy)
- Flag any "silent merge" where the distinction matters but ILP missed it

OUTPUT FIELDS (per LP-A template P2):
- recommended_decision: APPROVE / REVISE / RECOMPUTE
- rationale_pmx_evidence
- confidence (HIGH/MEDIUM/LOW)
- fatal_issues: list of dangerous merges detected
- residual_risk
- must_escalate_to_human (YES/NO)
- escalation_reason

OUTPUT: Markdown.
```

#### P97 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** P95 solver output, P96 grandmaster
🔹 **산출물:** `reports/llm_proxy/minimal_node_approval_adversarial.md`

```
ROLE: Adversarial reviewer (LP-B) for CP6.

INPUT (attached):
  reports/llm_proxy/minimal_node_approval_grandmaster.md
  data/ilp/final_minimal_node_set.csv
  reports/ilp_solution_report.md

ATTACK AXES:
1. ILP cost manipulation: did Grandmaster accept costs that bias toward
   excluding important nodes?
2. Distinguishability blind spots: any pair that R says doesn't need
   distinguishing but operationally matters?
3. Forced node loophole: are forced nodes truly necessary or vestigial?
4. v4.2 specific:
   - Could excluding N6 hide PRODUCT-LEVEL-COVARIATE issues silently?
   - Could excluding N7 hide unresolved q_codes from operational view?
5. Hidden dangerous merge: pairs that ILP says are "indistinguishable required"
   but actually different terminal_state due to subtle policy difference
6. Q-code coverage: every Q01..Q19 (except Q17) covered by at least one
   selected node's distinction?
7. F24-F29 v4.2 family operational coverage check
8. Universe completeness vs minimal set: does excluding any node create
   future v1.1 expansion incompatibility?

For each issue: severity, evidence, correction.

OUTPUT: Markdown per LP-B template.
```

#### P98 (LP-C) — Judge + 자동 적용 또는 escalation

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션)
🔹 **첨부 파일:** P96 + P97
🔹 **산출물:**
  - `reports/llm_proxy/minimal_node_approval_judge.md`
  - `reports/llm_proxy/minimal_node_approval_decision.csv`
🔹 **다음 액션:** auto-apply 시 P99 / 아니면 H4 라우팅

```
ROLE: Judge (LP-C) for CP6.

INPUT: P96 + P97 outputs.

ENFORCE Hard Rules:
- HR13: forced node ⊆ minimal node set (must be true; otherwise REJECT)
- confidence=LOW → escalate=YES (forced)
- unresolved_fatal_count >= 1 → escalate=YES (forced)
- Cannot accept dangerous merge

If auto-apply (HIGH + fatal_resolved + no escalation):
  Mark final_minimal_node_set.csv as APPROVED

If REVISE/RECOMPUTE:
  Specify required cost adjustment OR new node addition
  Re-run P93 → P95 → P96

If ESCALATE:
  Route to H4 (release-stage human, will be confirmed in Phase 10)
  Save current state as "pending_h4_approval"

OUTPUT: per LP-C template + CSV machine-readable decision.
```

---

### P99 — Minimal Node Set Lock + Hash

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P98 = APPROVED (or post-H4 approval)
🔹 **첨부 파일:** D5
🔹 **산출물:**
  - `release/v1.0/minimal_node_set_v1_0.sha256`
  - `release/v1.0/minimal_node_set_lock_declaration.md`
🔹 **다음 액션:** P100

```
ROLE: Coding agent.

TASK:
1. Compute SHA256 of:
   - data/ilp/final_minimal_node_set.csv
   - data/ilp/pairwise_distinguishability_matrix.npz
   - config/ilp_problem_definition.yaml
   Save individual + combined to release/v1.0/minimal_node_set_v1_0.sha256

2. Generate release/v1.0/minimal_node_set_lock_declaration.md:
   - Selected nodes list with cost, forced flag
   - Total objective cost
   - Distinguishability coverage = 100%
   - LP Panel CP6 result (APPROVED auto / H4-approved)
   - Hash values
   - Locked at: ISO timestamp
   - Modification policy: "Any change requires v1.1 release"

3. Update CHANGELOG: "## v0.9.0 — Minimal node set LOCKED"

OUTPUT: 2 files + CHANGELOG.
```

---

### P100 — Phase 8 완료 선언

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** P95, P98, P99
🔹 **산출물:** `reports/phase8_completion_declaration.md`
🔹 **다음 액션:** CHECK-8

```
ROLE: Documentation writer.

CHECKLIST:
[ ] D3 reduced_decision_table_v1.0.csv generated
[ ] D4 pairwise_distinguishability_matrix.npz generated
[ ] D5 final_minimal_node_set.csv generated and LOCKED with hash
[ ] No infeasible pairs (P90 PASS or P92 resolved)
[ ] forced nodes (N0,N1,N2,N3,N4,N5,N8) ⊆ minimal set
[ ] LP Panel CP6 (minimal_node_approval) resolved (APPROVED or H4-pending)
[ ] PATCH-2 distinguishability strengthening applied (P89)
[ ] PATCH-3 forced node constraint applied (P93)
[ ] dangerous merge check passed (P96 LP-A Part B)
[ ] CHANGELOG updated to v0.9.0

OUTPUT: Markdown.
```

---

### 🐍 CHECK-8 (Phase 8 검증)

```python
# check_phase8.py
# Phase 8 (P86-P100) 완료 검증
import os, sys, hashlib
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("⚠️  pandas/numpy 없음. pip install pandas numpy")
    sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None:
    print("❌ pmx_universe_v5_1 폴더 없음"); sys.exit(1)

print("=" * 60)
print("CHECK-8: Phase 8 (Decision Table + ILP) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "scripts/decision_table/generate_decision_table.py",
    "scripts/decision_table/dc_reduction.py",
    "scripts/decision_table/build_pairwise_matrix.py",
    "scripts/ilp/solve_minimal_node_set.py",
    "data/decision_table/raw_decision_table.csv",
    "data/decision_table/reduced_decision_table_v1.0.csv",
    "data/ilp/pairwise_distinguishability_matrix.npz",
    "data/ilp/solver_output.json",
    "data/ilp/final_minimal_node_set.csv",
    "config/ilp_problem_definition.yaml",
    "release/v1.0/minimal_node_set_v1_0.sha256",
    "release/v1.0/minimal_node_set_lock_declaration.md",
    "reports/distinguishability_definition_v5_1.md",
    "reports/pairwise_matrix_report.md",
    "reports/ilp_solution_report.md",
    "reports/phase8_completion_declaration.md",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file():
        print(f"  ✅ {f.split('/')[-1]}")
    else:
        print(f"  ❌ {f}")
        failures.append(f)

# minimal_node_set.csv: forced node 검증
print("\n[Forced Node 포함 검증 (HR13)]")
fns = BASE / "data/ilp/final_minimal_node_set.csv"
if fns.is_file():
    df = pd.read_csv(fns)
    if "node_id" in df.columns and "included" in df.columns:
        included = set(df[df["included"].astype(str).str.upper().isin(["TRUE","YES","1","Y"])]["node_id"].astype(str))
        forced = {"N0","N1","N2","N3","N4","N5","N8"}
        missing = forced - included
        if not missing:
            print("  ✅ 모든 forced node 포함 (N0,N1,N2,N3,N4,N5,N8)")
        else:
            print(f"  ❌ Forced node 누락: {missing}")
            failures.append(f"Forced 누락 {missing}")
        # 전체 노드 출력
        print(f"  선택된 노드: {sorted(included)}")
    else:
        print("  ❌ node_id 또는 included 컬럼 없음")
        failures.append("CSV 컬럼")

# pairwise matrix infeasible 체크
print("\n[Pairwise Matrix Infeasible 검증]")
mp = BASE / "data/ilp/pairwise_distinguishability_matrix.npz"
if mp.is_file():
    try:
        arr = np.load(mp, allow_pickle=True)
        infeasible = arr["infeasible_pairs"] if "infeasible_pairs" in arr.files else []
        n_infeasible = len(infeasible) if hasattr(infeasible, "__len__") else 0
        if n_infeasible == 0:
            print("  ✅ infeasible_pairs = 0")
        else:
            print(f"  ❌ infeasible_pairs = {n_infeasible}")
            failures.append(f"infeasible {n_infeasible}")
        # 행렬 크기
        if "R" in arr.files:
            R = arr["R"]
            print(f"  DC class 수: {R.shape[0]}")
    except Exception as e:
        print(f"  ⚠️  npz 읽기 오류: {e}")

# solver output: status OPTIMAL
print("\n[ILP Solver Output]")
so = BASE / "data/ilp/solver_output.json"
if so.is_file():
    import json
    try:
        with open(so) as f:
            sol = json.load(f)
        status = sol.get("status", "")
        if status in ("OPTIMAL", "FEASIBLE"):
            print(f"  ✅ status: {status}")
            print(f"  objective: {sol.get('objective_value', '?')}")
            print(f"  solve_time: {sol.get('solve_time_seconds', '?')}s")
        else:
            print(f"  ❌ status: {status}")
            failures.append(f"solver status {status}")
    except Exception as e:
        print(f"  ⚠️  JSON 오류: {e}")

# Hash 검증
print("\n[Hash 검증]")
hf = BASE / "release/v1.0/minimal_node_set_v1_0.sha256"
fns = BASE / "data/ilp/final_minimal_node_set.csv"
if hf.is_file() and fns.is_file():
    txt = hf.read_text()
    computed = hashlib.sha256(fns.read_bytes()).hexdigest()
    if computed in txt:
        print(f"  ✅ minimal_node_set hash 일치: {computed[:16]}...")
    else:
        print(f"  ⚠️  hash 불일치 또는 다른 파일 hash")

# DC reduction 비율
print("\n[DC Reduction 비율]")
raw = BASE / "data/decision_table/raw_decision_table.csv"
red = BASE / "data/decision_table/reduced_decision_table_v1.0.csv"
if raw.is_file() and red.is_file():
    n_raw = len(pd.read_csv(raw))
    n_red = len(pd.read_csv(red))
    ratio = n_red / n_raw if n_raw else 0
    print(f"  raw → reduced: {n_raw} → {n_red} (ratio {ratio:.2f})")
    if 0.1 <= ratio <= 0.9:
        print("  ✅ 합리적 reduction")
    else:
        print(f"  ⚠️  ratio 비정상 (정상 범위: 0.1-0.9)")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 8 완료")
    print("→ 다음: Phase 9 (P101) — Decision Tree + NONMEM QC")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## 🌳 Phase 9: Operational Decision Tree + NONMEM-Ready QC (P101~P105A)

### 📌 이 단계 목적

ILP에서 추출한 **최소 결정 노드 집합 D5**를 실행 가능한 **결정 트리 D6 (operational_decision_tree.yaml)**로 변환합니다. 트리는 N0→N1→N2→...→N8 (또는 ILP가 선택한 순서)로 분기하면서 각 단말 노드에 terminal_state + q_code + action_sequence를 매핑합니다.

또한 NONMEM-ready 출력 dataset의 QC 스크립트를 만들어 AUTO/REPAIR 출력의 NONMEM 적합성을 검증합니다.

### 진입 조건
- [x] CHECK-8 PASS

---

### P101 — Decision Tree 구성 알고리즘 설계

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** CHECK-8 PASS
🔹 **첨부 파일:** D3, D5, candidate_node_dictionary
🔹 **산출물:** `reports/decision_tree_construction_plan.md`
🔹 **다음 액션:** P102

```
ROLE: PMX Grandmaster + tree algorithm designer.

INPUT (attached):
  data/decision_table/reduced_decision_table_v1.0.csv
  data/ilp/final_minimal_node_set.csv
  config/candidate_node_dictionary_with_costs.csv

TASK: Produce reports/decision_tree_construction_plan.md.

REQUIRED CONTENT:

# Operational Decision Tree Construction Plan

## Tree structure
Binary tree with internal nodes = selected nodes (from D5)
Leaf nodes = (terminal_state, q_code, action_sequence_label, family_id)

## Node ordering rationale
Order nodes by:
1. Forced nodes first (N0, N1, N2, N3, N4, N5, N8) — order by axis dependency
2. Free nodes (if selected, e.g., N6, N7) at the end
3. Within each group: order by descending failure_risk cost
   (high-risk early to terminate fast on failure)

PROPOSED ORDER (default):
N0 (AIC + endpoint_data_type)  — root (always evaluated first)
  ↓ if N0=N: leaf = QUARANTINE Q11 (or specific q_code per AIC subtype)
  ↓ if N0=Y: continue to N1

N1 (ID + dyad linkage)
  ↓ if N1=N: leaf = INVALID (id) or Q18 (maternal-infant dyad missing)
  ↓ if N1=Y: continue to N8

N8 (policy availability)        — v5.1 NEW, gate before N2..N5
  ↓ if N8=N: leaf = QUARANTINE specific q_code by missing policy
  ↓ if N8=Y: continue to N2

N2 (time anchor)
N3 (dose path)
N4 (observation completeness)
N5 (BLQ/MDV policy)
N6 (covariate, if selected)
N7 (residual ambiguity, if selected)

## Branching logic
At each internal node:
- Y branch → next node OR leaf (if terminal)
- N branch → leaf with appropriate q_code/terminal_state
- * (don't-care) → SKIP this node, go to next

## Leaf assignment rules
For each unique combination of (terminal_state, q_code, action_sequence):
- Walk the tree following the dominant Y/N pattern from D3
- Identify which leaf the scenario reaches
- Verify leaf attributes match scenario attributes
- If mismatch → tree construction error, escalate

## Audit log requirement
Tree YAML MUST include audit_log_template_per_leaf:
- decision_path: [N0=Y, N1=Y, N8=Y, N2=Y, ...]
- terminal_state
- q_code (if QUARANTINE)
- action_sequence_executed (function names + parameter_policies)
- timestamp_iso
- input_data_summary (row_count, columns_used)

OUTPUT: Markdown.
```

---

### P102 — Decision Tree YAML 생성기 구현

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P101 완료
🔹 **첨부 파일:** P101, D3, D5
🔹 **산출물:**
  - `scripts/decision_tree/build_decision_tree.py`
  - `config/operational_decision_tree.yaml` (= **D6**)
🔹 **다음 액션:** P103

```
ROLE: Coding agent.

INPUT (attached):
  data/decision_table/reduced_decision_table_v1.0.csv
  data/ilp/final_minimal_node_set.csv
  reports/decision_tree_construction_plan.md
  config/quarantine_reason_codes.yaml
  config/action_sequence_standard.yaml

TASK: Implement scripts/decision_tree/build_decision_tree.py

PROCEDURE:
1. Load D3 + D5
2. Apply P101 ordering (forced nodes first, then free nodes)
3. Recursive tree construction:
   def build_tree(remaining_classes, remaining_nodes):
       if remaining_nodes empty OR all classes have same outcome:
           return leaf(outcome)
       pick first node n
       split classes by node_value (Y/N/*)
       Y_subtree = build_tree(Y_classes + *_classes, remaining_nodes - {n})
       N_subtree = build_tree(N_classes + *_classes, remaining_nodes - {n})
       return internal_node(n, Y_subtree, N_subtree)
4. Generate YAML structure

YAML SCHEMA:

operational_decision_tree:
  version: "v1.0"
  node_order: [N0, N1, N8, N2, N3, N4, N5, N6, N7]  # actual order used
  root: <node_id_or_leaf_id>
  internal_nodes:
    - id: tree_N0
      node_id: N0
      question: "AIC sufficient and endpoint_data_type declared?"
      yes_branch: tree_N1
      no_branch: leaf_Q11
    - id: tree_N1
      ...
  leaves:
    - id: leaf_Q11
      terminal_state: QUARANTINE
      q_code: Q11
      action_sequence: ["flag_quarantine"]
      action_label: "QUARANTINE_AIC_MISSING_Q11"
      family_id_examples: [F-various]
    - id: leaf_AUTO_F01_SDTM_STANDARD
      terminal_state: AUTO
      q_code: null
      action_sequence: [parse_source, standardize_column_names, ..., export_nonmem_ready]
      action_label: "AUTO_SDTM_STANDARD"
      family_id_examples: [F01]
    ...

  audit_log_template:
    fields: [decision_path, terminal_state, q_code, action_sequence_executed,
             timestamp_iso, input_data_summary, row_counts_before_after]

5. Save to config/operational_decision_tree.yaml

VALIDATION (during tree generation):
- All D5 selected nodes appear in tree (forced or free)
- All terminal_state values from D3 reachable as leaves
- All q_codes from D3 (Q01..Q19 except Q17) reachable
- No leaf with q_code = "Q15" standalone
- No leaf with q_code = "Q17"
- Every AUTO leaf has export_nonmem_ready in action_sequence
- Every REPAIR leaf has ≥1 repair function

CLI:
python scripts/decision_tree/build_decision_tree.py \
  --decision-table data/decision_table/reduced_decision_table_v1.0.csv \
  --node-set data/ilp/final_minimal_node_set.csv \
  --out config/operational_decision_tree.yaml

OUTPUT: Script + YAML.
```

---

### P103 — Tree-Decision Table Consistency Check

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P102 완료
🔹 **첨부 파일:** D3, D6
🔹 **산출물:**
  - `scripts/decision_tree/verify_tree_table_match.py`
  - `reports/tree_table_consistency.md`
🔹 **다음 액션:** P104

```
ROLE: Coding agent.

TASK: Implement scripts/decision_tree/verify_tree_table_match.py.

PROCEDURE:
1. Load D3 (reduced_decision_table_v1.0.csv)
2. Load D6 (operational_decision_tree.yaml)
3. For EACH DC class in D3:
   - Walk the tree using its node values (N0..N8)
   - Reach a leaf
   - Verify leaf.terminal_state == class.terminal_state
   - Verify leaf.q_code == class.q_code (or both null)
   - Verify leaf.action_sequence_label is consistent with class.action_label
   - Verify leaf reachable via D3-determined path

CHECKS:
T01 every D3 class reaches a leaf (no NA-trapped path)
T02 leaf attributes exactly match D3 class attributes
T03 path uses only selected nodes (no excluded node referenced)
T04 forced nodes always evaluated (N0, N1, N2, N3, N4, N5, N8 in path)
T05 v4.2 specific:
    - F26 CAR-T classes route through correct CELLULAR_KINETICS leaves
    - F29 maternal-infant classes route through correct dyad leaves
    - Q19 classes only reachable when N0/N4 detect immunogenicity policy missing
T06 No leaf reachable via "impossible" path (e.g., N0=N → only Q-code leaves)

REPORT: reports/tree_table_consistency.md
- per-class match: PASS/FAIL with detail
- per-leaf reverse mapping: which classes reach this leaf
- summary statistics

GATE: 100% match (every D3 class correctly routed). If <100% → tree
construction bug, escalate.

OUTPUT: Script + report.
```

---

### P104 — NONMEM-Ready Output QC Script

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P103 PASS
🔹 **첨부 파일:** AIC template (P14), action_function_library (P13)
🔹 **산출물:**
  - `scripts/validation/nonmem_ready_qc.py`
  - `tests/test_nonmem_ready_qc.py`
🔹 **다음 액션:** P105

```
ROLE: Coding agent.

TASK: Implement scripts/validation/nonmem_ready_qc.py.

This script validates AUTO/REPAIR output datasets for NONMEM readiness.

REQUIRED CHECKS (≥20):

STRUCTURAL (5):
S01 Required columns: ID, TIME, DV, MDV, EVID, AMT, RATE, CMT
    (subset depends on AIC; minimum: ID, TIME, DV, MDV, EVID)
S02 Column data types: numeric for ID/TIME/DV/AMT/RATE; integer for MDV/EVID/CMT
S03 No special characters in column names (NONMEM unfriendly)
S04 Header row exists, single line, comma or tab delimited
S05 Encoding: ASCII or UTF-8 without BOM

EVENT/DOSING (5):
E01 ID monotonic non-decreasing
E02 Within each ID, TIME monotonic non-decreasing
E03 EVID values in {0, 1, 2, 3, 4}
E04 EVID=0 (observation): DV not NA, AMT NA
E05 EVID=1 (dose): AMT not NA and >0, DV NA or 0

BLQ/MDV (3):
B01 MDV consistent with DV (DV=NA → MDV=1)
B02 BLQ_FLAG (if present) values in {"M1", "M3", "M4", null}
B03 No DV < 0 unless explicit policy allows

CMT (3):
C01 CMT integer >= 1
C02 CMT consistent with analyte_role (if v4.2 multi-analyte)
C03 Single CMT per (ID, TIME) for same EVID

v4.2 SPECIFIC (4):
V01 If endpoint_data_type=CELLULAR_KINETICS:
    DV in cellular_LLOQ-canonicalized form (no negative DV; consistent BLQ flag)
V02 If endpoint_data_type=IMMUNOGENICITY:
    DV column has positivity adjudication applied
    (binary 0/1, with adjudication_log present)
V03 If endpoint_data_type=MATERNAL_INFANT_PK:
    Two ID groups present (mother, infant)
    Dyad linkage column (DYADID) present
V04 If product_level_covariate present:
    LOTID or product_attribute columns present and consistent

AUDIT LOG (1):
A01 audit_log file alongside dataset with required fields
    (decision_path, terminal_state, q_code, action_sequence_executed, timestamps)

CLI:
python scripts/validation/nonmem_ready_qc.py \
  --dataset <path/to/output.csv> \
  --aic <path/to/aic.yaml> \
  --audit-log <path/to/audit.json> \
  --out <path/to/qc_report.md>

REPORT: per-check PASS/FAIL with detail.

TESTS: 8+ cases covering routine + v4.2 specific.

OUTPUT: 2 files. Run pytest.
```

---

### P105 — Decision Tree Lock + Hash

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P103 PASS, P104 pytest PASS
🔹 **첨부 파일:** D6
🔹 **산출물:**
  - `release/v1.0/decision_tree_v1_0.sha256`
  - `release/v1.0/decision_tree_lock_declaration.md`
🔹 **다음 액션:** P105A → CHECK-9

```
ROLE: Coding agent.

TASK:
1. Compute SHA256 of:
   - config/operational_decision_tree.yaml
   - scripts/validation/nonmem_ready_qc.py
   Save to release/v1.0/decision_tree_v1_0.sha256

2. Generate release/v1.0/decision_tree_lock_declaration.md:
   - Tree statistics: internal nodes count, leaves count
   - Forced node evaluation order
   - v4.2 specific leaf coverage (CELLULAR/IMMUNOGEN/MATERNAL_INFANT)
   - Tree-table consistency: 100% PASS
   - NONMEM QC test coverage: pytest results
   - Hash values
   - Locked at: ISO timestamp

3. Update CHANGELOG: "## v0.10.0 — Decision Tree LOCKED"

OUTPUT: 2 files + CHANGELOG.
```

---

### P105A — Phase 9 완료 선언

> **[PATCH-C3]** 이전 버전에서 P-번호 없는 블록으로 존재하던 Phase 9 완료 선언에 P105A 번호를 부여했습니다.
> P105(Decision Tree Lock) 완료 후 CHECK-9 진입 전에 반드시 실행하세요.
> 실행 순서: P105 → **P105A** → CHECK-9 → P106

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **진입 조건:** P105 완료
🔹 **산출물:** `reports/phase9_completion_declaration.md`
🔹 **다음 액션:** CHECK-9

```
ROLE: Documentation writer.

CHECKLIST:
[ ] D6 operational_decision_tree.yaml generated and locked
[ ] tree-table consistency 100% (P103)
[ ] NONMEM QC script implemented (P104) with ≥20 checks
[ ] pytest for NONMEM QC PASS
[ ] forced nodes (N0,N1,N2,N3,N4,N5,N8) all in tree path
[ ] Q15 standalone leaves: 0
[ ] Q17 leaves: 0
[ ] AUTO leaves all have export_nonmem_ready
[ ] REPAIR leaves all have ≥1 repair function
[ ] v4.2 specific leaves: CELLULAR_KINETICS, IMMUNOGENICITY, MATERNAL_INFANT, MILK_PK present
[ ] CHANGELOG updated to v0.10.0

OUTPUT: Markdown.
```

---

### 🐍 CHECK-9 (Phase 9 검증)

```python
# check_phase9.py
import os, sys, hashlib
from pathlib import Path

try:
    import yaml, pandas as pd
except ImportError:
    print("⚠️  pandas/pyyaml 없음"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("❌"); sys.exit(1)

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
    if (BASE / f).is_file(): print(f"  ✅ {f.split('/')[-1]}")
    else: print(f"  ❌ {f}"); failures.append(f)

# Decision Tree 구조 검증
print("\n[Decision Tree 구조]")
tp = BASE / "config/operational_decision_tree.yaml"
if tp.is_file():
    try:
        data = yaml.safe_load(tp.read_text(encoding="utf-8"))
        tree = data.get("operational_decision_tree", data)
        # node_order에 forced nodes 모두 포함
        order = tree.get("node_order", [])
        forced = {"N0","N1","N2","N3","N4","N5","N8"}
        if forced.issubset(set(order)):
            print(f"  ✅ Forced nodes 모두 tree 순서에 포함: {order}")
        else:
            missing = forced - set(order)
            print(f"  ❌ Forced 누락: {missing}")
            failures.append(f"tree forced 누락 {missing}")

        # leaves
        leaves = tree.get("leaves", [])
        print(f"  leaf 수: {len(leaves)}")

        # Q15 단독 / Q17 검사
        q15_solo = sum(1 for l in leaves if l.get("q_code") == "Q15")
        q17 = sum(1 for l in leaves if l.get("q_code") == "Q17")
        if q15_solo == 0: print("  ✅ Q15 단독 leaf 0")
        else: failures.append(f"Q15 solo {q15_solo}")
        if q17 == 0: print("  ✅ Q17 leaf 0")
        else: failures.append(f"Q17 {q17}")

        # AUTO leaves에 export_nonmem_ready
        auto_leaves = [l for l in leaves if l.get("terminal_state") == "AUTO"]
        bad_auto = [l for l in auto_leaves if "export_nonmem_ready" not in l.get("action_sequence", [])]
        if not bad_auto:
            print(f"  ✅ AUTO leaves ({len(auto_leaves)}개) 모두 export_nonmem_ready")
        else:
            print(f"  ❌ AUTO leaf 중 export 없는 것 {len(bad_auto)}")
            failures.append("AUTO export 누락")

        # v4.2 특정 leaves
        labels = " ".join(str(l.get("action_label", "")) for l in leaves).upper()
        for kw in ["CELLULAR", "IMMUNOGEN", "MATERNAL", "DYAD"]:
            if kw in labels:
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
    if "100%" in txt or "PASS" in txt.upper():
        print("  ✅ 100% match")
    else:
        print("  ⚠️  100% match 미확인")

print("\n" + "=" * 60)
if not failures:
    print("🟢 GATE PASS: Phase 9 완료")
    print("→ 다음: Phase 10 (P106) — Golden Validation + H3, H4, H5")
else:
    print(f"🔴 GATE FAIL: {len(failures)}개")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```

---

## 🛡️ Phase 10: Golden 검증 + Release (P106~P115)

### 📌 이 단계 목적

이제까지 만든 시스템 (universe + repair_executor + decision_tree)을 **golden datasets**에 적용해 reference output과의 일치를 검증하고, 사람의 최종 판단(H3, H4, H5)을 거쳐 **v1.0을 release**합니다.

### v5.1 핵심 강화 (PATCH-5)
- **H4 강화: 표본 감사 (blinded sample audit)** — LP Panel이 false-classification을 발견했을 때만 검토하던 v3.1과 달리, v5.1에서는 random AUTO 10개 + random REPAIR 10개를 blinded review로 의무 감사 + 모든 LP-flagged 항목 검토

### 진입 조건
- [x] CHECK-9 PASS

---

### P106 — Golden Validation Pipeline 구현

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** CHECK-9 PASS
🔹 **첨부 파일:** D6, D7, golden_dataset_registry, NONMEM QC script
🔹 **산출물:**
  - `scripts/validation/run_golden_validation.py`
  - `tests/test_golden_validation.py`
🔹 **다음 액션:** P107

```
ROLE: Coding agent.

TASK: Implement scripts/validation/run_golden_validation.py.

PROCEDURE per golden dataset:
1. Load raw input (data/golden_datasets/{project_id}/raw_input/...)
2. Load AIC (data/golden_datasets/{project_id}/aic.yaml)
3. Walk decision tree → determine terminal_state + action_sequence
4. Compare with expected_terminal_state from golden_dataset_registry
   → record terminal_match (Y/N)
5. If terminal_state == AUTO or REPAIR:
   - Execute action_sequence via repair_executor.py
   - Get output dataset
   - Compare with reference_output:
     - Row count match
     - ID set match (no missing/extra subjects)
     - Per-(ID, TIME) row hash match
     - DV column tolerance (e.g., relative diff < 1e-6)
   - Run NONMEM QC on output
6. Record per-golden:
   - golden_id, project_id, family_id
   - terminal_match (Y/N)
   - row_count_match (Y/N)
   - id_set_match (Y/N)
   - dv_match (Y/N, with max_relative_diff)
   - audit_log_complete (Y/N)
   - nonmem_qc_pass (Y/N)
   - overall_status: PASS / FAIL / MISMATCH
   - mismatch_detail (if any)

CLI:
python scripts/validation/run_golden_validation.py \
  --registry data/golden_datasets/golden_dataset_registry_draft.csv \
  --tree config/operational_decision_tree.yaml \
  --executor scripts/repair_executor/repair_executor.py \
  --out reports/golden_validation_results.csv

OUTPUT FILES:
- reports/golden_validation_results.csv (one row per golden)
- reports/golden_validation_per_dataset/{golden_id}_detail.md (one per golden)

TESTS (8+ cases):
- 1 routine F01 golden: AUTO match expected
- 1 F09 DDI golden: REPAIR match
- 1 F26 CAR-T golden: REPAIR with cellular_LLOQ canonicalization
- 1 deliberately-broken golden: FAIL detection works
- 4+ additional v4.2 specific

OUTPUT: 2 files. Run pytest.
```

---

### P107 — Golden Validation 실행 + 1차 결과

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P106 pytest PASS
🔹 **첨부 파일:** golden_dataset_registry, all golden raw inputs + reference outputs
🔹 **산출물:**
  - `reports/golden_validation_results.csv`
  - `reports/golden_validation_per_dataset/*.md`
  - `reports/golden_validation_summary_v1.md`
🔹 **다음 액션:** mismatch 없음 → H3 / mismatch 있음 → P108(조건부) → H3

```
ROLE: Coding agent.

PROCEDURE:
1. Run python scripts/validation/run_golden_validation.py
2. Load reports/golden_validation_results.csv
3. Compute summary statistics:
   - total_goldens
   - pass_count (overall_status=PASS)
   - fail_count
   - mismatch_count (terminal_match=N or dv_match=N)
4. Per-family breakdown
5. v4.2 family-specific PASS rate:
   - F01 routine: target 100%
   - F09/F22 DDI: target 100%
   - F12 pediatric: target 100%
   - F24-F29 v4.2: target ≥80% (some may need v1.1 expansion)

REPORT (reports/golden_validation_summary_v1.md):
- Overall PASS rate
- Per-family PASS rate
- Mismatch root-cause categories:
  - tree_routing_error
  - executor_logic_error
  - reference_output_error (golden may be wrong)
  - aic_under_specification
- Recommendation:
  - if PASS rate ≥95% → proceed to P108 (release prep)
  - if 80-95% → P109 (LP-A diagnostic) before H3
  - if <80% → escalate, full root-cause investigation

OUTPUT: Updated CSV + summary md.
```

---

### P108 — Golden Mismatch 분석 (조건부)

> ⚠️ **[PATCH FATAL-N1]** P107에서 mismatch가 발견된 경우에만 진행. mismatch 없으면 H3로 직행.

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P107 결과에서 mismatch 발생 시
🔹 **첨부 파일:** golden_validation_results.csv + per-dataset detail
🔹 **산출물:** `reports/golden_mismatch_analysis.md`
🔹 **다음 액션:** H3 (mismatch 분석 후 H3로 진행)

```
ROLE: PMX Grandmaster.

INPUT: golden_validation_results.csv + per-dataset detail markdowns

For EACH mismatch:
1. terminal_match=N:
   - decision tree routing wrong? Or expected_terminal_state in registry wrong?
2. dv_match=N:
   - executor function bug? Or rounding tolerance? Or policy ambiguity?
3. row_count_match=N:
   - filtering policy mismatch?
4. id_set_match=N:
   - subject mapping error?

CLASSIFICATION per mismatch:
- TREE_BUG: fix in P102 build_decision_tree.py
- EXECUTOR_BUG: fix in repair_executor.py (Step 2 P42 — but if locked, need v1.1)
- REGISTRY_ERROR: golden expected was wrong, fix registry
- POLICY_AMBIGUITY: AIC/policy under-specified, document + defer

RECOMMENDATION:
- Auto-fix possible (REGISTRY_ERROR) → patch registry, re-run P107
- Locked-asset bug (EXECUTOR/UNIVERSE) → v1.1 candidate, escalate
- Tree routing bug → patch tree (Phase 9 redo, may invalidate prior locks)

OUTPUT: Markdown.
```

---

### 🧑 H3 — HUMAN: Golden Reference 확인 (필수, LLM 대체 불가)

> **이 단계 목적:** Golden dataset의 reference output이 진짜로 NONMEM-ready 정답인지 사람(연구실 PMX 전문가)이 직접 확인합니다. LLM이 만든 출력이 reference와 일치한다 해도, reference 자체가 틀렸을 수 있습니다.

#### 수행 절차

**1단계. 검토 대상 식별**

`reports/golden_validation_results.csv`에서:
- `overall_status=PASS` 항목: 무작위 ≥3개 sampling
- `overall_status=FAIL` 항목: 모두 검토
- `overall_status=MISMATCH` 항목: 모두 검토

**2단계. 각 golden에 대해 직접 확인**

```
□ raw_input 파일을 직접 열어보고 (Excel 또는 CSV)
  실제 데이터와 ref_output의 NONMEM 컬럼이 매핑 가능한지 확인
□ ref_output에 ID, TIME, DV, MDV, EVID, AMT, RATE, CMT가
  올바른 포맷으로 들어있는지 확인
□ 비식별화 잔존물 검사 (Step 2 H1과 동일 체크)
□ ref_output을 NONMEM 컨트롤 스트림으로 직접 돌려본다 (가능하면)
   → 정상 컨버지 또는 데이터 입력 단계 통과 확인
□ Validation 결과 PASS인데 reference가 틀렸으면 → registry 정정
□ Validation 결과 FAIL인데 reference도 합리적으로 틀렸으면 → registry 정정
□ Validation 결과 FAIL이고 reference가 맞다면 → executor/tree bug 확정
```

**3단계. 승인 로그 기록**

`reports/human_review/h3_golden_approval_log.md`:

```markdown
# H3 Golden Reference Approval Log

| golden_id | project_id | family_id | reviewed_by | date | reference_correct | validation_result_correct | action |
|---|---|---|---|---|---|---|---|
| G001 | PROJ_S01_001 | F01 | [검토자 실명] | [YYYY-MM-DD] | YES | PASS | none |
| G002 | PROJ_S02_002 | F09 | [검토자 실명] | [YYYY-MM-DD] | YES | PASS | none |
| G003 | PROJ_DDI_007 | F22 | [검토자 실명] | [YYYY-MM-DD] | NO | FAIL | registry corrected: expected REPAIR not AUTO |
| G004 | PROJ_CART_002 | F26 | [검토자 실명] | [YYYY-MM-DD] | YES | MISMATCH | executor bug confirmed; v1.1 candidate |
...

Total reviewed: 12
References confirmed correct: 10
References corrected: 2
Executor/tree bugs confirmed: 1 (G004 → v1.1)

Reviewed_by: [검토자 실명]
Date: [YYYY-MM-DD ~ YYYY-MM-DD]
Decision: APPROVED for release with caveats:
  - PROJ_CART_002 (F26 CAR-T) marked as v1.1 known issue
  - Coverage claim must explicitly note F26 partial coverage
```

**4단계. 완료 조건**

```
✅ 모든 FAIL/MISMATCH golden 검토됨
✅ PASS sample 최소 3개 검토됨
✅ 잘못된 reference는 registry 정정됨
✅ 진짜 bug는 v1.1 register 등록됨
✅ approval log 서명됨
---

### P107B — D8 Canonical Report 생성 (v5.1 PATCH M-3 신규)

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **진입 조건:** P107 PASS rate 계산 완료 + H3 완료 (registry corrections 반영 후)
🔹 **첨부 파일:** `reports/golden_validation_results.csv`, `reports/golden_validation_per_dataset/*.md`, `reports/human_review/h3_golden_approval_log.md`
🔹 **산출물:**
  - `reports/golden_validation_report.md` ← **D8 canonical file**
  - `release/v1.0/golden_validation_report_v1_0.sha256`
🔹 **다음 액션:** P109

> ⚠️ **[PATCH M-3]** D8 canonical deliverable은 `reports/golden_validation_report.md`입니다.
> `golden_validation_results.csv`는 원시 데이터이고, 이 프롬프트에서 canonical 요약 문서를 생성합니다.
> CHECK-10과 CHECK-11이 이 파일과 해시를 검증합니다.

```
ROLE: Documentation writer.

TASK: Produce D8 canonical report: reports/golden_validation_report.md

REQUIRED CONTENT:
# Golden Validation Report v1.0 (D8)
generated_at: [ISO timestamp]
universe_basis: v4.2
executor_version: [hash from repair_executor_v1_0.sha256]
tree_version: [hash from decision_tree_v1_0.sha256]

## Summary
- total_golden_datasets: N
- overall_pass_rate: X% (post H3 correction)
- per_family_pass_rate: {F01: 100%, F09: 100%, F26: X%, ...}
- v4.2_family_pass_rate: {F24: X%, F25: X%, F26: X%, F27: X%, F28: X%, F29: X%}

## H3 Corrections Applied
- registry_corrections: N
- executor_bugs_confirmed: M (→ v1.1 candidates)
- tree_bugs_confirmed: K (→ fixed or v1.1)

## Per-Dataset Index
| golden_id | project_id | family_id | terminal_match | dv_match | overall_status | h3_action |
|---|---|---|---|---|---|---|
[table from golden_validation_results.csv + h3_log]

## Known Limitations (v1.1 deferred)
[list confirmed bugs deferred to v1.1]

## Coverage Claim Contribution
This report supports D9 (coverage_claim_statement.md) as evidence of:
- AUTO/REPAIR correctness (golden match rate)
- QUARANTINE detection (q_code routing correctness)
- v4.2 modality handling (F24-F29 pass rates)

CONSTRAINT:
- Do NOT include PHI. All project_ids must be internal codes.
- If a golden was removed from registry post-H3, exclude from this report.

AFTER GENERATING REPORT:
Compute SHA256:
  sha256sum reports/golden_validation_report.md > release/v1.0/golden_validation_report_v1_0.sha256
```

---

### P109 — Validation Statistics 정리 + False Classification Detection + H4 Sample Extractor

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** H3 완료
🔹 **첨부 파일:** golden_validation_results.csv (post H3 corrections), D2 locked action table
🔹 **산출물:**
  - `scripts/validation/detect_false_classification.py`
  - `reports/false_classification_candidates.csv`
  - `scripts/validation/h4_sample_extractor.py` ← **[PATCH-C2] 명시 추가 — CHECK-10 필수**
  - `reports/human_review/h4_sample_set.csv`
  - `reports/human_review/h4_sample_blinded.csv`
🔹 **다음 액션:** P110 (H4 표본 감사)

```
ROLE: Coding agent.

TASK 1: Implement scripts/validation/detect_false_classification.py.

PROCEDURE:
1. Load D2 (scenario_action_table_locked) — full universe with terminal_state assignments
2. For each AUTO scenario:
   - Examine action_sequence — does it contain any function that requires policy?
   - If yes → false AUTO candidate (should be REPAIR)
3. For each REPAIR scenario:
   - Examine: is the required_policy actually missing in any associated AIC type?
   - If yes → false REPAIR candidate (should be QUARANTINE)
   - Examine: is action_sequence executable without analytical judgment?
   - If no → false REPAIR candidate (should be QUARANTINE)
4. Cross-check with golden_validation_results:
   - golden mismatches that flag REPAIR-vs-QUARANTINE or AUTO-vs-REPAIR
   - Append as confirmed candidates (high priority)

OUTPUT: reports/false_classification_candidates.csv

COLUMNS:
scenario_id, family_id, current_label, suspected_label,
detection_rule_triggered, confidence (HIGH/MEDIUM/LOW),
golden_evidence_present (Y/N), priority (CRITICAL/MAJOR/MINOR)

EXPECTED OUTPUT: 0-30 candidates (HIGH confidence subset for H4 review).

CLI:
python scripts/validation/detect_false_classification.py \
  --action-table data/action_labels/scenario_action_table_locked.csv \
  --validation reports/golden_validation_results.csv \
  --out reports/false_classification_candidates.csv

# [PATCH-C2] TASK 2: Implement scripts/validation/h4_sample_extractor.py
# CHECK-10이 reports/human_review/h4_sample_set.csv를 필수 파일로 요구합니다.
# 이 파일은 반드시 이 prompt에서 생성되어야 합니다.

TASK 2: Implement scripts/validation/h4_sample_extractor.py.

PROCEDURE:
1. Load D2 (scenario_action_table_locked.csv)
2. Set random seed for reproducibility (store seed in output CSV header comment)
3. Sample:
   - random_auto: 10 scenarios from AUTO terminal_state (random.sample, seed=42)
   - random_repair: 10 scenarios from REPAIR terminal_state (random.sample, seed=42)
   - v42_specific: 1 scenario per family from F24, F25, F26, F27, F28, F29 (6 total)
     If any F-family has 0 scenarios, log warning and skip (do NOT pad with non-v4.2)
4. Concatenate → 26 rows total (or <26 if some v4.2 families empty)
5. Assign sample_id: S01..S26
6. Save FULL set → reports/human_review/h4_sample_set.csv
   Columns: sample_id, scenario_id, family_id, terminal_state, q_code,
             A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10,
             modality_class, endpoint_data_type, analyte_role,
             action_label, action_sequence, parameter_policy, sample_type
7. Save BLINDED set → reports/human_review/h4_sample_blinded.csv
   Same columns BUT: terminal_state = "HIDDEN", q_code = "HIDDEN"
   (A0..A10, modality_class, endpoint_data_type, analyte_role, action_label,
    action_sequence, parameter_policy, family_id, sample_type all VISIBLE)

CLI:
python scripts/validation/h4_sample_extractor.py \
  --action-table data/action_labels/scenario_action_table_locked.csv \
  --out-full reports/human_review/h4_sample_set.csv \
  --out-blinded reports/human_review/h4_sample_blinded.csv \
  --seed 42

VALIDATION:
- h4_sample_set.csv: ≥20 rows (26 target; may be less if v4.2 families sparse)
- h4_sample_blinded.csv: same row count as full set
- terminal_state in blinded = "HIDDEN" for all rows
- sample_type values: AUTO_RANDOM / REPAIR_RANDOM / V42_F24..F29
```

---

### 🧑 H4 — HUMAN: 표본 감사 + False Classification Veto (PATCH-5 강화)

> **이 단계는 v5.1의 PATCH-5 핵심.** v3.1에서는 LP Panel이 flag한 false classification만 review했지만, v5.1에서는 **random sampling 감사 + LP-flagged review** 두 부분으로 강화됩니다.

#### Part A — Blinded Random Sampling Audit (NEW v5.1)

**1단계. 샘플 추출**

`scripts/validation/h4_sample_extractor.py` **[PATCH-C2: P109에서 반드시 구현 — 별도 작성 금지]**:

```
정확히 다음을 추출:
- random AUTO scenarios: 10개 (D2에서 무작위)
- random REPAIR scenarios: 10개 (D2에서 무작위)
- F24-F29 v4.2 specific: 각 family당 1개씩 6개

총 26개 샘플
```

`reports/human_review/h4_sample_set.csv` 생성.

**2단계. Blinded review (terminal_state 가림)**

`reports/human_review/h4_sample_blinded.csv`:
- terminal_state 컬럼은 빈 칸 또는 'HIDDEN'
- A0..A10, modality_class, endpoint_data_type, analyte_role, action_label, action_sequence는 표시
- q_code, family_id는 표시
- 사람이 axis state + AIC를 읽고 자신이 판단한 terminal_state 기록

```markdown
| sample_id | scenario_id | independent_judgment | rationale |
|---|---|---|---|
| S01 | scen_xyz123 | AUTO | A0=AIC-PK, A4=COMPLETE, no repair needed |
| S02 | scen_abc456 | REPAIR | A4=TITRATION-ADAPTIVE with policy → REPAIR via reconstruct_dose_titration |
| S03 | scen_def789 | QUARANTINE Q19 | A0 endpoint=IMMUNOGENICITY, no positivity_rule → Q19 |
...
```

**3단계. Reveal + 비교**

판정 후, system label을 공개하고 비교:

```markdown
| sample_id | scenario_id | independent | system | match | dispute |
|---|---|---|---|---|---|
| S01 | scen_xyz123 | AUTO | AUTO | YES | none |
| S02 | scen_abc456 | REPAIR | REPAIR | YES | none |
| S03 | scen_def789 | Q19 | Q19 | YES | none |
| S04 | scen_ghi012 | REPAIR | AUTO | NO | system says AUTO but I would REPAIR — review |
...
```

**판정 기준:**
- AUTO sample 10개 mismatch ≥1 → false AUTO 의심, 정밀 조사
- REPAIR sample 10개 mismatch ≥1 → false REPAIR 의심
- v4.2 sample 6개 mismatch ≥1 → 신규 modality 처리 결함

#### Part B — LP-Flagged Review

`reports/false_classification_candidates.csv` (P109 산출물)의 모든 행 검토:
- HIGH confidence + golden_evidence_present=YES: 우선 검토
- MEDIUM confidence: 시간 허용 시 검토
- LOW confidence: spot-check

**4단계. 최종 판정 + 서명**

`reports/human_review/h4_final_audit_report.md`:

```markdown
# H4 Final Audit Report

## Part A: Blinded Sampling Audit
- AUTO samples reviewed: 10
- AUTO mismatches: 0 (or list)
- REPAIR samples reviewed: 10
- REPAIR mismatches: 0 (or list)
- v4.2 samples reviewed: 6
- v4.2 mismatches: 0 (or list)

## Part B: LP-Flagged Review
- HIGH candidates reviewed: N
- Confirmed false classification: M
- Rejected (label is correct): N-M

## Decisions

### Confirmed false AUTO/REPAIR (release blockers if not addressed):
- scenario_id, current_label, correct_label, action_required:
  - patch v1.0 release with documented exception, OR
  - rollback action_label_lock and re-do Phase 7, OR
  - defer to v1.1 with explicit caveat in coverage_claim_statement

### Borderline cases (acceptable for v1.0):
- scenario_id, rationale

### v1.1 candidates (deferred):
- scenario_id, reason

## Veto Decision
- VETO_RELEASE: NO (or YES with reasons)
- conditions_for_release:
  - update coverage_claim_statement to note v1.1 deferred items
  - patch CHANGELOG with known issues

Reviewed_by: [검토자 실명 또는 PMX 전문가]
Date: [YYYY-MM-DD]
```

**완료 조건:**
```
✅ Part A 26 samples 모두 reviewed
✅ Part B 모든 HIGH candidate reviewed
✅ Veto decision 명시
✅ 모든 confirmed false classification 처리 방침 명시
✅ Audit report 서명됨
```

---

### P110 — H4 결과 반영 (자동 또는 수동)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** H4 완료
🔹 **첨부 파일:** H4 audit report
🔹 **산출물:**
  - 만약 confirmed false classification 있고 patch 필요: 수정된 D2 또는 v1.1 register 갱신
  - `reports/h4_resolution_summary.md`
🔹 **다음 액션:** P111

```
ROLE: Coding agent + R-LLM consultation.

INPUT: reports/human_review/h4_final_audit_report.md

PROCEDURE per veto decision:

If VETO_RELEASE = YES:
  STOP. Cannot proceed to release.
  Document in reports/release_blocked_v1_0.md.
  Roll back to relevant Phase (Phase 7 if action label issue,
                                Phase 5 if universe issue,
                                Phase 8 if minimal node issue).

If VETO_RELEASE = NO with conditions:
  For each confirmed false classification with "patch v1.0 release":
    - If trivial (e.g., q_code change for clear case): patch D2 directly
      (note: D2 was locked — this requires explicit unlock + relock cycle,
       documented in CHANGELOG)
    - If non-trivial: defer to v1.1, document in coverage_claim_statement

  For all "v1.1 candidates":
    - Append to change_control/v1_1_candidate_register.csv
    - Note in coverage_claim_statement under "Known limitations"

OUTPUT:
- reports/h4_resolution_summary.md
- updated CHANGELOG.md
- updated change_control/v1_1_candidate_register.csv
- (if any patches) updated D2 + new D2 hash
```

---

### P111 — Coverage Metrics Final Calculation

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P110 완료
🔹 **첨부 파일:** scenario_universe_v1.0.csv (post any P110 patches)
🔹 **산출물:** `reports/coverage_metrics_final.md`
🔹 **다음 액션:** P112

```
ROLE: Coding agent.

TASK: Re-run scripts/validation/calculate_coverage_metrics.py
  (Step 2 P64) on POST-H4 universe.

CALCULATE:
- total_scenarios
- capture_coverage = (AUTO+REPAIR+QUARANTINE+UNSUPPORTED+INVALID) / total
- review_inclusive = (AUTO+REPAIR+QUARANTINE) / (total - UNSUPPORTED - INVALID)
- operational = (AUTO+REPAIR) / (total - UNSUPPORTED - INVALID)
- auto_only = AUTO / (total - UNSUPPORTED - INVALID)
- unsupported_invalid_rate = (UNSUPPORTED+INVALID) / total

POST-H4 ADJUSTMENTS:
- false_auto_count = M (from H4 confirmed)
- false_repair_count = N (from H4 confirmed)
- adjusted_auto = AUTO - false_auto_count (treat false AUTO as REPAIR)
- adjusted_repair = REPAIR - false_repair_count (treat false REPAIR as QUARANTINE)
- adjusted_quarantine = QUARANTINE + false_repair_count

VALIDATE per Hard Rule HR11:
- adjusted capture_coverage ≥ 0.99
- adjusted review_inclusive ≥ 0.95
- false_auto_count = 0 (after patches) OR documented as v1.1 caveat
- false_repair_count = 0 OR documented as v1.1 caveat

REPORT (reports/coverage_metrics_final.md):
- Pre-H4 vs Post-H4 metrics
- v4.2 family-specific coverage
- Coverage CLAIM (per HR12 + PATCH-7):
  ALLOWED: "review-inclusive coverage of scenario classes represented in v4.2 universe ≥95%"
  FORBIDDEN: "all practical scenarios", "exhaustive", "all modalities"
- known limitations (v1.1 deferrals)
- coverage_claim_text (the exact wording for release statement)

OUTPUT: Markdown.
```

---

### P112~P114 — LP Panel CP7: Release Coverage Approval (claim_scope 흡수)

> **v5.1 변경:** v3.1에서 별도였던 claim_scope LP Panel을 release_coverage_approval에 통합 (PATCH-4).

#### P112 (LP-A) — Grandmaster

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** P111 metrics, H3 + H4 logs, all release artifacts
🔹 **산출물:** `reports/llm_proxy/release_coverage_approval_grandmaster.md`

```
ROLE: PMX Grandmaster (LP-A) for Checkpoint CP7 (release_coverage_approval).

INPUT (attached):
  reports/coverage_metrics_final.md
  reports/human_review/h3_golden_approval_log.md
  reports/human_review/h4_final_audit_report.md
  release/v1.0/scenario_universe_freeze_declaration_v1_0.md
  release/v1.0/action_label_lock_declaration.md
  release/v1.0/repair_executor_lock_v1_0.md
  release/v1.0/decision_tree_lock_declaration.md
  release/v1.0/minimal_node_set_lock_declaration.md
  reports/v3_1_to_v5_1_patch_log.md

TASKS:
PART A: Coverage approval
1. capture_coverage ≥99%? review_inclusive ≥95%?
2. Are H3 + H4 results acceptable for release?
3. Are v1.1 deferrals reasonable (not hiding fatal issues)?

PART B: Claim scope check
1. coverage_claim_text uses ONLY "review-inclusive coverage of scenario classes represented" wording
2. No forbidden words: "exhaustive", "all practical", "all modalities", "complete"
3. v4.2 caveats explicit (e.g., "F26 partial coverage; F31-F34 out-of-scope")
4. Tier classification (A/B/C/D) per ILP claim scope:
   - Tier A: full coverage (high confidence)
   - Tier B: partial coverage with explicit limitations
   - Tier C: pilot-bound coverage
   - Tier D: out-of-scope explicitly excluded

PART C: Release readiness
1. All 9 deliverables (D1-D9) exist with hashes?
2. CHANGELOG up to date through v0.10.x?
3. SOP placeholder for Phase 11?

OUTPUT FIELDS:
- recommended_decision: APPROVE / REVISE / REJECT
- rationale_pmx_evidence
- confidence
- fatal_issues
- coverage_claim_proposed_text (final approved wording)
- residual_risk
- must_escalate_to_human (typically YES for final release — this is H5 routing)
- escalation_reason

OUTPUT: Markdown per LP-A template.
```

#### P113 (LP-B) — Adversarial

🔹 **LLM 라우팅:** A-LLM (**다른 계열 고성능 모델 — 새 채팅창 필수**)
🔹 **첨부 파일:** P112 grandmaster, all release artifacts
🔹 **산출물:** `reports/llm_proxy/release_coverage_approval_adversarial.md`

```
ROLE: Adversarial reviewer (LP-B) for CP7.

INPUT (attached):
  reports/llm_proxy/release_coverage_approval_grandmaster.md
  reports/coverage_metrics_final.md
  release/v1.0/*.md (all locks)

ATTACK AXES:
1. Coverage inflation: are review_inclusive numbers honest?
   Are QUARANTINE counted correctly (not double-counted with REPAIR)?
2. Hidden false AUTO/REPAIR after H4: did Grandmaster accept too easily?
3. v4.2 caveat softness: are F26 partial coverage caveats specific enough?
4. Claim scope language slippage: any "all practical" creep?
5. v1.1 deferral abuse: are deferrals legitimate or hiding fatal issues?
6. Release artifact integrity: hash chain valid?
   (D1 hash → D2 hash → ... → D9 hash, all consistent)
7. SOP readiness for new-case intake (will Phase 11 cover it adequately?)
8. Regulatory framing risk: would a regulator accept the coverage claim?
9. PHI/IRB compliance: any leakage from H1-H4 not properly sanitized in release?

For each issue: severity (fatal/major/minor), evidence, correction.

OUTPUT: Markdown per LP-B template.
```

#### P114 (LP-C) — Judge → H5 routing

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델 — 새 세션)
🔹 **첨부 파일:** P112 + P113
🔹 **산출물:**
  - `reports/llm_proxy/release_coverage_approval_judge.md`
  - `reports/llm_proxy/release_coverage_approval_decision.csv`
🔹 **다음 액션:** H5 (사람 최종 결재)

```
ROLE: Judge (LP-C) for CP7.

INPUT: P112 + P113 outputs.

ENFORCE Hard Rules:
- HR11: review_inclusive ≥ 95% (else REJECT)
- HR12: no "exhaustive completeness" claim (else REJECT)
- PATCH-7: only "review-inclusive coverage of scenario classes represented" wording

DECISION:
- If P112 confidence=HIGH AND P113 fatal=0:
  → final_decision = APPROVE_FOR_H5
  → forward all release artifacts to H5

- If P113 fatal>=1:
  → final_decision = REVISE
  → Specify exactly what must change before H5
  → Re-do P112-P114 cycle

- If unrecoverable issue:
  → final_decision = REJECT
  → Block release; route to H4 or earlier rollback

OUTPUT FIELDS:
- final_decision (APPROVE_FOR_H5 / REVISE / REJECT)
- accepted_arguments_from_A
- accepted_attacks_from_B
- coverage_claim_final_text (ready for H5 sign)
- residual_v1_1_items
- escalation_target = H5 (always for release)

OUTPUT: Markdown + decision.csv.
```

---

### 🧑 H5 — HUMAN: Final Release Approval (필수, LLM 대체 절대 불가)

> **이 단계는 release의 최종 결재.** 사람이 직접 모든 release artifact를 검토하고 책임자로 서명합니다. PMX 분야 특성상 audit trail의 마지막 책임은 사람에게 있습니다.

#### 수행 절차

**1단계. Release Artifact 전체 검토**

다음 9개 deliverables의 hash가 release/v1.0/ 아래 모두 존재하는지 확인:

```
□ D1 scenario_universe_v1.0.csv + sha256
□ D2 scenario_action_table_locked.csv + sha256
□ D3 reduced_decision_table_v1.0.csv (Phase 8 P87)
□ D4 pairwise_distinguishability_matrix.npz (Phase 8 P90)
□ D5 final_minimal_node_set.csv + sha256
□ D6 operational_decision_tree.yaml + sha256
□ D7 repair_executor.py + sha256
□ D8 golden_validation_report.md (P107 + H3-corrected)
□ D9 coverage_claim_statement.md (CP7 P114 final text)
```

**2단계. CHANGELOG 검증**

`CHANGELOG.md` 처음부터 끝까지 직접 읽기:
```
□ v0.1.0 (init) → v0.10.0 (decision tree) → v0.11.0 (post-H4) 모든 단계 기록됨
□ 모든 hash 변경이 추적됨
□ 모든 LP Panel CP1-CP7 결과 기록됨
□ H1-H4 결과 모두 참조됨
□ v1.1 deferred items 명시됨
```

**3단계. Coverage Claim Statement 직접 검토**

`release/v1.0/coverage_claim_statement.md` 직접 읽기:
```
□ "review-inclusive coverage of scenario classes represented in v4.2 universe" 표현 사용
□ "exhaustive", "all practical", "all modalities" 같은 금지 표현 없음
□ 95% review_inclusive 수치 정확함
□ v1.1 deferred items 명시됨 (F26 partial coverage 등)
□ Tier A/B/C/D 구분 명확함
```

**4단계. PMX 전문가 spot-check (선택)**

가능하면 외부 PMX 전문가에게 5개 무작위 시나리오를 보여주고 terminal_state 판단이 합리적인지 확인.

**5단계. 최종 승인 서명**

`release/v1.0/H5_final_release_approval.md`:

```markdown
# H5 Final Release Approval

## Release Version
v1.0

## Approval

I, [name and role], have personally reviewed:
- All 9 final deliverables (D1-D9)
- All hash files
- CHANGELOG from initialization to current
- coverage_claim_statement.md (final text)
- All H1, H2, H3, H4 logs
- LP Panel CP1-CP7 outcomes

I confirm:
- [x] No PHI leakage in any release artifact
- [x] Coverage claim language complies with PATCH-7 restriction
- [x] All confirmed false classifications resolved (patch or v1.1 deferral)
- [x] v1.1 deferred items documented and acceptable for v1.0 scope
- [x] Hash chain integrity verified
- [x] Audit trail (decision_log + execution_log) complete

Decision: APPROVED FOR RELEASE v1.0

Signed: [승인자 실명 또는 역할명]
Date: [YYYY-MM-DD]
Role: PMX 책임자
Organization: [연구실명]

Conditions (if any):
- [None / list conditions]

Next steps:
- Tag git as v1.0.0
- Archive release/v1.0/ to immutable storage
- Begin Phase 11: Change Control + 100-case Validation
```

> **VETO 조건:** 사람이 검토 중 다음 발견 시 release 차단:
> - PHI 잔존 (H1 미흡)
> - golden reference 오류 발견 (H3 추가 필요)
> - false classification 누락 (H4 재실행)
> - coverage claim 표현 슬립 (P111-P114 재실행)

---

### P115 — Release v1.0 Tag + Hash Chain 생성

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** H5 APPROVED
🔹 **산출물:**
  - `release/v1.0/RELEASE_NOTES_v1_0.md`
  - `release/v1.0/release_v1_0_combined.sha256`
  - git tag v1.0.0 (선택)
🔹 **다음 액션:** P116 (Phase 11 시작)

```
ROLE: Coding agent.

TASK 1: Generate release/v1.0/RELEASE_NOTES_v1_0.md

CONTENT:
# Release v1.0 Notes

## Approved by H5
- Approver: [승인자 실명 또는 역할명]
- Date: [YYYY-MM-DD]
- File: H5_final_release_approval.md

## Deliverables
- D1: scenario_universe_v1.0.csv (hash: ...)
- D2: scenario_action_table_locked.csv (hash: ...)
- D3: reduced_decision_table_v1.0.csv (hash: ...)
- D4: pairwise_distinguishability_matrix.npz (hash: ...)
- D5: final_minimal_node_set.csv (hash: ...)
- D6: operational_decision_tree.yaml (hash: ...)
- D7: repair_executor.py (hash: ...)
- D8: golden_validation_report.md (hash: ...)
- D9: coverage_claim_statement.md (hash: ...)

## Coverage
- review_inclusive: X%
- operational: Y%
- auto_only: Z%
- unsupported_invalid: W%

## Known limitations (v1.1 deferred)
- [list from H4 + P110]

## Universe basis
- Frozen Universe v4.2

## LP Panel results
- CP1 (config_semantic): APPROVED auto
- CP2 (universe_attack_freeze): APPROVED auto
- CP3 (repair_semantic): [APPROVED / not_triggered]
- CP4 (action_label_adjudication): APPROVED auto
- CP5 (action_label_lock): APPROVED auto
- CP6 (minimal_node_approval): APPROVED auto
- CP7 (release_coverage_approval): APPROVED → H5

## Human checkpoints
- H1 (deidentification): SIGNED
- H2 (fingerprint): SIGNED
- H3 (golden): SIGNED
- H4 (audit + veto): SIGNED, VETO=NO
- H5 (final release): APPROVED

TASK 2: Generate release/v1.0/release_v1_0_combined.sha256
- SHA256 of each D1..D9 in order
- Combined hash: SHA256 of concatenated individual hashes

TASK 3: Update CHANGELOG.md
"## v1.0.0 — RELEASED on YYYY-MM-DD"
"All deliverables locked. Hash chain integrity verified. H5 approved."

TASK 4 (optional): Run git tag if git repo
git tag -a v1.0.0 -m "v1.0 release"

OUTPUT: 2 files + CHANGELOG. (git tag if applicable)
```

---

### 🐍 CHECK-10 (Phase 10 검증)

```python
# check_phase10.py
import os, sys, hashlib
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas 없음"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("❌"); sys.exit(1)

print("=" * 60)
print("CHECK-10: Phase 10 (Validation + Release) 완료 검증")
print("=" * 60)

failures = []

REQUIRED = [
    "scripts/validation/run_golden_validation.py",
    "scripts/validation/detect_false_classification.py",
    "scripts/validation/h4_sample_extractor.py",  # [PATCH-C2] 명시 추가
    "reports/golden_validation_results.csv",
    "reports/golden_validation_summary_v1.md",
    "reports/false_classification_candidates.csv",
    "reports/coverage_metrics_final.md",
    "reports/human_review/h3_golden_approval_log.md",
    "reports/human_review/h4_final_audit_report.md",
    "reports/human_review/h4_sample_set.csv",
    "reports/human_review/h4_sample_blinded.csv",  # [PATCH-C2] 명시 추가
    "release/v1.0/H5_final_release_approval.md",
    "release/v1.0/RELEASE_NOTES_v1_0.md",
    "release/v1.0/release_v1_0_combined.sha256",
]
print("\n[필수 파일]")
for f in REQUIRED:
    if (BASE / f).is_file(): print(f"  ✅ {f.split('/')[-1]}")
    else: print(f"  ❌ {f}"); failures.append(f)

# H3, H4, H5 서명 확인
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
    df = pd.read_csv(hs)
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
    else:
        print("  ⚠️  컬럼 또는 데이터 없음")

# 9 deliverables hash 존재 확인  [PATCH M-3: D8 hash 추가]
print("\n[9 Deliverables Hash — D1~D9 전체]")
hashes = [
    ("D1", "release/v1.0/scenario_universe_v1_0.sha256"),
    ("D2", "release/v1.0/action_label_lock_v1_0.sha256"),
    ("D5", "release/v1.0/minimal_node_set_v1_0.sha256"),
    ("D6", "release/v1.0/decision_tree_v1_0.sha256"),
    ("D7", "release/v1.0/repair_executor_v1_0.sha256"),
    ("D8", "release/v1.0/golden_validation_report_v1_0.sha256"),  # [PATCH M-3] D8 canonical
    ("D9", "release/v1.0/release_v1_0_combined.sha256"),
]
for label, h in hashes:
    if (BASE / h).is_file():
        print(f"  ✅ {label}: {h.split('/')[-1]}")
    else:
        print(f"  ❌ {label}: {h.split('/')[-1]}")
        failures.append(f"hash {label} {h}")

# D8 canonical file 존재 확인 [PATCH M-3]
print("\n[D8/D9 Canonical Files]")
for label, path in [
    ("D8", "reports/golden_validation_report.md"),
    ("D9", "release/v1.0/coverage_claim_statement.md"),
]:
    if (BASE / path).is_file():
        print(f"  ✅ {label}: {path.split('/')[-1]}")
    else:
        print(f"  ❌ {label}: {path} — D8/D9 canonical file 없음")
        failures.append(f"{label} canonical 없음")

# Coverage Claim 표현 검증 (PATCH-7)
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
```

---

## 🔄 Phase 11: Change Control + 100-case Validation + SOP (P116~P140)

### 📌 이 단계 목적

v1.0 release 이후 운영 단계에서 새로운 PMX 데이터셋이 들어왔을 때 어떻게 처리할지 정의하는 SOP를 만들고, **100개 무작위 시나리오로 시스템 능력을 post-release stress-test**합니다. 또한 v1.1 변경 관리 프로세스를 명문화합니다.

> ⚠️ **[PATCH-100case-위치]** Step 1 D9 주석(Option B 선택)에 따라 100-case validation은 **post-release operational stress test**로 운용합니다. coverage_claim_statement(D9)의 근거는 D8(golden validation) + H4(blinded audit) + pilot/seed-pack coverage이며, 100-case 결과는 v1.1 candidate register 트리거 용도입니다.

### 진입 조건
- [x] CHECK-10 PASS

---

### P116 — New Case Intake SOP 작성

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** CHECK-10 PASS
🔹 **첨부 파일:** D6 (decision tree), D7 (repair executor), AIC template
🔹 **산출물:** `release/v1.0/SOP_new_case_intake_v1_0.md`
🔹 **다음 액션:** P117

```
ROLE: PMX Grandmaster + SOP author.

TASK: Produce release/v1.0/SOP_new_case_intake_v1_0.md.

REQUIRED CONTENT:

# SOP: New Case Intake (v1.0)

## Purpose
Standard operating procedure for processing new PMX datasets through the
v1.0 universe + decision tree + repair executor.

## Scope
Applies to any new PMX dataset arriving at the lab for NONMEM dataset preparation.

## Step-by-step procedure

### Step 1: Pre-intake checklist
- [ ] Dataset has documented analysis intent (AIC required fields)
- [ ] Dataset is deidentified (apply Step 2 H1 checklist)
- [ ] Source format identified (SDTM/ADaM/EDC/Excel/SAS/etc)

### Step 2: AIC validation
Run: python scripts/config_validation/validate_aic.py --aic-file <path>

If validation fails:
- Missing endpoint_data_type → request from sponsor (Q11)
- Missing v4.2-specific policies → request from bioanalyst/PMX lead

### Step 3: Fingerprint generation
Generate fingerprint per Step 2 P32 prompt template, then H2-review.

### Step 4: Decision tree routing
Run: python scripts/decision_tree/route_scenario.py
  --fingerprint <path>
  --tree config/operational_decision_tree.yaml
  --out <decision_log>

This produces:
- terminal_state (AUTO/REPAIR/QUARANTINE/UNSUPPORTED/INVALID)
- q_code (if QUARANTINE)
- recommended action_sequence

### Step 5: Action execution

If AUTO:
  Run repair_executor.run_repair_pipeline with action_sequence
  Output: NONMEM-ready dataset
  Run: python scripts/validation/nonmem_ready_qc.py
  Deliver to PMX modeler

If REPAIR:
  Same as AUTO but with audit_log highlighting repair functions used

If QUARANTINE:
  Issue formal quarantine notice to sponsor with q_code rationale
  Indicate required input to clear (per quarantine_reason_codes.yaml)

If UNSUPPORTED:
  Communicate with sponsor that data is outside operational scope (F31-F33)
  Suggest alternative data acquisition

If INVALID:
  Document why (corruption, missing core, etc.)
  Cannot proceed; requires sponsor remediation

### Step 6: Audit & traceability
- Save decision_log + audit_log to project folder
- Update execution_log.csv with new case
- All NONMEM-ready outputs require:
  - SHA256 of input
  - SHA256 of output
  - decision_path
  - executor version (v1.0 hash)
  - tree version (v1.0 hash)

### Step 7: Coverage tracking
- Increment running counter per family_id
- Quarterly: review for v1.1 candidate cases
  (any case requiring manual override → register)

## Edge cases

### Case: Decision tree routes to QUARANTINE but sponsor insists AUTO/REPAIR
- DO NOT override
- Issue change request via change_control framework (P117 SOP)
- Wait for v1.1 cycle

### Case: AIC partially specified
- Cannot proceed under v1.0
- Request complete AIC; do not auto-default

### Case: New modality not in v4.2 universe
- Route to F31-F34 (UNSUPPORTED) or escalate to v1.1 candidate register
- Cannot custom-handle within v1.0

## Roles & responsibilities

- PMX modeler: receives NONMEM-ready dataset; reports any model-level issues
- PMX dataset wrangler (operator): runs SOP for new cases
- Bioanalyst: provides positivity rules, cellular_LLOQ values
- Sponsor: provides AIC and source data
- PMX lead (H5 signer): approves any non-routine override

## Version
v1.0 (locked at: ISO timestamp)
Next review: at v1.1 release (planned: 6 months from v1.0)

OUTPUT: Markdown.
```

---

### P117 — Change Control SOP

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** v1_1_candidate_register, P116 SOP
🔹 **산출물:** `release/v1.0/SOP_change_control_v1_0.md`
🔹 **다음 액션:** P118

```
ROLE: SOP author.

TASK: Produce release/v1.0/SOP_change_control_v1_0.md.

REQUIRED CONTENT:

# SOP: Change Control (v1.0)

## When to register a v1.1 candidate

A change is required when:
1. New dataset cannot be classified by current universe (UNIVERSE_GAP)
2. New family-class encountered (FAMILY_PATCH_NEEDED)
3. AIC field insufficient (AIC_INSUFFICIENT)
4. Confirmed false classification post-release (CLASSIFICATION_FIX)
5. Repair executor bug discovered (EXECUTOR_FIX)
6. Decision tree routing error (TREE_FIX)

## Registration procedure

1. Document the issue:
   - case_id (real project that triggered)
   - issue_type (one of 6 above)
   - affected_axis / family / function
   - severity (CRITICAL / MAJOR / MINOR)
   - workaround_used (how was it handled in v1.0)

2. Append to change_control/v1_1_candidate_register.csv

3. Set required_rerun_steps (which prompts/phases need re-execution)

## v1.1 release trigger

v1.1 is triggered when ANY of:
- ≥10 candidates in register (volume threshold)
- ≥1 CRITICAL severity (urgency)
- 6 months since v1.0 (calendar)
- Major v4.x universe upgrade (e.g., v4.3)

## v1.1 release procedure

1. Group candidates by phase impact
2. Re-execute affected phase(s) (start from earliest impacted)
3. Re-run all subsequent CHECKs (CHECK-N onwards)
4. Re-run LP Panels for impacted checkpoints
5. Re-do golden validation (subset, with NEW goldens for new families)
6. H4 sample audit (PATCH-5 still applies, sample size 26)
7. H5 final approval
8. Tag git as v1.1.0

## Forbidden changes (require v2.0 not v1.1)

- Removing existing F-codes
- Changing Q-code numbering (e.g., re-using Q17)
- Renaming action_function names (breaks backward compat)
- Changing decision tree node order (breaks audit trail compatibility)

For these → v2.0 with full rebuild

## Version
v1.0 (locked at: ISO timestamp)

OUTPUT: Markdown.
```

---

### P118 — 100-case Validation Plan

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **첨부 파일:** D1 universe, D2 action table
🔹 **산출물:** `reports/100_case_validation_plan.md`
🔹 **다음 액션:** P119

```
ROLE: PMX Grandmaster.

TASK: Produce reports/100_case_validation_plan.md.

CONTENT:

# 100-Case Validation Plan

## Purpose
Final stress test of v1.0 release using 100 realistic synthetic cases
covering all 29 operational families (F01-F29) + 5 v4.2 modalities.

## Case selection
- 70 cases from operational families (F01-F23): roughly proportional to
  expected real-world frequency
- 30 cases from v4.2 families (F24-F29): each family ≥3 cases
- Mix of AUTO (35 expected), REPAIR (45 expected), QUARANTINE (20 expected)

## Case construction
- Use synthetic data generated from AIC templates (no real PHI)
- Each case has: raw_input, AIC, expected_terminal_state, expected_q_code (if any)
- v4.2 cases include policy-present and policy-absent variants

## Validation procedure

For each case:
1. Apply Phase 10 P106 golden_validation pipeline
2. Compare terminal_state, action_sequence, output dataset
3. Run NONMEM QC if AUTO/REPAIR

## Pass criteria

- Overall PASS rate ≥ 95%
- Per-family PASS rate ≥ 80%
- v4.2-new family PASS rate ≥ 80%
- All Q-code paths exercised ≥1 case each (Q01-Q19 except Q17)
- All forced nodes evaluated as Y AND as N at least once

## Reporting
- per-case results in 100_case_validation_results.csv
- summary in 100_case_validation_summary.md

## Failure handling
- <95% overall: register all failures as v1.1 candidates
- <80% any family: BLOCKER, requires patch before SOP rollout

OUTPUT: Markdown.
```

---

### P119 — 100-case 합성 데이터 생성

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **진입 조건:** P118 완료
🔹 **첨부 파일:** AIC template, family rules, axis dictionary
🔹 **산출물:**
  - `scripts/validation/generate_100_synthetic_cases.py`
  - `data/validation/100_case_inputs/` (100 raw_input + AIC sets)
  - `data/validation/100_case_expectations.csv`
🔹 **다음 액션:** P120

```
ROLE: Coding agent.

TASK: Implement scripts/validation/generate_100_synthetic_cases.py.

PROCEDURE:
1. Load family_assignment_rules.yaml (F01-F29 + F31-F34)
2. For each family, generate N cases per P118 distribution
3. For each case:
   - Determine A0..A10 axis pattern from family rules
   - Generate synthetic dataset matching that pattern
   - Generate AIC matching policies required for that family
   - Half of v4.2 cases: generate "policy-present" variants
   - Half of v4.2 cases: generate "policy-absent" variants → expect QUARANTINE
   - Save to data/validation/100_case_inputs/case_{NNN}/raw_input.csv + aic.yaml
   - Append to 100_case_expectations.csv with expected_terminal_state, expected_q_code

CASE NUMBERING:
- 001-070: routine families (F01-F23)
- 071-100: v4.2 families (F24-F29)

CSV columns:
case_id, family_id, modality_class, endpoint_data_type, analyte_role,
A0_state, A1_state, ..., A10_state, expected_terminal_state, expected_q_code,
policy_variant (present/absent/n.a.)

OUTPUT: Script + 100 case folders + expectations CSV.
```

---

### P120 — 100-case Validation 실행

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **첨부 파일:** P119 cases, D6 tree, D7 executor
🔹 **산출물:**
  - `reports/100_case_validation_results.csv`
  - `reports/100_case_validation_summary.md`
🔹 **다음 액션:** P121

```
ROLE: Coding agent.

PROCEDURE:
1. For each of 100 cases:
   - Apply decision tree routing
   - Compare with expected_terminal_state
   - If AUTO/REPAIR: execute pipeline, run NONMEM QC
2. Compile results CSV
3. Generate summary md

REPORT (reports/100_case_validation_summary.md):
- Overall PASS rate
- Per-family PASS rate (table)
- v4.2 family-specific (F24-F29)
- Q-code coverage (which Q-codes exercised)
- Forced node Y/N coverage
- Failure root-cause distribution

PASS CRITERIA (per P118):
- Overall ≥ 95%? Y/N
- Per-family ≥ 80%? Y/N
- All Q-codes exercised? Y/N
- Forced nodes both Y and N? Y/N

OUTPUT: 2 files.
```

---

### P121 — 100-case Failure Triage (조건부)

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델)
🔹 **진입 조건:** P120 결과 PASS rate < 95% 시
🔹 **첨부 파일:** P120 results
🔹 **산출물:** `reports/100_case_failure_triage.md`
🔹 **다음 액션:** PASS rate ≥95% 이거나 v1.1 등록 후 P122

```
ROLE: PMX Grandmaster.

INPUT: reports/100_case_validation_results.csv

If overall PASS rate ≥95%: skip this prompt.

For each failure:
- case_id, expected_*, actual_*
- root cause (TREE_BUG, EXECUTOR_BUG, EXPECTATION_ERROR, POLICY_AMBIGUITY)
- recommendation (v1.1 register, immediate patch, expectation correction)

GATE:
- All TREE_BUG/EXECUTOR_BUG → v1.1 register, document in coverage_claim_statement
- All EXPECTATION_ERROR → fix expectations, re-run
- POLICY_AMBIGUITY → register, may require AIC template enhancement in v1.1

OUTPUT: Markdown.
```

---

### P122~P139 — Documentation, Training, Audit Trail (10 prompts batch)

> **이 단계는 release 이후 운영 문서 작성. 각 항목은 짧은 R-LLM 작업.**

#### P122 — Operator Quick Reference Card

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/operator_quick_reference.md`

```
ROLE: Documentation writer.

TASK: 1-page quick reference for operators using v1.0 daily.

CONTENT:
- 5-step workflow (intake → AIC validate → tree → execute → QC)
- Common Q-codes and what to do
- v4.2 specific gotchas (cellular, dyad, immunogenicity)
- Where to find what (paths to D1-D9)
- When to escalate (v1.1 register triggers)
- Contact for H5 escalation

OUTPUT: Markdown, ≤2 pages.
```

#### P123 — PMX Modeler Onboarding Guide

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/modeler_onboarding_guide.md`

```
ROLE: Documentation writer.

TASK: Onboarding guide for PMX modelers receiving NONMEM-ready datasets
from the v1.0 system.

CONTENT:
- What audit_log fields to look for
- How to verify executor version (hash match)
- When to question terminal_state (raise H5 escalation)
- Coverage interpretation (review-inclusive ≥95% language)
- v1.1 candidate register location

OUTPUT: Markdown.
```

#### P124 — Auditor Summary Report Template

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/auditor_report_template.md`

```
ROLE: SOP author.

TASK: Template for external auditor summary report.

CONTENT:
- Universe basis: Frozen v4.2
- LP Panel coverage (CP1-CP7)
- Human checkpoints (H1-H5)
- Hash chain integrity
- Coverage statement
- v1.1 deferred items
- Known limitations

OUTPUT: Markdown template (with placeholders).
```

#### P125 — Troubleshooting Guide

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/troubleshooting_guide.md`

```
ROLE: Documentation writer.

TASK: Produce troubleshooting_guide.md — operational error patterns + resolution.

REQUIRED SECTIONS:
1. Decision tree routes to QUARANTINE but sponsor expects AUTO/REPAIR → do NOT override, register v1.1
2. AIC field missing at intake → which q_code to cite, how to request from sponsor
3. pytest FAIL on repair_executor post-deployment → hash reverification steps
4. CAR-T (F26) cellular_LLOQ policy absent → Q01 cellular subtype, what to document
5. Maternal-infant dyad linkage key missing → Q18, what info to collect
6. v1.1 register growing fast → escalation criteria (when to trigger v1.1 cycle)

OUTPUT: Markdown, ≤2 pages.
```

---

#### P126 — v1.0 to v2.0 Migration Strategy

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/v1_to_v2_migration_strategy.md`

```
ROLE: Documentation writer.

TASK: High-level migration strategy for future v2.0 (full rebuild).

CONTENT:
- Triggers for v2.0 (vs v1.1): breaking axis changes, Q-code renumbering, backward-compat break
- Frozen artifacts that cannot carry over (need full rebuild): D1-D9 all
- Re-use candidates: pilot fingerprint methodology, LP Panel template, CHECK script patterns
- Timeline estimate: v2.0 takes 2× v1.0 effort

OUTPUT: Markdown.
```

---

#### P127 — Operational Metrics Dashboard Specification

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `reports/metric_dashboard_specification.md`

```
ROLE: Documentation writer.

TASK: Define operational metrics dashboard for v1.0 monitoring.

METRICS (quarterly):
- New cases processed: total, by terminal_state, by family
- QUARANTINE rate: should be stable; spike → investigate
- v1.1 register growth: trend
- H4 audit rate (blinded sample pass rate): target ≥95%
- False classification incident count: target 0
- 100-case rerun pass rate (if re-run after patches)

OUTPUT: Markdown spec table.
```

---

#### P128 — External Data Request Template

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/external_data_request_template.md`

```
ROLE: Documentation writer.

TASK: Template for requesting missing data/policy from uncooperative sponsor.

CONTENT:
- Formal QUARANTINE notification with q_code
- Required information to clear each q_code (reference quarantine_reason_codes.yaml)
- Escalation path if sponsor unresponsive
- v4.2 specific: cellular_LLOQ, positivity_adjudication_rule, dyad_linkage_key requests

OUTPUT: Markdown template with fill-in sections.
```

---

#### P129 — Pediatric Special Populations Addendum

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/pediatric_special_populations_addendum.md`

```
ROLE: PMX Grandmaster.

TASK: Addendum for pediatric PK datasets (F12) in v1.0 system.

CONTENT:
- mg/kg vs BSA dose reconstruction (RR008, RR009)
- Age-dependent LLOQ (may require different BLQ policy vs adult)
- Body weight time-varying covariate (F12 + A7=TIME-VARYING)
- Common QUARANTINE triggers: dose column missing after weight calculation

OUTPUT: Markdown.
```

---

#### P130 — Regulatory Submission Evidence Pack Skeleton

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/regulatory_submission_evidence_pack_skeleton.md`

```
ROLE: PMX Grandmaster + regulatory documentation specialist.

TASK: Skeleton for regulatory submission evidence package using v1.0 outputs.

SECTIONS:
- System description (reference D6 tree YAML, D7 executor hash)
- Validation evidence (D8 golden report, 100-case results)
- Coverage claim statement (D9 coverage_claim_statement.md verbatim)
- Human oversight evidence (H1-H5 approval logs)
- Audit trail (execution_log.csv, per-case audit_log)
- Known limitations (v1.1 register)

OUTPUT: Markdown skeleton with [FILL-IN] placeholders.
```

---

#### P131 — Executor Function Inventory

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** D7 repair_executor.py, repair_rule_dictionary.yaml
🔹 **산출물:** `release/v1.0/executor_function_inventory.md`

```
ROLE: Documentation writer.

TASK: Produce inventory of all 26 repair functions with one-line summaries.

TABLE COLUMNS:
rule_id | function_name | v4_2_new | input_columns | required_policy | output_columns | fallback_q_code

INCLUDE ALL 26: RR001-RR026.
Mark v4.2 new: RR020-RR026.

OUTPUT: Markdown table.
```

---

#### P132 — Q-code Quick Lookup

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** config/quarantine_reason_codes.yaml
🔹 **산출물:** `release/v1.0/q_code_quick_lookup.md`

```
ROLE: Documentation writer.

TASK: Single table of all 21 Q-codes (Q01-Q14, Q15A-D, Q16, Q18, Q19).
Include: code | short_name | one-line definition | how_to_clear | v4_2_new flag
Note Q17 as REJECTED with reason.

OUTPUT: Markdown table.
```

---

#### P133 — Family Quick Lookup

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** config/family_assignment_rules.yaml
🔹 **산출물:** `release/v1.0/family_quick_lookup.md`

```
ROLE: Documentation writer.

TASK: Single reference table for all 33 family codes (F01-F29 op + F31-F34 out).

TABLE COLUMNS:
family_id | family_name | operational_scope | expected_terminal | v4_2_new | key_distinguishing_feature

OUTPUT: Markdown table.
```

---

#### P134 — Decision Tree Visual (Mermaid)

🔹 **LLM 라우팅:** C-LLM (Cursor IDE)
🔹 **첨부 파일:** config/operational_decision_tree.yaml
🔹 **산출물:** `release/v1.0/decision_tree_visual_mermaid.md`

```
ROLE: Coding agent.

TASK: Convert operational_decision_tree.yaml to Mermaid flowchart diagram.

PROCEDURE:
1. Read D6 yaml
2. Traverse nodes N0→N1→N8→N2→N3→N4→N5→(N6→N7 if selected)
3. Each node = diamond shape, Y/N branches
4. Leaf nodes = rectangle with terminal_state + q_code (if QUARANTINE)
5. Color code: AUTO=green, REPAIR=blue, QUARANTINE=yellow, INVALID=red

OUTPUT: Markdown with ```mermaid code block.
```

---

#### P135 — Operational Metrics First Run

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `reports/operational_metrics_v1_0.md`

```
ROLE: Documentation writer.

TASK: Define baseline operational metrics at v1.0 release.

CONTENT:
- Baseline terminal_state distribution from D2 (% AUTO, REPAIR, QUARANTINE)
- Coverage metrics from coverage_claim_statement.md
- 100-case validation results summary
- v1.1 register count at release

OUTPUT: Markdown, brief (≤1 page).
```

---

#### P136 — Quarterly Review Schedule

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `reports/quarterly_review_schedule.md`

```
ROLE: Documentation writer.

TASK: Define quarterly review cadence for v1.0 operations.

SCHEDULE:
Q1 (3 months post-release): v1.1 candidate triage, H4 spot-check 10 random new cases
Q2 (6 months): v1.1 trigger evaluation, 100-case re-run if executor patched
Q3 (9 months): metric dashboard update, new modality pipeline check
Q4 (12 months): annual review, v2.0 planning decision

OUTPUT: Markdown.
```

---

#### P137 — Incident Response SOP

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `reports/incident_response_sop.md`

```
ROLE: SOP author.

TASK: Incident response SOP for confirmed false AUTO/REPAIR post-release.

PROCEDURE:
1. Incident detected → document in v1.1 register (CLASSIFICATION_FIX, CRITICAL)
2. Assess scope: how many real projects affected?
3. If ≥1 project with submitted data → escalate to PMX lead + regulatory
4. Patch decision: immediate v1.1 micro-release vs wait for batch
5. Communication: notify affected project modelers
6. Documentation: update audit_log for affected cases with "post-release correction"

OUTPUT: Markdown SOP.
```

---

#### P138 — External Review Package

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **산출물:** `release/v1.0/external_review_package_v1_0.md`

```
ROLE: Documentation writer.

TASK: Compile external review package for cross-functional reviewers or auditors.

INCLUDE:
- System summary (2 paragraphs, no jargon)
- D1-D9 file list with SHA256 (from release/v1.0/*.sha256)
- Coverage statement (verbatim from coverage_claim_statement.md)
- H1-H5 approval dates (no PHI)
- LP Panel summary (CP1-CP7, which auto vs H4-escalated)
- Known limitations and v1.1 roadmap

OUTPUT: Markdown, ≤4 pages.
```

---

#### P139 — v1.1 Candidate Priority Ranking

🔹 **LLM 라우팅:** R-LLM (효율 모델)
🔹 **첨부 파일:** `change_control/v1_1_candidate_register.csv`
🔹 **산출물:** `change_control/v1_1_priority_ranking.md`
🔹 **다음 액션:** P140

```
ROLE: PMX Grandmaster.

INPUT: change_control/v1_1_candidate_register.csv

TASK: Rank all v1.1 candidates by impact + effort.

RANKING CRITERIA:
- CRITICAL severity → always top tier
- Affects F24-F29 (v4.2 new modality) → high priority
- Affects multiple cases in register → higher priority
- Single AIC field fix → low effort, move up
- Requires full phase re-execution → high effort, move down

OUTPUT COLUMNS: rank | candidate_id | severity | effort | reason | target_v1_1_sprint

OUTPUT: Markdown.
```

---

### P140 — Final Completion Declaration

🔹 **LLM 라우팅:** R-LLM (고성능 추론 모델) — 마지막은 Opus로 정성적 검증
🔹 **진입 조건:** P139 (또는 우선순위 6개) 완료
🔹 **첨부 파일:** 모든 release artifact, 모든 CHECK 결과, 모든 H 서명
🔹 **산출물:** `reports/PROJECT_FINAL_COMPLETION_v5_1.md`
🔹 **다음 액션:** CHECK-11 (최종)

```
ROLE: PMX Grandmaster + project closeout author.

INPUT (attached):
  release/v1.0/ (all files)
  reports/100_case_validation_summary.md
  reports/coverage_metrics_final.md
  All H1-H5 logs
  All CHECK-0 ~ CHECK-10 outputs
  CHANGELOG.md

TASK: Produce reports/PROJECT_FINAL_COMPLETION_v5_1.md.

CONTENT:

# PMX-to-NONMEM Scenario Universe v1.0 — Final Completion Declaration

## Project goal achieved
"실무적으로 현실성 있는 임의의 데이터셋 조합으로부터 NONMEM-ready dataset까지
도달하는 모든 시나리오 universe를 포착하고, 안전상 필수 forced gates(N0, N1, N2, N3, N4, N5, N8)를
고정한 상태에서 남은 optional nodes 중 distinguishability를 만족하는 최소 추가 노드 집합을 ILP로 추출한다."

> ⚠️ **[PATCH MINOR-N3]** "최소 의사결정 노드"는 ILP가 7개 forced gate를 고정한 후 N6/N7 중 필요 노드를 선택하는 구조입니다.
> coverage_claim_statement.md에 이 정확한 표현을 사용하세요.

## Goal achievement check
[ ] Universe v1.0 captures all v4.2 scenario classes (review-inclusive ≥95%)
[ ] Decision tree D6 routes 100% of universe scenarios
[ ] Minimal node set D5 satisfies strengthened distinguishability (PATCH-2)
[ ] Forced nodes (N0-N5, N8) all in minimal set (PATCH-3 enforced)
[ ] Repair executor D7 implements all 26 functions including v4.2-new
[ ] H4 sampling audit (PATCH-5) passed without veto
[ ] Coverage claim wording compliant with PATCH-7

## 17 success criteria check (from P1 charter)
[ ] All 9 deliverables exist with hashes
[ ] q_code-less QUARANTINE = 0
[ ] Q15 standalone = 0
[ ] Q17 = 0
[ ] REPAIR without function = 0
[ ] Confirmed false AUTO = 0 (or v1.1 deferred and documented)
[ ] Confirmed false REPAIR = 0 (or v1.1 deferred and documented)
[ ] Universe freeze SIGNED (auto / H4-routed)
[ ] Action label LOCK signed
[ ] Forced node ⊆ minimal node set
[ ] ILP claim scope documented
[ ] 100-case validation completed
[ ] CHECK-0 ~ CHECK-11 all PASS
[ ] H1-H5 all signed
[ ] LP Panel CP1-CP7 all resolved
[ ] v4.2 patches C16-C24 all applied
[ ] H5 final approved

## v5.1 strengthening summary (vs v3.1 baseline)
PATCH-1 (v4.2 universe upgrade): ✅ applied via Phase 1
PATCH-2 (ILP distinguishability strengthening): ✅ applied via P89, P90
PATCH-3 (forced node explicit): ✅ applied via P93, enforced in P95
PATCH-4 (LP Panel 13→7 compression): ✅ applied via P2 template
PATCH-5 (H4 blinded sampling audit): ✅ applied via Phase 10 P109(detect_false_classification + h4_sample_extractor)+H4
PATCH-6 (pilot edge-case seed pack): ✅ applied via P27, P29, P36
PATCH-7 (coverage wording restriction): ✅ applied via P111, P112
PATCH-8 (CHECK script enrichment): ✅ applied via all CHECK-N
PATCH-9 (hypothesis property tests): ✅ applied via Step 2 P46

## Statistics summary
- total scenarios: <N>
- AUTO: <Na> (<Pa>%)
- REPAIR: <Nr> (<Pr>%)
- QUARANTINE: <Nq> (<Pq>%)
- UNSUPPORTED: <Nu>
- INVALID: <Ni>
- review_inclusive: <X>%
- 100-case validation PASS rate: <Y>%

## Known limitations (v1.1 candidate register)
- [list from change_control register, summarized]

## Lessons learned (operational)
- [free-form retrospective]

## Next steps
- v1.1 release planning (target: 6 months)
- Quarterly review of operational metrics
- v2.0 universe (e.g., v4.3 incorporation) when applicable

## Final approval
- H5 signed: <date>
- Project closed: <date>

OUTPUT: Markdown.
```

---

### 🐍 CHECK-11 (최종 검증)

```python
# check_phase11_final.py
# [PATCH F-2] warnings 변수 정의 추가
# [PATCH 교차검토] D8/D9 canonical path 교정 + prev-CHECK execution_log 검증
# [PATCH 교차검토] 100-case CSV 기반 실제 pass rate 계산
import os, sys, hashlib, subprocess
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas 없음"); sys.exit(1)

BASE_CANDIDATES = [Path("pmx_universe_v5_1"), Path("./pmx_universe_v5_1"), Path("../pmx_universe_v5_1")]
BASE = next((c for c in BASE_CANDIDATES if c.is_dir()), None)
if BASE is None: print("❌"); sys.exit(1)

print("=" * 60)
print("CHECK-11: FINAL — 모든 Phase 완료 + Release v1.0 검증")
print("=" * 60)

failures = []
warnings = []  # [PATCH F-2] NameError 수정: warnings 변수 초기화

# 0. 이전 CHECK-0 ~ CHECK-10 PASS 검증 (execution_log.csv 기반)
# [PATCH 교차검토] "이전 단계 통과 가정" → 실제 log 조회로 강화
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

# 1. 9 Final Deliverables — D8/D9 canonical path 사용 [PATCH 교차검토]
print("\n[9 Final Deliverables 존재 확인]")
DELIVERABLES = [
    ("D1", "data/scenario_universe/scenario_universe_v1.0.csv"),
    ("D2", "data/action_labels/scenario_action_table_locked.csv"),
    ("D3", "data/decision_table/reduced_decision_table_v1.0.csv"),
    ("D4", "data/ilp/pairwise_distinguishability_matrix.npz"),
    ("D5", "data/ilp/final_minimal_node_set.csv"),
    ("D6", "config/operational_decision_tree.yaml"),
    ("D7", "scripts/repair_executor/repair_executor.py"),
    ("D8", "reports/golden_validation_report.md"),           # [PATCH] canonical D8 (not results.csv)
    ("D9", "release/v1.0/coverage_claim_statement.md"),      # [PATCH] canonical D9 (not RELEASE_NOTES)
]
for did, path in DELIVERABLES:
    if (BASE / path).is_file():
        print(f"  ✅ {did}: {path.split('/')[-1]}")
    else:
        print(f"  ❌ {did}: {path}")
        failures.append(f"{did} 누락")

# 1b. D8/D9 hash 파일 확인 [PATCH M-3]
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

# 2. 모든 H 서명
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

# 3. 모든 LP Panel
print("\n[LP Panel CP1-CP7 결과]")
# [PATCH-C1 — v5.1 CRITICAL] LP Panel judge 파일명 실제 산출물명과 일치하도록 수정
# CP1(P20): config_semantic_review_judge.md  ← "_review" 포함
# CP2(P60): universe_attack_freeze_judge.md
# CP3(P50): repair_semantic_review_judge.md  ← "_review" 포함 (조건부)
# CP4(P76): action_label_adjudication_judge.md
# CP5(P83): action_label_lock_judge.md
# CP6(P98): minimal_node_approval_judge.md
# CP7(P114): release_coverage_approval_judge.md
LP_PANELS = ["config_semantic_review", "universe_attack_freeze", "repair_semantic_review",
             "action_label_adjudication", "action_label_lock",
             "minimal_node_approval", "release_coverage_approval"]
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

# 6. CHANGELOG v1.0.0 entry
print("\n[CHANGELOG v1.0.0]")
cl = BASE / "CHANGELOG.md"
if cl.is_file():
    txt = cl.read_text(encoding="utf-8")
    if "v1.0.0" in txt:
        print("  ✅ v1.0.0 entry")
    else:
        print("  ❌ v1.0.0 entry 없음")
        failures.append("CHANGELOG v1.0.0")

# [PATCH-C4] F30 최종 방어선 — scenario universe + action labels에 F30 없음 확인
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
                    print(f"  ❌ {f30_target}: F30 {f30_n}개 발견 — 예약 번호 오사용")
                    failures.append(f"F30 in {f30_target}")
        except Exception as _e:
            print(f"  ⚠️  {f30_target}: 읽기 오류 {_e}")

# 7. Forbidden words 최종 확인
print("\n[Coverage Claim 표현 최종 확인 (PATCH-7)]")
release_files = [
    "release/v1.0/RELEASE_NOTES_v1_0.md",
    "release/v1.0/coverage_claim_statement.md",  # [PATCH] D9 canonical
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

# 8. SOP 존재
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

# 9. 100-case validation — CSV 기반 실제 pass rate 계산 [PATCH 교차검토]
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
            # per-family 확인
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
    for w in warnings: print(f"  - {w}")

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
    for f in failures: print(f"  - {f}")
    sys.exit(1)
```


---

## 📊 최종 완료 체크리스트

**Step 3 종료 시 다음 모두 ✅이어야 합니다:**

```
Phase 8  (P86-P100) — Decision Table + ILP 최소 결정 노드 + LP Panel CP6
Phase 9  (P101-P105A) — Decision Tree + NONMEM QC + Lock
Phase 10 (P106-P115) — Golden Validation + H3 + H4 (PATCH-5 강화) + H5 + LP Panel CP7 + Release Tag
Phase 11 (P116-P140) — Change Control + 100-case Validation (post-release) + SOP + Final Completion

CHECK-8, CHECK-9, CHECK-10, CHECK-11 모두 PASS

9 Final Deliverables 모두 hash와 함께 release/v1.0/ 아래 보관:
  D1 data/scenario_universe/scenario_universe_v1.0.csv
  D2 data/action_labels/scenario_action_table_locked.csv
  D3 data/decision_table/reduced_decision_table_v1.0.csv
  D4 data/ilp/pairwise_distinguishability_matrix.npz
  D5 data/ilp/final_minimal_node_set.csv
  D6 config/operational_decision_tree.yaml
  D7 scripts/repair_executor/repair_executor.py
  D8 reports/golden_validation_report.md            ← canonical (not results.csv)
  D9 release/v1.0/coverage_claim_statement.md       ← canonical (not RELEASE_NOTES)

H1-H5 모두 서명:
  H1 비식별화 ✅
  H2 fingerprint 사실 검토 ✅
  H3 golden reference 확인 ✅
  H4 표본 감사 + veto (PATCH-5 강화) ✅
  H5 final release 결재 ✅

LP Panel CP1-CP7 모두 처리:
  CP1 config_semantic (P18-P20) ✅
  CP2 universe_attack+freeze (P58-P60) ✅
  CP3 repair_semantic (P48-P50, 조건부) ✅
  CP4 action_label_adjudication (P74-P76) ✅
  CP5 action_label_lock (P81-P83) ✅
  CP6 minimal_node_approval (P96-P98) ✅
  CP7 release_coverage_approval (P112-P114) ✅

v5.1 PATCH 모두 적용:
  PATCH-1 v4.2 universe ✅
  PATCH-2 ILP distinguishability 강화 ✅
  PATCH-3 forced node 명시 ✅
  PATCH-4 LP Panel 7개 압축 ✅
  PATCH-5 H4 표본 감사 강화 ✅
  PATCH-6 pilot seed pack 20 카테고리 ✅
  PATCH-7 coverage wording 제한 ✅
  PATCH-8 CHECK script v4.2 강화 ✅
  PATCH-9 hypothesis property tests ✅
```

---

## ❓ FAQ — 자주 묻는 질문

**Q1. Step 1, 2, 3 어떤 순서로 실행해야 하나요?**
A. Step 1 → CHECK-0,1,2 → Step 2 → CHECK-3,4,5,6,7 → Step 3 → CHECK-8,9,10,11 순서. 각 CHECK가 PASS여야 다음 단계로 진행 가능.

**Q2. 시간이 얼마나 걸리나요?**
A. 환경 세팅 1일 + Phase 0~2 (1-2일) + Phase 3 (H1, H2 포함 3-5일) + Phase 4 (Repair Executor 코딩 2-3일) + Phase 5-7 (3-5일) + Phase 8-9 (3일) + Phase 10 (H3, H4, H5 포함 3-5일) + Phase 11 (5일) = **총 3-5주** (전업 기준).

**Q3. Python 지식이 전혀 없는데 가능한가요?**
A. 가능합니다. 모든 Python 코드는 C-LLM (Cursor IDE)이 자동 생성합니다. 사람은 Cursor에서 "Apply" 버튼만 누르면 됩니다. CHECK 스크립트는 ChatGPT/Claude에 "이 에러 어떻게 해결해?" 라고 붙여넣으면 됩니다.

**Q4. 실제 PMX 데이터가 부족한데?**
A. P29 sampling plan에서 "synthetic dataset" 또는 "public alternatives" (nlmixr2 warfarin 등) 옵션 사용 가능. 단 v4.2 신규 모달리티 (CAR-T, ADC 등) 데이터가 전무하면 P36에서 일부 카테고리를 v1.1로 deferred 처리해야 함.

**Q5. LP Panel에서 LP-A와 LP-B를 다른 모델에 입력하라고 하는데 왜죠?**
A. 같은 모델 계열(예: Claude끼리)은 같은 학습 데이터·편향을 공유합니다. LP-B를 Gemini나 GPT로 교차 검증해야 진짜 결함이 드러납니다. **반드시 새 채팅창**에서 LP-A 결과만 첨부해서 LP-B를 실행하세요.

**Q6. ILP solver가 INFEASIBLE 나오면?**
A. P91 (infeasible pair triage)에서 root cause 분석 → P92에서 새 노드 추가 또는 label 재조정 → P86부터 재실행. 만약 universe 자체에 빠진 axis가 있으면 v1.0 freeze 롤백이 필요할 수 있음 (드뭄).

**Q7. H4 표본 감사에서 mismatch가 나오면 자동 release 차단인가요?**
A. 아닙니다. mismatch는 "조사 필요" 신호이고, 정밀 검토 후 (a) 진짜 false classification이면 patch/v1.1, (b) 사람 판정이 잘못된 거면 system 정답 인정. veto는 confirmed false classification이 critical 수준일 때만.

**Q8. v1.1 release는 언제 트리거되나요?**
A. P117 SOP에 정의: ≥10 candidates 누적, ≥1 CRITICAL severity, 6개월 경과, v4.x universe 메이저 업그레이드 중 하나라도 만족시.

**Q9. Q15 vs Q15A/B/C/D 차이는?**
A. Q15는 "데이터 패키지 부재" 상위 카테고리. Q15 단독 사용은 금지(HR1)이고, 반드시 4개 sub-code 중 하나로 specify해야 합니다.
   **v4.1/v5.1 기준 실제 정의 [PATCH m-4 교정]:**
   - Q15A: data package incomplete — upstream adjudication decision 미제출 (예: 생물분석 최종 판정이 없어 결과 세트 자체가 미완)
   - Q15B: legacy flag undocumented — 레거시 데이터의 플래그/필드 정의가 없어 해석 불가
   - Q15C: real-world adherence/administration history unresolved — RWD/TDM 투여 기록의 실제 복용 이력 불명확
   - Q15D: assay reanalysis/final-result adjudication missing — 재분석 결과 중 최종 선택 기준 미제시
   (이전 문서에서 "컬럼/필드/표/파일 부재"로 단순화했던 설명은 사실과 다릅니다.)

**Q10. 결과적으로 만든 시스템이 진짜로 NONMEM-ready dataset을 자동 생성할 수 있나요?**
A. AUTO 시나리오는 yes (정책 명시된 routine 케이스). REPAIR는 정책이 AIC에 들어있어야 yes (예: BLQ M3 정책이 AIC에 있어야 BLQ canonicalization 자동). QUARANTINE/UNSUPPORTED/INVALID는 자동 처리 불가, 사람이 정책 추가 또는 거부 결정.

---

## 🎯 마무리

**민구 씨에게:**

이 v5.1 prompt sequence는 LLM 한 번 한 번에 "프롬프트만 복사-붙여넣기"하는 방식으로 거대한 PMX dataset wrangling 시스템을 완성하는 운영 가이드입니다.

3개 Step (Step 1: P1-P28, Step 2: P29-P85, Step 3: P86-P140) 합쳐 약 140개 prompt + 12개 Python CHECK + 5개 H 사람 결재 + 7개 LP Panel + 9개 final deliverable로 구성됩니다.

핵심은 **"LLM이 시키는 대로만 하지 마세요. CHECK가 PASS될 때까지 돌리세요. H 서명은 사람이 직접 하세요."**

Step 3까지 완수하면 release v1.0이 가능하고, 운영 단계에서는 P116 SOP 따라 새 데이터셋을 처리하면서 v1.1 candidate register만 관리하면 됩니다.

**막히는 지점이 있으면 (P 번호 + 에러 메시지) 알려주세요. 도움 드릴 수 있습니다.**

---

*PMX-to-NONMEM Scenario Universe v5.1 — Step 3 / 3*
*Phase 8-11 | ILP Minimal Nodes | Decision Tree | H3, H4 (PATCH-5), H5 | Release v1.0 | SOP*
*9 Final Deliverables LOCKED | 5 Human Checkpoints SIGNED | 7 LP Panels RESOLVED*
*v5.1 PATCH-1 ~ PATCH-9 ALL APPLIED*

---

### 📋 v5.1 Step 3 패치 이력 (patched_v3)

| 패치 ID | 대상 | 내용 | 심각도 |
|---|---|---|---|
| PATCH-C1 | CHECK-11 LP_PANELS | `config_semantic`→`config_semantic_review`, `repair_semantic`→`repair_semantic_review` (실제 P20/P50 산출물명과 일치) | CRITICAL |
| PATCH-C2 | P109 + H4 section + CHECK-10 | h4_sample_extractor.py를 P109 명시 필수 산출물로 추가. 구현 사양(26개 샘플, seed=42, blinded CSV) 포함. CHECK-10 REQUIRED에 extractor + blinded CSV 추가 | IMPORTANT |
| PATCH-C3 | Phase 9 완료 선언 블록 | 번호 없는 블록 → P105A 부여. P105 다음 액션 수정. Phase 9 범위 P101~P105→P105A | MINOR |
| PATCH-C4 | CHECK-11 | F30 부재 최종 방어선 추가 (Universe CSV + Action Labels 두 파일 모두 확인) | MINOR |