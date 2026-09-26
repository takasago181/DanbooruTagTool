#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
BATCH=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_PREFILL.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_CATALOG_CHECK.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/root_review_batch_a_catalog_check_summary.json"
def main():
    with CAT.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    copyrights={r["canonical_tag"] for r in rows if r.get("category_name","").lower()=="copyright"}
    with BATCH.open("r",encoding="utf-8-sig",newline="") as fh: batch=list(csv.DictReader(fh))
    out=[]; c=Counter()
    for r in batch:
        exists=r["proposed_root"] in copyrights
        c["ROOT_EXISTS" if exists else "ROOT_MISSING"]+=1
        r["catalog_root_check"]="ROOT_EXISTS" if exists else "ROOT_MISSING"
        out.append(r)
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    fam={}
    for r in out: fam.setdefault(r["qualifier"],[r["proposed_root"],r["catalog_root_check"]])
    summary={"review_rows":len(out),"row_counts":dict(c),
      "families":{q:{"proposed_root":v[0],"catalog_root_check":v[1]} for q,v in fam.items()},
      "authority_approved":False,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
