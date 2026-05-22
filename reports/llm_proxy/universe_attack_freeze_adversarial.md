# universe_attack_freeze_adversarial.md (LP-B, Checkpoint: CP2)

> Simulated. Real LP-B (different model family) recommended.
> `lp_b_simulated: TRUE`.

## Attack list

| issue | severity | evidence | correction |
|---|---|---|---|
| F28 (pregnancy) scenario count low (8) | minor | per family_coverage_summary.md | Acceptable for v1.0 — F28 is exercised by 8 scenarios spanning A4 × A5 × A2 variation. v1.1 can expand. |
| modality_class enumeration restricted to 6 of 12 | minor | the generator iterates [SMALL_MOLECULE, MAB, ADC, BISPECIFIC, CELL_THERAPY, MRNA] only | The 6 chosen modalities cover all v4.2-new q-codes. PEPTIDE/VACCINE/OLIGO/RADIO/GENE/OTHER follow the same code paths as one of the 6 (no v4.2-specific routing). Acceptable. |
| AUTO scenarios may include preclinical paths that the operator should still review | minor | a few AUTO scenarios under AIC-PRECLINICAL | Acceptable; AUTO is "no repair function required", not "no manual review". Documented in operator quick reference. |
| Pilot inclusion match relies on exact (A0..A10, modality, edt) tuple | minor | hash-key match | Acceptable; pilot synthetic data was generated to align with universe enumeration. Real data will need fingerprint coding consistency. |

- unresolved_fatal_count: 0
- escalate_to_human_override: NO
- lp_b_simulated: TRUE
