#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from parallel_overlay import load_checkpoint_union, apply_corrections

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
    neutral_path=Path(args.input)
    neutral=read_csv(neutral_path)
    parallel=Path(args.parallel_dir)
    contract=Path(args.contract_manifest)
    _,errors=base.verify_contract_manifest(contract,neutral_path,neutral)
    merged=[]; lane_stats={}

    for lane in LANES:
        assigned=[r for r in neutral if ((int(r["review_seq"])-1)%3)+1==lane]
        raw,ranges,load_errs=load_checkpoint_union(ROOT,lane,base.FIELDS)
        errors.extend(load_errs)
        expected=[r["identity_key"] for r in assigned[:len(raw)]]
        actual=[r.get("identity_key","") for r in raw]
        if actual!=expected:
            errors.append(f"lane {lane}: checkpoint union is not exact assigned prefix")
        effective,correction_count,corr_errs=apply_corrections(ROOT,lane,raw,ranges,base.FIELDS)
        errors.extend(corr_errs)
        for row in effective:
            ident=row.get("identity_key","")
            seq=next((int(x["review_seq"]) for x in assigned if x["identity_key"]==ident),None)
            if seq is None:
                errors.append(f"lane {lane}: unassigned identity {ident}")
            else:
                errors.extend(base.validate_row(row,seq))
        complete=len(effective)==len(assigned)
        lane_stats[str(lane)]={
            "reviewed_count":len(effective),
            "assigned_count":len(assigned),
            "remaining_count":len(assigned)-len(effective),
            "checkpoint_count":len(ranges),
            "corrections_applied":correction_count,
            "complete":complete
        }
        merged.extend(effective)

    merged.sort(key=lambda r:int(r["review_seq"]))
    if errors:
        for e in errors[:100]: print("ERROR:",e)
        raise SystemExit(1)

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=base.FIELDS,lineterminator="\n")
        w.writeheader(); w.writerows(merged)

    complete=all(x["complete"] for x in lane_stats.values())
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
        "schema_version":"issue132-parallel-merge-v2",
        "lane_count":3,
        "reviewed_count":len(merged),
        "remaining_count":31_003-len(merged),
        "complete":complete,
        "lanes":lane_stats,
        "final_full_validator_run":complete,
        "semantic_decisions_made_by_merge":False,
        "checkpoint_rows_mutated":False,
        "correction_overlay_applied":True
    }
    Path(args.summary).parent.mkdir(parents=True,exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if args.require_complete and not complete:
        raise SystemExit("parallel Pass A incomplete")

if __name__=="__main__":
    main()
