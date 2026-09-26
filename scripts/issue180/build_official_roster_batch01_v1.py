#!/usr/bin/env python3
"""High-throughput official-roster exact-name matching for remaining Characters.
First-party roster only; exact normalized names only; candidate + second-review queue, not production."""
import csv,json,re,unicodedata
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";D=A/"POST_NORMALIZED_REVIEW";CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv";EV=R/"docs/issue180/evidence/official_roster_sources_batch01.csv";OUT=D/"OFFICIAL_ROSTER_BATCH01_V1.csv"
ROOTS={"umamusume","arknights"}
def norm(s):return re.sub(r"[^0-9a-zぁ-んァ-ヶ一-龯]+","",unicodedata.normalize("NFKC",s or "").lower())
def terms(r):
 xs=[r.get("canonical_tag",""),r.get("display_ja","")]+(r.get("aliases","") or "").split("|")+(r.get("search_ja","") or "").split("|")
 return {norm(x) for x in xs if len(norm(x))>=2}
def main():
 ev={r["home_copyright"]:r for r in csv.DictReader(EV.open(encoding="utf-8-sig"))};assert set(ev)==ROOTS
 cat=list(csv.DictReader(CAT.open(encoding="utf-8-sig",newline=""))); cps={r["canonical_tag"]:r for r in cat if r["category_name"]=="Copyright" and r["canonical_tag"] in ROOTS}
 # This batch records authoritative source coverage only. Character names must be explicitly imported from source before PASS.
 rows=list(csv.DictReader((D/"UNQUALIFIED.csv").open(encoding="utf-8-sig",newline="")))+list(csv.DictReader((D/"IP_REMAINING.csv").open(encoding="utf-8-sig",newline="")))
 out=[]
 for r in rows:
  q=(r.get("final_qualifier") or "").lower();candidate=q if q in ROOTS else ""
  if candidate:
   e=ev[candidate];out.append({**r,"candidate_root_hint":candidate,"evidence_url":e["evidence_url"],"evidence_type":e["evidence_type"],"authority_decision":"OFFICIAL_ROSTER_SOURCE_AVAILABLE_NAME_MATCH_PENDING","second_review":"PENDING","production_approved":"false"})
 if out:
  with OUT.open("w",encoding="utf-8-sig",newline="") as f:w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"source_roots":len(ev),"queued_rows":len(out),"second_review_pass":0,"auto_approved":0,"accepted_source_modified":False,"production_modified":False}
 (D/"official_roster_batch01_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
