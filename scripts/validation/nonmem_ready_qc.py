#!/usr/bin/env python3
"""NONMEM-ready dataset QC (P104).

Validates an AUTO/REPAIR output CSV for NONMEM readiness against the AIC.

Implements 21 checks across 6 groups:
  STRUCTURAL  S01..S05
  EVENT/DOSING E01..E05
  BLQ/MDV      B01..B03
  CMT          C01..C03
  v4.2         V01..V04
  AUDIT LOG    A01

CLI:
  python3 scripts/validation/nonmem_ready_qc.py \\
      --dataset    path/to/output.csv \\
      --aic        path/to/aic.yaml \\
      --audit-log  path/to/audit.json \\
      --out        path/to/qc_report.md

Exit code: 0 = all PASS; 1 = at least one FAIL.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


MIN_REQUIRED_COLUMNS = ["ID", "TIME", "DV", "MDV", "EVID"]
OPTIONAL_DOSE_COLUMNS = ["AMT", "RATE", "CMT"]
EVID_ALLOWED = {0, 1, 2, 3, 4}
BLQ_ALLOWED = {"M1", "M3", "M4", "", None}
COLUMN_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
AUDIT_REQUIRED_FIELDS = {
    "decision_path", "terminal_state", "action_sequence_executed",
    "timestamp_iso",
}
AUDIT_OPTIONAL_BUT_TRACKED = {"q_code", "parameter_policies", "input_data_summary",
                              "operator", "aic_hash"}


# ---------------------------------------------------------------------------
@dataclass
class CheckResult:
    code: str
    name: str
    status: str  # PASS / FAIL / SKIP
    detail: str = ""
    severity: str = "ERROR"  # ERROR / WARN

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "name": self.name, "status": self.status,
                "detail": self.detail, "severity": self.severity}


@dataclass
class QCContext:
    dataset_path: Path
    aic: dict[str, Any] = field(default_factory=dict)
    audit_log: dict[str, Any] = field(default_factory=dict)
    rows: list[dict[str, str]] = field(default_factory=list)
    header: list[str] = field(default_factory=list)
    encoding: str = "utf-8"
    has_bom: bool = False
    delimiter: str = ","
    raw_bytes: bytes = b""


# ---------------------------------------------------------------------------
def _is_na(s: str | None) -> bool:
    return s is None or s == "" or str(s).strip().upper() in ("NA", "N/A", ".", "NAN")


def _to_float(s: str | None) -> float | None:
    if _is_na(s):
        return None
    try:
        return float(str(s).strip())
    except ValueError:
        return None


def _to_int(s: str | None) -> int | None:
    if _is_na(s):
        return None
    try:
        v = float(str(s).strip())
        if not v.is_integer():
            return None
        return int(v)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
def load_context(dataset: Path, aic_path: Path | None, audit_log_path: Path | None) -> QCContext:
    raw = dataset.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig" if has_bom else "utf-8", errors="replace")
    # Determine delimiter from header line.
    header_line = text.split("\n", 1)[0]
    delimiter = "\t" if "\t" in header_line else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    aic_data: dict[str, Any] = {}
    audit_data: dict[str, Any] = {}
    if aic_path and aic_path.is_file():
        aic_data = yaml.safe_load(aic_path.read_text(encoding="utf-8")) or {}
        if isinstance(aic_data, dict) and "analysis_intent_contract" in aic_data:
            aic_data = aic_data["analysis_intent_contract"]
    if audit_log_path and audit_log_path.is_file():
        if audit_log_path.suffix.lower() == ".json":
            audit_data = json.loads(audit_log_path.read_text(encoding="utf-8"))
        else:
            audit_data = yaml.safe_load(audit_log_path.read_text(encoding="utf-8")) or {}
    return QCContext(
        dataset_path=dataset,
        aic=aic_data,
        audit_log=audit_data,
        rows=rows,
        header=reader.fieldnames or [],
        encoding="utf-8",
        has_bom=has_bom,
        delimiter=delimiter,
        raw_bytes=raw,
    )


# ---------------------------------------------------------------------------
# STRUCTURAL S01..S05
# ---------------------------------------------------------------------------
def check_s01(ctx: QCContext) -> CheckResult:
    missing = [c for c in MIN_REQUIRED_COLUMNS if c not in ctx.header]
    if missing:
        return CheckResult("S01", "Required columns present", "FAIL",
                           f"missing columns: {missing}")
    return CheckResult("S01", "Required columns present", "PASS",
                       f"all of {MIN_REQUIRED_COLUMNS} present")


def check_s02(ctx: QCContext) -> CheckResult:
    bad = {}
    numeric_cols = [c for c in ["ID", "TIME", "DV", "AMT", "RATE"] if c in ctx.header]
    int_cols = [c for c in ["MDV", "EVID", "CMT"] if c in ctx.header]
    for c in numeric_cols:
        for i, r in enumerate(ctx.rows, start=2):
            if not _is_na(r.get(c)) and _to_float(r.get(c)) is None:
                bad.setdefault(c, []).append(i)
                break
    for c in int_cols:
        for i, r in enumerate(ctx.rows, start=2):
            if not _is_na(r.get(c)) and _to_int(r.get(c)) is None:
                bad.setdefault(c, []).append(i)
                break
    if bad:
        return CheckResult("S02", "Column data types", "FAIL",
                           "; ".join(f"{c} first bad row {rows[0]}" for c, rows in bad.items()))
    return CheckResult("S02", "Column data types", "PASS",
                       f"checked {numeric_cols + int_cols}")


def check_s03(ctx: QCContext) -> CheckResult:
    bad = [c for c in ctx.header if not COLUMN_NAME_RE.match(c)]
    if bad:
        return CheckResult("S03", "Column name characters", "FAIL",
                           f"non-conformant column names: {bad}")
    return CheckResult("S03", "Column name characters", "PASS",
                       f"{len(ctx.header)} columns all match [A-Za-z_][A-Za-z0-9_]*")


def check_s04(ctx: QCContext) -> CheckResult:
    if not ctx.header:
        return CheckResult("S04", "Header row exists / delimiter", "FAIL",
                           "no header row detected")
    if ctx.delimiter not in (",", "\t"):
        return CheckResult("S04", "Header row exists / delimiter", "FAIL",
                           f"unsupported delimiter {ctx.delimiter!r}")
    return CheckResult("S04", "Header row exists / delimiter", "PASS",
                       f"single header row, delimiter={ctx.delimiter!r}")


def check_s05(ctx: QCContext) -> CheckResult:
    if ctx.has_bom:
        return CheckResult("S05", "Encoding: ASCII/UTF-8 no BOM", "FAIL",
                           "UTF-8 BOM present at start of file")
    try:
        ctx.raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return CheckResult("S05", "Encoding: ASCII/UTF-8 no BOM", "FAIL",
                           "file is not valid UTF-8")
    return CheckResult("S05", "Encoding: ASCII/UTF-8 no BOM", "PASS",
                       "UTF-8 without BOM")


# ---------------------------------------------------------------------------
# EVENT/DOSING E01..E05
# ---------------------------------------------------------------------------
def check_e01(ctx: QCContext) -> CheckResult:
    if "ID" not in ctx.header:
        return CheckResult("E01", "ID monotonic non-decreasing", "SKIP",
                           "ID column absent (covered by S01 FAIL)")
    prev = None
    for i, r in enumerate(ctx.rows, start=2):
        v = _to_float(r.get("ID"))
        if v is None:
            continue
        if prev is not None and v < prev:
            return CheckResult("E01", "ID monotonic non-decreasing", "FAIL",
                               f"ID decreases at row {i}: {prev} -> {v}")
        prev = v
    return CheckResult("E01", "ID monotonic non-decreasing", "PASS",
                       f"{len(ctx.rows)} rows checked")


def check_e02(ctx: QCContext) -> CheckResult:
    if not {"ID", "TIME"}.issubset(set(ctx.header)):
        return CheckResult("E02", "TIME monotonic within ID", "SKIP", "ID/TIME missing")
    cur_id = None
    prev_t = None
    for i, r in enumerate(ctx.rows, start=2):
        idv = _to_float(r.get("ID"))
        tv = _to_float(r.get("TIME"))
        if idv != cur_id:
            cur_id = idv
            prev_t = None
        if tv is None:
            continue
        if prev_t is not None and tv < prev_t:
            return CheckResult("E02", "TIME monotonic within ID", "FAIL",
                               f"TIME decreases within ID={cur_id} at row {i}: {prev_t} -> {tv}")
        prev_t = tv
    return CheckResult("E02", "TIME monotonic within ID", "PASS",
                       f"{len(ctx.rows)} rows checked")


def check_e03(ctx: QCContext) -> CheckResult:
    if "EVID" not in ctx.header:
        return CheckResult("E03", "EVID in {0,1,2,3,4}", "SKIP", "EVID absent")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        v = _to_int(r.get("EVID"))
        if v is None or v not in EVID_ALLOWED:
            bad.append((i, r.get("EVID")))
            if len(bad) >= 3:
                break
    if bad:
        return CheckResult("E03", "EVID in {0,1,2,3,4}", "FAIL",
                           f"bad EVID rows: {bad}")
    return CheckResult("E03", "EVID in {0,1,2,3,4}", "PASS",
                       f"{len(ctx.rows)} rows checked")


def check_e04(ctx: QCContext) -> CheckResult:
    if "EVID" not in ctx.header:
        return CheckResult("E04", "EVID=0 obs invariants", "SKIP", "EVID absent")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        if _to_int(r.get("EVID")) != 0:
            continue
        dv = r.get("DV")
        amt = r.get("AMT")
        mdv = _to_int(r.get("MDV"))
        # DV may be NA on EVID=0 only when MDV=1 (BLQ-flagged or otherwise missing).
        if _is_na(dv) and mdv != 1:
            bad.append((i, "DV=NA on EVID=0 with MDV!=1"))
        if "AMT" in ctx.header and not _is_na(amt):
            bad.append((i, f"AMT={amt} not NA on EVID=0"))
        if len(bad) >= 3:
            break
    if bad:
        return CheckResult("E04", "EVID=0 obs invariants", "FAIL", f"violations: {bad}")
    return CheckResult("E04", "EVID=0 obs invariants", "PASS",
                       "DV present (or MDV=1) and AMT NA on all EVID=0")


def check_e05(ctx: QCContext) -> CheckResult:
    if "EVID" not in ctx.header:
        return CheckResult("E05", "EVID=1 dose invariants", "SKIP", "EVID absent")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        if _to_int(r.get("EVID")) != 1:
            continue
        amt = _to_float(r.get("AMT")) if "AMT" in ctx.header else None
        if amt is None or amt <= 0:
            bad.append((i, f"AMT={r.get('AMT')!r} invalid on EVID=1"))
        dv = r.get("DV")
        if not _is_na(dv) and (_to_float(dv) or 0) != 0:
            bad.append((i, f"DV={dv} not NA/0 on EVID=1"))
        if len(bad) >= 3:
            break
    if bad:
        return CheckResult("E05", "EVID=1 dose invariants", "FAIL", f"violations: {bad}")
    return CheckResult("E05", "EVID=1 dose invariants", "PASS", "AMT>0, DV NA/0 on all EVID=1")


# ---------------------------------------------------------------------------
# BLQ/MDV B01..B03
# ---------------------------------------------------------------------------
def check_b01(ctx: QCContext) -> CheckResult:
    if not {"MDV", "DV"}.issubset(set(ctx.header)):
        return CheckResult("B01", "MDV consistent with DV", "SKIP", "MDV/DV missing")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        mdv = _to_int(r.get("MDV"))
        dv = r.get("DV")
        if _is_na(dv) and mdv != 1:
            bad.append((i, f"DV NA but MDV={mdv}"))
        if not _is_na(dv) and mdv == 1:
            # acceptable for dose rows; only flag for EVID=0
            if _to_int(r.get("EVID", "0")) == 0:
                bad.append((i, f"DV={dv} present but MDV=1 on EVID=0"))
        if len(bad) >= 3:
            break
    if bad:
        return CheckResult("B01", "MDV consistent with DV", "FAIL", f"violations: {bad}")
    return CheckResult("B01", "MDV consistent with DV", "PASS", "consistent")


def check_b02(ctx: QCContext) -> CheckResult:
    col = next((c for c in ctx.header if c.upper() in ("BLQ_FLAG", "BLQ")), None)
    if not col:
        return CheckResult("B02", "BLQ_FLAG values", "PASS",
                           "no BLQ flag column present")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        v = (r.get(col) or "").strip().upper()
        if v not in BLQ_ALLOWED:
            bad.append((i, v))
            if len(bad) >= 3:
                break
    if bad:
        return CheckResult("B02", "BLQ_FLAG values", "FAIL", f"violations: {bad}")
    return CheckResult("B02", "BLQ_FLAG values", "PASS", "all in {M1,M3,M4,null}")


def check_b03(ctx: QCContext) -> CheckResult:
    if "DV" not in ctx.header:
        return CheckResult("B03", "DV non-negative (unless policy)", "SKIP", "DV missing")
    allow_neg = bool(ctx.aic.get("allow_negative_dv", False))
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        v = _to_float(r.get("DV"))
        if v is not None and v < 0 and not allow_neg:
            bad.append((i, v))
            if len(bad) >= 3:
                break
    if bad:
        return CheckResult("B03", "DV non-negative (unless policy)", "FAIL", f"violations: {bad}")
    return CheckResult("B03", "DV non-negative (unless policy)", "PASS",
                       f"DV ≥ 0 (allow_negative_dv={allow_neg})")


# ---------------------------------------------------------------------------
# CMT C01..C03
# ---------------------------------------------------------------------------
def check_c01(ctx: QCContext) -> CheckResult:
    if "CMT" not in ctx.header:
        return CheckResult("C01", "CMT integer ≥ 1", "PASS", "CMT column absent")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        v = _to_int(r.get("CMT"))
        if v is None or v < 1:
            bad.append((i, r.get("CMT")))
            if len(bad) >= 3:
                break
    if bad:
        return CheckResult("C01", "CMT integer ≥ 1", "FAIL", f"violations: {bad}")
    return CheckResult("C01", "CMT integer ≥ 1", "PASS", "all rows CMT≥1 integer")


def check_c02(ctx: QCContext) -> CheckResult:
    if "CMT" not in ctx.header:
        return CheckResult("C02", "CMT consistent with analyte_role", "SKIP",
                           "CMT column absent")
    analyte_role = ctx.aic.get("analyte_role")
    cmt_role_map = ctx.aic.get("cmt_role_map", {})
    if not analyte_role and not cmt_role_map:
        return CheckResult("C02", "CMT consistent with analyte_role", "PASS",
                           "no analyte_role declared (single-analyte assumed)")
    if not isinstance(cmt_role_map, dict) or not cmt_role_map:
        return CheckResult("C02", "CMT consistent with analyte_role", "FAIL",
                           "analyte_role declared but cmt_role_map missing/empty")
    declared_cmts = {int(k) for k in cmt_role_map.keys() if str(k).isdigit()}
    seen = {_to_int(r.get("CMT")) for r in ctx.rows} - {None}
    bad = seen - declared_cmts
    if bad:
        return CheckResult("C02", "CMT consistent with analyte_role", "FAIL",
                           f"CMT values used but not in cmt_role_map: {sorted(bad)}")
    return CheckResult("C02", "CMT consistent with analyte_role", "PASS",
                       f"CMT values {sorted(seen)} all in cmt_role_map")


def check_c03(ctx: QCContext) -> CheckResult:
    if not {"CMT", "ID", "TIME", "EVID"}.issubset(set(ctx.header)):
        return CheckResult("C03", "Single CMT per (ID,TIME,EVID)", "SKIP",
                           "required columns missing")
    seen: dict[tuple, int] = {}
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        key = (r.get("ID"), r.get("TIME"), r.get("EVID"))
        cmt = _to_int(r.get("CMT"))
        if cmt is None:
            continue
        if key in seen and seen[key] != cmt:
            bad.append((i, key, seen[key], cmt))
            if len(bad) >= 3:
                break
        else:
            seen[key] = cmt
    if bad:
        return CheckResult("C03", "Single CMT per (ID,TIME,EVID)", "FAIL", f"violations: {bad}")
    return CheckResult("C03", "Single CMT per (ID,TIME,EVID)", "PASS", "consistent")


# ---------------------------------------------------------------------------
# v4.2 V01..V04
# ---------------------------------------------------------------------------
def _endpoint(ctx: QCContext) -> str:
    return (ctx.aic.get("endpoint_data_type") or "").strip().upper()


def check_v01(ctx: QCContext) -> CheckResult:
    ep = _endpoint(ctx)
    if ep != "CELLULAR_KINETICS":
        return CheckResult("V01", "CELLULAR_KINETICS canonicalization", "SKIP",
                           f"endpoint={ep}")
    if "DV" not in ctx.header:
        return CheckResult("V01", "CELLULAR_KINETICS canonicalization", "FAIL", "DV missing")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        v = _to_float(r.get("DV"))
        if v is not None and v < 0:
            bad.append((i, v))
            if len(bad) >= 3:
                break
    blq_col = next((c for c in ctx.header if c.upper() in ("BLQ_FLAG", "BLQ")), None)
    if blq_col is None:
        return CheckResult("V01", "CELLULAR_KINETICS canonicalization", "FAIL",
                           "cellular endpoint requires BLQ flag column")
    if bad:
        return CheckResult("V01", "CELLULAR_KINETICS canonicalization", "FAIL",
                           f"negative DV violations: {bad}")
    return CheckResult("V01", "CELLULAR_KINETICS canonicalization", "PASS",
                       f"DV ≥ 0 and BLQ column {blq_col} present")


def check_v02(ctx: QCContext) -> CheckResult:
    ep = _endpoint(ctx)
    if ep != "IMMUNOGENICITY":
        return CheckResult("V02", "IMMUNOGENICITY adjudication", "SKIP", f"endpoint={ep}")
    if "DV" not in ctx.header:
        return CheckResult("V02", "IMMUNOGENICITY adjudication", "FAIL", "DV missing")
    bad = []
    for i, r in enumerate(ctx.rows, start=2):
        if _to_int(r.get("EVID")) != 0:
            continue
        v = _to_int(r.get("DV"))
        if v not in (0, 1):
            bad.append((i, r.get("DV")))
            if len(bad) >= 3:
                break
    has_adj = bool(ctx.aic.get("adjudication_log") or ctx.audit_log.get("adjudication_log"))
    if bad:
        return CheckResult("V02", "IMMUNOGENICITY adjudication", "FAIL",
                           f"non-binary DV on obs rows: {bad}")
    if not has_adj:
        return CheckResult("V02", "IMMUNOGENICITY adjudication", "FAIL",
                           "adjudication_log not declared in AIC or audit log")
    return CheckResult("V02", "IMMUNOGENICITY adjudication", "PASS",
                       "binary DV and adjudication_log present")


def check_v03(ctx: QCContext) -> CheckResult:
    ep = _endpoint(ctx)
    if ep != "MATERNAL_INFANT_PK":
        return CheckResult("V03", "MATERNAL_INFANT dyad/group", "SKIP", f"endpoint={ep}")
    dyad_col = next((c for c in ctx.header if c.upper() in ("DYADID", "DYAD_ID")), None)
    role_col = next((c for c in ctx.header if c.upper() in ("ROLE", "SUBJECT_ROLE")), None)
    if dyad_col is None:
        return CheckResult("V03", "MATERNAL_INFANT dyad/group", "FAIL", "DYADID column missing")
    if role_col is not None:
        roles = {(r.get(role_col) or "").strip().upper() for r in ctx.rows}
        if not ({"MOTHER", "INFANT"} <= roles):
            return CheckResult("V03", "MATERNAL_INFANT dyad/group", "FAIL",
                               f"need MOTHER+INFANT roles, got {roles}")
    return CheckResult("V03", "MATERNAL_INFANT dyad/group", "PASS",
                       f"DYADID present (role column={role_col})")


def check_v04(ctx: QCContext) -> CheckResult:
    if not ctx.aic.get("product_level_covariate"):
        return CheckResult("V04", "Product-level covariate consistency", "SKIP",
                           "no product_level_covariate declared")
    has_lotid = "LOTID" in ctx.header
    has_product = any(c.upper().startswith("PRODUCT_") for c in ctx.header)
    if not (has_lotid or has_product):
        return CheckResult("V04", "Product-level covariate consistency", "FAIL",
                           "neither LOTID nor PRODUCT_* columns present")
    return CheckResult("V04", "Product-level covariate consistency", "PASS",
                       f"LOTID={has_lotid} product_cols={has_product}")


# ---------------------------------------------------------------------------
# AUDIT LOG A01
# ---------------------------------------------------------------------------
def check_a01(ctx: QCContext) -> CheckResult:
    if not ctx.audit_log:
        return CheckResult("A01", "Audit log present and complete", "FAIL",
                           "audit_log file missing or empty")
    missing = AUDIT_REQUIRED_FIELDS - set(ctx.audit_log.keys())
    if missing:
        return CheckResult("A01", "Audit log present and complete", "FAIL",
                           f"missing audit log fields: {sorted(missing)}")
    return CheckResult("A01", "Audit log present and complete", "PASS",
                       f"present with required fields ({sorted(AUDIT_REQUIRED_FIELDS)})")


# ---------------------------------------------------------------------------
ALL_CHECKS = [
    check_s01, check_s02, check_s03, check_s04, check_s05,
    check_e01, check_e02, check_e03, check_e04, check_e05,
    check_b01, check_b02, check_b03,
    check_c01, check_c02, check_c03,
    check_v01, check_v02, check_v03, check_v04,
    check_a01,
]


def run_qc(ctx: QCContext) -> list[CheckResult]:
    return [fn(ctx) for fn in ALL_CHECKS]


# ---------------------------------------------------------------------------
def emit_report(results: list[CheckResult], out_path: Path, ctx: QCContext) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pass_n = sum(1 for r in results if r.status == "PASS")
    fail_n = sum(1 for r in results if r.status == "FAIL")
    skip_n = sum(1 for r in results if r.status == "SKIP")
    overall = "PASS" if fail_n == 0 else "FAIL"
    lines = [
        "# NONMEM-Ready QC Report",
        "",
        f"**Dataset:** `{ctx.dataset_path}`",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Overall:** **{overall}**  (pass={pass_n}, fail={fail_n}, skip={skip_n}, total={len(results)})",
        "",
        "| code | name | status | severity | detail |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r.code} | {r.name} | {r.status} | {r.severity} | {r.detail} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", required=True, type=Path)
    p.add_argument("--aic", type=Path, default=None)
    p.add_argument("--audit-log", type=Path, default=None)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)

    ctx = load_context(args.dataset, args.aic, args.audit_log)
    results = run_qc(ctx)
    emit_report(results, args.out, ctx)
    fail_n = sum(1 for r in results if r.status == "FAIL")
    print(f"[nonmem_ready_qc] dataset={args.dataset} fail={fail_n} report={args.out}")
    return 1 if fail_n else 0


if __name__ == "__main__":
    sys.exit(main())
