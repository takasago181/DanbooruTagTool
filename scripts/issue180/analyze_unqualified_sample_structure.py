#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_REVIEW_SAMPLE.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/UNQUALIFIED_SAMPLE_STRUCTURE.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/unqualified_sample_structure_summary.json"
def bucket(tag):
    if re.search(r"_\([^()]+\)$",tag): return "HAS_TRAILING_QUALIFIER_UNEXPECTED"
    if "_" not in tag: return "SINGLE_TOKEN"
    if re.search(r"_(alter|young|adult|female|male|swimsuit|school_uniform|casual)$",tag): return "VARIANT_LIKE_SUFFIX"
    return "MULTI_TOKEN_UNQUALIFIED"
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]; c=Counter()
    for r in rows:
        b=bucket(r["canonical_tag"]);c[b]+=1;out.append({**r,"structure_bucket":b})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"sample_rows":len(out),"buckets":dict(c),"authority_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
