"""
study/_build_v3.py
─────────────────────────────────────────────────────────────────────
v3 보강 빌드: r_code_library.json에 v3_* prefix 키만 추가.
규칙:
  - 기존 key 절대 무변경 (v3_* prefix로만 추가)
  - 음슴체 (~음, ~함, ~임)
  - "실무에서 약 X%는 …" 같은 구체 표현
  - "raw 데이터에는 보통 `<...>` 같은 형태로 옴" 명시
  - "✨ 일타강사의 핵심" R 코드 한 줄 평
"""

from __future__ import annotations
import json
import pathlib
import sys
from copy import deepcopy

ROOT = pathlib.Path(__file__).resolve().parent
RLIB_PATH = ROOT / "data" / "r_code_library.json"


# ═══════════════════════════════════════════════════════════════════
# v3 보강 데이터
# ═══════════════════════════════════════════════════════════════════
V3: dict[str, dict] = {}

# ─── N0 ───────────────────────────────────────────────────────────────
V3["N0"] = {
    "v3_persona_intro": "지금 보는 게 AIC라는 한 페이지짜리 YAML 계약서임. 데이터 받자마자 가장 먼저 이거 있는지부터 확인해야 함.",
    "v3_context_card": {
        "glossary": "AIC = Analysis Intent Contract(분석 의도 계약). '내가 이 데이터로 뭘 할지' 한 페이지로 적은 YAML 메타 파일임. endpoint_data_type = 이 데이터가 어떤 종류인지 (PK 농도 / PD 효과 / 면역원성 등) 분류하는 키.",
        "raw_data_shape": "raw 데이터 폴더에는 보통 `study_001.csv` + `aic/study_001.yaml` 짝으로 옴. YAML 안에는 `type: AIC-PKPD`, `endpoint_data_type: PK_CONCENTRATION`, `blq_handling_policy: M3`, `lloq: 1.0` 같은 키가 들어있음.",
        "practical_distribution": "실무에서 약 30% 케이스는 이 AIC 파일 자체가 누락된 채로 옴. 가장 흔한 격리 사유가 Q11(AIC 누락)인 이유임. 나머지 70% 중에서도 endpoint_data_type 키가 빠져서 오는 경우가 흔함.",
        "nonmem_condition": "AIC type이 정해지고 endpoint_data_type이 선언되어야 BLQ를 M1으로 뺄지 M3 likelihood로 둘지, 시간을 elapsed로 변환할지 nominal로 둘지 등 모든 후속 wrangling 결정이 정해짐. 이게 정리되어야 NONMEM control stream에서 $DATA가 일관되게 잘 돌아감.",
        "situation": "데이터 받자마자 가장 먼저 AIC YAML 파일이 있는지, type 필드가 들어있는지, 그리고 PKPD/ER/TTE/BIOMARKER/CELL_THERAPY/IMMUNOGEN/LACTATION 같은 type이면 endpoint_data_type까지 선언됐는지 확인함. 이 단계가 모든 분기의 출발점이라 'forced gate'로 분류됨.",
        "why_important": "AIC가 없으면 분석자마다 다른 정책으로 같은 데이터를 다르게 wrangling하게 됨. 누구는 BLQ를 그냥 빼버리고(M1) 누구는 LLOQ로 대체(M4)함. 결과가 매번 다르고 재현성이 망가짐. 이걸 첫 단계에서 막아야 후속 작업이 의미 있음."
    },
    "v3_r_code_kpoint": {
        "check_kpoint": "✨ 일타강사의 핵심: `file.exists()` → `is.null(aic$type)` → `aic$type %in% requires` 3단계로 분리한 게 포인트임. 한 번에 묶어서 검사하면 '뭐 때문에 실패했는지' 디버깅이 안 됨. 단계별로 끊으면 Q-code도 더 구체적으로 줄 수 있음.",
        "pass_kpoint": "✨ 일타강사의 핵심: `aic` 객체를 메모리에 보관해서 N1/N4/N5에서 계속 참조하는 패턴임. AIC를 매번 다시 읽지 말고 한 번 읽어서 통째로 들고 다니면 코드가 훨씬 깔끔해짐."
    },
    "v3_best_practice_tips": [
        "AIC YAML은 데이터 패키지 받자마자 가장 먼저 열어보는 게 습관임. type만 봐도 뭐 할지 80% 짐작 가능함.",
        "`%||%` (null-coalescing)는 rlang 패키지에 있음. AIC 키가 optional인 경우 기본값 줄 때 유용함.",
        "Q-code 분기를 처음부터 정확히 매기면 의뢰자에게 '뭘 보완해서 재제출 해달라' 회신이 명확해짐."
    ]
}

