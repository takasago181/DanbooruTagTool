#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/UNKNOWN_QUALIFIER_TRIAGE.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_REVIEW_FAMILIES.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/next_root_review_families_summary.json"
EXCLUDE={"fire_emblem","girls'_frontline","genshin_impact","kemono_friends","nikke","granblue_fantasy","project_moon","reverse:1999","pgr","zenless_zone_zero","one_piece","xenoblade","honkai_impact"}
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    candidates=[r for r in rows if r["triage_bucket"]=="IP_ROOT_OR_AMBIGUOUS_REVIEW" and r["qualifier"] not in EXCLUDE]
    candidates.sort(key=lambda r:(-int(r["character_count"]),r["qualifier"]))
    top=candidates[:50]
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        fields=["rank","qualifier","character_count","sample_tags","review_state"]
        w=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n");w.writeheader()
        for i,r in enumerate(top,1): w.writerow({"rank":i,"qualifier":r["qualifier"],"character_count":r["character_count"],"sample_tags":r["sample_tags"],"review_state":"PENDING_TRIAGE"})
    summary={"next_families":len(top),"covered_character_rows":sum(int(r["character_count"]) for r in top),
      "auto_approved":0,"purpose":"parallel backlog only","production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
