#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CHECK=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_CATALOG_CHECK.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_FAMILY_GATE.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/root_review_batch_a_family_gate_summary.json"
def main():
    with CAT.open("r",encoding="utf-8-sig",newline="") as fh: cat=list(csv.DictReader(fh))
    copyright={r["canonical_tag"]:r for r in cat if r.get("category_name","").lower()=="copyright"}
    with CHECK.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    groups=defaultdict(list)
    for r in rows: groups[r["qualifier"]].append(r)
    out=[]; pass_rows=0
    for q,items in sorted(groups.items()):
        root=items[0]["proposed_root"]; exists=root in copyright
        consistent=all(r["proposed_root"]==root for r in items)
        unique_samples=len({r["canonical_tag"] for r in items})==len(items)
        state="READY_FOR_AUTHORITY_REVIEW" if exists and consistent and unique_samples else "BLOCKED_MECHANICAL"
        if state=="READY_FOR_AUTHORITY_REVIEW": pass_rows+=sum(1 for r in items)
        out.append({"qualifier":q,"proposed_root":root,"sample_rows":len(items),
          "catalog_root_exists":str(exists).lower(),"single_candidate_root":str(consistent).lower(),
          "unique_sample_rows":str(unique_samples).lower(),"mechanical_gate":state,
          "authority_state":"PENDING","home_semantics_state":"PENDING"})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"families":len(out),"ready_families":sum(r["mechanical_gate"]=="READY_FOR_AUTHORITY_REVIEW" for r in out),
      "blocked_families":sum(r["mechanical_gate"]!="READY_FOR_AUTHORITY_REVIEW" for r in out),
      "ready_sample_rows":pass_rows,"authority_approved":0,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
