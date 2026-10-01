#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_FAMILY_GATE.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_AUTHORITY_WORKLIST.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/root_review_batch_a_authority_worklist_summary.json"
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]
    for r in rows:
        if r["mechanical_gate"]!="READY_FOR_AUTHORITY_REVIEW": continue
        out.append({**r,"official_source_url":"","official_source_claim":"","root_semantics":"PENDING","authority_decision":"PENDING","second_review":"REQUIRED"})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"families":len(out),"authority_approved":0,"second_review_required":len(out),"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