# ─── N1 ───────────────────────────────────────────────────────────────
V3["N1"] = {
    "v3_persona_intro": "USUBJID 같은 문자열 ID를 NONMEM이 읽는 정수 ID로 바꾸는 단계임. 단일 study면 단순하지만 multi-study 풀링은 ID 충돌 거의 100% 생김.",
    "v3_context_card": {
        "glossary": "USUBJID = Unique Subject Identifier (CDISC SDTM 표준). 보통 'study_id-site-subject' 형태 문자열. dyad linkage = 모자(엄마-아기) PK에서 두 ID를 한 짝으로 묶는 키.",
        "raw_data_shape": "raw 데이터 컬럼에는 `USUBJID = 'CDISCPILOT01-701-1015'` 같은 긴 문자열로 옴. 일부 옛 데이터는 `SUBJID = 1015` 같이 짧게 오기도 함. NONMEM은 정수만 받음.",
        "practical_distribution": "실무에서 약 60%는 단일 study 데이터라 `factor() |> as.integer()` 두 줄이면 끝남. 약 30%는 다기관 통합(F02 family)인데 study A의 'S001'과 study B의 'S001'이 별 사람이라 study offset이 필요함. 약 5%는 모자 PK라 dyad_linkage_key가 추가로 와야 함.",
        "nonmem_condition": "ID 컬럼이 정수형으로 정리되고 같은 환자는 항상 같은 ID 번호를 받아야 NONMEM이 group_by(ID)로 환자별 PK 곡선을 fit함. ID가 문자열이면 NONMEM이 그냥 에러 내고 멈춤.",
        "situation": "USUBJID/SUBJID/ID/SUBJECT 같은 후보 컬럼 중 하나 골라서 정수로 매핑함. 결측 검사 + 다기관 정책 확인 + 모자 연결 키 확인까지 한 번에 함.",
        "why_important": "ID 매핑이 잘못되면 두 환자의 데이터가 한 사람으로 합쳐져서 PK 곡선이 짬뽕됨. CL이 두 배로 보이거나 V가 절반으로 보이는 식. 모자 PK에서 dyad_linkage_key 빠지면 엄마 농도와 아기 농도를 한 시간축에서 비교 불가 → Q18 격리."
    },
    "v3_r_code_kpoint": {
        "pass_kpoint": "✨ 일타강사의 핵심: `factor(., levels = unique(.))` 패턴이 핵심임. `levels =` 안 쓰면 R이 알파벳 순으로 정렬해서 ID 번호가 데이터 순서랑 어긋남. 그러면 디버깅할 때 'ID=1이 누구지?' 추적이 안 됨. `levels = unique()` 쓰면 등장 순서대로 번호가 매겨져서 USUBJID 매핑 사전을 별도로 만들기 쉬움."
    },
    "v3_best_practice_tips": [
        "USUBJID → 정수 ID 매핑 사전(tibble(USUBJID, ID))을 별도 파일로 저장하면 audit trail 용으로 재현 가능함.",
        "`relocate(ID, .before = everything())`로 ID를 맨 앞에 두는 게 NONMEM 컨트롤 스트림 작성할 때 편함.",
        "dyad는 ID 컬럼과 별도 컬럼(DYAD_KEY)로 두는 게 깔끔함. ID에 짝 정보 섞으면 group_by 망가짐."
    ]
}

# ─── N2 ───────────────────────────────────────────────────────────────
V3["N2"] = {
    "v3_persona_intro": "datetime 문자열을 hour 단위 numeric으로 바꾸는 단계임. 첫 투여 = 0이 NONMEM 기본 관례.",
    "v3_context_card": {
        "glossary": "ATIME = Actual Time (실제 채혈/투여 시각, 보통 datetime). NTIME = Nominal Time (계획된 시점, 예: 'Hour 2 post-dose'). elapsed time = 어떤 기준점(보통 첫 투여)부터 흐른 시간.",
        "raw_data_shape": "raw 데이터에는 `ATIME = '2025-01-15 09:00:00'` 같은 datetime 문자열로 오거나, `NTIME = 2` (계획된 시점 hour) 형태로 옴. 일부는 둘 다 옴.",
        "practical_distribution": "실무에서 약 70%는 ATIME만 깔끔하게 와서 `lubridate::ymd_hms() |> difftime()` 두 줄이면 변환 끝. 약 20%는 ATIME과 NTIME 둘 다 있고 차이가 있어서 어느 걸 쓸지 정책 필요. 약 5%는 임신/수유 PK라 분만 시각(delivery_anchor)이 추가로 와야 함.",
        "nonmem_condition": "TIME 컬럼이 환자별로 0부터 시작하는 numeric hour로 정리되어야 NONMEM의 ADVAN/TRANS 모델이 time-concentration 곡선을 fit함. 음수 TIME이 있으면 NONMEM이 에러 냄.",
        "situation": "시간 후보 컬럼 찾고, lubridate로 파싱하고, 환자별 첫 투여 시각을 기준점으로 잡아서 difftime으로 hour 단위 numeric 만드는 단계임.",
        "why_important": "ATIME/NTIME 충돌을 정책 없이 임의로 한쪽 골라 쓰면 분석마다 결과가 달라짐 (Q02). 임신/수유 PK는 첫 투여가 아니라 분만 시점을 0으로 둬야 산후 며칠/몇 주 같은 임상적으로 의미 있는 해석이 가능함."
    },
    "v3_r_code_kpoint": {
        "pass_kpoint": "✨ 일타강사의 핵심: `group_by(ID) |> mutate(.first_dose = min(.time_parsed[EVID == 1], na.rm = TRUE))` 패턴이 진짜 중요함. 환자별로 첫 투여 시각이 다르니까 group_by 안에서 anchor를 잡아야 함. 만약 전체 데이터에서 min() 잡으면 늦게 투여 시작한 환자는 음수 TIME이 나옴. `units = \"hours\"`는 명시 안 하면 R 로케일 따라 단위 바뀜 — 반드시 명시."
    },
    "v3_best_practice_tips": [
        "lubridate::ymd_hms()는 다양한 datetime 포맷 자동 인식함. 단 시간대 표시가 섞이면 헷갈리니 사전에 UTC로 통일하는 게 안전함.",
        "임시 변수는 `.first_dose` 같이 점으로 시작하는 이름을 쓰면 마지막에 `select(-.first_dose)`로 한 번에 제거 가능.",
        "산후 PK는 TIME(약물 elapsed)과 TIME_POSTPARTUM(분만 elapsed) 두 축을 같이 들고 다니는 게 분석에 유연함."
    ]
}

