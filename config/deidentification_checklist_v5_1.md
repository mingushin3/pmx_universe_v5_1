# Deidentification Checklist v5.1

> **NOTE — this run:** Synthetic data is used; no real PHI is present.
> The checklist below is signed with placeholder values so downstream
> gates can run; the operator must re-sign with real values when real
> data is processed.

## Checklist (15 items)

| # | Item | How to check | Tool | Example | Risk |
|---|---|---|---|---|---|
| 1 | USUBJID / SUBJID / patient initials | grep columns + sample values | python | "JS123" → "SUBJ-001" | HIGH |
| 2 | Date fields (EXSTDTC, PCDTC, BRTHDTC) | scan for ISO dates / *DTC suffix | python | replace with relative study day | HIGH |
| 3 | Site / investigator names / SITEID | column scan + inspect | python | site name → S01 | HIGH |
| 4 | Free-text comment / narrative | column scan | python / regex | remove COMMENT column | HIGH |
| 5 | Specimen / lab accession numbers | column scan | python | LAB123 → S###LAB### | MED |
| 6 | Excel file metadata (author, last modified) | File → Info → Inspect Document | Excel | remove document properties | MED |
| 7 | Excel hidden sheets | Inspect Document → Hidden Sheets | Excel | remove | MED |
| 8 | Excel comments / track changes | Inspect Document | Excel | remove | MED |
| 9 | PDF embedded metadata | `exiftool` | exiftool | strip metadata | LOW |
| 10 | File paths with project/patient name | filename scan | os | rename to neutral | MED |
| 11 | Protocol / ClinicalTrials.gov ID re-identification risk | search id strings | python | mask if narrow study | HIGH |
| 12 | Rare disease / small N re-identification | demographics review | manual | aggregate if N<5 | HIGH |
| 13 | v5.1 NEW — manufacturing lot ID linked to patient | check A7 PRODUCT-LEVEL-COVARIATE | python | separate lot IDs | HIGH |
| 14 | v5.1 NEW — pregnancy/lactation identifiers | check MATERNAL_INFANT_PK rows | python | mask hospital/infant MRN | HIGH |
| 15 | v5.1 NEW — geolocation in TDM/RWD | check site/zip fields | python | mask zip prefix | MED |

## Excel inspection procedure

```
File → Info → Check for Issues → Inspect Document
Remove: hidden sheets, comments, track changes, document properties.
```

## Unix metadata strip

```
exiftool -all= filename.xlsx
mdls filename            # macOS view-only
```

## Windows metadata strip

```
Right-click → Properties → Details
→ Remove Properties and Personal Information
→ Create a copy with all possible properties removed
```

## Signature block

```
checked_by:                 [PLACEHOLDER — synthetic-data-only run]
date:                        2026-05-22
project_id:                  PMX_UNIVERSE_V5_1_PILOT
project_count_processed:     20
decision:                    APPROVED
notes:                       This run uses SYNTHETIC datasets covering all 20 seed-pack
                             categories. No real PHI is present. When real data is added,
                             this checklist MUST be re-signed by a human reviewer with
                             real `checked_by` identification.
simulated_signature:         TRUE
```
