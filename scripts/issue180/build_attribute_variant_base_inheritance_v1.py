#!/usr/bin/env python3
"""Extract safe base-character inheritance candidates from all 844 attribute/variant rows.
Only accepts an exact canonical base tag already HOME_CONFIRMED_RESEARCH."""
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";D=A/"POST_NORMALIZED_REVIEW";IN=D/"ATTRIBUTE_VARIANT.csv";ALL=A/"GLOBAL_APPROVED_QUALIFIER_HOME_V1.csv";OUT=D/"ATTRIBUTE_VARIANT_BASE_INHERITANCE_V1.csv"
SUFFIX=re.compile(r"_(?:\((?:new_year|casual|stand|timeskip|female|male|summer|school_uniform|young|human|character|racehorse|cat|[0-9]+(?:st|nd|rd|th)_costume)\))+$",re.I)
def main():
 allr=list(csv.DictReader(ALL.open(encoding="utf-8-sig",newline="")));home={r.get("canonical_tag",""):r["home_copyright"] for r in allr if r["home_state"]=="HOME_CONFIRMED_RESEARCH"}
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));out=[];ok=0
 for r in rows:
  tag=r.get("canonical_tag","");base=SUFFIX.sub("",tag);h=home.get(base,"");state="BASE_HOME_CONFIRMED_CANDIDATE" if h and base!=tag else "BASE_NOT_CONFIRMED"
  ok+=state.startswith("BASE_HOME");out.append({**r,"base_character":base,"candidate_root_hint":h,"inheritance_state":state,"authority_decision":"PENDING_SECOND_REVIEW","second_review":"PENDING","production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"variant_rows":len(rows),"base_home_confirmed_candidates":ok,"base_not_confirmed":len(rows)-ok,"auto_approved":0,"accepted_source_modified":False,"production_modified":False}
 (D/"attribute_variant_base_inheritance_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
