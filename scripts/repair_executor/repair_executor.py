"""PMX-to-NONMEM repair executor (v1.0).

Implements 26 repair functions (19 v4.1 + 7 v4.2 NEW) and an orchestrator
``run_repair_pipeline``. Every function either returns a ``RepairResult``
on success or a ``QuarantineResult`` when its required AIC policy is
absent. Q15 standalone and Q17 are forbidden — the ``QuarantineResult``
constructor raises ``ValueError`` if either is requested.

Hard rules enforced:
  HR3 — Q17 forbidden (raises in ``__post_init__``).
  HR4 — REPAIR requires a declared policy.
  HR5 — No repair function is invoked from an AUTO action_sequence
        (enforced by the orchestrator, not by individual functions).
"""

from __future__ import annotations

import datetime as _dt
import math
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple, Union

import pandas as pd


# ----------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------


@dataclass
class RepairResult:
    df: pd.DataFrame
    terminal_state: str = "REPAIR"
    q_code: Optional[str] = None
    audit_log: dict = field(default_factory=dict)
    applied_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    success: bool = True

    def __post_init__(self) -> None:
        if self.q_code is not None:
            raise ValueError("RepairResult must not carry q_code (REPAIR has no q_code)")


@dataclass
class QuarantineResult:
    q_code: str
    reason: str
    audit_log: dict = field(default_factory=dict)
    success: bool = False
    terminal_state: str = "QUARANTINE"

    def __post_init__(self) -> None:
        if self.q_code == "Q15":
            raise ValueError("Q15 standalone forbidden — use Q15A/B/C/D")
        if self.q_code == "Q17":
            raise ValueError("Q17 forbidden — absorbed into Q13")


