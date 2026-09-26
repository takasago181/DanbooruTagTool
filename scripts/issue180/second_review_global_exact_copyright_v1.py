#!/usr/bin/env python3
"""Conservative second-review triage for all exact Copyright candidates.
Exact equality is necessary evidence, not sufficient proof. Obvious umbrella/generic roots remain unresolved."""
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";IN=A/"GLOBAL_EXACT_COPYRIGHT_CANDIDATES_V1.csv";OUT=A/"GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv";SUM=A/"global_exact_copyright_second_review_v1_summary.json"
# Known semantic classes that cannot safely mean one canonical home merely by exact qualifier equality.
BLOCK={"disney","marvel","final_fantasy","idolmaster","precure","yu-gi-oh!","nijisanji","dragon_ball","mega_man","tales","persona","megami_tensei","zelda","kirby","naruto","neptunia","nanoha","x-men","transformers","mario"}
GENERIC=re.compile(r"^(character|human|male|female|young|cat|vtuber|racehorse|school_uniform|summer|casual|new_year|[0-9]+(?:st|nd|rd|th)_costume)$")
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));out=[];p=u=0;pc=uc=0
 for r in rows:
  fam=r["family"]; n=int(r["character_rows"])
  blocked=fam in BLOCK or bool(GENERIC.match(fam))
  if blocked: decision="HOME_UNRESOLVED_SEMANTIC_REVIEW";second="UNRESOLVED";u+=1;uc+=n
  else: decision="SECOND_REVIEW_PASS_RESEARCH_ONLY";second="PASS";p+=1;pc+=n
  out.append({**r,"authority_decision":decision,"second_review":second,"production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"second_review_pass_families":p,"unresolved_families":u,"second_review_pass_character_rows":pc,"unresolved_character_rows":uc,
 "auto_approved":0,"production_approved":0,"accepted_source_modified":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if p+u!=len(out) or pc+uc!=sum(int(r["character_rows"]) for r in rows):raise SystemExit(1)
if __name__=="__main__":main()
