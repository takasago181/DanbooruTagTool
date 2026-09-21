#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CENSUS=ROOT/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
OUTDIR=ROOT/"artifacts/issue180-full-preflight"
OUT=OUTDIR/"ROOT_REVIEW_BATCH_A.csv"
SUMMARY=OUTDIR/"root_review_batch_a_summary.json"

TARGETS=[
"fire_emblem","girls'_frontline","genshin_impact","kemono_friends","nikke",
"granblue_fantasy","project_moon","reverse:1999","pgr","zenless_zone_zero",
"one_piece","xenoblade","honkai_impact",
]

def main():
    with CENSUS.open("r",encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    groups=defaultdict(list)
    for r in rows:
        if r["preflight_state"]=="UNKNOWN_QUALIFIER" and r["final_qualifier"] in TARGETS:
            groups[r["final_qualifier"]].append(r)
    out=[]
    for q in TARGETS:
        items=groups[q]
        if not items: raise SystemExit(f"target qualifier missing: {q}")
        # deterministic semantic sample: first 10 canonical tags per family
        for r in sorted(items,key=lambda x:x["canonical_tag"])[:10]:
            out.append({
              "qualifier":q,"family_character_count":len(items),"canonical_tag":r["canonical_tag"],
              "proposed_root":"","authority_evidence":"","semantic_result":"",
              "conflict_check":"","reviewer_note":"","second_review_required":"true"
            })
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"families":len(TARGETS),"review_rows":len(out),
      "covered_character_rows":sum(len(groups[q]) for q in TARGETS),
      "per_family_sample":10,"auto_approval":False,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
