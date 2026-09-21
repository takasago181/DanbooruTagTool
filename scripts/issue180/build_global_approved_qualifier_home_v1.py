#!/usr/bin/env python3
"""Issue #180: apply every already-approved qualifier root to the entire 35,890 Character population.
Research-only. This is global, not franchise-specific."""
import csv,json,re
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2]; A=R/"artifacts/issue180-full-preflight"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
PREF=A/"CHARACTER_QUALIFIER_CENSUS.csv"
SOURCES=[A/"ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv",A/"BATCH_A_REMAINING_7_SECOND_REVIEW_V2.csv",A/"P1_P3_AUTHORITY_SECOND_REVIEW_V1.csv",A/"GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv",A/"POST_EXACT_REVIEW/IP_ROOT_NORMALIZED_SECOND_REVIEW_V1.csv"]
OUT=A/"GLOBAL_APPROVED_QUALIFIER_HOME_V1.csv"; SUM=A/"global_approved_qualifier_home_v1_summary.json"
def approved():
 d={}; conflicts={}
 for p in SOURCES:
  if not p.exists(): continue
  for r in csv.DictReader(p.open(encoding="utf-8-sig",newline="")):
   q=(r.get("qualifier") or r.get("family") or "").strip().lower()
   passed=r.get("second_review")=="PASS" or r.get("authority_decision")=="SECOND_REVIEW_PASS_RESEARCH_ONLY"
   home=(r.get("candidate_root") or r.get("proposed_root") or r.get("candidate_root_hint") or "").strip()
   if not(q and passed and home): continue
   if q in d and d[q]!=home: conflicts.setdefault(q,set()).update((d[q],home))
   else:d[q]=home
 if conflicts: raise SystemExit("approved qualifier conflict: "+repr(conflicts))
 return d
def main():
 cat=list(csv.DictReader(CAT.open(encoding="utf-8-sig",newline=""))); cps={r["canonical_tag"] for r in cat if r["category_name"]=="Copyright"}
 rows=list(csv.DictReader(PREF.open(encoding="utf-8-sig",newline=""))); dec=approved()
 missing=sorted({h for h in dec.values() if h not in cps})
 if missing: raise SystemExit("missing roots: "+repr(missing))
 out=[]; states=Counter()
 for r in rows:
  q=(r.get("final_qualifier") or "").strip().lower(); h=dec.get(q,"")
  st="HOME_CONFIRMED_RESEARCH" if h else "HOME_UNRESOLVED";states[st]+=1
  out.append({**r,"home_copyright":h,"home_state":st,"authority":"APPROVED_QUALIFIER_GLOBAL" if h else "",
   "accepted_home_count":"1" if h else "0","legacy_relation_used_as_authority":"false","production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"character_rows":len(out),"approved_qualifier_families":len(dec),"state_counts":dict(states),
    "coverage_percent":round(states["HOME_CONFIRMED_RESEARCH"]*100/len(out),2),"missing_roots":len(missing),
    "multi_home_conflicts":0,"accepted_source_modified":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if len(out)!=35890: raise SystemExit("row count regression")
if __name__=="__main__":main()
