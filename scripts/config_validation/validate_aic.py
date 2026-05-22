"""AIC schema validator for pmx_universe_v5_1 (Frozen Universe v4.2).

Runs 8 validators (A01..A08) against an Analysis Intent Contract instance
(a single YAML file declaring fields per analysis_intent_contract_template).

Usage:
    python scripts/config_validation/validate_aic.py \\
        --aic-file <path/to/aic.yaml> \\
        --out reports/aic_validation_report.md
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ----------------------------------------------------------------------
# Q-code mapping (must match quarantine_reason_codes.yaml entries used
# by the dependency_constraints).
# ----------------------------------------------------------------------

AIC_TYPES_REQUIRING_ENDPOINT = {
    "AIC-PKPD", "AIC-ER", "AIC-TTE", "AIC-BIOMARKER",
    "AIC-CELL_THERAPY", "AIC-IMMUNOGEN", "AIC-LACTATION",
}

MULTI_ANALYTE_A8_STATES = {
    "MULTI-CMT-DEFINED", "DDI-VICTIM-PERPETRATOR", "METABOLITE-DEFINED",
}

MODALITIES_REQUIRING_ANALYTE_ROLE = {
    "ADC", "BISPECIFIC", "CELL_THERAPY", "GENE_THERAPY",
}


@dataclass
class AicError:
    validator: str
    detail: str
    q_code: str | None = None


@dataclass
class AicReport:
    aic_path: Path
    errors: list[AicError] = field(default_factory=list)

    def add(self, validator: str, detail: str, q_code: str | None = None) -> None:
        self.errors.append(AicError(validator, detail, q_code))


def _get(aic: dict, key: str) -> Any:
    if not aic:
        return None
    return aic.get(key)


def _present(aic: dict, key: str) -> bool:
    val = _get(aic, key)
    if val is None:
        return False
    if isinstance(val, str) and not val.strip():
        return False
    if isinstance(val, (list, dict)) and not val:
        return False
    return True


# ----------------------------------------------------------------------
# Validators
# ----------------------------------------------------------------------

def a01_core_fields_present(rep: AicReport, aic: dict) -> None:
    for f in ("model_family", "analysis_objective"):
        if not _present(aic, f):
            rep.add("A01", f"required field missing: {f}", q_code="Q11")


def a02_endpoint_data_type_for_complex_aic(rep: AicReport, aic: dict) -> None:
    aic_type = _get(aic, "aic_type") or _get(aic, "A0_state")
    if aic_type in AIC_TYPES_REQUIRING_ENDPOINT and not _present(aic, "endpoint_data_type"):
        rep.add("A02", f"endpoint_data_type required for aic_type={aic_type}", q_code="Q11")


def a03_cellular_lloq_for_cellular_kinetics(rep: AicReport, aic: dict) -> None:
    if _get(aic, "endpoint_data_type") == "CELLULAR_KINETICS":
        if not _present(aic, "cellular_LLOQ_derivation_policy"):
            rep.add("A03", "cellular_LLOQ_derivation_policy required for endpoint_data_type=CELLULAR_KINETICS",
                    q_code="Q01")


def a04_positivity_rule_for_immunogenicity(rep: AicReport, aic: dict) -> None:
    if _get(aic, "endpoint_data_type") == "IMMUNOGENICITY":
        if not _present(aic, "positivity_adjudication_rule"):
            rep.add("A04", "positivity_adjudication_rule required for endpoint_data_type=IMMUNOGENICITY",
                    q_code="Q19")


def a05_dyad_and_anchor_for_maternal_infant(rep: AicReport, aic: dict) -> None:
    if _get(aic, "endpoint_data_type") == "MATERNAL_INFANT_PK":
        if not _present(aic, "dyad_linkage_policy"):
            rep.add("A05", "dyad_linkage_policy required for endpoint_data_type=MATERNAL_INFANT_PK",
                    q_code="Q18")
        if not _present(aic, "delivery_anchor_policy"):
            rep.add("A05", "delivery_anchor_policy required for endpoint_data_type=MATERNAL_INFANT_PK",
                    q_code="Q12")


def a06_milk_matrix_lloq_for_milk_pk(rep: AicReport, aic: dict) -> None:
    if _get(aic, "endpoint_data_type") == "MILK_PK":
        if not _present(aic, "milk_matrix_lloq_policy"):
            rep.add("A06", "milk_matrix_lloq_policy required for endpoint_data_type=MILK_PK",
                    q_code="Q01")


def a07_analyte_role_for_required_modalities(rep: AicReport, aic: dict) -> None:
    modality = _get(aic, "modality_class")
    a8_state = _get(aic, "A8_state")
    if (
        modality in MODALITIES_REQUIRING_ANALYTE_ROLE
        and a8_state in MULTI_ANALYTE_A8_STATES
        and not _present(aic, "analyte_role")
    ):
        rep.add("A07", f"analyte_role required for modality_class={modality} with A8={a8_state}",
                q_code="Q16")


# Map "policy field name" → expected q_code when missing under its trigger.
_MISSING_TO_QCODE = {
    "model_family": "Q11",
    "analysis_objective": "Q11",
    "endpoint_data_type": "Q11",
    "cellular_LLOQ_derivation_policy": "Q01",
    "positivity_adjudication_rule": "Q19",
    "dyad_linkage_policy": "Q18",
    "delivery_anchor_policy": "Q12",
    "milk_matrix_lloq_policy": "Q01",
    "analyte_role": "Q16",
    "product_level_covariate_linkage_policy": "Q13",
    "addl_actual_conflict_policy": "Q14",
    "infusion_reconstruction_policy": "Q04",
    "covariate_policy": "Q06",
    "cmt_analyte_policy": "Q09",
    "external_linkage_policy": "Q07",
    "bioanalytical_final_selection_policy": "Q15A",
    "reanalysis_final_selection_policy": "Q15D",
    "adherence_imputation_policy": "Q15C",
    "id_disambiguation_policy": "Q03",
}


def a08_qcode_mapping_consistent(rep: AicReport, aic: dict) -> None:
    """Cross-check: every error A01..A07 surfaced for a missing field maps
    to the q_code declared for that field in _MISSING_TO_QCODE."""
    seen_pairs: set[tuple[str, str | None]] = set()
    for e in rep.errors:
        if e.validator == "A08":
            continue
        # extract field name from the detail string (prefix before space)
        # Detail strings look like: "<field> required ..." or "required field missing: <field>"
        text = e.detail
        if "required field missing:" in text:
            field_name = text.split(":", 1)[1].strip()
        else:
            # take first word as field name
            field_name = text.split()[0]
        expected = _MISSING_TO_QCODE.get(field_name)
        if expected and e.q_code != expected:
            pair = (field_name, e.q_code)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            rep.add("A08",
                    f"q_code mismatch for missing {field_name}: got {e.q_code}, expected {expected}",
                    q_code=None)


VALIDATORS = [
    ("A01", a01_core_fields_present),
    ("A02", a02_endpoint_data_type_for_complex_aic),
    ("A03", a03_cellular_lloq_for_cellular_kinetics),
    ("A04", a04_positivity_rule_for_immunogenicity),
    ("A05", a05_dyad_and_anchor_for_maternal_infant),
    ("A06", a06_milk_matrix_lloq_for_milk_pk),
    ("A07", a07_analyte_role_for_required_modalities),
    ("A08", a08_qcode_mapping_consistent),
]


def run(aic_path: Path) -> AicReport:
    aic = yaml.safe_load(aic_path.read_text(encoding="utf-8")) or {}
    rep = AicReport(aic_path=aic_path)
    for vid, fn in VALIDATORS:
        try:
            fn(rep, aic)
        except Exception as exc:
            rep.add(vid, f"validator raised {type(exc).__name__}: {exc}")
    return rep


def write_report(rep: AicReport, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# AIC Validation Report",
        "",
        f"generated_at: {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}",
        f"aic_file: {rep.aic_path}",
        f"total_validators: {len(VALIDATORS)}",
        f"total_errors: {len(rep.errors)}",
        "",
        "## errors",
        "",
    ]
    if not rep.errors:
        lines.append("(none)")
    else:
        for e in rep.errors:
            lines.append(f"- validator: {e.validator} | q_code: {e.q_code or '-'} | detail: {e.detail}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an AIC instance.")
    parser.add_argument("--aic-file", required=True, type=Path)
    parser.add_argument("--out", default=Path("reports/aic_validation_report.md"), type=Path)
    args = parser.parse_args(argv)
    rep = run(args.aic_file)
    write_report(rep, args.out)
    print(f"total_errors: {len(rep.errors)}")
    for e in rep.errors:
        print(f"ERROR | {e.validator} | q={e.q_code or '-'} | {e.detail}")
    return 0 if not rep.errors else 1


if __name__ == "__main__":
    sys.exit(main())