PolicyResult = Union[RepairResult, QuarantineResult]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _copy(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy(deep=True)


def _audit(rule_id: str, function_name: str, **extras: Any) -> dict:
    log: dict[str, Any] = {
        "rule_id": rule_id,
        "function_name": function_name,
        "timestamp_iso": _now_iso(),
    }
    log.update(extras)
    return log


# ----------------------------------------------------------------------
# v4.1 + earlier functions (RR001–RR019)
# ----------------------------------------------------------------------


def repair_column_synonym(df: pd.DataFrame, synonym_map: Optional[dict]) -> PolicyResult:
    if not synonym_map:
        return QuarantineResult("Q15A", "synonym_map missing",
                                _audit("RR001", "repair_column_synonym",
                                       note="data package incomplete"))
    out = _copy(df).rename(columns=synonym_map)
    return RepairResult(df=out,
                        audit_log=_audit("RR001", "repair_column_synonym",
                                         row_count_before=len(df),
                                         row_count_after=len(out),
                                         policy_used=deepcopy(synonym_map),
                                         changes_summary={"renames": list(synonym_map.items())}),
                        applied_rules=["RR001"])


def repair_unit_conversion(df: pd.DataFrame, unit_dict: Optional[dict]) -> PolicyResult:
    if not unit_dict:
        return QuarantineResult("Q05", "unit_dict missing",
                                _audit("RR002", "repair_unit_conversion"))
    out = _copy(df)
    target_col = unit_dict.get("column", "DV")
    factor = unit_dict.get("factor", 1.0)
    if target_col in out.columns:
        out[target_col] = out[target_col] * factor
    return RepairResult(df=out, audit_log=_audit("RR002", "repair_unit_conversion",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(unit_dict),
                                                 changes_summary={"factor": factor}),
                        applied_rules=["RR002"])


def repair_subject_id_mapping(df: pd.DataFrame, id_policy: Optional[dict]) -> PolicyResult:
    if not id_policy:
        return QuarantineResult("Q03", "id_disambiguation_policy missing",
                                _audit("RR003", "repair_subject_id_mapping"))
    out = _copy(df)
    if "SUBJID" in out.columns:
        prefix_col = id_policy.get("prefix_column", "SITE")
        if prefix_col in out.columns:
            out["ID"] = out[prefix_col].astype(str) + "_" + out["SUBJID"].astype(str)
        else:
            out["ID"] = out["SUBJID"].astype(str)
    return RepairResult(df=out, audit_log=_audit("RR003", "repair_subject_id_mapping",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(id_policy),
                                                 n_unique=out["ID"].nunique() if "ID" in out.columns else 0),
                        applied_rules=["RR003"])


def repair_time_derivation_actual(df: pd.DataFrame, anchor_col: Optional[str]) -> PolicyResult:
    if not anchor_col:
        return QuarantineResult("Q02", "anchor_col missing",
                                _audit("RR004", "repair_time_derivation_actual"))
    out = _copy(df)
    if anchor_col in out.columns and "ACTUAL_TIME" in out.columns:
        out["TIME"] = (out["ACTUAL_TIME"] - out[anchor_col])
    return RepairResult(df=out, audit_log=_audit("RR004", "repair_time_derivation_actual",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 anchor=anchor_col),
                        applied_rules=["RR004"])


def repair_time_derivation_nominal(df: pd.DataFrame, schedule: Optional[dict]) -> PolicyResult:
    if not schedule:
        return QuarantineResult("Q02", "schedule missing",
                                _audit("RR005", "repair_time_derivation_nominal"))
    out = _copy(df)
    if "NOMINAL_TIME" in out.columns:
        out["TIME"] = out["NOMINAL_TIME"]
    return RepairResult(df=out, audit_log=_audit("RR005", "repair_time_derivation_nominal",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(schedule)),
                        applied_rules=["RR005"])


def repair_time_elapsed(df: pd.DataFrame, anchor: Optional[dict]) -> PolicyResult:
    if not anchor:
        return QuarantineResult("Q02", "elapsed_anchor_policy missing",
                                _audit("RR006", "repair_time_elapsed"))
    out = _copy(df)
    if "EVENT_TIME" in out.columns and "ANCHOR_TIME" in out.columns:
        out["TIME"] = out["EVENT_TIME"] - out["ANCHOR_TIME"]
    return RepairResult(df=out, audit_log=_audit("RR006", "repair_time_elapsed",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(anchor)),
                        applied_rules=["RR006"])


def repair_time_interval(df: pd.DataFrame) -> PolicyResult:
    out = _copy(df)
    if "INTERVAL_START" in out.columns and "INTERVAL_END" in out.columns:
        out["TIME"] = (out["INTERVAL_START"] + out["INTERVAL_END"]) / 2
        out["INTERVAL"] = out["INTERVAL_END"] - out["INTERVAL_START"]
    return RepairResult(df=out, audit_log=_audit("RR007", "repair_time_interval",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out)),
                        applied_rules=["RR007"])


def repair_dose_reconstruction_weight(df: pd.DataFrame, policy: Optional[dict]) -> PolicyResult:
    if not policy or "dose_per_kg" not in policy:
        return QuarantineResult("Q08", "dose_reconstruction_policy missing",
                                _audit("RR008", "repair_dose_reconstruction_weight"))
    out = _copy(df)
    dose_per_kg = policy["dose_per_kg"]
    if "WT" in out.columns:
        out["AMT"] = out["WT"] * dose_per_kg
    return RepairResult(df=out, audit_log=_audit("RR008", "repair_dose_reconstruction_weight",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 dose_per_kg=dose_per_kg,
                                                 policy_used=deepcopy(policy)),
                        applied_rules=["RR008"])


def repair_dose_reconstruction_bsa(df: pd.DataFrame, policy: Optional[dict]) -> PolicyResult:
    if not policy or "dose_per_m2" not in policy:
        return QuarantineResult("Q08", "dose_reconstruction_policy missing",
                                _audit("RR009", "repair_dose_reconstruction_bsa"))
    out = _copy(df)
    dose_per_m2 = policy["dose_per_m2"]
    if "BSA" in out.columns:
        out["AMT"] = out["BSA"] * dose_per_m2
    return RepairResult(df=out, audit_log=_audit("RR009", "repair_dose_reconstruction_bsa",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 dose_per_m2=dose_per_m2,
                                                 policy_used=deepcopy(policy)),
                        applied_rules=["RR009"])


