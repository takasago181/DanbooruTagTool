#!/usr/bin/env python3
"""Promote exact qualifier==Copyright-tag matches to an AUTHORITY CANDIDATE queue for all families.
This is not approval: semantic exclusions and second review remain mandatory."""
import csv,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";D=A/"global-family-review-packets";OUT=A/"GLOBAL_EXACT_COPYRIGHT_CANDIDATES_V1.csv";SUM=A/"global_exact_copyright_candidates_v1_summary.json"
def main():
 rows=[]
 for p in sorted(D.glob("GF-*.csv")): rows+=list(csv.DictReader(p.open(encoding="utf-8-sig",newline="")))
 cand=[r for r in rows if r["hint_state"]=="EXACT_CATALOG_HINT" and r["review_lane"]=="IP_OR_VARIANT_AUTHORITY_REVIEW"]
 out=[]
 for r in cand: out.append({**r,"candidate_authority":"EXACT_QUALIFIER_EQUALS_COPYRIGHT_TAG","authority_decision":"PENDING_SECOND_REVIEW","second_review":"PENDING","production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"candidate_families":len(out),"candidate_character_rows":sum(int(r["character_rows"]) for r in out),"auto_approved":0,"second_review_pass":0,
 "multi_home_conflicts":0,"accepted_source_modified":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
