#!/usr/bin/env python3
"""Audit the 9 unqualified exact-overlap candidates conservatively.
Identity overlap is not ownership authority; export for explicit authority review only."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW";IN=D/"UNQUALIFIED_ROSTER_CANDIDATES_V1.csv";OUT=D/"UNQUALIFIED_EXACT_9_REVIEW_V1.csv"
def main():
 rows=[r for r in csv.DictReader(IN.open(encoding="utf-8-sig",newline="")) if r["roster_candidate_state"]=="UNIQUE_IDENTITY_OVERLAP_CANDIDATE"]
 out=[]
 for r in rows:
  out.append({**r,"authority_decision":"NEEDS_OFFICIAL_ROSTER_AUTHORITY","second_review":"UNRESOLVED","production_approved":"false"})
 if out:
  with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"reviewed_rows":len(rows),"home_confirmed":0,"unresolved":len(rows),"reason":"identity overlap alone does not prove canonical home","accepted_source_modified":False,"production_modified":False}
 (D/"unqualified_exact_9_review_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if len(rows)!=9: raise SystemExit("expected 9 exact-overlap candidates, got "+str(len(rows)))
if __name__=="__main__":main()