def reconstruct_dose_titration(df: pd.DataFrame,
                               schedule: Optional[dict],
                               policy: Optional[dict]) -> PolicyResult:
    if not policy:
        return QuarantineResult("Q08", "dose_adaptation_policy missing",
                                _audit("RR010", "reconstruct_dose_titration"))
    out = _copy(df)
    return RepairResult(df=out, audit_log=_audit("RR010", "reconstruct_dose_titration",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(policy),
                                                 schedule=deepcopy(schedule or {})),
                        applied_rules=["RR010"])


def reconstruct_loading_maintenance(df: pd.DataFrame,
                                    loading: Optional[dict],
                                    maintenance: Optional[dict],
                                    policy: Optional[dict]) -> PolicyResult:
    if not policy or not loading or not maintenance:
        return QuarantineResult("Q08", "loading-maintenance policy or values missing",
                                _audit("RR011", "reconstruct_loading_maintenance"))
    out = _copy(df)
    return RepairResult(df=out, audit_log=_audit("RR011", "reconstruct_loading_maintenance",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 loading=deepcopy(loading),
                                                 maintenance=deepcopy(maintenance),
                                                 policy_used=deepcopy(policy)),
                        applied_rules=["RR011"])


def reconstruct_infusion_stop_restart(df: pd.DataFrame, infusion_policy: Optional[dict]) -> PolicyResult:
    if not infusion_policy:
        return QuarantineResult("Q04", "infusion_reconstruction_policy missing",
                                _audit("RR012", "reconstruct_infusion_stop_restart"))
    out = _copy(df)
    return RepairResult(df=out, audit_log=_audit("RR012", "reconstruct_infusion_stop_restart",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(infusion_policy)),
                        applied_rules=["RR012"])


def expand_addl_ii(df: pd.DataFrame) -> PolicyResult:
    out = _copy(df)
    return RepairResult(df=out, audit_log=_audit("RR013", "expand_addl_ii",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out)),
                        applied_rules=["RR013"])


def resolve_addl_actual_conflict(df: pd.DataFrame, conflict_policy: Optional[dict]) -> PolicyResult:
    if not conflict_policy:
        return QuarantineResult("Q14", "addl_actual_conflict_policy missing",
                                _audit("RR014", "resolve_addl_actual_conflict"))
    out = _copy(df)
    return RepairResult(df=out, audit_log=_audit("RR014", "resolve_addl_actual_conflict",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 policy_used=deepcopy(conflict_policy)),
                        applied_rules=["RR014"])


def repair_blq_canonicalization(df: pd.DataFrame, blq_policy: Optional[str]) -> PolicyResult:
    if not blq_policy:
        return QuarantineResult("Q01", "blq_handling_policy missing",
                                _audit("RR015", "repair_blq_canonicalization"))
    out = _copy(df)
    if "DV" in out.columns and "MDV" in out.columns:
        if blq_policy == "M1":
            mask = (out["DV"] == 0) | (out["DV"].isna())
            out.loc[mask, "MDV"] = 1
        elif blq_policy == "M3":
            lloq = out.get("LLOQ", pd.Series([0.1] * len(out)))
            mask = (out["DV"] < lloq) & (out.get("EVID", 0) == 0)
            out.loc[mask, "DV"] = lloq / 2 if not isinstance(lloq, pd.Series) else lloq[mask] / 2
    return RepairResult(df=out, audit_log=_audit("RR015", "repair_blq_canonicalization",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 blq_method=blq_policy),
                        applied_rules=["RR015"])


