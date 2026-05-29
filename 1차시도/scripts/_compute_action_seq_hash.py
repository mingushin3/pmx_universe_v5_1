"""Compute SHA256 hashes for the action_sequence lock files (P26)."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config" / "action_sequence_standard.yaml",
    ROOT / "config" / "action_function_library.yaml",
    ROOT / "config" / "analysis_intent_contract_template.yaml",
]


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> None:
    individual = [(p, file_sha256(p)) for p in FILES]
    combined = hashlib.sha256()
    for i, (p, h) in enumerate(individual):
        combined.update(p.read_bytes())
        if i != len(individual) - 1:
            combined.update(b"\n")
    combined_hex = combined.hexdigest()

    sha_path = ROOT / "release" / "v1.0" / "action_sequence_v1_0.sha256"
    sha_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for p, h in individual:
        rel = p.relative_to(ROOT).as_posix()
        lines.append(f"{h}  {rel}")
    lines.append(f"{combined_hex}  COMBINED")
    sha_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", sha_path)
    print("\n".join(lines))

    return None


if __name__ == "__main__":
    main()
