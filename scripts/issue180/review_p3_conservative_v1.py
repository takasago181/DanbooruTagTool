#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P3_RESEARCH_BATCH.csv";OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_P3_CONSERVATIVE_REVIEW_V1.csv";SUM=ROOT/"artifacts/issue180-full-preflight/next_root_p3_conservative_review_v1_summary.json"
KNOWN={"league":"league_of_legends","housamo":"tokyo_afterschool_summoners","girls'_frontline_2":"girls'_frontline_2:_exilium","p&d":"puzzle_&_dragons","sao":"sword_art_online","tf2":"team_fortress_2"}
AMBIG={"mega_man","sekaiju","splatoon","cookie","hetalia","tales","kirby","naruto","neptunia","nanoha","neural_cloud"}
def main():
 rows=list(csv.DictReader(SRC.open("r",encoding="utf-8-sig",newline="")));out=[]
 for r in rows:
  q=r["qualifier"]
  if q in KNOWN:r["candidate_root"]=KNOWN[q];r["decision"]="CANDIDATE_NORMALIZATION_REQUIRES_CATALOG_AND_AUTHORITY";r["research_reason"]="NORMALIZATION_CANDIDATE_ONLY"
  else:r["decision"]="HOME_UNRESOLVED";r["research_reason"]="SEMANTIC_OR_SERIES_AMBIGUITY"
  out.append(r)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"normalization_candidates":sum(r["decision"].startswith("CANDIDATE_") for r in out),"unresolved":sum(r["decision"]=="HOME_UNRESOLVED" for r in out),"auto_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
