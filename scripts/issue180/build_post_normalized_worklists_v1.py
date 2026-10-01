#!/usr/bin/env python3
"""Rebuild post-normalized unresolved worklists from current 35,890 state."""
import csv,json,re
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";IN=A/"GLOBAL_APPROVED_QUALIFIER_HOME_V1.csv";D=A/"POST_NORMALIZED_REVIEW";D.mkdir(parents=True,exist_ok=True)
ATTR=re.compile(r"^(?:[0-9]+(?:st|nd|rd|th)_costume|new_year|casual|stand|timeskip|female|male|summer|school_uniform|young|human|character|racehorse|cat)$")
def wr(n,rs):
 if rs:
  with (D/n).open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=rs[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rs)
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));u=[r for r in rows if r["home_state"]=="HOME_UNRESOLVED"];uq=[];av=[];ip=[]
 for r in u:
  q=(r.get("final_qualifier") or "").strip().lower()
  (uq if not q else av if ATTR.match(q) else ip).append(r)
 wr("UNQUALIFIED.csv",uq);wr("ATTRIBUTE_VARIANT.csv",av);wr("IP_REMAINING.csv",ip);fam=Counter((r.get("final_qualifier") or "").strip().lower() for r in ip)
 x={"confirmed_rows":len(rows)-len(u),"unresolved_rows":len(u),"unqualified_rows":len(uq),"attribute_variant_rows":len(av),"ip_remaining_rows":len(ip),"ip_remaining_families":len(fam),"top500_ip_rows":sum(n for _,n in fam.most_common(500)),"accepted_source_modified":False,"production_modified":False}
 (D/"summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
