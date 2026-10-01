#!/usr/bin/env python3
"""Build large-batch authority queues for all remaining Issue #180 work.
No HOME is approved here; this removes per-franchise turn granularity."""
import csv,json,hashlib
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW";OD=D/"MEGABATCH_AUTHORITY";OD.mkdir(parents=True,exist_ok=True)
SPECS=[("IP_REMAINING.csv","IP",64),("ATTRIBUTE_VARIANT.csv","VARIANT",16),("UNQUALIFIED_ROSTER_CANDIDATES_V1.csv","UNQUALIFIED",128)]
def key(r):return r.get("canonical_tag") or r.get("character_tag") or ""
def main():
 summary={}
 for fn,label,n in SPECS:
  rows=list(csv.DictReader((D/fn).open(encoding="utf-8-sig",newline="")))
  if label=="UNQUALIFIED": rows=[r for r in rows if r.get("roster_candidate_state")!="UNIQUE_IDENTITY_OVERLAP_CANDIDATE"]
  buckets=[[] for _ in range(n)]
  for r in rows:buckets[int(hashlib.sha256(key(r).encode()).hexdigest()[:8],16)%n].append(r)
  for i,rs in enumerate(buckets):
   if not rs:continue
   with (OD/f"{label}-{i+1:03d}-of-{n}.csv").open("w",encoding="utf-8-sig",newline="") as f:
    fields=list(rs[0].keys())+["authority_decision","second_review","production_approved"];w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader()
    for r in rs:w.writerow({**r,"authority_decision":"PENDING_OFFICIAL_AUTHORITY","second_review":"PENDING","production_approved":"false"})
  summary[label]={"rows":len(rows),"shards":n,"min_rows":min(map(len,buckets)),"max_rows":max(map(len,buckets))}
 summary.update({"total_review_rows":sum(v["rows"] for v in summary.values()),"auto_approved":0,"accepted_source_modified":False,"production_modified":False})
 (OD/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
 if summary["IP"]["rows"]!=4797 or summary["VARIANT"]["rows"]!=844 or summary["UNQUALIFIED"]["rows"]!=16791:raise SystemExit("population regression")
if __name__=="__main__":main()