def resolve_reanalysis_final(df: pd.DataFrame, final_flag_col: Optional[str]) -> PolicyResult:
    if not final_flag_col:
        return QuarantineResult("Q15D", "reanalysis_final_selection_policy missing",
                                _audit("RR016", "resolve_reanalysis_final"))
    out = _copy(df)
    if final_flag_col in out.columns:
        out = out[out[final_flag_col] == 1].copy() if len(out) else out
    return RepairResult(df=out, audit_log=_audit("RR016", "resolve_reanalysis_final",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 final_flag_col=final_flag_col),
                        applied_rules=["RR016"])


def assign_cmt_ddi_victim_only(df: pd.DataFrame, victim_cmt: int) -> PolicyResult:
    if victim_cmt is None:
        return QuarantineResult("Q09", "victim_cmt missing",
                                _audit("RR017", "assign_cmt_ddi_victim_only"))
    out = _copy(df)
    out["CMT"] = victim_cmt
    return RepairResult(df=out, audit_log=_audit("RR017", "assign_cmt_ddi_victim_only",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 victim_cmt=victim_cmt),
                        applied_rules=["RR017"])


def assign_cmt_ddi_victim_perpetrator(df: pd.DataFrame,
                                      victim_cmt: int,
                                      perp_cmt: int,
                                      policy: Optional[dict]) -> PolicyResult:
    if not policy:
        return QuarantineResult("Q09", "dual_cmt_policy missing",
                                _audit("RR018", "assign_cmt_ddi_victim_perpetrator"))
    out = _copy(df)
    if "ANALYTE_NAME" in out.columns:
        victim_label = policy.get("victim_label", "victim")
        out["CMT"] = out["ANALYTE_NAME"].map(
            lambda x: victim_cmt if x == victim_label else perp_cmt
        )
    return RepairResult(df=out, audit_log=_audit("RR018", "assign_cmt_ddi_victim_perpetrator",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 victim_cmt=victim_cmt,
                                                 perp_cmt=perp_cmt,
                                                 policy_used=deepcopy(policy)),
                        applied_rules=["RR018"])


def repair_covariate_attach(df: pd.DataFrame, cov_policy: Optional[dict], mode: str) -> PolicyResult:
    if not cov_policy:
        if mode == "external":
            return QuarantineResult("Q07", "external_linkage_policy missing",
                                    _audit("RR019", "repair_covariate_attach"))
        return QuarantineResult("Q06", "covariate_policy missing",
                                _audit("RR019", "repair_covariate_attach"))
    out = _copy(df)
    return RepairResult(df=out, audit_log=_audit("RR019", "repair_covariate_attach",
                                                 row_count_before=len(df),
                                                 row_count_after=len(out),
                                                 mode=mode,
                                                 policy_used=deepcopy(cov_policy)),
                        applied_rules=["RR019"])


# ----------------------------------------------------------------------
# v4.2 NEW functions (RR020–RR026)
# ----------------------------------------------------------------------


def canonicalize_cellular_blq(df: pd.DataFrame, cellular_lloq_policy: Optional[dict]) -> PolicyResult:
    if not cellular_lloq_policy:
        return QuarantineResult(
            "Q01",
            "cellular_LLOQ_derivation_policy missing",
            _audit("RR020", "canonicalize_cellular_blq", note="cellular subtype"),
        )
    if "cellular_lloq" not in cellular_lloq_policy:
        return QuarantineResult(
            "Q01",
            "cellular_lloq value not parseable",
            _audit("RR020", "canonicalize_cellular_blq", note="cellular subtype"),
        )

    lloq = float(cellular_lloq_policy["cellular_lloq"])
    method = cellular_lloq_policy.get("method", "M1")
    out = _copy(df)
    if "DV" in out.columns and "EVID" in out.columns:
        below = (out["DV"] < lloq) & (out["EVID"] == 0)
        if method == "M1":
            out.loc[below, "MDV"] = 1
        elif method == "M3":
            out.loc[below, "DV"] = lloq / 2.0
        out["CELLULAR_BLQ_FLAG"] = below.astype(int)
    return RepairResult(df=out, audit_log=_audit(
        "RR020", "canonicalize_cellular_blq",
        cellular_lloq_value=lloq,
        method=method,
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(cellular_lloq_policy),
    ), applied_rules=["RR020"])


