#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def run(*args: str) -> None:
    result=subprocess.run(
        [sys.executable,*args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8"
    )
    print(result.stdout,end="")
    if result.returncode:
        raise SystemExit(result.returncode)

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",default="artifacts/issue132")
    ap.add_argument("--review-dir",default="docs/issue132/full_review")
    args=ap.parse_args()

    artifact_root=ROOT/args.artifact_root
    review_dir=ROOT/args.review_dir
    neutral=artifact_root/"luna-neutral/luna_neutral_review_input_v2.csv"
    contract=review_dir/"pass_a_contract_manifest_v1.json"
    ledger=review_dir/"pass_a_independent_discovery.csv"
    progress=review_dir/"pass_a_progress_summary.json"
    census=artifact_root/"full-discovery-audit"
    pass_b=artifact_root/"pass-b"
    pass_b.mkdir(parents=True,exist_ok=True)

    required=[neutral,contract,ledger]
    missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise SystemExit("missing finalization inputs: "+", ".join(missing))

    run(
        "scripts/issue132/validate_luna_pass_a.py",
        "--input",str(neutral.relative_to(ROOT)),
        "--ledger",str(ledger.relative_to(ROOT)),
        "--contract-manifest",str(contract.relative_to(ROOT)),
        "--summary",str(progress.relative_to(ROOT)),
        "--require-complete"
    )

    run(
        "scripts/issue132/full_discovery_coverage_audit.py",
        "--root",".",
        "--out",str(census.relative_to(ROOT))
    )

    run(
        "scripts/issue132/build_pass_b_diff.py",
        "--pass-a",str(ledger.relative_to(ROOT)),
        "--current-audit",str((census/"identity_audit.csv").relative_to(ROOT)),
        "--out",str((pass_b/"pass_b_current_diff.csv").relative_to(ROOT)),
        "--summary",str((pass_b/"pass_b_summary.json").relative_to(ROOT))
    )

    print("\nPASS_A_COMPLETE_AND_PASS_B_READY")
    print(f"ledger={ledger.relative_to(ROOT)}")
    print(f"progress={progress.relative_to(ROOT)}")
    print(f"pass_b_diff={(pass_b/'pass_b_current_diff.csv').relative_to(ROOT)}")
    print(f"pass_b_summary={(pass_b/'pass_b_summary.json').relative_to(ROOT)}")

if __name__=="__main__":
    main()
