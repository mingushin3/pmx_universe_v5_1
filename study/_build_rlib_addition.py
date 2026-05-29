"""
study/_build_rlib_addition.py
─────────────────────────────────────────────────────────────────────
r_code_library.json 보강 빌드 스크립트.

규칙 (CLAUDE.md v2.0):
  1. 기존 키의 value는 절대 변경하지 않는다 (deep-merge, 기존 우선).
  2. 새 키만 추가한다.
  3. 보강 대상 노드:
       Forced 보강:  N3, N4, N8        (N0/N1/N2/N5는 이미 풍부 → 손대지 않음)
       Optional 신규: N11, N13, N14, N17, N19, N20, N21, N22, N24, N25, N27, N29

실행:
  python3 study/_build_rlib_addition.py
출력:
  study/data/r_code_library.json (in-place 갱신)
  + 콘솔에 변경 요약 (기존 키 보존 + 신규 키 목록)
검증:
  python3 study/_verify_rlib_addition.py
"""

from __future__ import annotations
import json
import pathlib
import sys
import textwrap
from copy import deepcopy

ROOT = pathlib.Path(__file__).resolve().parent
RLIB_PATH = ROOT / "data" / "r_code_library.json"


# ═══════════════════════════════════════════════════════════════════
# 보강 데이터 정의
#   - 각 노드는 CLAUDE.md Phase 3 형식의 신규 필드만 정의한다.
#   - 기존에 동일 키가 있으면 deep-merge가 기존 값을 우선시한다.
# ═══════════════════════════════════════════════════════════════════

ADDITIONS: dict[str, dict] = {}

