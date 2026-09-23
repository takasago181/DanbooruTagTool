#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LANES=(1,2,3)

def run(*args:str)->None:
    p=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8")
    print(p.stdout,end="")
    if p.returncode:
        raise SystemExit(p.returncode)

def load_fields():
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_parallel_fields",path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load validator fields")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return list(mod.FIELDS)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",default="artifacts/issue132")
    ap.add_argument("--parallel-dir",default="docs/issue132/parallel")
    args=ap.parse_args()

    artifact_root=ROOT/args.artifact_root
    parallel_dir=ROOT/args.parallel_dir
    neutral=artifact_root/"luna-neutral/luna_neutral_review_input_v2.csv"
    neutral_manifest=neutral.with_suffix(".manifest.json")
    contract=parallel_dir/"pass_a_contract_manifest_v1.json"
    fields=load_fields()

    neutral.parent.mkdir(parents=True,exist_ok=True)
    parallel_dir.mkdir(parents=True,exist_ok=True)

    run("scripts/issue132/build_luna_neutral_input.py","--out",str(neutral.relative_to(ROOT)))
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

    plan={
        "schema_version":"issue132-parallel-plan-v1",
        "lane_count":3,
        "assignment_rule":"((review_seq-1)%3)+1",
        "semantic_sharding":False,
        "note":"Operational distribution only; neutral input is already deterministic hash order."
    }
    plan_path=parallel_dir/"parallel_plan_v1.json"
    if not plan_path.exists():
        plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    for lane in LANES:
        lane_dir=parallel_dir/f"lane-{lane}"
        lane_dir.mkdir(parents=True,exist_ok=True)
        ledger=lane_dir/"pass_a_fragment.csv"
        summary=lane_dir/"status.json"
        if not ledger.exists():
            with ledger.open("w",encoding="utf-8",newline="") as f:
                csv.writer(f,lineterminator="\n").writerow(fields)
        run(
            "scripts/issue132/validate_luna_lane.py",
            "--input",str(neutral.relative_to(ROOT)),
            "--ledger",str(ledger.relative_to(ROOT)),
            "--lane",str(lane),
            "--contract-manifest",str(contract.relative_to(ROOT)),
            "--summary",str(summary.relative_to(ROOT))
        )

    print("\nREADY_FOR_PARALLEL_PASS_A")
    print(f"neutral={neutral.relative_to(ROOT)}")
    print(f"contract={contract.relative_to(ROOT)}")
    print(f"plan={plan_path.relative_to(ROOT)}")

if __name__=="__main__":
    main()
