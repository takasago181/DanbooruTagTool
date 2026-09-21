#!/usr/bin/env python3
"""Build one prioritized queue for every unresolved Issue #180 Character."""
import csv,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2]; D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW"
MASTER=D/"MASTER_HOME/CHARACTER_HOME_MASTER_V1.csv"; OUT=D/"MASTER_HOME/UNRESOLVED_PRIORITY_V1.csv"
SOURCES=[("IP_REMAINING.csv","IP_QUALIFIER"),("ATTRIBUTE_VARIANT.csv","VARIANT"),("UNQUALIFIED_ROSTER_CANDIDATES_V1.csv","UNQUALIFIED")]
KNOWN_ATTR={"1st_costume","2nd_costume","3rd_costume","4th_costume","5th_costume","new_year","summer","casual","school_uniform","female","male","young","timeskip","stand","racehorse","human","character"}
def read(p): return list(csv.DictReader(p.open(encoding="utf-8-sig",newline="")))
def main():
 master=read(MASTER); unresolved={r["canonical_tag"] for r in master if r["final_state"]=="HOME_UNRESOLVED"}
 meta={}
 for fn,kind in SOURCES:
  p=D/fn
  if not p.exists(): raise SystemExit("missing triage source "+fn)
  for r in read(p):
   tag=r.get("canonical_tag") or r.get("character_tag") or ""
   if not tag: continue
   x=meta.setdefault(tag,{"queue_kind":kind,"final_qualifier":"","roster_candidate_state":""})
   if x["queue_kind"]!=kind: x["queue_kind"]="MULTI_SOURCE"
   x["final_qualifier"]=r.get("final_qualifier","") or x["final_qualifier"]
   x["roster_candidate_state"]=r.get("roster_candidate_state","") or x["roster_candidate_state"]
 out=[]
 for tag in sorted(unresolved):
  x=meta.get(tag,{})
  kind=x.get("queue_kind","OTHER_UNRESOLVED")
  qualifier=x.get("final_qualifier","")
  if qualifier in KNOWN_ATTR: priority="P2_VARIANT_OR_ATTRIBUTE"
  elif kind=="IP_QUALIFIER": priority="P1_FAMILY_AUTHORITY"
  elif x.get("roster_candidate_state")=="UNIQUE_IDENTITY_OVERLAP_CANDIDATE": priority="P1_DIRECT_ROSTER_REVIEW"
  elif kind=="VARIANT": priority="P2_VARIANT_OR_ATTRIBUTE"
  elif kind=="UNQUALIFIED": priority="P3_UNQUALIFIED_ROSTER"
  else: priority="P4_OTHER"
  out.append({"canonical_tag":tag,"priority":priority,"queue_kind":kind,"final_qualifier":qualifier,
              "roster_candidate_state":x.get("roster_candidate_state",""),"final_state":"HOME_UNRESOLVED"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="
");w.writeheader();w.writerows(out)
 pc=Counter(r["priority"] for r in out); kc=Counter(r["final_qualifier"] for r in out if r["priority"]=="P2_VARIANT_OR_ATTRIBUTE" and r["final_qualifier"]); qc=Counter(r["final_qualifier"] for r in out if r["priority"]=="P1_FAMILY_AUTHORITY" and r["final_qualifier"])
 s={"unresolved_rows":len(out),"priority_counts":dict(pc),"top_variant_attribute_families":kc.most_common(100),"top_ip_families":qc.most_common(100),
    "master_unresolved_match":len(out)==len(unresolved),"auto_approved":0,"production_modified":False}
 (D/"MASTER_HOME/unresolved_priority_v1_summary.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"
",encoding="utf-8")
 print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
