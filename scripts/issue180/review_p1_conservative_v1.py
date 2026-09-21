#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P1_REVIEW_BATCH.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P1_CONSERVATIVE_REVIEW_V1.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/next_root_p1_conservative_review_v1_summary.json"
# Exact catalog match is necessary but not sufficient. Umbrella/franchise roots remain semantic-review.
UMBRELLA={"precure","final_fantasy","yu-gi-oh!","nijisanji","dragon_ball","disney","marvel","idolmaster"}
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline="")));out=[]
 for r in rows:
  if r["catalog_match_state"]!="EXACT_ROOT_EXISTS": r["decision"]="HOME_UNRESOLVED";r["home_semantics"]="CATALOG_MISMATCH"
  elif r["qualifier"] in UMBRELLA: r["decision"]="HOME_UNRESOLVED";r["home_semantics"]="UMBRELLA_OR_SERIES_REVIEW_REQUIRED"
  else: r["decision"]="AUTHORITY_REVIEW_REQUIRED";r["home_semantics"]="EXACT_ROOT_NOT_AUTHORITY"
  out.append(r)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"authority_review_required":sum(r["decision"]=="AUTHORITY_REVIEW_REQUIRED" for r in out),
 "umbrella_or_mismatch_unresolved":sum(r["decision"]=="HOME_UNRESOLVED" for r in out),"auto_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
