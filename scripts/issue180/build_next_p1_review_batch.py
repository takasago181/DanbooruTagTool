#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_REVIEW_PRIORITY.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P1_REVIEW_BATCH.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/next_root_p1_review_batch_summary.json"
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=[r for r in csv.DictReader(fh) if r["priority_bucket"]=="P1_EXACT_ROOT"]
    out=[]
    for r in rows:
        out.append({**r,"authority_evidence":"","home_semantics":"PENDING","decision":"PENDING","second_review":"REQUIRED"})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"families":len(out),"character_rows":sum(int(r["character_count"]) for r in out),"auto_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
