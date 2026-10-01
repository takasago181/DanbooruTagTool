#!/usr/bin/env python3
"""Build next global worklists from the post-second-review 35,890 HOME state."""
import csv,json,re
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";IN=A/"GLOBAL_APPROVED_QUALIFIER_HOME_V1.csv";OD=A/"POST_EXACT_REVIEW";OD.mkdir(parents=True,exist_ok=True)
ATTR=re.compile(r"^(?:[0-9]+(?:st|nd|rd|th)_costume|new_year|casual|stand|timeskip|female|male|summer|school_uniform|young|human|character|racehorse|cat)$")
def write(name,rows):
 p=OD/name
 if rows:
  with p.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));u=[r for r in rows if r["home_state"]=="HOME_UNRESOLVED"]
 uq=[r for r in u if not (r.get("final_qualifier") or "").strip()]
 av=[r for r in u if ATTR.match((r.get("final_qualifier") or "").strip().lower())]
 ip=[r for r in u if r not in uq and r not in av]
 write("UNQUALIFIED_ROSTER_ALL.csv",uq);write("ATTRIBUTE_VARIANT_ALL.csv",av);write("IP_ROOT_REMAINING_ALL.csv",ip)
 fam=Counter((r.get("final_qualifier") or "").strip().lower() for r in ip)
 x={"character_rows":len(rows),"confirmed_rows":len(rows)-len(u),"unresolved_rows":len(u),"unqualified_rows":len(uq),"attribute_variant_rows":len(av),"ip_root_remaining_rows":len(ip),"ip_root_remaining_families":len(fam),"top500_ip_rows":sum(n for _,n in fam.most_common(500)),"accepted_source_modified":False,"production_modified":False}
 (OD/"summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if sum((len(uq),len(av),len(ip)))!=len(u):raise SystemExit("partition regression")
if __name__=="__main__":main()