# ─── N3 ───────────────────────────────────────────────────────────────
V3["N3"] = {
    "v3_persona_intro": "AMT 컬럼이 NONMEM이 읽는 형태(mg, EVID=1 행에만 값)인지, mg/kg 같이 재구성 필요한 경우 정책 있는지 확인함.",
    "v3_context_card": {
        "glossary": "AMT = Amount (투여량, mg 단위 기본). DOSE = 처방된 용량 (mg/kg 또는 mg/m² 같은 normalized form 가능). ADDL = Additional Doses (추가 투여 횟수, 한 줄로 다회투여 표현). II = Interdose Interval (투여 간격, hour).",
        "raw_data_shape": "raw 데이터에는 `AMT = 350` (mg) 또는 `DOSE_PER_KG = 5, WT = 70` (mg/kg + 체중) 형태로 옴. 일부는 `DOSE = 100, ADDL = 6, II = 24`로 다회투여를 한 줄에 압축해서 옴.",
        "practical_distribution": "실무에서 약 70%는 plain AMT(mg)로 와서 if_else로 0/값 채우면 끝남. 약 20%는 mg/kg weight-based라 reconstruct_dose_weight 필요함. 약 5%는 mg/m² BSA-based. ADC/생물의약품에서는 loading dose + maintenance dose 패턴(약 10%)도 흔함.",
        "nonmem_condition": "EVID=1 행에는 AMT가 mg numeric으로 들어가야 하고, EVID=0 행은 AMT=0 (NA 아님). ADDL/II로 다회투여 표현했으면 펼치거나 그대로 두거나 정책에 따라 결정. 이게 일관되면 NONMEM이 dose 이벤트를 시간순으로 잘 처리함.",
        "situation": "AMT/DOSE 컬럼 존재 + 결측 검사 + dose_type 정책 확인 (weight/bsa/titration/infusion/addl) + 단위 통일까지 한 단계에서 처리.",
        "why_important": "mg/kg 그대로 NONMEM에 넘기면 5mg/kg = 5mg으로 들어가서 실제 350mg이 70배 작게 입력됨 → CL이 70배 커지는 침묵 오류. 가장 자주 발생하는 false-REPAIR 원인이라 v5.1에서 cost가 3.6 → 4.5로 올라간 게이트임."
    },
    "v3_r_code_kpoint": {
        "pass_kpoint": "✨ 일타강사의 핵심: `if_else(EVID == 1, AMT, 0)`이 핵심임. NONMEM 규약상 관측 행은 AMT=0이 정답임. NA로 두면 NONMEM이 'missing'으로 처리해서 경고만 내거나 에러 낼 수 있음. 명시적 0이 가장 안전함. `case_when()` 안 써도 되는 단순한 분기는 `if_else()`가 더 빠르고 가독성 좋음."
    },
    "v3_best_practice_tips": [
        "재구성 정책(reconstruct_dose_weight_policy 등)은 AIC에 명시되어야 함. 코드에 박지 말고 정책으로 받는 게 다음 study에서도 재사용 가능.",
        "AMT 단위는 항상 mg로 통일하는 게 NONMEM 관례. μg나 g로 오면 convert_units로 먼저 정리.",
        "ADDL/II 펼치기(expand_addl_ii)는 환자별로 다회투여 수가 다를 때 group별 처리가 필요함 — `rowwise() |> mutate(extra = list(tibble(...))) |> unnest()` 패턴."
    ]
}

