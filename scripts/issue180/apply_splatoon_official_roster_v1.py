#!/usr/bin/env python3
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW";E=R/"docs/issue180/evidence/splatoon_official_roster_v1.csv";IN=D/"IP_REMAINING.csv";OUT=D/"SPLATOON_OFFICIAL_HOME_V1.csv"
def main():
 ev=list(csv.DictReader(E.open(encoding="utf-8-sig"))); bases={r["canonical_base"]:r for r in ev}; rows=[r for r in csv.DictReader(IN.open(encoding="utf-8-sig")) if (r.get("final_qualifier") or "").lower()=="splatoon"];out=[]
 for r in rows:
  t=r["canonical_tag"];hits=[b for b in bases if t==b+"_(splatoon)" or t.startswith(b+"_(")]
  if len(hits)==1:
   e=bases[hits[0]];state="SECOND_REVIEW_PASS_RESEARCH_ONLY";home=e["home_copyright"]
  else: state="HOME_UNRESOLVED";home="";e={"evidence_url":"","evidence_type":""}
  out.append({**r,"base_character":hits[0] if len(hits)==1 else "","candidate_root_hint":home,"evidence_url":e["evidence_url"],"evidence_type":e["evidence_type"],"authority_decision":state,"second_review":"PASS" if home else "UNRESOLVED","production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 n=sum(bool(r["candidate_root_hint"]) for r in out);x={"splatoon_rows":len(rows),"official_home_pass":n,"unresolved":len(rows)-n,"evidence_bases":len(bases),"accepted_source_modified":False,"production_modified":False}
 (D/"splatoon_official_home_v1_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if len(rows)!=70 or n!=47: raise SystemExit(f"regression rows={len(rows)} pass={n}")
if __name__=="__main__":main()