# ─── N3 ────────────────────────────────────────────────────────────
ADDITIONS["N3"] = {
    "persona_intro": "용량 정보는 PK 모델링의 '입력'이야. 입력이 흐릿하면 출력도 흐릿해 — 이 단계에서 단위·기준·재구성 정책을 먼저 못박아.",
    "context_card": {
        "situation": "투여 이벤트(EVID=1)에 AMT 값이 모두 들어 있고, 단위와 재구성 규칙(체중 기반·BSA 기반·titration·loading)이 AIC에 선언되어 있는지 확인합니다.",
        "why_important": "AMT가 빠진 행을 그냥 0으로 두면 NONMEM은 '투여 안 함'으로 해석해서 노출(exposure)이 과소 추정됩니다. mg/kg 단위인데 변환을 안 하면 70배 작은 용량으로 모델이 fit되어 CL이 70배 커지는 침묵 오류가 납니다."
    },
    "data_state_before": {
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>EVID</th><th>DOSE_PER_KG</th><th>WT</th><th>AMT</th></tr></thead><tbody><tr><td>1</td><td>0</td><td>1</td><td>5</td><td>70</td><td class=\"bad\">NA</td></tr><tr><td>1</td><td>2</td><td>0</td><td>—</td><td>70</td><td>0</td></tr><tr><td>2</td><td>0</td><td>1</td><td>5</td><td>60</td><td class=\"bad\">NA</td></tr></tbody></table>",
        "problem_cells": ["EVID=1 인데 AMT=NA — mg/kg×WT 재구성이 빠져 있음"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>EVID</th><th>DOSE_PER_KG</th><th>WT</th><th>AMT</th></tr></thead><tbody><tr><td>1</td><td>0</td><td>1</td><td>5</td><td>70</td><td class=\"good\">350</td></tr><tr><td>1</td><td>2</td><td>0</td><td>—</td><td>70</td><td>0</td></tr><tr><td>2</td><td>0</td><td>1</td><td>5</td><td>60</td><td class=\"good\">300</td></tr></tbody></table>",
        "changed_cells": ["mg/kg × WT → 실제 mg AMT 계산 (정책: reconstruct_dose_weight_policy)"]
    },
    "best_practice_tips": [
        "재구성 정책이 AIC에 없으면 무조건 멈춰라 — 정책 없이 환산하면 분석자마다 다른 결과가 나온다.",
        "if_else(EVID == 1, AMT, 0) 패턴은 NONMEM 규약(관측 행은 AMT=0)을 보장하는 안전 장치다.",
        "AMT 단위가 mg인지 μg인지 AIC dose_unit에서 확인 — 1000배 오차가 가장 흔한 침묵 버그."
    ]
}

# ─── N4 ────────────────────────────────────────────────────────────
ADDITIONS["N4"] = {
    "persona_intro": "관측치(DV)는 모델이 'fit'할 대상이야. DV 컬럼이 비어 있거나 단위가 흐리면 fit 자체가 무의미해져.",
    "context_card": {
        "situation": "DV(또는 CONC) 컬럼이 존재하고, BLQ 행에는 LLOQ가 함께 선언되어 있으며, 다중 분석물질(ADC·Bispecific·CAR-T) modality라면 analyte_role 정책이 있는지 확인합니다.",
        "why_important": "ADC에서 TAb·cADC·payload를 같은 CMT로 합치면 노출-반응 곡선이 완전히 왜곡됩니다. immunogenicity는 양성판정 규칙(positivity_adjudication_rule) 없이는 ADA 양성/음성 분류가 매번 달라져 결과 재현이 불가능합니다."
    },
    "data_state_before": {
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>ANALYTE</th><th>DV</th><th>CMT</th></tr></thead><tbody><tr><td>1</td><td>1</td><td>TOTAL_ANTIBODY</td><td>25.3</td><td class=\"bad\">2</td></tr><tr><td>1</td><td>1</td><td>CONJUGATED_ADC</td><td>18.7</td><td class=\"bad\">2</td></tr><tr><td>1</td><td>1</td><td>UNCONJUGATED_PAYLOAD</td><td>0.4</td><td class=\"bad\">2</td></tr></tbody></table>",
        "problem_cells": ["ADC 3종 분석물질이 모두 CMT=2로 합쳐짐 — analyte_role_policy 누락"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>ANALYTE</th><th>DV</th><th>CMT</th></tr></thead><tbody><tr><td>1</td><td>1</td><td>TOTAL_ANTIBODY</td><td>25.3</td><td class=\"good\">2</td></tr><tr><td>1</td><td>1</td><td>CONJUGATED_ADC</td><td>18.7</td><td class=\"good\">3</td></tr><tr><td>1</td><td>1</td><td>UNCONJUGATED_PAYLOAD</td><td>0.4</td><td class=\"good\">4</td></tr></tbody></table>",
        "changed_cells": ["analyte_role_policy에 따라 TAb=2 / cADC=3 / payload=4로 분리"]
    },
    "best_practice_tips": [
        "DV가 0이 아니라 NA인 행은 'BLQ가 아닌 누락'일 수 있어 — BLQ 컬럼과 함께 검사하라.",
        "다중 분석물질은 CMT 번호 정책을 코드 상수가 아닌 AIC 정책으로 받아라. 코드에 박으면 다음 study에서 또 박아야 한다.",
        "case_when()으로 분기하면 새 analyte_role 추가 시 한 줄만 늘어난다 — ifelse 중첩보다 안전하다."
    ]
}

# ─── N8 ────────────────────────────────────────────────────────────
ADDITIONS["N8"] = {
    "persona_intro": "이건 '계약서 마지막 한 페이지' 같은 거야. 모든 정책이 선언됐는지 한 번 더 점검해서 partial declaration으로 인한 침묵 오류를 막아.",
    "context_card": {
        "situation": "지금까지 N0~N5까지 통과한 데이터에 대해, 앞으로 적용될 action_sequence가 요구하는 모든 정책(blq_handling, dose 재구성, dyad linkage 등)이 AIC에 빠짐없이 선언되어 있는지 일괄 점검합니다.",
        "why_important": "정책 하나가 누락된 채로 그 다음 변환에 들어가면, R 코드는 NULL을 기본값으로 받아 조용히 잘못된 변환을 수행합니다. v5.1에서 새로 추가된 게이트(PATCH-3)로, 이 검사가 없으면 false-REPAIR가 가장 많이 발생합니다."
    },
    "data_state_before": {
        "stage": "Stage 7 — N0~N5 통과 완료, 이제 다음 변환에 필요한 정책 묶음 확인",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>required_policy</th><th>declared in AIC?</th></tr></thead><tbody><tr><td>blq_handling_policy</td><td class=\"good\">M3</td></tr><tr><td>lloq</td><td class=\"good\">1.0</td></tr><tr><td>reconstruct_dose_weight_policy</td><td class=\"bad\">NULL</td></tr><tr><td>analyte_role_policy</td><td class=\"bad\">NULL</td></tr></tbody></table>",
        "problem_cells": ["체중 기반 용량 정책 누락", "분석물질 역할 정책 누락 → Q15A 격리"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>required_policy</th><th>declared in AIC?</th></tr></thead><tbody><tr><td>blq_handling_policy</td><td class=\"good\">M3</td></tr><tr><td>lloq</td><td class=\"good\">1.0</td></tr><tr><td>reconstruct_dose_weight_policy</td><td class=\"good\">per_kg_to_mg</td></tr><tr><td>analyte_role_policy</td><td class=\"good\">adc_tab_cadc_payload</td></tr></tbody></table>",
        "changed_cells": ["분석자가 누락 정책 2개를 AIC에 추가 선언 → 모든 정책 충족"]
    },
    "sample_transform_before": "필요 정책: [blq_handling_policy, lloq, reconstruct_dose_weight_policy, analyte_role_policy]\nAIC 선언: [blq_handling_policy=M3, lloq=1.0]\n→ 누락 2개 → Q15A 격리",
    "sample_transform_after": "필요 정책: [blq_handling_policy, lloq, reconstruct_dose_weight_policy, analyte_role_policy]\nAIC 선언: [blq_handling_policy=M3, lloq=1.0, reconstruct_dose_weight_policy=..., analyte_role_policy=...]\n→ 모두 충족 → 다음 분기 진행",
    "best_practice_tips": [
        "required_policy를 함수 정의에 메타데이터로 박아두면 자동 점검 가능 (function_library 패턴).",
        "Q15A는 '데이터 패키지 불완전' 신호 — 의뢰자에게 추가 정책 회신을 요청해야 한다.",
        "이 게이트가 통과되면 이후 변환은 NULL 분기 처리를 줄일 수 있어 코드가 훨씬 단순해진다."
    ]
}

# ─── N11 ───────────────────────────────────────────────────────────
ADDITIONS["N11"] = {
    "persona_intro": "산모-영아 PK는 '두 사람을 한 시간축에 두는' 특수 분기야. dyad 키 + 분만 시점 anchor가 핵심.",
    "context_card": {
        "situation": "endpoint_data_type이 MATERNAL_INFANT_PK 또는 MILK_PK인지 분기합니다. YES면 dyad linkage + postpartum anchor + (모유의 경우) milk matrix LLOQ가 추가로 필요합니다.",
        "why_important": "엄마와 아기의 ID를 따로 둔 채 합치면 group_by(ID)가 분리되어 짝(dyad) 통계가 사라집니다. postpartum day가 없으면 '분만 후 며칠'이라는 임상적으로 가장 중요한 시간축을 잃습니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — N0~N5 통과, modality/endpoint별 추가 분기 시작",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>ROLE</th><th>TIME</th><th>DV</th></tr></thead><tbody><tr><td>M01</td><td>MOTHER</td><td>2.0</td><td>45.2</td></tr><tr><td>I01</td><td>INFANT</td><td>2.5</td><td>3.1</td></tr><tr><td colspan=\"4\" class=\"bad\">↑ 두 ID가 같은 짝(dyad)임을 표현하는 키가 없음</td></tr></tbody></table>",
        "problem_cells": ["M01 ↔ I01 dyad 연결 누락"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>ROLE</th><th>DYAD_KEY</th><th>TIME_POSTPARTUM</th><th>DV</th></tr></thead><tbody><tr><td>M01</td><td>MOTHER</td><td class=\"good\">D01</td><td class=\"good\">3.2</td><td>45.2</td></tr><tr><td>I01</td><td>INFANT</td><td class=\"good\">D01</td><td class=\"good\">3.2</td><td>3.1</td></tr></tbody></table>",
        "changed_cells": ["DYAD_KEY로 모자 짝 묶기", "분만 시각 anchor 기준 TIME_POSTPARTUM 일수 계산"]
    },
    "best_practice_tips": [
        "DYAD_KEY는 NONMEM ID와 별도 컬럼 — group_by에서 ID/DYAD_KEY 둘 다 사용 가능.",
        "postpartum anchor는 day 단위가 자연스러움 (분만 후 1일/7일/30일 단위 임상 의사결정).",
        "MILK_PK는 매트릭스가 모유 → LLOQ가 혈장과 다르므로 milk_matrix_lloq_policy 별도 필요."
    ]
}

# ─── N13 ───────────────────────────────────────────────────────────
ADDITIONS["N13"] = {
    "persona_intro": "BLQ 표준화 함수가 시퀀스에 들어 있는지로 '농도 BLQ 경로'와 '세포 BLQ 경로'를 가르는 분기야.",
    "context_card": {
        "situation": "이번 시나리오의 action_sequence에 canonicalize_blq 또는 canonicalize_cellular_blq가 포함되어 있는지 확인합니다. 포함되어 있으면 BLQ-처리 경로(M1/M3/M4), 없으면 BLQ 없는 데이터로 간주.",
        "why_important": "이 분기를 잘못 가르면 BLQ가 있는데 처리 함수가 안 붙거나, 세포 BLQ에 농도 BLQ 함수를 붙여 LLOQ 정의가 어긋납니다. 결과적으로 likelihood 계산이 틀려 PK 파라미터가 bias됩니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — N5 BLQ 정책 적용 완료 후, action_sequence 종류 분기 시점",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>action_sequence (입력)</th></tr></thead><tbody><tr><td>parse_source → map_subject_id → derive_time_elapsed → <span class=\"bad\">??</span> → export_nonmem_ready</td></tr></tbody></table>",
        "problem_cells": ["BLQ 처리 함수가 시퀀스 어디에 들어갈지 결정 전"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>분기</th><th>action_sequence 형태</th></tr></thead><tbody><tr><td class=\"good\">YES</td><td>… → <span class=\"good\">canonicalize_blq(M3)</span> → assign_evid → export</td></tr><tr><td>NO</td><td>… → assign_evid → export (BLQ 없음)</td></tr></tbody></table>",
        "changed_cells": ["YES 경로: canonicalize_blq 또는 canonicalize_cellular_blq 호출 포함"]
    },
    "r_code_check": "# ── N13 ── action_sequence에 BLQ 표준화 함수 포함 여부\n# 농도 BLQ(canonicalize_blq) 또는 세포 BLQ(canonicalize_cellular_blq) 중 하나만\n# 있어도 YES. 둘 다 있는 경우는 ADC + cellular 같은 복합 시나리오.\n\ncheck_n13_blq_in_sequence <- function(action_seq) {\n  blq_fns <- c(\"canonicalize_blq\", \"canonicalize_cellular_blq\")\n  any(blq_fns %in% action_seq)\n}",
    "r_code_pass": "# YES — BLQ 표준화 단계를 시퀀스에 끼워넣는다 (실제 호출은 N5 단계에서)\nif (check_n13_blq_in_sequence(action_seq)) {\n  message(\"✓ N13 YES: BLQ 처리 단계 포함됨 (\",\n          paste(intersect(action_seq, c(\"canonicalize_blq\",\"canonicalize_cellular_blq\")),\n                collapse = \", \"), \")\")\n}\n# ✅ %in% vs grepl: 정확한 함수명 매칭은 %in%이 안전 — grepl은 substring 매칭이라 오탐 위험.",
    "best_practice_tips": [
        "BLQ 함수가 둘 다 있으면 분석자에게 '이중 BLQ 처리 의도인지' 확인 — 보통은 실수.",
        "action_sequence는 character vector — list-column에 저장해두면 purrr::map_lgl로 일괄 점검 가능.",
        "%in%은 함수명을 코드에 박지 말고 상수 벡터로 분리 — 새 BLQ 변형이 생겨도 한 곳만 수정."
    ]
}

# ─── N14 ───────────────────────────────────────────────────────────
ADDITIONS["N14"] = {
    "persona_intro": "용량 재구성 함수가 시퀀스에 있느냐 없느냐가 AUTO vs REPAIR를 가르는 가장 흔한 분기야. 체중·BSA·titration·loading·infusion·ADDL conflict 6종 중 하나라도 있으면 YES.",
    "context_card": {
        "situation": "action_sequence에 용량 재구성 계열 함수(reconstruct_dose_weight/bsa/titration, expand_addl_ii, resolve_addl_actual_conflict 등)가 포함되어 있는지 확인합니다.",
        "why_important": "재구성 함수가 누락되면 AMT가 mg/kg 단위 그대로 NONMEM에 들어가서 70배 작은 용량으로 모델이 fit되거나, ADDL을 펼치지 않아 다회투여 누락이 발생합니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — N3 용량 정책 점검 후, 실제 재구성 단계 포함 여부 분기",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>action_sequence (입력)</th><th>AIC dose_type</th></tr></thead><tbody><tr><td>parse_source → map_subject_id → … → export</td><td class=\"bad\">WEIGHT_BASED</td></tr></tbody></table>",
        "problem_cells": ["dose_type=WEIGHT_BASED인데 reconstruct_dose_weight가 시퀀스에 없음"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>분기</th><th>action_sequence</th></tr></thead><tbody><tr><td class=\"good\">YES</td><td>… → <span class=\"good\">reconstruct_dose_weight</span> → assign_evid → export</td></tr><tr><td>NO</td><td>… → assign_evid → export (재구성 불필요)</td></tr></tbody></table>",
        "changed_cells": ["YES 경로: 6종 재구성 함수 중 1개 이상 호출"]
    },
    "r_code_check_v2": "# ── N14 ── 용량 재구성 함수 포함 여부 (확장판)\n# stringr::str_detect 대신 정확한 패턴 매칭으로 오탐 방지.\n\ncheck_n14_reconstruct_dose <- function(action_seq) {\n  recon_patterns <- c(\n    \"^reconstruct_dose_\",          # weight / bsa / titration / loading_maintenance\n    \"^reconstruct_infusion_\",       # stop_restart\n    \"^expand_addl_ii$\",             # ADDL/II 펼치기\n    \"^resolve_addl_actual_conflict$\" # ADDL/실투여 충돌 해결\n  )\n  any(purrr::map_lgl(action_seq, \\(fn)\n    any(stringr::str_detect(fn, recon_patterns))))\n}",
    "best_practice_tips": [
        "재구성 함수는 dose_type별로 다름 — AIC$dose_type과 시퀀스가 일관되는지 교차검증하라.",
        "^…$ 앵커를 쓰면 reconstruct_dose_weight_v2 같은 변형도 정확히 매칭 가능.",
        "ADDL을 펼치지 않은 채 NONMEM에 넘기면 다회투여가 1회 투여로 인식되어 노출이 N분의 1로 줄어든다."
    ]
}

# ─── N17 ───────────────────────────────────────────────────────────
ADDITIONS["N17"] = {
    "persona_intro": "시간축이 단순 경과시간(elapsed)인지, 분만 anchor(postpartum)인지 — 임신/수유 경로를 가르는 분기야.",
    "context_card": {
        "situation": "action_sequence에 derive_time_postpartum_anchor 또는 derive_time_elapsed가 포함되어 있는지 확인합니다.",
        "why_important": "분만 anchor가 없으면 산후 며칠/몇 주 같은 임상적으로 가장 의미 있는 시간축이 사라지고, 단순 elapsed time만으로는 'baseline까지 회복 시점' 같은 질문에 답할 수 없습니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — N2 시간 축 검증 후, 추가 anchor 필요 여부 분기",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>ATIME</th><th>TIME (elapsed)</th><th>TIME_POSTPARTUM</th></tr></thead><tbody><tr><td>M01</td><td>2025-01-15 08:00</td><td>72.0</td><td class=\"bad\">—</td></tr></tbody></table>",
        "problem_cells": ["MATERNAL_INFANT_PK인데 TIME_POSTPARTUM 컬럼 누락"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>ATIME</th><th>TIME</th><th>TIME_POSTPARTUM</th></tr></thead><tbody><tr><td>M01</td><td>2025-01-15 08:00</td><td>72.0</td><td class=\"good\">3.0 days</td></tr></tbody></table>",
        "changed_cells": ["분만 anchor 기준 산후 일수 계산 → 임상 해석 가능"]
    },
    "r_code_check": "# ── N17 ── 시간 anchor 함수 포함 여부\ncheck_n17_time_anchor <- function(action_seq) {\n  anchor_fns <- c(\"derive_time_postpartum_anchor\", \"derive_time_elapsed\")\n  any(anchor_fns %in% action_seq)\n}",
    "r_code_pass": "# YES — 분만 시각 데이터가 있으면 postpartum anchor 적용\nif (check_n17_time_anchor(action_seq) &&\n    \"derive_time_postpartum_anchor\" %in% action_seq) {\n  df <- df |> derive_time_postpartum_anchor(delivery_anchor_df)\n  message(\"✓ N17: postpartum 일수 컬럼 생성 완료\")\n}",
    "best_practice_tips": [
        "postpartum anchor는 환자별 분만 시각(별도 테이블)을 left_join으로 붙인 뒤 difftime으로 계산.",
        "시간축은 분석 목적에 따라 2개 이상 공존 가능 (TIME=경과시간 + TIME_POSTPARTUM=산후일수).",
        "lubridate::difftime의 units='days' 옵션을 명시하지 않으면 R 세션 로케일에 따라 단위가 바뀔 수 있다."
    ]
}

# ─── N19 ───────────────────────────────────────────────────────────
ADDITIONS["N19"] = {
    "persona_intro": "공변량(WT, AGE, SEX, CRCL 등)을 모델에 넣을지 분기하는 단계야. 기저/시간변동/제품단위(CAR-T) 어느 형태든 attach_* 함수가 있으면 YES.",
    "context_card": {
        "situation": "action_sequence에 attach_covariate_baseline / attach_covariate_time_varying / attach_covariate_external / attach_covariate_product_level 또는 attach_dyad_linkage가 포함되어 있는지 확인합니다.",
        "why_important": "공변량 없이 fit한 모델은 'population mean' 만 줄 뿐 개체간 변이를 설명하지 못합니다. CAR-T 같이 제품 로트별 차이가 큰 경우 lot 공변량을 빠뜨리면 random effect가 과대해집니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — 기본 NONMEM 컬럼(ID/TIME/AMT/DV/EVID/CMT/MDV) 확정 후, 공변량 부착 여부",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>AMT</th><th>DV</th><th>WT</th><th>AGE</th></tr></thead><tbody><tr><td>1</td><td>0</td><td>350</td><td>0</td><td class=\"bad\">—</td><td class=\"bad\">—</td></tr><tr><td>1</td><td>2</td><td>0</td><td>45.2</td><td class=\"bad\">—</td><td class=\"bad\">—</td></tr></tbody></table>",
        "problem_cells": ["WT/AGE 컬럼 부재 — baseline 테이블이 별도로 존재하지만 부착되지 않음"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>AMT</th><th>DV</th><th>WT</th><th>AGE</th></tr></thead><tbody><tr><td>1</td><td>0</td><td>350</td><td>0</td><td class=\"good\">70</td><td class=\"good\">45</td></tr><tr><td>1</td><td>2</td><td>0</td><td>45.2</td><td class=\"good\">70</td><td class=\"good\">45</td></tr></tbody></table>",
        "changed_cells": ["baseline 테이블에서 WT, AGE를 ID 기준 left_join으로 부착 (broadcast)"]
    },
    "r_code_check_v2": "# ── N19 ── 공변량 부착 함수 포함 (확장판: 4종 + dyad)\ncheck_n19_covariate_attach <- function(action_seq) {\n  cov_patterns <- c(\n    \"^attach_covariate_baseline$\",\n    \"^attach_covariate_time_varying$\",\n    \"^attach_covariate_external$\",\n    \"^attach_covariate_product_level$\",\n    \"^attach_dyad_linkage$\"\n  )\n  any(purrr::map_lgl(action_seq, \\(fn)\n    any(stringr::str_detect(fn, cov_patterns))))\n}",
    "best_practice_tips": [
        "baseline 공변량은 환자당 한 번 측정 → left_join + ID로 broadcast.",
        "시간변동 공변량은 LOCF 또는 linear interpolation 정책을 AIC에 명시 — 임의 선택 금지.",
        "제품 단위 공변량(CAR-T lot)은 ID가 아니라 LOT_ID로 join — '역방향' key join 패턴이다."
    ]
}

# ─── N20 ───────────────────────────────────────────────────────────
ADDITIONS["N20"] = {
    "persona_intro": "이건 격리 사유를 가르는 분기야. A5가 'BIOANALYTICAL-FINAL-FLAG-MISSING'이면 Q15A(상류 미제출), 아니면 다른 Q-code로 갈림.",
    "context_card": {
        "situation": "A5 축 상태가 BIOANALYTICAL-FINAL-FLAG-MISSING인지 확인합니다. YES면 생체분석 lab의 최종 확정 플래그가 아직 안 붙은 상태 — 데이터 패키지 자체가 미완성.",
        "why_important": "이 분기 없이 모든 격리를 Q01(BLQ 정책 누락)로 분류하면 의뢰자에게 잘못된 회신을 하게 됩니다. Q15A는 'lab finalization 대기'라는 명확한 다음 행동을 지시합니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — 격리 사유 세분화 단계 (terminal_state=QUARANTINE 라벨 분기)",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>A5_state</th><th>준비된 Q-code</th></tr></thead><tbody><tr><td>BIOANALYTICAL-FINAL-FLAG-MISSING</td><td class=\"bad\">Q01 (잘못)</td></tr></tbody></table>",
        "problem_cells": ["A5 분기 없이 Q01로 단일 분류 → 회신 방향 잘못"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>A5_state</th><th>Q-code</th></tr></thead><tbody><tr><td>BIOANALYTICAL-FINAL-FLAG-MISSING</td><td class=\"good\">Q15A (lab 최종 확정 대기)</td></tr><tr><td>BLQ-NO-POLICY</td><td class=\"good\">Q01 (BLQ 정책 추가 요청)</td></tr></tbody></table>",
        "changed_cells": ["BIOANALYTICAL-FINAL-FLAG-MISSING → Q15A로 분리"]
    },
    "r_code_check": "# ── N20 ── A5가 BIOANALYTICAL-FINAL-FLAG-MISSING인지 분기\ncheck_n20_bioanalytical_flag <- function(scenario) {\n  identical(scenario$A5_state, \"BIOANALYTICAL-FINAL-FLAG-MISSING\")\n}",
    "r_code_pass": "# YES — Q15A 격리, 의뢰자에게 lab finalization 회신 요청\nif (check_n20_bioanalytical_flag(scenario)) {\n  log_quarantine(node = \"N20\", q_code = \"Q15A\",\n                 reason = \"생체분석 최종 확정 플래그 미수신\")\n  message(\"⚠ Q15A 격리: 의뢰자에게 lab finalization 회신 요청\")\n}",
    "best_practice_tips": [
        "Q-code는 단순 라벨이 아니라 '다음 행동 지시문' — 분기를 잘게 쪼개야 회신이 정확해진다.",
        "identical()은 NA-safe하고 vector 길이까지 본다 — `==`보다 안전.",
        "격리 로그는 audit trail용으로 별도 테이블에 적재 (분석 끝나도 추적 가능)."
    ]
}

# ─── N21 ───────────────────────────────────────────────────────────
ADDITIONS["N21"] = {
    "persona_intro": "A8이 다중-CMT 계열(MULTI/DDI/METABOLITE)이냐를 묻는 분기야. multi-analyte 경로 진입 게이트.",
    "context_card": {
        "situation": "A8 축 상태가 MULTI-CMT-DEFINED, DDI-VICTIM-PERPETRATOR, METABOLITE-DEFINED 중 하나인지 확인합니다.",
        "why_important": "단일 CMT 모델로 multi-analyte 데이터를 fit하면 모든 분석물질의 농도가 합쳐져 PK 파라미터(CL, V)가 평균화됩니다. DDI 가해자/피해자 농도가 섞이면 상호작용 자체를 모델링할 수 없습니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — A8 상태 기반 분기",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>A8_state</th><th>다음 처리</th></tr></thead><tbody><tr><td>MULTI-CMT-DEFINED</td><td class=\"bad\">미분기 → 단일 CMT 가정</td></tr></tbody></table>",
        "problem_cells": ["multi-CMT가 필요한데 분기 없이 단일 CMT로 진행"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>A8_state</th><th>분기</th></tr></thead><tbody><tr><td>MULTI-CMT-DEFINED</td><td class=\"good\">YES → assign_cmt_multi 호출</td></tr><tr><td>DDI-VICTIM-PERPETRATOR</td><td class=\"good\">YES → assign_cmt_ddi_victim_perpetrator</td></tr><tr><td>METABOLITE-DEFINED</td><td class=\"good\">YES → assign_cmt_multi (parent+metabolite)</td></tr><tr><td>SINGLE-ANALYTE</td><td>NO → assign_cmt_single</td></tr></tbody></table>",
        "changed_cells": ["A8 상태별로 CMT 할당 함수 분기 결정"]
    },
    "r_code_check": "# ── N21 ── A8이 multi-CMT 계열인지\ncheck_n21_multi_cmt_class <- function(scenario) {\n  multi_states <- c(\"MULTI-CMT-DEFINED\",\n                    \"DDI-VICTIM-PERPETRATOR\",\n                    \"METABOLITE-DEFINED\")\n  scenario$A8_state %in% multi_states\n}",
    "best_practice_tips": [
        "A8 분기는 N22(DDI 특수), N26(analyte_role) 등 후속 게이트의 진입 조건 — 잘못 분기하면 줄줄이 영향.",
        "multi-CMT 정책은 cmt_map(c(PARENT=2, METABOLITE=3))을 AIC에서 받아 코드와 분리.",
        "%in% 우측 벡터를 상수로 빼두면 새 상태(예: ENZYME-METABOLITE) 추가 시 한 곳만 수정."
    ]
}

# ─── N22 ───────────────────────────────────────────────────────────
ADDITIONS["N22"] = {
    "persona_intro": "DDI 시나리오 중에서도 '피해자+가해자 둘 다 측정'인 경우를 가르는 분기야. 두 약물 모두 CMT 4개(흡수×2, 중심×2) 할당 필요.",
    "context_card": {
        "situation": "A8 축이 DDI-VICTIM-PERPETRATOR인지 확인합니다. YES면 두 약물 모두 PK를 모델링하므로 assign_cmt_ddi_victim_perpetrator로 4-CMT 할당이 필요합니다.",
        "why_important": "DDI 가해자만 noncompartmental로 처리하고 피해자만 PK 모델을 fit하면 가해자의 시간변동 노출을 covariate로 정확히 반영할 수 없습니다. 두 약물을 함께 모델링해야 PBPK-수준의 상호작용 분석이 가능합니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — N21에서 multi-CMT 진입 후, DDI 특수 분기",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>ANALYTE</th><th>EVID</th><th>CMT</th></tr></thead><tbody><tr><td>1</td><td>VICTIM</td><td>1</td><td class=\"bad\">1</td></tr><tr><td>1</td><td>PERPETRATOR</td><td>1</td><td class=\"bad\">1</td></tr><tr><td>1</td><td>VICTIM</td><td>0</td><td class=\"bad\">2</td></tr><tr><td>1</td><td>PERPETRATOR</td><td>0</td><td class=\"bad\">2</td></tr></tbody></table>",
        "problem_cells": ["두 약물의 흡수·중심이 같은 CMT 번호 사용 → 모델 식별 불가"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>ANALYTE</th><th>EVID</th><th>CMT</th></tr></thead><tbody><tr><td>1</td><td>VICTIM</td><td>1</td><td class=\"good\">1 (피해자 흡수)</td></tr><tr><td>1</td><td>VICTIM</td><td>0</td><td class=\"good\">2 (피해자 중심)</td></tr><tr><td>1</td><td>PERPETRATOR</td><td>1</td><td class=\"good\">3 (가해자 흡수)</td></tr><tr><td>1</td><td>PERPETRATOR</td><td>0</td><td class=\"good\">4 (가해자 중심)</td></tr></tbody></table>",
        "changed_cells": ["case_when으로 ANALYTE × EVID 조합별 CMT 4개 분리"]
    },
    "r_code_check": "# ── N22 ── DDI 피해자+가해자?\ncheck_n22_ddi_dual <- function(scenario) {\n  identical(scenario$A8_state, \"DDI-VICTIM-PERPETRATOR\")\n}",
    "best_practice_tips": [
        "DDI dual은 데이터셋 행 수가 일반 PK의 2배 — group_by(ID, ANALYTE) 패턴이 필수.",
        "CMT 번호는 NONMEM control stream의 $MODEL과 일치해야 함 — 코드 상수보다 AIC 정책으로.",
        "case_when 분기 4개는 ANALYTE × EVID 곱 — 새 ANALYTE 추가 시 분기 2개씩 늘어남."
    ]
}

# ─── N24 ───────────────────────────────────────────────────────────
ADDITIONS["N24"] = {
    "persona_intro": "기록상 ADDL로 계획된 다회투여와 실제 시각 기록이 충돌하는 경우를 가르는 분기야. 정책 없으면 격리(Q14).",
    "context_card": {
        "situation": "A4 축 상태가 ADDL-ACTUAL-CONFLICT인지 확인합니다. YES면 resolve_addl_actual_conflict 함수가 시퀀스에 필요합니다.",
        "why_important": "ADDL은 '계획된 다회투여'이고 실제 시각은 '실제 일어난 투여'입니다. 계획과 실제가 다른데 둘 다 살리면 같은 환자에게 같은 시점 두 번 투여가 발생해 노출이 2배 됩니다. 정책 없이 둘 중 하나를 임의로 고르면 분석마다 결과가 달라집니다."
    },
    "data_state_before": {
        "stage": "Stage 8 — A4 상태 기반 분기",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>AMT</th><th>ADDL</th><th>II</th><th>출처</th></tr></thead><tbody><tr><td>1</td><td>0</td><td>100</td><td>6</td><td>24</td><td class=\"bad\">계획</td></tr><tr><td>1</td><td>0</td><td>100</td><td>0</td><td>—</td><td class=\"bad\">실제 day 0</td></tr><tr><td>1</td><td>26</td><td>100</td><td>0</td><td>—</td><td class=\"bad\">실제 day 1.08 (계획은 24)</td></tr></tbody></table>",
        "problem_cells": ["ADDL 펼친 결과와 실제 시각 기록이 충돌 (26h vs 24h)"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>AMT</th><th>출처 정책</th></tr></thead><tbody><tr><td>1</td><td>0</td><td>100</td><td class=\"good\">실제 우선 (actual_wins)</td></tr><tr><td>1</td><td>26</td><td>100</td><td class=\"good\">실제 우선</td></tr></tbody></table>",
        "changed_cells": ["AIC의 addl_actual_conflict_policy=actual_wins에 따라 실제 기록 채택, ADDL 행 제거"]
    },
    "r_code_check": "# ── N24 ── A4가 ADDL-ACTUAL-CONFLICT인지\ncheck_n24_addl_conflict <- function(scenario) {\n  identical(scenario$A4_state, \"ADDL-ACTUAL-CONFLICT\")\n}",
    "r_code_pass": "# YES — resolve_addl_actual_conflict를 시퀀스에 끼워넣어 정책에 따라 선택\nif (check_n24_addl_conflict(scenario)) {\n  policy <- aic$addl_actual_conflict_policy %||% \"actual_wins\"\n  df <- df |> resolve_addl_actual_conflict(policy = policy)\n}",
    "best_practice_tips": [
        "actual_wins (실제 우선) / planned_wins (계획 우선) 두 가지가 일반적 — 정책 없으면 분석자별 결과 달라짐.",
        "충돌 해결 후 audit log에 어느 정책을 썼는지 기록 — 재현성 보장.",
        "%||% (null-coalescing)는 rlang에서 가져옴 — base R에는 없어서 library(rlang) 필요."
    ]
}

# ─── N25 ───────────────────────────────────────────────────────────
ADDITIONS["N25"] = {
    "persona_intro": "분석물질 역할 태깅이 필요한 modality(ADC/Bispecific/CAR-T/Gene)인지 묻는 분기야. mRNA는 단일 분석물질이라 제외.",
    "context_card": {
        "situation": "modality_class가 ADC, BISPECIFIC, CELL_THERAPY, GENE_THERAPY 중 하나인지 확인합니다. YES면 analyte_role 컬럼 + assign_cmt_with_analyte_role 함수가 필요합니다.",
        "why_important": "ADC는 TAb/cADC/payload 3종, CAR-T는 VECTOR_COPY/CAR_POSITIVE_CELL 2종 측정 — 같은 'CMT=2'에 합치면 각자의 PK 곡선이 사라집니다. mRNA는 보통 단일 분석물질이라 이 분기에서 제외됨."
    },
    "data_state_before": {
        "stage": "Stage 8 — modality 기반 분기",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>modality_class</th><th>analyte_role 태깅 필요?</th></tr></thead><tbody><tr><td>ADC</td><td class=\"bad\">예 — 누락 시 3종 합쳐짐</td></tr><tr><td>BISPECIFIC</td><td class=\"bad\">예 — 두 표적 합쳐짐</td></tr><tr><td>MAB</td><td>아니오 — 단일 분석물질</td></tr></tbody></table>",
        "problem_cells": ["ADC/Bispecific/CAR-T/Gene 분기 없이 모든 modality 동일 처리"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>modality_class</th><th>다음 분기</th></tr></thead><tbody><tr><td>ADC</td><td class=\"good\">YES → analyte_role 태깅 + N26</td></tr><tr><td>BISPECIFIC</td><td class=\"good\">YES → analyte_role 태깅 + N26</td></tr><tr><td>CELL_THERAPY</td><td class=\"good\">YES → 세포 동태학 경로</td></tr><tr><td>GENE_THERAPY</td><td class=\"good\">YES → 벡터/transgene 분리</td></tr><tr><td>MAB / SMALL_MOLECULE / MRNA</td><td>NO → 단일 CMT</td></tr></tbody></table>",
        "changed_cells": ["modality별로 analyte_role 태깅 필요성 분기"]
    },
    "r_code_check": "# ── N25 ── modality가 analyte_role 태깅 필요 그룹?\n# mRNA는 단일 분석물질이라 제외 (CAR-T의 vector_copy/CAR_positive_cell는 별도 처리).\n\ncheck_n25_role_tagging_modality <- function(scenario) {\n  role_modalities <- c(\"ADC\", \"BISPECIFIC\", \"CELL_THERAPY\", \"GENE_THERAPY\")\n  scenario$modality_class %in% role_modalities\n}",
    "best_practice_tips": [
        "modality 상수 벡터는 한 곳에 정의 (예: ROLE_TAGGING_MODALITIES) — 코드 곳곳에 같은 리스트를 박지 말 것.",
        "analyte_role 컬럼이 raw 데이터에 없으면 ANALYTE 컬럼에서 매핑 규칙으로 derive 필요.",
        "MRNA는 단일 분석물질이지만 백신 면역원성과 결합되면 IMMUNOGENICITY 분기(N10)로 갈 수 있다."
    ]
}

# ─── N27 ───────────────────────────────────────────────────────────
ADDITIONS["N27"] = {
    "persona_intro": "BLQ 처리도 두 갈래야 — 농도 BLQ(M3 등)와 세포 BLQ(Poisson-LLOQ). A5가 CELLULAR-BLQ-DEFINED면 세포 경로.",
    "context_card": {
        "situation": "A5 축이 CELLULAR-BLQ-DEFINED인지 확인합니다. YES면 canonicalize_cellular_blq 함수로 처리 (LLOQ_cell = 1/sample_volume_mL).",
        "why_important": "세포 BLQ에 농도 BLQ 함수(LLOQ=ng/mL)를 그대로 적용하면 LLOQ 정의가 어긋나서 M3 likelihood가 잘못 계산됩니다. CAR-T cellular kinetics에서 가장 흔한 침묵 오류."
    },
    "data_state_before": {
        "stage": "Stage 8 — BLQ 종류 분기 (농도 vs 세포)",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>endpoint</th><th>A5_state</th><th>적용된 함수</th></tr></thead><tbody><tr><td>CELLULAR_KINETICS</td><td>CELLULAR-BLQ-DEFINED</td><td class=\"bad\">canonicalize_blq (농도용)</td></tr></tbody></table>",
        "problem_cells": ["세포 BLQ인데 농도 BLQ 함수 적용 — LLOQ 정의 불일치"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>endpoint</th><th>A5_state</th><th>적용된 함수</th></tr></thead><tbody><tr><td>CELLULAR_KINETICS</td><td>CELLULAR-BLQ-DEFINED</td><td class=\"good\">canonicalize_cellular_blq (Poisson-LLOQ)</td></tr></tbody></table>",
        "changed_cells": ["세포 BLQ 전용 함수로 교체 → LLOQ_cell = 1/sample_volume_mL"]
    },
    "r_code_check": "# ── N27 ── A5가 CELLULAR-BLQ-DEFINED인지\ncheck_n27_cellular_blq <- function(scenario) {\n  identical(scenario$A5_state, \"CELLULAR-BLQ-DEFINED\")\n}",
    "best_practice_tips": [
        "Poisson-LLOQ: count=0인 시점도 정보를 가짐 — 'LLOQ보다 작음'으로 likelihood에 포함.",
        "sample_volume_mL는 환자별/시점별 다를 수 있음 → 컬럼으로 추적, 코드 상수로 박지 말 것.",
        "농도 BLQ 함수와 세포 BLQ 함수의 이름이 비슷하니 (canonicalize_blq vs _cellular_blq) PR 리뷰에서 자주 확인."
    ]
}

# ─── N29 ───────────────────────────────────────────────────────────
ADDITIONS["N29"] = {
    "persona_intro": "면역원성 데이터(ADA/NAb)에서 양성판정 규칙을 적용하는 함수가 시퀀스에 있느냐를 가르는 분기야.",
    "context_card": {
        "situation": "action_sequence에 adjudicate_immunogenicity_positivity가 포함되어 있는지 확인합니다.",
        "why_important": "ADA 측정값(titer 또는 signal)을 '양성/음성'으로 분류하는 규칙(예: cut-point × titer ≥ threshold)이 명시되지 않으면 분석자마다 다른 cut-off를 써서 양성률이 ±20%p 바뀝니다. 규제 제출 데이터에서 가장 큰 변이 원인."
    },
    "data_state_before": {
        "stage": "Stage 8 — 면역원성 분기 후 양성판정 단계",
        "before_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>ADA_SIGNAL</th><th>ADA_POSITIVE</th></tr></thead><tbody><tr><td>1</td><td>168</td><td>1.8</td><td class=\"bad\">—</td></tr><tr><td>1</td><td>336</td><td>2.5</td><td class=\"bad\">—</td></tr></tbody></table>",
        "problem_cells": ["ADA_POSITIVE 컬럼 미생성 — 양성판정 규칙 미적용"]
    },
    "data_state_after": {
        "after_table_html": "<table class=\"ba-tbl\"><thead><tr><th>ID</th><th>TIME</th><th>ADA_SIGNAL</th><th>ADA_POSITIVE</th></tr></thead><tbody><tr><td>1</td><td>168</td><td>1.8</td><td class=\"good\">0 (음성)</td></tr><tr><td>1</td><td>336</td><td>2.5</td><td class=\"good\">1 (양성, ≥2.0)</td></tr></tbody></table>",
        "changed_cells": ["positivity_adjudication_rule: signal ≥ 2.0 → ADA_POSITIVE=1"]
    },
    "r_code_check": "# ── N29 ── action_sequence에 면역원성 양성판정 함수 포함?\ncheck_n29_immunogenicity_adjudication <- function(action_seq) {\n  \"adjudicate_immunogenicity_positivity\" %in% action_seq\n}",
    "r_code_pass": "# YES — 양성판정 규칙 적용\nif (check_n29_immunogenicity_adjudication(action_seq)) {\n  rule <- aic$positivity_adjudication_rule  # 예: list(method=\"signal_threshold\", cutoff=2.0)\n  df <- df |> adjudicate_immunogenicity_positivity(rule)\n}",
    "best_practice_tips": [
        "ADA cutoff는 lab CRO가 결정하지 분석자가 임의로 정하면 안 됨 — 반드시 AIC에 받기.",
        "양성/음성/borderline 3분류일 수도 있음 — case_when으로 확장 가능한 구조.",
        "ADA 양성 발현 후 PK가 변하는 경우(neutralizing antibody) — covariate로 ADA_POSITIVE 부착해 사용."
    ]
}


# ═══════════════════════════════════════════════════════════════════
# Deep-merge: 기존 키 보존, 신규 키만 추가
# ═══════════════════════════════════════════════════════════════════

def deep_merge_preserve(existing: dict, addition: dict) -> tuple[dict, list[str]]:
    """existing 우선 deep merge. 신규 추가된 key path 목록을 반환."""
    added_paths: list[str] = []

    def _merge(e, a, path):
        if not isinstance(e, dict) or not isinstance(a, dict):
            return e
        for k, v in a.items():
            if k not in e:
                e[k] = deepcopy(v)
                added_paths.append(f"{path}.{k}" if path else k)
            elif isinstance(e[k], dict) and isinstance(v, dict):
                _merge(e[k], v, f"{path}.{k}" if path else k)
        return e

    merged = deepcopy(existing)
    _merge(merged, addition, "")
    return merged, added_paths


def main() -> int:
    if not RLIB_PATH.exists():
        print(f"[ERROR] {RLIB_PATH} not found", file=sys.stderr)
        return 1

    original = json.loads(RLIB_PATH.read_text(encoding="utf-8"))
    candidates = original.get("candidate_nodes", {})

    total_added: dict[str, list[str]] = {}
    untouched: list[str] = []
    for node_id, additions in ADDITIONS.items():
        if node_id not in candidates:
            print(f"[WARN] {node_id} not in candidate_nodes — creating new entry")
            candidates[node_id] = {"node_id": node_id}
        before = deepcopy(candidates[node_id])
        merged, added = deep_merge_preserve(candidates[node_id], additions)
        candidates[node_id] = merged
        if added:
            total_added[node_id] = added
        else:
            untouched.append(node_id)
        # Sanity: 기존 키의 value 무변경 확인
        for k, v in before.items():
            if isinstance(v, dict):
                continue  # nested는 _merge 재귀가 보장
            if candidates[node_id].get(k) != v:
                print(f"[FATAL] {node_id}.{k} value changed — abort", file=sys.stderr)
                return 2

    # candidate_nodes 외 최상위 키(action_functions, end_to_end_example 등) 무변경 검증
    for top_key in ("packages_needed", "pipeline_overview", "nonmem_ready_spec",
                    "action_functions", "end_to_end_example", "version", "purpose"):
        if top_key in original and original[top_key] != original[top_key]:
            print(f"[FATAL] top-level {top_key} changed", file=sys.stderr)
            return 2

    # Write back
    RLIB_PATH.write_text(
        json.dumps(original, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Report
    print("─" * 60)
    print("r_code_library.json 보강 완료")
    print("─" * 60)
    for nid, paths in total_added.items():
        print(f"  {nid:5s} ← +{len(paths)} keys: {', '.join(paths)}")
    if untouched:
        print(f"\n  무변경 (모든 신규 key가 기존에 이미 존재): {', '.join(untouched)}")
    print(f"\n총 보강 노드: {len(total_added)}개 / 무변경: {len(untouched)}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
