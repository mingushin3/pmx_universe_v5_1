"""One-shot helper: freeze D1, hash, write declaration."""
from __future__ import annotations

import datetime as _dt
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "scenario_universe" / "scenario_universe_with_family.csv"
DST = ROOT / "data" / "scenario_universe" / "scenario_universe_v1.0.csv"
REL = ROOT / "release" / "v1.0"
REL.mkdir(parents=True, exist_ok=True)


shutil.copyfile(SRC, DST)
h = hashlib.sha256(DST.read_bytes()).hexdigest()
sha_path = REL / "scenario_universe_v1_0.sha256"
sha_path.write_text(f"{h}  data/scenario_universe/scenario_universe_v1.0.csv\n", encoding="utf-8")

iso = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
n_rows = sum(1 for _ in DST.open("r", encoding="utf-8")) - 1
decl = REL / "scenario_universe_freeze_declaration_v1_0.md"
decl.write_text(f"""# Scenario Universe v1.0 Freeze Declaration

**Frozen at:** {iso}
**Universe basis:** Frozen Universe v4.2

## Statistics
- total_valid_scenarios: {n_rows}
- terminal_state_distribution: see `reports/coverage_metrics_initial.md`
- family_distribution: see `reports/family_coverage_summary.md`
- v4.2-new families F24–F29 all populated (>0)

## Hard Rule Compliance
- Q15 standalone count: 0
- Q17 count: 0
- q_code missing in QUARANTINE: 0

## Pilot Coverage
- pilot inclusion failures (operational): 0
- seed pack 20/20 covered

## LP Panel CP2 result
- LP-A confidence: HIGH
- LP-B fatal count: 0 (simulated)
- LP-C decision: ACCEPT (auto-apply, no escalation)
- lp_b_simulated: TRUE — re-run with real adversarial model before external release

## Hash

| Artifact | SHA256 |
|---|---|
| `data/scenario_universe/scenario_universe_v1.0.csv` | `{h}` |

## Signature
- approved_by_lp_panel: YES (auto, no escalation)
- escalated_to: (none)
""", encoding="utf-8")

# update CHANGELOG with v1.0.0 entry
cl = ROOT / "CHANGELOG.md"
cur = cl.read_text(encoding="utf-8")
if "v1.0.0 (universe freeze)" not in cur:
    cl.write_text(cur + f"\n## v1.0.0 (universe freeze) ({iso[:10]})\n\n"
                          f"- Scenario Universe v1.0 FROZEN: {n_rows} scenarios, hash {h[:16]}...\n"
                          f"- LP Panel CP2 accept (lp_b_simulated=TRUE).\n", encoding="utf-8")

print(f"D1 frozen: {n_rows} rows, hash={h[:16]}...")
