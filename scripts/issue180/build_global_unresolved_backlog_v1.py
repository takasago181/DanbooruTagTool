#!/usr/bin/env python3
"""Build the complete unresolved authority backlog after all approved qualifier HOME decisions."""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight"; IN=A/"GLOBAL_APPROVED_QUALIFIER_HOME_V1.csv"
OUT=A/"GLOBAL_UNRESOLVED_BACKLOG_V1.csv"; FAM=A/"GLOBAL_UNRESOLVED_FAMILIES_V1.csv"; SUM=A/"global_unresolved_backlog_v1_summary.json"
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline=""))); unresolved=[r for r in rows if r["home_state"]=="HOME_UNRESOLVED"]
 fam=Counter((r.get("final_qualifier") or "").strip().lower() or "__UNQUALIFIED__" for r in unresolved)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=unresolved[0].keys(),lineterminator="\n");w.writeheader();w.writerows(unresolved)
 fr=[{"family":q,"character_rows":n,"lane":"UNQUALIFIED_ROSTER" if q=="__UNQUALIFIED__" else "QUALIFIER_AUTHORITY","priority":i+1} for i,(q,n) in enumerate(fam.most_common())]
 with FAM.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fr[0].keys(),lineterminator="\n");w.writeheader();w.writerows(fr)
 x={"character_rows":len(rows),"unresolved_rows":len(unresolved),"unresolved_families":len(fr),
 "unqualified_rows":fam.get("__UNQUALIFIED__",0),"qualified_unresolved_rows":len(unresolved)-fam.get("__UNQUALIFIED__",0),
 "accepted_source_modified":False,"production_modified":False}
 # explicit top-N yield excluding unqualified
 qs=[n for q,n in fam.most_common() if q!="__UNQUALIFIED__"];x["top_100_qualified_rows"]=sum(qs[:100]);x["top_500_qualified_rows"]=sum(qs[:500])
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 print("TOP_FAMILIES");print("\n".join(f"{r['priority']:04d} {r['family']} {r['character_rows']}" for r in fr[:120]))
if __name__=="__main__":main()
