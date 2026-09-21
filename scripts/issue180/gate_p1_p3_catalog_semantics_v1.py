#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
P1=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P1_CONSERVATIVE_REVIEW_V1.csv"
P3=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P3_CONSERVATIVE_REVIEW_V1.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/P1_P3_CATALOG_SEMANTIC_GATE_V1.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/p1_p3_catalog_semantic_gate_v1_summary.json"
def main():
 with CAT.open("r",encoding="utf-8-sig",newline="") as f:
  catalog={r["canonical_tag"] for r in csv.DictReader(f) if r["category_name"]=="Copyright"}
 out=[]
 for src,lane in ((P1,"P1"),(P3,"P3")):
  for r in csv.DictReader(src.open("r",encoding="utf-8-sig",newline="")):
   root=(r.get("catalog_candidates") if lane=="P1" else r.get("candidate_root")) or ""
   exists=root in catalog
   decision=r.get("decision","")
   if lane=="P1" and decision=="AUTHORITY_REVIEW_REQUIRED" and exists: gate="CATALOG_OK_AUTHORITY_PENDING"
   elif lane=="P3" and decision.startswith("CANDIDATE_") and exists: gate="NORMALIZATION_ROOT_EXISTS_AUTHORITY_PENDING"
   else: gate="HOME_UNRESOLVED"
   out.append({"lane":lane,"qualifier":r["qualifier"],"character_count":r["character_count"],"candidate_root":root,
    "catalog_root_exists":str(exists).lower(),"input_decision":decision,"gate_state":gate,"authority_approved":"false","production_modified":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"catalog_ok_authority_pending":sum(r["gate_state"]=="CATALOG_OK_AUTHORITY_PENDING" for r in out),
    "normalization_root_exists_authority_pending":sum(r["gate_state"]=="NORMALIZATION_ROOT_EXISTS_AUTHORITY_PENDING" for r in out),
    "home_unresolved":sum(r["gate_state"]=="HOME_UNRESOLVED" for r in out),"authority_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
