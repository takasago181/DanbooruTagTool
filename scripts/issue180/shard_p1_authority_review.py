#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P1_REVIEW_BATCH.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P1_SHARDS.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/next_root_p1_shards_summary.json"
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]
    for i,r in enumerate(rows):
        shard=(i%6)+1
        out.append({**r,"review_shard":f"P1-{shard:02d}","shard_state":"READY_FOR_PARALLEL_AUTHORITY_REVIEW"})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    counts={f"P1-{i:02d}":sum(x["review_shard"]==f"P1-{i:02d}" for x in out) for i in range(1,7)}
    summary={"shards":6,"families":len(out),"distribution":counts,"auto_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
