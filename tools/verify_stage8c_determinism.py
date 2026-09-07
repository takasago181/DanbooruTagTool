"""Rebuild the Stage 8C Phase 0 audit artifacts twice and compare bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "data/semantic/stage8c_review_status.csv",
    "data/semantic/stage8c_family_rule_review.csv",
    "data/semantic/stage8c_family_relation_proposals.csv",
    "data/semantic/stage8c_family_candidate_applicability.csv",
    "data/semantic/stage8c_model_familiarity.csv",
    "data/semantic/stage8c_non_tag_strategy.csv",
    "data/semantic/stage10_test_slots.csv",
    "data/semantic/stage8c_practical_use.csv",
    "data/semantic/stage8c_relation_evidence_events.csv",
    "benchmarks/stage8c/coverage_audit.csv",
    "benchmarks/stage8c/static_family_summary.csv",
    "benchmarks/stage8c/family_rule_summary.csv",
    "benchmarks/stage8c/validation_summary.json",
    "benchmarks/stage8c/protected_hashes.json",
    "benchmarks/stage8c/pilot_evidence_seed_preview.csv",
    "benchmarks/stage8c/extension_boundary_audit.csv",
)


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def rebuild() -> None:
    for tool in ("tools/build_stage8c_phase0.py", "tools/stage8c_coverage_audit.py"):
        subprocess.run((sys.executable, tool), cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def main() -> int:
    rebuild()
    first = {path: digest(path) for path in ARTIFACTS}
    rebuild()
    second = {path: digest(path) for path in ARTIFACTS}
    report = {
        "runs": 2,
        "file_count": len(ARTIFACTS),
        "all_byte_identical": first == second,
        "files": [{"path": path, "sha256": second[path], "identical": first[path] == second[path]}
                  for path in ARTIFACTS],
    }
    (ROOT / "benchmarks/stage8c/determinism.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_byte_identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
