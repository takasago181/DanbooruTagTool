#!/usr/bin/env python3
"""Generate all unqualified Character roster candidates from authoritative catalog search/display/alias identity overlap.
Candidate-only; no automatic HOME approval."""
import csv,json,re
from collections import defaultdict,Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";D=A/"POST_NORMALIZED_REVIEW";CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv";IN=D/"UNQUALIFIED.csv";OUT=D/"UNQUALIFIED_ROSTER_CANDIDATES_V1.csv"
def terms(r):
 vals=[r.get("canonical_tag",""),r.get("display_ja","")]+(r.get("aliases","") or "").split("|")+(r.get("search_ja","") or "").split("|")
 return {re.sub(r"\s+","",x).lower() for x in vals if x and len(re.sub(r"\s+","",x))>=2}
def main():
 cat=list(csv.DictReader(CAT.open(encoding="utf-8-sig",newline=""))); cps=[r for r in cat if r["category_name"]=="Copyright"]
 idx=defaultdict(set)
 for r in cps:
  for t in terms(r):idx[t].add(r["canonical_tag"])
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));out=[];st=Counter()
 for r in rows:
  hits=set()
  # Exact identity overlap only; intentionally not fuzzy substring matching.
  for t in terms(r):hits.update(idx.get(t,set()))
  state="UNIQUE_IDENTITY_OVERLAP_CANDIDATE" if len(hits)==1 else ("AMBIGUOUS_IDENTITY_OVERLAP" if hits else "NO_IDENTITY_OVERLAP")
  st[state]+=1;out.append({**r,"roster_candidate_roots":"|".join(sorted(hits)),"roster_candidate_state":state,"authority_decision":"PENDING","second_review":"PENDING","production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"unqualified_rows":len(rows),"candidate_states":dict(st),"auto_approved":0,"accepted_source_modified":False,"production_modified":False}
 (D/"unqualified_roster_candidate_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