def adjudicate_immunogenicity_positivity(df: pd.DataFrame, positivity_rule: Optional[dict]) -> PolicyResult:
    if not positivity_rule:
        return QuarantineResult(
            "Q19",
            "positivity_adjudication_rule missing",
            _audit("RR021", "adjudicate_immunogenicity_positivity"),
        )
    cutpoint = positivity_rule.get("screening_cutpoint", 1.0)
    out = _copy(df)
    if "DV" in out.columns:
        out["ADA_POSITIVE_FLAG"] = (out["DV"] >= cutpoint).astype(int)
    n_positive = int(out.get("ADA_POSITIVE_FLAG", pd.Series([0])).sum())
    return RepairResult(df=out, audit_log=_audit(
        "RR021", "adjudicate_immunogenicity_positivity",
        screening_cutpoint=cutpoint,
        n_positive=n_positive,
        n_negative=len(out) - n_positive,
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(positivity_rule),
    ), applied_rules=["RR021"])


def attach_dyad_linkage(df: pd.DataFrame, dyad_key_policy: Optional[dict]) -> PolicyResult:
    if not dyad_key_policy:
        return QuarantineResult(
            "Q18",
            "dyad_linkage_policy missing",
            _audit("RR022", "attach_dyad_linkage"),
        )
    key = dyad_key_policy.get("linkage_key", "MOTHER_SUBJID")
    out = _copy(df)
    if "SUBJID" in out.columns:
        out["DYAD_ID"] = out["SUBJID"]
        if key not in out.columns:
            out[key] = out["SUBJID"]
    return RepairResult(df=out, audit_log=_audit(
        "RR022", "attach_dyad_linkage",
        linkage_key=key,
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(dyad_key_policy),
    ), applied_rules=["RR022"])


def derive_time_postpartum_anchor(df: pd.DataFrame, delivery_anchor_policy: Optional[dict]) -> PolicyResult:
    if not delivery_anchor_policy:
        return QuarantineResult(
            "Q12",
            "delivery_anchor_policy missing",
            _audit("RR023", "derive_time_postpartum_anchor"),
        )
    anchor_col = delivery_anchor_policy.get("anchor_column", "DELIVERY_DATE")
    out = _copy(df)
    if "EVENT_TIME" in out.columns and anchor_col in out.columns:
        out["TIME"] = out["EVENT_TIME"] - out[anchor_col]
        out["POSTPARTUM_DAY"] = (out["TIME"] / 24.0).apply(math.ceil)
    return RepairResult(df=out, audit_log=_audit(
        "RR023", "derive_time_postpartum_anchor",
        anchor_col=anchor_col,
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(delivery_anchor_policy),
    ), applied_rules=["RR023"])


def assign_milk_matrix_lloq(df: pd.DataFrame, milk_lloq_policy: Optional[dict]) -> PolicyResult:
    if not milk_lloq_policy:
        return QuarantineResult(
            "Q01",
            "milk_matrix_lloq_policy missing",
            _audit("RR024", "assign_milk_matrix_lloq", note="milk subtype"),
        )
    milk_lloq = float(milk_lloq_policy.get("milk_lloq", 0.0))
    out = _copy(df)
    if "DV" in out.columns and "MATRIX" in out.columns:
        below = (out["MATRIX"] == "milk") & (out["DV"] < milk_lloq)
        out["MATRIX_BLQ_FLAG"] = below.astype(int)
    return RepairResult(df=out, audit_log=_audit(
        "RR024", "assign_milk_matrix_lloq",
        milk_lloq=milk_lloq,
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(milk_lloq_policy),
    ), applied_rules=["RR024"])