# ─── N4 ───────────────────────────────────────────────────────────────
V3["N4"] = {
    "v3_persona_intro": "DV(농도 측정값)와 CMT(구획 번호) 컬럼이 NONMEM이 fit할 수 있는 형태인지 확인. ADC/CAR-T 같은 다중 분석물질은 여기서 침묵 오류 가장 많이 남.",
    "v3_context_card": {
        "glossary": "DV = Dependent Variable (모델이 fit할 측정값, 보통 농도 ng/mL). CMT = Compartment (구획 번호, 1=흡수 depot / 2=중심 central). analyte_role = ADC에서 TAb(전체 항체) / cADC(결합 ADC) / payload (페이로드) 중 어느 것인지 표시.",
        "raw_data_shape": "raw 데이터에는 `DV = 25.3` 또는 `CONC = 25.3` 형태로 옴. 단일 분석물질이면 한 컬럼이지만, ADC는 `ANALYTE = 'TAb', DV = 25.3` / `ANALYTE = 'cADC', DV = 18.7` 같이 long format으로 와서 분석물질 정보가 별도 컬럼에 있음.",
        "practical_distribution": "실무에서 약 85%는 단일 분석물질(MAB, small molecule)이라 CMT=1/2 자동 할당이면 끝. 약 5%는 ADC(TAb/cADC/payload 3종). 약 3%는 CAR-T (vector copy + CAR+ cell 2종). 약 2%는 면역원성(ADA/NAb)이라 양성판정 규칙 필요.",
        "nonmem_condition": "DV 컬럼이 numeric으로 정리되고, CMT가 분석물질별로 분리된 정수로 할당되고, BLQ 행은 LLOQ 정보와 함께 표시되어야 NONMEM의 $ERROR 블록이 likelihood 계산함. 다중 분석물질에서 CMT가 분리 안 되면 PK 곡선이 합쳐져서 모델 식별 불가.",
        "situation": "DV/CONC 컬럼 존재 확인 + BLQ/LLOQ 정책 확인 + cellular kinetics면 cellular_LLOQ_derivation 정책 + immunogenicity면 positivity 규칙 + multi-analyte면 analyte_role 정책까지 한 번에 점검.",
        "why_important": "ADC 3종을 같은 CMT에 합치면 페이로드 농도가 항체 농도에 묻혀서 노출-반응 관계가 사라짐. cellular kinetics에 농도 LLOQ 적용하면 Poisson-LLOQ가 어긋나서 BLQ likelihood가 잘못 계산됨. v4.2 modality(ADC/Bispecific/CAR-T)의 silent error가 거의 다 이 단계에서 시작됨."
    },
    "v3_r_code_kpoint": {
        "pass_kpoint": "✨ 일타강사의 핵심: `case_when()` 안에서 `EVID == 0` 조건을 먼저 거는 게 포인트임. 투여 행(EVID=1)에는 DV가 의미 없으니 한꺼번에 0으로 밀어내고, 관측 행만 분석물질별로 분기. nested ifelse 5단계 쌓는 것보다 case_when 한 블록이 새 분석물질 추가할 때 한 줄만 늘리면 됨."
    },
    "v3_best_practice_tips": [
        "DV=0과 DV=NA는 다른 의미임. 0=BLQ 처리됨, NA=정량값 없음(누락). 헷갈리지 말 것.",
        "CMT 번호는 NONMEM control stream의 $MODEL 블록과 일치해야 함. 코드 상수보다 AIC 정책으로 받는 게 안전.",
        "ADC TAb/cADC/payload는 보통 CMT 2/3/4로 분리. AIC에 cmt_map으로 명시해두면 다른 study에서도 재사용 가능."
    ]
}

# ─── N5 ───────────────────────────────────────────────────────────────
V3["N5"] = {
    "v3_persona_intro": "BLQ(정량한계 미만) 행을 NONMEM 규약(DV=값, MDV=0 또는 1)으로 표준화함. M1/M3/M4 정책 중 어느 걸 쓸지가 핵심.",
    "v3_context_card": {
        "glossary": "BLQ = Below Lower Limit of Quantification (정량 하한 미만 측정값). LLOQ = Lower Limit Of Quantification (정량 하한값). MDV = Missing DV flag (1이면 NONMEM이 DV를 likelihood 계산에서 뺌). M1/M3/M4 = Beal 2001이 정의한 BLQ 처리 방법들.",
        "raw_data_shape": "raw 데이터에 BLQ는 보통 별도 `BLQ = 1` 플래그 컬럼으로 오거나, `DV = 'BQL'`, `DV = '<LLOQ'`, `DV = NA` 같은 문자열로 옴. LLOQ 값(예: 1.0)은 AIC에 따로 선언됨.",
        "practical_distribution": "실무에서 약 90%는 M3 (likelihood-based) 정책 씀 — BLQ 행에 `DV = LLOQ, MDV = 0`으로 두고 NONMEM이 'LLOQ보다 작다'는 정보로 처리. 약 8%는 M1(단순 제외), 그러나 bias 있어서 줄어드는 추세. 약 2%는 M4(LLOQ/2 대체)나 project-specific.",
        "nonmem_condition": "BLQ 행에 DV=LLOQ + MDV=0 (M3 기준)이면 NONMEM의 F_FLAG=1 옵션이 censored likelihood로 처리함. M1이면 행 자체를 제외. 정책 일관성이 가장 중요함 — 한 데이터셋 안에서 M1/M3 섞이면 안 됨.",
        "situation": "AIC의 blq_handling_policy 확인 + LLOQ 값 확인 + 정책에 따라 DV/MDV 컬럼 갱신. cellular kinetics는 별도 함수(canonicalize_cellular_blq) 사용.",
        "why_important": "BLQ를 NA로 두면 NONMEM이 자동으로 빼서 PK 모델이 high concentration만 fit함 → terminal slope 왜곡, CL 과소추정. M3가 가장 정확하지만(Beal 2001) 모든 model이 M3 지원하는 건 아니라 정책 선택이 분석 목적에 따라 달라짐."
    },
    "v3_r_code_kpoint": {
        "pass_kpoint": "✨ 일타강사의 핵심: BLQ 처리는 `BLQ == 1 & EVID == 0` 조건을 정확히 거는 게 핵심임. 투여 행(EVID=1)도 MDV=1이라 함부로 BLQ 분기에 넣으면 AMT까지 망가짐. switch()로 정책 분기하면 새 정책(M5, M6 등) 추가가 한 줄로 끝남 — nested if문보다 훨씬 깔끔."
    },
    "v3_best_practice_tips": [
        "M3 vs M1 선택은 분석 목적에 따라 다름 — pivotal popPK는 M3, scoping/IVIVC는 M1로 단순화도 OK.",
        "LLOQ가 시간변동(다른 batch에서 다른 LLOQ)이면 LLOQ 컬럼을 따로 두고 행마다 매칭하는 패턴 필요.",
        "BLQ 비율이 30% 넘으면 모델 진단에서 NPDE plot 별도 점검 필수 — censored data가 fit 결과에 미치는 영향 큼."
    ]
}

