#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_REVIEW_CATALOG_MATCHES.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_REVIEW_PRIORITY.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/next_root_review_priority_summary.json"
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    for r in rows:
        n=int(r["character_count"]); st=r["catalog_match_state"]
        r["priority_bucket"]="P1_EXACT_ROOT" if st=="EXACT_ROOT_EXISTS" else ("P2_NORMALIZATION" if st=="NORMALIZED_MATCH" else "P3_SEMANTIC_RESEARCH")
        r["priority_score"]=str(n)
    rows.sort(key=lambda r:({"P1_EXACT_ROOT":0,"P2_NORMALIZATION":1,"P3_SEMANTIC_RESEARCH":2}[r["priority_bucket"]],-int(r["character_count"]),r["qualifier"]))
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=rows[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rows)
    counts={b:sum(r["priority_bucket"]==b for r in rows) for b in ["P1_EXACT_ROOT","P2_NORMALIZATION","P3_SEMANTIC_RESEARCH"]}
    coverage={b:sum(int(r["character_count"]) for r in rows if r["priority_bucket"]==b) for b in counts}
    summary={"families":len(rows),"family_counts":counts,"character_coverage":coverage,"auto_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
