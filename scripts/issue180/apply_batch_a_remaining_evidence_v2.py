#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/BATCH_A_REMAINING_7_RESEARCH.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/BATCH_A_REMAINING_7_EVIDENCE_V2.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/batch_a_remaining_7_evidence_v2_summary.json"
# First-party evidence URLs are intentionally separate from HOME approval.
E={
"genshin_impact":("https://genshin.hoyoverse.com/","HoYoverse official Genshin Impact site.","FIRST_PARTY_FRANCHISE_EVIDENCE"),
"honkai_impact":("https://honkaiimpact3.hoyoverse.com/","HoYoverse official Honkai Impact 3rd site.","FIRST_PARTY_NORMALIZATION_EVIDENCE"),
"nikke":("https://nikke-en.com/","Official GODDESS OF VICTORY: NIKKE site.","FIRST_PARTY_NORMALIZATION_EVIDENCE"),
"pgr":("https://pgr.kurogame.net/","Kuro Games official Punishing: Gray Raven site.","FIRST_PARTY_NORMALIZATION_EVIDENCE"),
"reverse:1999":("https://re1999.bluepoch.com/","Bluepoch official Reverse: 1999 site.","FIRST_PARTY_FRANCHISE_EVIDENCE"),
}
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline="")));out=[]
 for r in rows:
  q=r["qualifier"]
  if q in E:
   url,claim,state=E[q];r["official_source_url"]=url;r["official_source_claim"]=claim;r["research_state"]=state;r["authority_decision"]="EVIDENCE_FOUND_HOME_SEMANTICS_PENDING"
  elif q=="project_moon":
   r["research_state"]="UMBRELLA_AMBIGUOUS";r["authority_decision"]="HOME_UNRESOLVED";r["official_source_claim"]="Project Moon is an umbrella/company-universe candidate; do not infer a single work home from qualifier alone."
  elif q=="girls'_frontline":
   r["research_state"]="FIRST_PARTY_EVIDENCE_STILL_PENDING";r["authority_decision"]="HOME_UNRESOLVED"
  out.append(r)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"first_party_evidence_added":sum(bool(r["official_source_url"]) for r in out),"explicit_unresolved":sum(r["authority_decision"]=="HOME_UNRESOLVED" for r in out),"home_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
