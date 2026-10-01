#!/usr/bin/env python3
"""Build high-throughput candidate queues for the remaining 24,969 unresolved rows.
No automatic authority approval."""
import csv,json,re
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";D=A/"POST_EXACT_REVIEW";CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
def norm(s):return re.sub(r"[^a-z0-9]+","",(s or "").lower())
def main():
 cat=list(csv.DictReader(CAT.open(encoding="utf-8-sig",newline=""))); cps=[r for r in cat if r["category_name"]=="Copyright"]
 idx=defaultdict(set)
 for r in cps:
  vals=[r.get("canonical_tag",""),r.get("display_ja","")]+(r.get("aliases","") or "").split("|")+(r.get("search_ja","") or "").split("|")
  for v in vals:
   n=norm(v)
   if n:idx[n].add(r["canonical_tag"])
 ip=list(csv.DictReader((D/"IP_ROOT_REMAINING_ALL.csv").open(encoding="utf-8-sig",newline="")))
 out=[];counts=defaultdict(int);rows=defaultdict(int)
 for r in ip:
  q=(r.get("final_qualifier") or "").strip(); cand=sorted(idx.get(norm(q),set()))
  state="UNIQUE_NORMALIZED_COPYRIGHT_CANDIDATE" if len(cand)==1 else ("AMBIGUOUS_NORMALIZED_COPYRIGHT" if cand else "NO_NORMALIZED_COPYRIGHT")
  counts[state]+=1;rows[state]+=1
  out.append({"family":q,"candidate_roots":"|".join(cand),"candidate_state":state,"authority_decision":"PENDING","second_review":"PENDING"})
 # dedupe family output
 seen={};[seen.setdefault(r["family"],r) for r in out]
 p=D/"IP_ROOT_NORMALIZED_CANDIDATES_V1.csv"
 with p.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=next(iter(seen.values())).keys(),lineterminator="\n");w.writeheader();w.writerows(seen.values())
 x={"ip_rows":len(ip),"ip_families":len(seen),"candidate_family_states":dict(__import__("collections").Counter(r["candidate_state"] for r in seen.values())),"auto_approved":0,"accepted_source_modified":False,"production_modified":False}
 (D/"normalized_candidate_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
