#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
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

def load_fields() -> list[str]:
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_bootstrap_validator",path)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load Pass A validator")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.FIELDS)

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",default="artifacts/issue132")
    ap.add_argument("--review-dir",default="docs/issue132/full_review")
    args=ap.parse_args()

    artifact_root=ROOT/args.artifact_root
    review_dir=ROOT/args.review_dir
    neutral=artifact_root/"luna-neutral/luna_neutral_review_input_v2.csv"
    neutral_manifest=neutral.with_suffix(".manifest.json")
    contract=review_dir/"pass_a_contract_manifest_v1.json"
    ledger=review_dir/"pass_a_independent_discovery.csv"
    summary=review_dir/"pass_a_progress_summary.json"

    neutral.parent.mkdir(parents=True,exist_ok=True)
    review_dir.mkdir(parents=True,exist_ok=True)

    run(
        "scripts/issue132/build_luna_neutral_input.py",
        "--out",str(neutral.relative_to(ROOT))
    )
    run("scripts/issue132/check_review_vocabulary_against_code.py")

    if not contract.exists():
        run(
            "scripts/issue132/build_pass_a_contract_manifest.py",
            "--neutral",str(neutral.relative_to(ROOT)),
            "--neutral-manifest",str(neutral_manifest.relative_to(ROOT)),
            "--out",str(contract.relative_to(ROOT))
        )
    else:
        print(f"Using existing frozen contract: {contract.relative_to(ROOT)}")

    if not ledger.exists():
        fields=load_fields()
        with ledger.open("w",encoding="utf-8",newline="") as f:
            csv.writer(f,lineterminator="\n").writerow(fields)
        print(f"Initialized empty Pass A ledger: {ledger.relative_to(ROOT)}")
    else:
        print(f"Using existing Pass A ledger: {ledger.relative_to(ROOT)}")

    run(
        "scripts/issue132/validate_luna_pass_a.py",
        "--input",str(neutral.relative_to(ROOT)),
        "--ledger",str(ledger.relative_to(ROOT)),
        "--contract-manifest",str(contract.relative_to(ROOT)),
        "--summary",str(summary.relative_to(ROOT))
    )

    print("\nREADY_FOR_PASS_A")
    print(f"neutral={neutral.relative_to(ROOT)}")
    print(f"contract={contract.relative_to(ROOT)}")
    print(f"ledger={ledger.relative_to(ROOT)}")
    print(f"summary={summary.relative_to(ROOT)}")

if __name__=="__main__":
    main()
