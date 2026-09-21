#!/usr/bin/env python3
"""Seed the 208-shard authority campaign with high-precision evidence already validated in this lane.
Consumes evidence outputs only; never invents relations."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";D=A/"POST_NORMALIZED_REVIEW";OD=D/"MEGABATCH_AUTHORITY";OUT=OD/"AUTHORITY_LEDGER_V1.csv"
SOURCES=[D/"SPLATOON_OFFICIAL_HOME_V1.csv"]
def main():
 ledger=[];seen={}
 for p in SOURCES:
  if not p.exists():continue
  for r in csv.DictReader(p.open(encoding="utf-8-sig",newline="")):
   if r.get("second_review")!="PASS" or not r.get("candidate_root_hint"):continue
   tag=r.get("canonical_tag","");home=r["candidate_root_hint"]
   if tag in seen and seen[tag]!=home:raise SystemExit("HOME conflict "+tag)
   seen[tag]=home;ledger.append({"canonical_tag":tag,"home_copyright":home,"evidence_url":r.get("evidence_url",""),"evidence_type":r.get("evidence_type",""),"source_file":p.name,"second_review":"PASS","production_approved":"false"})
 if ledger:
  with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=ledger[0].keys(),lineterminator="\n");w.writeheader();w.writerows(ledger)
 x={"authority_ledger_rows":len(ledger),"unique_characters":len(seen),"conflicts":0,"auto_inferred":0,"accepted_source_modified":False,"production_modified":False}
 (OD/"authority_ledger_v1_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if len(ledger)!=47:raise SystemExit("expected 47 validated Splatoon rows, got "+str(len(ledger)))
if __name__=="__main__":main()
