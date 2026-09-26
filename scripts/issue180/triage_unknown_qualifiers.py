#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CENSUS=ROOT/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
OUTDIR=ROOT/"artifacts/issue180-full-preflight"
OUT=OUTDIR/"UNKNOWN_QUALIFIER_TRIAGE.csv"
SUMMARY=OUTDIR/"unknown_qualifier_triage_summary.json"

VARIANT_EXACT={
"1st_costume","2nd_costume","3rd_costume","4th_costume","5th_costume",
"new_year","casual","stand","timeskip","female","male","summer",
"school_uniform","human","character","vtuber","racehorse",
}
VARIANT_RE=re.compile(r"^(?:\d+(?:st|nd|rd|th)_costume|.*(?:costume|outfit|uniform|ver\.?|version))$",re.I)

def main():
    with CENSUS.open("r",encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    groups=defaultdict(list)
    for r in rows:
        if r["preflight_state"]=="UNKNOWN_QUALIFIER":
            groups[r["final_qualifier"]].append(r)
    out=[]; counts=Counter()
    for q,items in groups.items():
        if q in VARIANT_EXACT or VARIANT_RE.match(q or ""):
            bucket="VARIANT_OR_ATTRIBUTE"
        else:
            bucket="IP_ROOT_OR_AMBIGUOUS_REVIEW"
        counts[bucket]+=len(items)
        out.append({
          "qualifier":q,"character_count":len(items),"triage_bucket":bucket,
          "sample_tags":" | ".join(r["canonical_tag"] for r in items[:5])
        })
    out.sort(key=lambda r:(-int(r["character_count"]),r["qualifier"]))
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"unknown_character_rows":sum(len(v) for v in groups.values()),"distinct_qualifiers":len(groups),
      "row_bucket_counts":dict(counts),"heuristic_only":True,"auto_approval":False,
      "accepted_source_modified":False,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