# ─── N8 ───────────────────────────────────────────────────────────────
V3["N8"] = {
    "v3_persona_intro": "지금까지 통과한 데이터에 대해 '앞으로 적용할 모든 변환 함수가 요구하는 정책'이 AIC에 빠짐없이 선언됐는지 마지막 점검. v5.1에서 신규 추가된 가장 까다로운 게이트.",
    "v3_context_card": {
        "glossary": "required_policy = 각 변환 함수(canonicalize_blq, reconstruct_dose_weight 등)가 동작하려면 AIC에 있어야 하는 정책 키 목록. partial declaration = 정책 일부만 선언된 상태 (silent bug의 가장 흔한 원인).",
        "raw_data_shape": "AIC YAML 안에 `blq_handling_policy: M3`, `lloq: 1.0`, `reconstruct_dose_weight_policy: per_kg_to_mg`, `analyte_role_policy: adc_tab_cadc_payload` 같은 정책 키들이 들어있어야 함. 이중 일부가 빠져 있으면 다음 변환 단계에서 silent default behavior로 잘못된 처리.",
        "practical_distribution": "실무에서 약 60%는 AIC가 완전하게 와서 N8 PASS. 약 40%는 정책 일부 누락이라 N8에서 잡아내 Q15A 격리 → 의뢰자에게 'AIC에 X 정책 추가 후 재제출' 회신.",
        "nonmem_condition": "모든 required policy가 declared되면 그 다음 변환 단계들이 NULL 분기 없이 정상 진행 → NONMEM-ready 데이터셋이 일관되게 생성됨.",
        "situation": "예상 action_sequence가 요구하는 정책 목록을 모으고(setdiff 패턴), AIC에 선언된 키 목록과 비교해서 누락 키를 찾아냄. 누락 있으면 Q15A 격리.",
        "why_important": "N8 없으면 partial policy인 데이터가 다음 단계에서 silent default로 잘못 처리됨. 예: blq_policy가 없으면 R 코드가 `policy %||% 'M1'`으로 자동 M1 적용 → 분석자는 모르고 PK 추정. v5.1에서 이걸 막으려고 게이트 신설(PATCH-3)."
    },
    "v3_r_code_kpoint": {
        "check_kpoint": "✨ 일타강사의 핵심: `purrr::map() |> unlist() |> unique()`로 모든 함수의 required_policy를 한 줄에 모으는 게 핵심임. `setdiff(required, declared)`로 누락 키만 추려내는 함수형 패턴 — base R loop보다 훨씬 깔끔하고 새 함수 추가해도 자동 적용."
    },
    "v3_best_practice_tips": [
        "각 변환 함수 정의에 `required_policy = c('blq_handling_policy', ...)` 메타데이터를 박아두면 N8 검사가 자동화됨.",
        "Q15A는 '데이터 패키지 불완전' 신호 — 의뢰자에게 어떤 정책 어떻게 추가해야 하는지 회신 메일에 정확히 적어줘야 재제출이 한 번에 끝남.",
        "AIC 완전성 검사를 데이터 도착 즉시 N0과 함께 하면, 이후 wrangling 시간 낭비를 막을 수 있음."
    ]
}

