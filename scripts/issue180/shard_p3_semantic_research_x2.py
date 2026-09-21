#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SRC=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P3_RESEARCH_BATCH.csv"; OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P3_SHARDS_X2.csv"; SUM=ROOT/"artifacts/issue180-full-preflight/next_root_p3_shards_x2_summary.json"
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline=""))); out=[]
 for i,r in enumerate(rows): out.append({**r,"review_shard":f"P3X-{i%8+1:02d}","shard_state":"READY_FOR_PARALLEL_SEMANTIC_RESEARCH"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 d={f"P3X-{i:02d}":sum(x["review_shard"]==f"P3X-{i:02d}" for x in out) for i in range(1,9)}
 x={"shards":8,"families":len(out),"distribution":d,"auto_approved":0,"production_modified":False};SUM.write_text(json.dumps(x,indent=2)+"\n");print(json.dumps(x,indent=2))
if __name__=="__main__":main()
