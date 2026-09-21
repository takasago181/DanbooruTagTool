#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CENSUS=ROOT/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_REVIEW_SAMPLE.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/unqualified_review_sample_summary.json"
def main():
    with CENSUS.open("r",encoding="utf-8-sig",newline="") as fh:
        rows=[r for r in csv.DictReader(fh) if r["preflight_state"]=="UNQUALIFIED"]
    rows=sorted(rows,key=lambda r:r["canonical_tag"])
    # deterministic spread over the whole sorted population
    n=min(200,len(rows)); idx=[(i*len(rows))//n for i in range(n)]
    sample=[rows[i] for i in idx]
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        fields=["canonical_tag","review_state","authority_evidence","proposed_root","note"]
        w=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n");w.writeheader()
        for r in sample:w.writerow({"canonical_tag":r["canonical_tag"],"review_state":"PENDING_AUTHORITY_REVIEW","authority_evidence":"","proposed_root":"","note":"Unqualified control; do not use legacy relation as authority."})
    summary={"unqualified_population":len(rows),"sample_rows":len(sample),"auto_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
