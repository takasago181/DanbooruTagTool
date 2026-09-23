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

def read_csv(path: Path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def load_base():
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_merge_base",path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load base validator")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def run(*args:str)->None:
    p=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8")
    print(p.stdout,end="")
    if p.returncode:
        raise SystemExit(p.returncode)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--contract-manifest",required=True)
    ap.add_argument("--parallel-dir",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--summary",required=True)
    ap.add_argument("--require-complete",action="store_true")
    args=ap.parse_args()

    base=load_base()
    parallel=Path(args.parallel_dir)
    merged=[]; lane_stats={}

    for lane in LANES:
        ledger=parallel/f"lane-{lane}/pass_a_fragment.csv"
        status=parallel/f"lane-{lane}/status.json"
        cmd=[
            "scripts/issue132/validate_luna_lane.py",
            "--input",args.input,
            "--ledger",str(ledger),
            "--lane",str(lane),
            "--contract-manifest",args.contract_manifest,
            "--summary",str(status)
        ]
        if args.require_complete:
            cmd.append("--require-complete")
        run(*cmd)
        rows=read_csv(ledger)
        merged.extend(rows)
        lane_stats[str(lane)]=json.loads(status.read_text(encoding="utf-8"))

    merged.sort(key=lambda r:int(r["review_seq"]))
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=base.FIELDS,lineterminator="\n")
        w.writeheader(); w.writerows(merged)

    complete=all(x["complete"] for x in lane_stats.values())
    errors=0
    if complete:
        full_summary=out.with_suffix(".validation.json")
        run(
            "scripts/issue132/validate_luna_pass_a.py",
            "--input",args.input,
            "--ledger",str(out),
            "--contract-manifest",args.contract_manifest,
            "--summary",str(full_summary),
            "--require-complete"
        )

    summary={
        "schema_version":"issue132-parallel-merge-v1",
        "lane_count":3,
        "reviewed_count":len(merged),
        "remaining_count":31_003-len(merged),
        "complete":complete,
        "lanes":lane_stats,
        "final_full_validator_run":complete,
        "semantic_decisions_made_by_merge":False
    }
    Path(args.summary).parent.mkdir(parents=True,exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

    if args.require_complete and not complete:
        raise SystemExit("parallel Pass A incomplete")

if __name__=="__main__":
    main()
