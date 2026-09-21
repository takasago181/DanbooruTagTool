#!/usr/bin/env python3
"""Generate all 96 authority-review packets plus deterministic candidate-root hints. Never auto-confirms."""
import csv,json,re
from collections import defaultdict,Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";IN=A/"GLOBAL_UNRESOLVED_FAMILY_SHARDS_V1.csv";CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv";OD=A/"global-family-review-packets";SUM=A/"global_family_review_packets_v1_summary.json"
def norms(s):
 s=s.lower();return {s,s.replace("_",""),s.replace("_"," "),re.sub(r"[^a-z0-9]","",s)}
def main():
 cps=[]
 for r in csv.DictReader(CAT.open(encoding="utf-8-sig",newline="")):
  if r.get("category_name")=="Copyright":cps.append((r["canonical_tag"],norms(r["canonical_tag"])))
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));OD.mkdir(parents=True,exist_ok=True);groups=defaultdict(list);hints=Counter()
 for r in rows:
  fam=r["family"]; cand=[]
  if fam!="__UNQUALIFIED__" and r["review_lane"]!="ATTRIBUTE_VARIANT_REVIEW":
   fn=norms(fam)
   cand=[tag for tag,tn in cps if fn & tn]
  state="EXACT_CATALOG_HINT" if len(cand)==1 else ("AMBIGUOUS_CATALOG_HINT" if len(cand)>1 else "NO_CATALOG_HINT")
  hints[state]+=1;r={**r,"candidate_root_hint":cand[0] if len(cand)==1 else "","hint_state":state,"hint_count":str(len(cand)),"authority_decision":"PENDING","second_review":"PENDING"}
  groups[r["review_shard"]].append(r)
 for shard,rs in groups.items():
  p=OD/f"{shard}.csv"
  with p.open("w",encoding="utf-8-sig",newline="") as f:
   w=csv.DictWriter(f,fieldnames=rs[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rs)
 x={"families":len(rows),"packets":len(groups),"hint_states":dict(hints),"auto_approved":0,"second_review_pass":0,"accepted_source_modified":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if len(groups)!=96 or len(rows)!=3849:raise SystemExit(1)
if __name__=="__main__":main()
