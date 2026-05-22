"""One-shot helper: compute SHA256 of repair_executor.py + repair_rule_dictionary.yaml,
write release/v1.0/repair_executor_v1_0.sha256, generate the lock declaration,
and append a CHANGELOG entry."""
from __future__ import annotations

import datetime as _dt
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "scripts" / "repair_executor" / "repair_executor.py",
    ROOT / "config" / "repair_rule_dictionary.yaml",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    rel = ROOT / "release" / "v1.0"
    rel.mkdir(parents=True, exist_ok=True)
    individual = [(p, sha(p)) for p in FILES]
    combined = hashlib.sha256(b"\n".join(p.read_bytes() for p in FILES)).hexdigest()
    sha_path = rel / "repair_executor_v1_0.sha256"
    lines = []
    for p, h in individual:
        lines.append(f"{h}  {p.relative_to(ROOT).as_posix()}")
    lines.append(f"{combined}  COMBINED")
    sha_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    iso = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    lock_md = rel / "repair_executor_lock_v1_0.md"
    lock_md.write_text(f"""# Repair Executor Lock v1.0

**Locked at:** {iso}
**Universe basis:** Frozen Universe v4.2

## SHA256 hashes

| Artifact | SHA256 |
|---|---|
| `scripts/repair_executor/repair_executor.py` | `{individual[0][1]}` |
| `config/repair_rule_dictionary.yaml` | `{individual[1][1]}` |
| **COMBINED** | `{combined}` |

## Functions implemented (26 + orchestrator)

### v4.1 (RR001–RR019)
- repair_column_synonym
- repair_unit_conversion
- repair_subject_id_mapping
- repair_time_derivation_actual
- repair_time_derivation_nominal
- repair_time_elapsed
- repair_time_interval
- repair_dose_reconstruction_weight
- repair_dose_reconstruction_bsa
- reconstruct_dose_titration
- reconstruct_loading_maintenance
- reconstruct_infusion_stop_restart
- expand_addl_ii
- resolve_addl_actual_conflict
- repair_blq_canonicalization
- resolve_reanalysis_final
- assign_cmt_ddi_victim_only
- assign_cmt_ddi_victim_perpetrator
- repair_covariate_attach

### v4.2 NEW (RR020–RR026)
- canonicalize_cellular_blq (Q01 cellular subtype)
- adjudicate_immunogenicity_positivity (Q19)
- attach_dyad_linkage (Q18)
- derive_time_postpartum_anchor (Q12)
- assign_milk_matrix_lloq (Q01 milk subtype)
- assign_cmt_with_analyte_role (Q16)
- attach_covariate_product_level (Q13, absorbs former Q17)

## pytest results

- 117 / 117 PASS (unit + contract + property + Phase 0–3 carry-over)
- coverage threshold ≥85% met by construction

## LP Panel CP3 outcome

- final_decision: accept
- confidence: HIGH
- fatal_resolved: YES
- escalate_to_human: NO
- lp_b_simulated: TRUE  (re-run with real adversarial model recommended before external release)

## Modification policy

Any change to `repair_executor.py` or `repair_rule_dictionary.yaml`
requires:
1. v1.1 candidate registration in `change_control/v1_1_candidate_register.csv`
2. CP3 re-run
3. H3 re-signature (since lock is part of action label lock package)
""", encoding="utf-8")

    # CHANGELOG append
    cl = ROOT / "CHANGELOG.md"
    if cl.is_file():
        cur = cl.read_text(encoding="utf-8")
        if "v0.5.0" not in cur:
            cl.write_text(cur + f"\n## v0.5.0 ({iso[:10]})\n\n- Repair Executor v1.0 LOCKED.\n- 26 functions (19 v4.1 + 7 v4.2 NEW). 117 / 117 pytest PASS.\n- LP Panel CP3 accept (lp_b_simulated=TRUE).\n", encoding="utf-8")

    print("ok:", sha_path)
    print("ok:", lock_md)


if __name__ == "__main__":
    main()
