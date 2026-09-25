#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path

from parallel_overlay import load_checkpoint_union, apply_corrections
from staging_repair_overlay import resolve_repair_overlay
from rebuild_manual_audit_structural_repairs import parse_source
from staging_v2 import compact_row_to_full
from validate_luna_pass_a import FIELDS

ROOT=Path(__file__).resolve().parents[2]
PARALLEL=ROOT/"docs/issue132/parallel"
NEUTRAL=PARALLEL/"input/luna_neutral_review_input_v2.csv"
LANE=2
OUT=PARALLEL/"audits/lane-2_effective_manual_audit_export.csv"

def read_neutral():
    with NEUTRAL.open("r",encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    return [r for r in rows if ((int(r["review_seq"])-1)%3)+1==LANE]

def main():
    neutral=read_neutral()
    raw,ranges,errs=load_checkpoint_union(ROOT,LANE,FIELDS)
    if errs: raise SystemExit("\n".join(errs))
    eff,_,corr_errs=apply_corrections(ROOT,LANE,raw,ranges,FIELDS)
    if corr_errs: raise SystemExit("\n".join(corr_errs))
    out=[]
    for idx,row in enumerate(eff,1):
        out.append({"lane_local_index":idx,**row})
    stage=PARALLEL/f"lane-{LANE}/staging"
    for p in sorted(stage.glob("window_*.json")):
        obj,_=parse_source(p)
        a=int(obj["lane_local_start"]); b=int(obj["lane_local_end"])
        repaired,_,rerrs=resolve_repair_overlay(p,LANE,a,b)
        if rerrs: raise SystemExit("\n".join(rerrs))
        win=repaired if repaired is not None else obj
        for r in win.get("rows",[]):
            idx=int(r.get("lane_local_index") or ((int(r["review_seq"])-2)//3+1))
            expected=neutral[idx-1]
            if win.get("schema_version")=="issue132-pass-a-staging-window-v2":
                full=compact_row_to_full(r,expected,FIELDS)
            elif isinstance(r,dict):
                full={k:str(r.get(k,"")) for k in FIELDS}
            else:
                full=dict(zip(FIELDS,[str(x) for x in r]))
            out.append({"lane_local_index":idx,**full})
        for h in win.get("holds",[]):
            idx=int(h["lane_local_index"])
            expected=neutral[idx-1]
            row={k:"" for k in FIELDS}
            row["review_seq"]=expected["review_seq"]
            row["identity_key"]=expected["identity_key"]
            row["manual_seen"]="YES"
            row["semantic_summary_ja"]="HOLD"
            row["discovery_mode"]="HOLD"
            row["route_vocabulary_gap"]="NO"
            row["review_depth"]="RESEARCHED"
            out.append({"lane_local_index":idx,**row})
    by={}
    for r in out:
        by[int(r["lane_local_index"])]=r
    max_idx=max(by)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    cols=["lane_local_index"]+FIELDS
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        for idx in range(1,max_idx+1):
            if idx not in by:
                raise SystemExit(f"missing effective row {idx}")
            w.writerow(by[idx])
    print(f"wrote {OUT} rows={max_idx}")

if __name__=="__main__":
    main()
