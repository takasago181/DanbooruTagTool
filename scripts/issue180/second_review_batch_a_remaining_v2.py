#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/BATCH_A_REMAINING_7_EVIDENCE_V2.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/BATCH_A_REMAINING_7_SECOND_REVIEW_V2.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/batch_a_remaining_7_second_review_v2_summary.json"
# These mappings are direct franchise roots or explicit shorthand->official-title normalizations.
# Project Moon remains umbrella-ambiguous; Girls' Frontline remains evidence-pending.
SAFE={"genshin_impact","honkai_impact","nikke","pgr","reverse:1999"}
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline="")));out=[]
 for r in rows:
  q=r["qualifier"]
  if q in SAFE and r["official_source_url"] and r["research_state"].startswith("FIRST_PARTY_"):
   r["root_semantics"]="CANONICAL_FRANCHISE_ROOT"
   r["authority_decision"]="SECOND_REVIEW_PASS_RESEARCH_ONLY"
   r["second_review"]="PASS"
  else:
   r["second_review"]="UNRESOLVED"
  out.append(r)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 passed=sum(r["second_review"]=="PASS" for r in out)
 x={"families":len(out),"second_review_pass":passed,"unresolved":len(out)-passed,
    "production_approved":0,"research_only":True,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
