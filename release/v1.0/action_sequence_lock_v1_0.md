# Action Sequence + AIC Template Lock v1.0

**Locked at:** 2026-05-22 (UTC)
**Universe basis:** Frozen Universe v4.2
**Source decision:** `reports/action_sequence_lock_decision.md`

## SHA256 hashes

| Artifact | SHA256 |
|---|---|
| `config/action_sequence_standard.yaml` | `f4a0324ca311b9d2a7ae83c96f4ca88af3b55b8d4af13ebaeffb33679cc71211` |
| `config/action_function_library.yaml` | `2b37c7660598a4eb76feb3347f92bc378efbb0b7dc194c3b887ec6be65f7f249` |
| `config/analysis_intent_contract_template.yaml` | `88e04aeab0a25bf1e55265ab39097eebcec183d19811b8ca40d73e1841e52f16` |
| **COMBINED** | `6a932eede194e19dea852f5f930089ab59557d8fb977d58533098c4613fd3ce6` |

Hashes also stored verbatim in `release/v1.0/action_sequence_v1_0.sha256`.

## Lock declaration

- [x] All 60 boundary cases semantic-review PASS.
- [x] All 9 boundary-case automated checks PASS (`reports/boundary_case_qcode_validation.md`).
- [x] `action_sequence_standard.yaml` contains all 7 v4.2 NEW functions.
- [x] `analysis_intent_contract_template.yaml` covers all v4.2 conditional fields.

**Action sequence vocabulary and AIC template are FROZEN for v1.0.**
Future modifications require a `change_control/` RFC + H3 re-signature.

## Verification command

```powershell
python -c "import hashlib,pathlib;p=pathlib.Path('config/action_sequence_standard.yaml');print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

Output must match the `action_sequence_standard.yaml` row above.
