#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_PREFILL.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/root_review_batch_a_prefill_summary.json"

# Candidate root spellings only. These are NOT approvals.
CANDIDATES={
"fire_emblem":"fire_emblem",
"girls'_frontline":"girls'_frontline",
"genshin_impact":"genshin_impact",
"kemono_friends":"kemono_friends",
"nikke":"goddess_of_victory:_nikke",
"granblue_fantasy":"granblue_fantasy",
"project_moon":"project_moon",
"reverse:1999":"reverse:1999",
"pgr":"punishing:_gray_raven",
"zenless_zone_zero":"zenless_zone_zero",
"one_piece":"one_piece",
"xenoblade":"xenoblade_(series)",
"honkai_impact":"honkai_impact_3rd",
}

def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    out=[]
    for r in rows:
        q=r["qualifier"]
        r["proposed_root"]=CANDIDATES[q]
        r["semantic_result"]="PENDING_AUTHORITY_REVIEW"
        r["conflict_check"]="PENDING"
        r["reviewer_note"]="Candidate spelling prefill only; frequency/qualifier text is not HOME authority."
        out.append(r)
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"review_rows":len(out),"families":len(CANDIDATES),"auto_approved":0,
      "authority_review_required":len(out),"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
