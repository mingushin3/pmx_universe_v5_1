# Boundary Case Q-code Validation Report

generated_at: 2026-05-22T07:32:19+00:00
csv_file: reports\repair_quarantine_boundary_cases_v4_2.csv
config_dir: config

## Distribution

- AUTO: 4
- REPAIR: 29
- QUARANTINE: 23
- UNSUPPORTED: 2
- INVALID: 2

## By family_id_hint

- F01: 18
- F02: 1
- F03: 1
- F05: 1
- F06: 1
- F07: 2
- F08: 1
- F09: 1
- F10: 1
- F12: 1
- F13: 2
- F16: 1
- F19: 1
- F20: 2
- F21: 1
- F22: 1
- F23: 3
- F24: 2
- F25: 1
- F26: 5
- F27: 2
- F28: 1
- F29: 6
- F31: 1
- F32: 1
- F34: 2

## Checks (BC1..BC9)

- [PASS] BC1: QUARANTINE rows have valid q_code
- [PASS] BC2: No Q15 standalone
- [PASS] BC3: No Q17
- [PASS] BC4: action_sequence starts with parse_source (AUTO/REPAIR)
- [PASS] BC5: Terminal endings consistent (export vs flag_*)
- [PASS] BC6: AUTO rows contain no REPAIR functions
- [PASS] BC7: v4.2 endpoint-specific REPAIR functions present
- [PASS] BC8: family_id_hint references exist
- [PASS] BC9: Distribution within tolerance of (4/30/22/2/2)

failed_checks: 0