# ─── 주요 optional 보강 (N11, N13, N14, N19, N25) ───────────────────
V3["N11"] = {
    "v3_persona_intro": "endpoint가 MATERNAL_INFANT_PK / MILK_PK면 dyad + postpartum anchor + milk LLOQ 같은 특수 처리 경로로 빠지는 분기 게이트.",
    "v3_context_card": {
        "glossary": "MATERNAL_INFANT_PK = 산모 약물이 태반/모유 통해 영아에 노출되는 PK. dyad = 엄마-아기 짝 (두 ID를 짝으로 묶는 키). postpartum anchor = 분만 시각을 0으로 두는 별도 시간축.",
        "raw_data_shape": "raw 데이터에 `DYAD_KEY = 'D01'`이 엄마(M01)와 아기(I01) 행 모두에 들어있고, `delivery_anchor.csv`에 환자별 분만 datetime이 별도 테이블로 옴.",
        "practical_distribution": "전체 PK 데이터의 약 1~2%만 산모-영아 PK임. 빈도는 낮지만 한 번 만나면 특수 처리가 많아서 헤매기 쉬움.",
        "nonmem_condition": "DYAD_KEY 컬럼이 있고 TIME_POSTPARTUM 컬럼이 별도로 있어야 분만 후 며칠/몇 주 같은 임상 의사결정이 가능함. NONMEM에서는 DYAD_KEY가 covariate처럼 활용됨.",
        "situation": "AIC endpoint_data_type 확인하고 MATERNAL_INFANT_PK이면 dyad linkage + postpartum anchor 적용, MILK_PK까지면 milk matrix LLOQ도 별도 정책 필요.",
        "why_important": "분만 anchor가 없으면 '산후 30일 시점 농도'라는 임상적으로 가장 중요한 시점 정의가 안 됨. 모유 매트릭스 LLOQ는 혈장과 달라서(보통 더 높음) 잘못 적용하면 BLQ 비율이 통째로 어긋남."
    },
    "v3_r_code_kpoint": {
        "pass_kpoint": "✨ 일타강사의 핵심: dyad linkage 부착할 때 `bind_rows(엄마_view, 아기_view)` 패턴 쓰면 한 환자가 양쪽 ID 갖는 long format이 깔끔하게 만들어짐. left_join으로 매번 두 번 붙이는 것보다 효율적."
    },
    "v3_best_practice_tips": [
        "DYAD_KEY와 ID 컬럼은 분리해서 유지 — group_by(ID)와 group_by(DYAD_KEY) 둘 다 자유롭게.",
        "postpartum 일수는 day 단위가 임상에서 자연스러움 — TIME(hour)과 별도 단위 권장.",
        "모유 PK는 모유 채취 volume 정보가 함께 와야 함 (matrix dilution 등 계산용)."
    ]
}

V3["N13"] = {
    "v3_persona_intro": "BLQ 표준화 함수가 시퀀스에 들어가는지 확인 — 'BLQ 처리 경로'와 'BLQ 없는 경로'를 가르는 분기.",
    "v3_context_card": {
        "glossary": "canonicalize_blq = 농도 BLQ 표준화 (M1/M3/M4). canonicalize_cellular_blq = 세포 BLQ 표준화 (Poisson-LLOQ, count 데이터용).",
        "raw_data_shape": "action_sequence는 character vector로 옴 (예: `c('parse_source', 'canonicalize_blq', 'assign_evid', 'export')`). 이 안에 BLQ 함수가 포함되어 있으면 YES.",
        "practical_distribution": "실무 PK 데이터의 약 60%는 BLQ가 있어서 canonicalize_blq 호출. 약 35%는 BLQ 없음(early-phase 농도 충분). 약 5%는 cellular kinetics라 canonicalize_cellular_blq.",
        "nonmem_condition": "BLQ가 있으면 처리 함수가 시퀀스에 있어야 NONMEM이 받는 데이터에 BLQ가 표준화된 형태로 들어감 — DV=LLOQ, MDV=0 (M3 기준).",
        "situation": "현재 시나리오의 action_sequence에 canonicalize_blq 또는 canonicalize_cellular_blq 중 하나라도 있는지 단순 boolean 분기.",
        "why_important": "BLQ 처리 함수가 빠지면 BLQ 행이 raw 그대로 NONMEM에 들어감 → 'BQL' 같은 문자열 만나면 NONMEM 에러. 세포 BLQ인데 농도 함수 적용하면 LLOQ 정의 어긋남 (cellular는 1/sample_volume_mL)."
    },
    "v3_r_code_kpoint": {
        "check_kpoint": "✨ 일타강사의 핵심: `%in%`을 쓰는 게 핵심임. `grepl()`로 substring 매칭하면 'canonicalize_blq_v2' 같은 미래 변형도 오탐. 정확한 함수명 매칭은 `%in%`이 안전 + 빠름."
    },
    "v3_best_practice_tips": [
        "BLQ 함수가 둘 다 있으면 ADC + cellular kinetics 복합 시나리오 — 분석자에게 의도 확인 필요.",
        "함수명 상수 벡터를 한 곳에 정의해두면 새 BLQ 변형 추가될 때 코드 한 줄만 수정.",
        "action_sequence가 list-column이면 `purrr::map_lgl(seq, ~ any(.x %in% blq_fns))` 패턴으로 일괄 처리."
    ]
}

