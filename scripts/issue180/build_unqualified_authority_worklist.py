#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_SAMPLE_STRUCTURE.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_AUTHORITY_WORKLIST.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/unqualified_authority_worklist_summary.json"
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]
    for r in rows:
        out.append({**r,"candidate_home":"","authority_source":"","decision":"PENDING","second_review":"REQUIRED"})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"rows":len(out),"single_token":sum(r["structure_bucket"]=="SINGLE_TOKEN" for r in out),"multi_token":sum(r["structure_bucket"]=="MULTI_TOKEN_UNQUALIFIED" for r in out),"auto_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