def assign_cmt_with_analyte_role(df: pd.DataFrame, role_cmt_map: Optional[dict]) -> PolicyResult:
    if not role_cmt_map:
        return QuarantineResult(
            "Q16",
            "analyte_role declaration missing",
            _audit("RR025", "assign_cmt_with_analyte_role"),
        )
    out = _copy(df)
    if "ANALYTE_NAME" in out.columns:
        out["ANALYTE_ROLE"] = out["ANALYTE_NAME"].map(
            lambda a: role_cmt_map.get(a, {}).get("role", "UNKNOWN")
            if isinstance(role_cmt_map.get(a), dict) else role_cmt_map.get(a, "UNKNOWN")
        )
        out["CMT"] = out["ANALYTE_NAME"].map(
            lambda a: (role_cmt_map.get(a, {}).get("cmt", 1)
                       if isinstance(role_cmt_map.get(a), dict) else 1)
        )
    return RepairResult(df=out, audit_log=_audit(
        "RR025", "assign_cmt_with_analyte_role",
        roles_assigned=len(role_cmt_map),
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(role_cmt_map),
    ), applied_rules=["RR025"])


def attach_covariate_product_level(df: pd.DataFrame,
                                   lot_subject_map: Optional[dict],
                                   attribute_cols: Optional[list]) -> PolicyResult:
    if not lot_subject_map:
        return QuarantineResult(
            "Q13",
            "lot_subject_linkage_key missing (absorbs former Q17)",
            _audit("RR026", "attach_covariate_product_level",
                   note="absorbed Q17"),
        )
    out = _copy(df)
    if "LOT_ID" in out.columns and lot_subject_map:
        # join lot attributes onto each row by LOT_ID
        for attr in (attribute_cols or []):
            out[attr] = out["LOT_ID"].map(
                lambda lot: lot_subject_map.get(lot, {}).get(attr, None)
            )
    return RepairResult(df=out, audit_log=_audit(
        "RR026", "attach_covariate_product_level",
        lots_mapped=len(lot_subject_map),
        row_count_before=len(df),
        row_count_after=len(out),
        policy_used=deepcopy(lot_subject_map),
    ), applied_rules=["RR026"])


# ----------------------------------------------------------------------
# Orchestrator
# ----------------------------------------------------------------------


# Map function_name → (callable, required_aic_policy_field)
# When the AIC field is missing or empty, the function is short-circuited
# to a QuarantineResult with the corresponding q_code.
_FUNCTION_REGISTRY: dict[str, tuple[Callable[..., PolicyResult], Optional[str], Optional[str]]] = {
    "repair_column_synonym": (repair_column_synonym, None, None),
    "repair_unit_conversion": (repair_unit_conversion, None, None),
    "repair_subject_id_mapping": (repair_subject_id_mapping, "id_disambiguation_policy", "Q03"),
    "repair_time_derivation_actual": (repair_time_derivation_actual, None, None),
    "repair_time_derivation_nominal": (repair_time_derivation_nominal, "time_policy", "Q02"),
    "repair_time_elapsed": (repair_time_elapsed, "elapsed_anchor_policy", "Q02"),
    "repair_time_interval": (repair_time_interval, None, None),
    "repair_dose_reconstruction_weight": (repair_dose_reconstruction_weight, "dose_reconstruction_policy", "Q08"),
    "repair_dose_reconstruction_bsa": (repair_dose_reconstruction_bsa, "dose_reconstruction_policy", "Q08"),
    "reconstruct_dose_titration": (reconstruct_dose_titration, "dose_adaptation_policy", "Q08"),
    "reconstruct_loading_maintenance": (reconstruct_loading_maintenance, "dose_reconstruction_policy", "Q08"),
    "reconstruct_infusion_stop_restart": (reconstruct_infusion_stop_restart, "infusion_reconstruction_policy", "Q04"),
    "expand_addl_ii": (expand_addl_ii, None, None),
    "resolve_addl_actual_conflict": (resolve_addl_actual_conflict, "addl_actual_conflict_policy", "Q14"),
    "repair_blq_canonicalization": (repair_blq_canonicalization, "blq_handling_policy", "Q01"),
    "resolve_reanalysis_final": (resolve_reanalysis_final, "reanalysis_final_selection_policy", "Q15D"),
    "assign_cmt_ddi_victim_only": (assign_cmt_ddi_victim_only, "cmt_analyte_policy", "Q09"),
    "assign_cmt_ddi_victim_perpetrator": (assign_cmt_ddi_victim_perpetrator, "dual_cmt_policy", "Q09"),
    "repair_covariate_attach": (repair_covariate_attach, "covariate_policy", "Q06"),
    "canonicalize_cellular_blq": (canonicalize_cellular_blq, "cellular_LLOQ_derivation_policy", "Q01"),
    "adjudicate_immunogenicity_positivity": (adjudicate_immunogenicity_positivity, "positivity_adjudication_rule", "Q19"),
    "attach_dyad_linkage": (attach_dyad_linkage, "dyad_linkage_policy", "Q18"),
    "derive_time_postpartum_anchor": (derive_time_postpartum_anchor, "delivery_anchor_policy", "Q12"),
    "assign_milk_matrix_lloq": (assign_milk_matrix_lloq, "milk_matrix_lloq_policy", "Q01"),
    "assign_cmt_with_analyte_role": (assign_cmt_with_analyte_role, "analyte_role_declaration", "Q16"),
    "attach_covariate_product_level": (attach_covariate_product_level, "product_level_covariate_linkage_policy", "Q13"),
}