V3["N14"] = {
    "v3_persona_intro": "용량 재구성 함수(weight/bsa/titration/loading/infusion/ADDL conflict 중 하나)가 시퀀스에 있는지 분기. AUTO vs REPAIR 가르는 가장 흔한 게이트.",
    "v3_context_card": {
        "glossary": "reconstruct_dose_weight = mg/kg → mg 환산. expand_addl_ii = 한 줄 ADDL/II 표기를 여러 줄로 펼치기. resolve_addl_actual_conflict = ADDL 계획과 실제 투여 시각 충돌 해결.",
        "raw_data_shape": "AIC dose_type이 WEIGHT_BASED/BSA_BASED/TITRATION/LOADING_MAINTENANCE/INFUSION/ADDL 중 하나면 해당 재구성 함수가 action_sequence에 들어가야 함.",
        "practical_distribution": "실무에서 약 30%는 weight-based 또는 BSA-based 재구성 필요. 약 10%는 ADDL/II 펼치기. 약 5%는 infusion stop/restart. 합치면 약 40~50%가 재구성 함수 어느 형태로든 필요.",
        "nonmem_condition": "재구성 함수가 정확히 적용되면 AMT가 mg 단위 numeric으로 정리됨 → NONMEM PREDPP가 dose event를 정상 처리.",
        "situation": "action_sequence character vector에 reconstruct_dose_* / expand_addl_ii / resolve_addl_actual_conflict 중 하나라도 포함됐는지 확인.",
        "why_important": "재구성 빠뜨리면 mg/kg이 mg으로 둔갑(70배 작은 용량), ADDL 안 펼치면 다회투여가 1회로 인식(노출 N분의 1) — 가장 자주 발생하는 false-REPAIR 원인."
    },
    "v3_r_code_kpoint": {
        "check_kpoint": "✨ 일타강사의 핵심: `^...$` 앵커를 쓰는 게 핵심임. `str_detect(fn, 'reconstruct_dose_')` 처럼 앵커 없으면 'reconstruct_dose_weight_v2' 같은 미래 변형도 정확히 잡힘. 미래의 자기 자신에게 친절한 코드."
    },
    "v3_best_practice_tips": [
        "재구성 함수는 dose_type별로 1:1 대응 — AIC의 dose_type과 시퀀스에 있는 함수가 일관되는지 교차검증.",
        "ADDL/II 펼친 후 행 수가 늘어남 → assign_evid 같은 후속 함수가 새 행에도 적용되는지 확인.",
        "loading dose + maintenance는 전환 시점을 정확히 잡아야 함 — AIC에 transition_time 명시 권장."
    ]
}

V3["N19"] = {
    "v3_persona_intro": "공변량 부착 함수(baseline/time-varying/external/product-level/dyad 중 하나)가 시퀀스에 있는지 분기.",
    "v3_context_card": {
        "glossary": "attach_covariate_baseline = 환자별 한 번 측정한 변수 (WT, AGE, SEX 등)를 broadcast. time-varying = 시점별 변하는 변수 (lab values, WT 변동 등). product-level = CAR-T lot 등 제품 메타데이터를 ID가 아닌 LOT_ID로 join.",
        "raw_data_shape": "baseline 공변량은 보통 별도 `baseline.csv` (ID, WT, AGE, SEX, CRCL) 형태로 옴. time-varying은 `labs.csv` (ID, TIME, ALT, AST). CAR-T lot 정보는 `lot_metadata.csv` (LOT_ID, VECTOR_COPY_PER_CELL, MANUFACTURE_DATE).",
        "practical_distribution": "실무에서 약 80%는 baseline covariate만 부착해도 충분 (popPK 표준). 약 15%는 time-varying까지 필요. 약 5%는 CAR-T 등 제품 단위 covariate.",
        "nonmem_condition": "공변량 컬럼들이 행마다 채워지면 NONMEM $PK 블록에서 TVCL = THETA(1) * (WT/70)**THETA(2) 같은 covariate effect 모델링 가능.",
        "situation": "action_sequence에 attach_covariate_* 또는 attach_dyad_linkage가 포함되어 있는지 확인.",
        "why_important": "공변량 없으면 population mean만 fit 가능 — 개체간 변이 설명 불가. CAR-T는 lot별 효능 차이가 커서 lot covariate 빠지면 random effect가 과대해짐."
    },
    "v3_r_code_kpoint": {
        "check_kpoint": "✨ 일타강사의 핵심: 패턴 벡터(`cov_patterns`)를 함수 밖에 두지 말고 함수 안에 두는 게 핵심임. 새 covariate 함수 추가될 때 한 곳만 수정 → 함수 시그니처 변경 안 됨. `purrr::map_lgl + any` 조합으로 multi-pattern 매칭."
    },
    "v3_best_practice_tips": [
        "baseline은 left_join(by='ID')로 broadcast — 환자당 한 번 매칭.",
        "time-varying은 LOCF (na.locf) 또는 linear interpolation 정책을 AIC에 명시. 임의 선택 금지.",
        "CAR-T lot covariate는 'reverse join' 패턴 — ID가 아니라 LOT_ID로 join, 같은 lot 환자는 같은 값 부착."
    ]
}

