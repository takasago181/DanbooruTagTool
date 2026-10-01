#!/usr/bin/env python3
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]; P=R/"artifacts/issue180-full-preflight"
IN=P/"P1_P3_AUTHORITY_EVIDENCE_V1.csv"; OUT=P/"P1_P3_AUTHORITY_SECOND_REVIEW_V1.csv"; SUM=P/"p1_p3_authority_second_review_v1_summary.json"
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline=""))); out=[]
 for r in rows:
  if r["authority_state"]=="FIRST_PARTY_EVIDENCE_FOUND_PENDING_SECOND_REVIEW" and r["candidate_root"] and r["gate_state"]!="HOME_UNRESOLVED":
   decision="SECOND_REVIEW_PASS_RESEARCH_ONLY"; second="PASS"
  else:
   decision="HOME_UNRESOLVED"; second="UNRESOLVED"
  out.append({**r,"authority_decision":decision,"second_review":second,"production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"second_review_pass":sum(r["second_review"]=="PASS" for r in out),
 "unresolved":sum(r["second_review"]!="PASS" for r in out),"production_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,indent=2)+"\n"); print(json.dumps(x,indent=2))
if __name__=="__main__":main()
