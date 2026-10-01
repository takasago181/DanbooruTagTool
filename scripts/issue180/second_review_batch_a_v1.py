#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_AUTHORITY_EVIDENCE_V1.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/root_review_batch_a_second_review_v1_summary.json"
# Conservative second review: approve only direct franchise roots where the first-party evidence
# supports character membership and no umbrella/subwork ambiguity is introduced by the mapping.
SAFE={"fire_emblem","granblue_fantasy","kemono_friends","one_piece","zenless_zone_zero"}
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]
    for r in rows:
        q=r["qualifier"]; evidence=bool(r["official_source_url"])
        if q in SAFE and evidence:
            r["root_semantics"]="CANONICAL_FRANCHISE_ROOT"
            r["authority_decision"]="SECOND_REVIEW_PASS_RESEARCH_ONLY"
            r["second_review"]="PASS"
        elif evidence:
            r["second_review"]="REVIEW"
        out.append(r)
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    passed=sum(r["second_review"]=="PASS" for r in out)
    summary={"families":len(out),"second_review_pass":passed,"still_pending":len(out)-passed,
      "production_approved":0,"research_only":True,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
