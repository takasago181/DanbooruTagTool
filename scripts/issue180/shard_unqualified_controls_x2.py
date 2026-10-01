#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SRC=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_AUTHORITY_WORKLIST.csv"; OUT=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_AUTHORITY_SHARDS_X2.csv"; SUM=ROOT/"artifacts/issue180-full-preflight/unqualified_authority_shards_x2_summary.json"
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline=""))); out=[]
 for i,r in enumerate(rows): out.append({**r,"review_shard":f"UQX-{i%16+1:02d}","shard_state":"READY_FOR_PARALLEL_CONTROL_REVIEW"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 d={f"UQX-{i:02d}":sum(x["review_shard"]==f"UQX-{i:02d}" for x in out) for i in range(1,17)}
 x={"shards":16,"rows":len(out),"distribution":d,"auto_approved":0,"production_modified":False};SUM.write_text(json.dumps(x,indent=2)+"\n");print(json.dumps(x,indent=2))
if __name__=="__main__":main()
