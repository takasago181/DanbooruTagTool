#!/usr/bin/env python3
"""Second-review the 196 normalized Copyright candidates conservatively.
Normalization is supporting evidence; umbrella/generic/variant semantics stay unresolved."""
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/"artifacts/issue180-full-preflight/POST_EXACT_REVIEW";IN=D/"IP_ROOT_NORMALIZED_CANDIDATES_V1.csv";OUT=D/"IP_ROOT_NORMALIZED_SECOND_REVIEW_V1.csv"
BLOCK={"disney","marvel","final_fantasy","idolmaster","precure","yu-gi-oh!","nijisanji","dragon_ball","mega_man","tales","persona","megami_tensei","zelda","kirby","naruto","neptunia","nanoha","x-men","transformers","mario"}
GEN=re.compile(r"(costume|uniform|summer|winter|new.year|casual|female|male|young|timeskip|stand|human|character|racehorse|vtuber)",re.I)
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));out=[];p=u=0
 for r in rows:
  if r["candidate_state"]!="UNIQUE_NORMALIZED_COPYRIGHT_CANDIDATE":continue
  fam=r["family"].lower();root=r["candidate_roots"]
  bad=fam in BLOCK or root in BLOCK or bool(GEN.search(fam))
  dec="HOME_UNRESOLVED_SEMANTIC_REVIEW" if bad else "SECOND_REVIEW_PASS_RESEARCH_ONLY"
  sr="UNRESOLVED" if bad else "PASS";u+=bad;p+=not bad
  out.append({**r,"candidate_root_hint":root,"authority_decision":dec,"second_review":sr,"production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"reviewed_families":len(out),"second_review_pass_families":p,"unresolved_families":u,"auto_approved":0,"production_approved":0,"accepted_source_modified":False,"production_modified":False}
 (D/"normalized_second_review_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
