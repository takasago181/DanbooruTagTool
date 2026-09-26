#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/BATCH_A_REMAINING_7_RESEARCH.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/batch_a_remaining_7_research_summary.json"
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline="")))
 out=[]
 for r in rows:
  if r["second_review"]=="PASS": continue
  out.append({**r,"research_lane":"REMAINING_AUTHORITY","research_state":"PENDING_FIRST_PARTY_EVIDENCE","do_not_infer_home":"true"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"remaining_families":len(out),"already_second_review_pass":len(rows)-len(out),"auto_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