V3["N25"] = {
    "v3_persona_intro": "modality가 analyte_role 태깅 필요한 그룹(ADC/Bispecific/CAR-T/Gene)인지 분기. mRNA는 단일 분석물질이라 제외.",
    "v3_context_card": {
        "glossary": "modality_class = 약물의 분자 형태 분류 (SMALL_MOLECULE / MAB / ADC / BISPECIFIC / CELL_THERAPY / GENE_THERAPY / MRNA / VACCINE 등). analyte_role = 측정값이 어떤 분석물질인지 (TAb / cADC / payload 등).",
        "raw_data_shape": "AIC `modality_class` 키로 옴. ADC면 raw 데이터 ANALYTE 컬럼에 'TOTAL_ANTIBODY', 'CONJUGATED_ADC', 'UNCONJUGATED_PAYLOAD' 같은 값이 long format으로 들어있음.",
        "practical_distribution": "실무에서 약 60%는 MAB/SmallMolecule(단일 분석물질) — 이 분기 NO. 약 5%는 ADC, 3%는 Bispecific, 3%는 CAR-T, 2%는 Gene — 합 약 13%가 analyte_role 태깅 필요.",
        "nonmem_condition": "ANALYTE_ROLE 컬럼이 있어야 N26(assign_cmt_with_analyte_role)에서 CMT 번호를 정확히 분리할 수 있음. 그래야 NONMEM에서 분석물질별 PK 곡선이 분리되어 fit 가능.",
        "situation": "modality_class가 4가지 중 하나인지 단순 boolean 분기. YES면 analyte_role 컬럼 derivation + CMT 분리 경로로.",
        "why_important": "ADC 3종을 같은 CMT에 넣으면 결합 ADC와 페이로드 곡선이 평균화되어 PK-PD 관계가 사라짐. ADC 효능 평가의 핵심이 cADC + payload 분리인데 이게 망가지면 efficacy 결론 못 냄."
    },
    "v3_r_code_kpoint": {
        "check_kpoint": "✨ 일타강사의 핵심: 상수 벡터(`role_modalities`)를 한 곳에 정의해두는 게 핵심임. 새 modality(예: ADC2.0) 등장하면 이 벡터만 업데이트 → 다른 노드에서 같은 벡터 재사용 가능."
    },
    "v3_best_practice_tips": [
        "mRNA는 단일 분석물질이라 이 분기에서 제외 — 백신 면역원성과 결합되면 N10(immunogenicity) 분기로.",
        "modality 상수는 enum처럼 다뤄야 함 — 오타 방지 위해 `match.arg()` 패턴도 좋음.",
        "ADC 페이로드는 보통 small molecule cytotoxin — payload PK는 small molecule 모델 + ADC PK는 mAb 모델 같이 fit."
    ]
}


# ═══════════════════════════════════════════════════════════════════
# Deep-merge: v3_* prefix 키만 추가
# ═══════════════════════════════════════════════════════════════════

def deep_merge_v3(existing: dict, addition: dict) -> tuple[dict, list[str]]:
    added_paths: list[str] = []
    merged = deepcopy(existing)
    for k, v in addition.items():
        if not k.startswith("v3_"):
            print(f"[FATAL] non-v3 key in addition: {k}", file=sys.stderr)
            sys.exit(2)
        if k in merged:
            print(f"[FATAL] v3 key {k} already exists in original — would overwrite!", file=sys.stderr)
            sys.exit(2)
        merged[k] = deepcopy(v)
        added_paths.append(k)
    return merged, added_paths


def main() -> int:
    if not RLIB_PATH.exists():
        print(f"[ERROR] {RLIB_PATH} not found", file=sys.stderr)
        return 1

    original = json.loads(RLIB_PATH.read_text(encoding="utf-8"))
    candidates = original.get("candidate_nodes", {})
    before_snapshot = json.dumps(candidates, ensure_ascii=False, sort_keys=True)

    total_added: dict[str, list[str]] = {}
    for node_id, additions in V3.items():
        if node_id not in candidates:
            print(f"[FATAL] {node_id} not in candidate_nodes", file=sys.stderr)
            return 2
        merged, added = deep_merge_v3(candidates[node_id], additions)
        candidates[node_id] = merged
        total_added[node_id] = added

    # 무변경 sanity: v3_* 키 제외하고 모든 candidate_nodes 내용은 그대로여야 함
    after_check = {nid: {k: v for k, v in node.items() if not k.startswith("v3_")}
                   for nid, node in candidates.items()}
    before_check = json.loads(before_snapshot)
    if after_check != before_check:
        print("[FATAL] non-v3 keys mutated!", file=sys.stderr)
        return 2

    RLIB_PATH.write_text(
        json.dumps(original, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("─" * 60)
    print("r_code_library.json v3 보강 완료")
    print("─" * 60)
    for nid, paths in total_added.items():
        print(f"  {nid:5s} ← +{len(paths)} keys: {', '.join(paths)}")
    print(f"\n총 v3 보강 노드: {len(total_added)}개")
    print(f"기존 키 무변경 보장: ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
