#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
BACKLOG=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_REVIEW_FAMILIES.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/NEXT_ROOT_REVIEW_CATALOG_MATCHES.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/next_root_review_catalog_matches_summary.json"
def norm(s): return s.lower().replace(" ","_")
def main():
    with CAT.open("r",encoding="utf-8-sig",newline="") as fh: cat=list(csv.DictReader(fh))
    roots=sorted({r["canonical_tag"] for r in cat if r.get("category_name","").lower()=="copyright"})
    rootset=set(roots)
    with BACKLOG.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]; exact=0
    for r in rows:
        q=r["qualifier"]; candidates=[]
        if q in rootset: candidates=[q]
        else:
            nq=norm(q)
            candidates=[x for x in roots if norm(x)==nq][:10]
        state="EXACT_ROOT_EXISTS" if q in rootset else ("NORMALIZED_MATCH" if candidates else "NO_DIRECT_MATCH")
        exact+=state=="EXACT_ROOT_EXISTS"
        out.append({**r,"catalog_match_state":state,"catalog_candidates":" | ".join(candidates)})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"families":len(out),"exact_root_exists":exact,
      "normalized_or_no_direct":len(out)-exact,"auto_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