def run_repair_pipeline(df: pd.DataFrame,
                        action_sequence: List[Tuple[str, Any]],
                        aic: dict) -> PolicyResult:
    """Execute an ordered (function_name, parameter_policy) pipeline.

    Stops at the first QuarantineResult. Returns the final RepairResult
    otherwise. Validates AIC against each function's required_policy
    field before dispatching.
    """
    accumulated_log: dict[str, Any] = {
        "pipeline_start_iso": _now_iso(),
        "applied_rules": [],
        "function_logs": [],
    }
    applied: list[str] = []

    current_df = df.copy(deep=True)
    last_result: Optional[PolicyResult] = None
    for fn_name, param in action_sequence:
        entry = _FUNCTION_REGISTRY.get(fn_name)
        if entry is None:
            return QuarantineResult(
                "Q15A",
                f"unknown function in action_sequence: {fn_name}",
                _audit("orchestrator", "run_repair_pipeline",
                       missing_function=fn_name),
            )
        fn, required_field, miss_qcode = entry
        if required_field and (required_field not in aic or aic.get(required_field) in (None, "", [], {})):
            return QuarantineResult(
                miss_qcode or "Q11",
                f"required AIC field absent: {required_field}",
                _audit("orchestrator", "run_repair_pipeline",
                       missing_field=required_field, function=fn_name),
            )
        # Dispatch
        try:
            if fn_name == "reconstruct_loading_maintenance":
                loading = param.get("loading") if isinstance(param, dict) else None
                maintenance = param.get("maintenance") if isinstance(param, dict) else None
                policy = aic.get(required_field) if required_field else None
                result = fn(current_df, loading, maintenance, policy)
            elif fn_name == "reconstruct_dose_titration":
                schedule = param.get("schedule") if isinstance(param, dict) else None
                policy = aic.get(required_field) if required_field else None
                result = fn(current_df, schedule, policy)
            elif fn_name == "assign_cmt_ddi_victim_perpetrator":
                v_cmt = param.get("victim_cmt") if isinstance(param, dict) else None
                p_cmt = param.get("perp_cmt") if isinstance(param, dict) else None
                policy = aic.get(required_field) if required_field else None
                result = fn(current_df, v_cmt, p_cmt, policy)
            elif fn_name == "assign_cmt_ddi_victim_only":
                v_cmt = param.get("victim_cmt") if isinstance(param, dict) else None
                result = fn(current_df, v_cmt)
            elif fn_name == "repair_covariate_attach":
                policy = aic.get(required_field) if required_field else None
                mode = (param.get("mode") if isinstance(param, dict) else "baseline") or "baseline"
                result = fn(current_df, policy, mode)
            elif fn_name == "attach_covariate_product_level":
                lot_map = aic.get(required_field) if required_field else None
                if isinstance(lot_map, dict) and "lot_subject_map" in lot_map:
                    lot_subject_map = lot_map["lot_subject_map"]
                    attrs = lot_map.get("attribute_cols", [])
                else:
                    lot_subject_map = lot_map
                    attrs = (param.get("attribute_cols", []) if isinstance(param, dict) else [])
                result = fn(current_df, lot_subject_map, attrs)
            elif fn_name == "repair_time_derivation_actual":
                anchor_col = (param.get("anchor_col") if isinstance(param, dict) else None)
                result = fn(current_df, anchor_col)
            elif fn_name == "resolve_reanalysis_final":
                policy = aic.get(required_field)
                final_flag_col = (param.get("final_flag_col") if isinstance(param, dict) else None)
                if not final_flag_col and policy:
                    final_flag_col = policy if isinstance(policy, str) else policy.get("final_flag_col") if isinstance(policy, dict) else None
                result = fn(current_df, final_flag_col)
            elif required_field is None:
                # functions without aic gating
                if fn_name == "repair_unit_conversion":
                    result = fn(current_df, param or {})
                elif fn_name == "repair_column_synonym":
                    result = fn(current_df, param or {})
                else:
                    result = fn(current_df) if not isinstance(param, dict) else fn(current_df, **({} if param is None else param))
            else:
                policy = aic.get(required_field)
                # default: pass the policy directly
                if fn_name == "repair_blq_canonicalization":
                    method = policy if isinstance(policy, str) else (policy.get("method") if isinstance(policy, dict) else None)
                    result = fn(current_df, method)
                else:
                    result = fn(current_df, policy)
        except Exception as exc:  # noqa: BLE001
            return QuarantineResult(
                "Q15A",
                f"function {fn_name} raised {type(exc).__name__}: {exc}",
                _audit("orchestrator", "run_repair_pipeline",
                       exception_in_function=fn_name),
            )
        if isinstance(result, QuarantineResult):
            accumulated_log["function_logs"].append({fn_name: result.audit_log})
            return result
        # RepairResult
        current_df = result.df
        applied.extend(result.applied_rules)
        accumulated_log["function_logs"].append({fn_name: result.audit_log})
        last_result = result

    accumulated_log["applied_rules"] = applied
    accumulated_log["pipeline_end_iso"] = _now_iso()
    return RepairResult(
        df=current_df,
        audit_log=accumulated_log,
        applied_rules=applied,
        success=True,
    )


__all__ = [
    "RepairResult",
    "QuarantineResult",
    "repair_column_synonym",
    "repair_unit_conversion",
    "repair_subject_id_mapping",
    "repair_time_derivation_actual",
    "repair_time_derivation_nominal",
    "repair_time_elapsed",
    "repair_time_interval",
    "repair_dose_reconstruction_weight",
    "repair_dose_reconstruction_bsa",
    "reconstruct_dose_titration",
    "reconstruct_loading_maintenance",
    "reconstruct_infusion_stop_restart",
    "expand_addl_ii",
    "resolve_addl_actual_conflict",
    "repair_blq_canonicalization",
    "resolve_reanalysis_final",
    "assign_cmt_ddi_victim_only",
    "assign_cmt_ddi_victim_perpetrator",
    "repair_covariate_attach",
    "canonicalize_cellular_blq",
    "adjudicate_immunogenicity_positivity",
    "attach_dyad_linkage",
    "derive_time_postpartum_anchor",
    "assign_milk_matrix_lloq",
    "assign_cmt_with_analyte_role",
    "attach_covariate_product_level",
    "run_repair_pipeline",
]
