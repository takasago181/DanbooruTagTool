#!/usr/bin/env python3
"""Accumulate high-precision Issue #180 HOME authority evidence.
Consumes second-reviewed evidence outputs only; never invents relations."""
import csv,json
from pathlib import Path

R=Path(__file__).resolve().parents[2]
A=R/"artifacts/issue180-full-preflight"
D=A/"POST_NORMALIZED_REVIEW"
OD=D/"MEGABATCH_AUTHORITY"
OUT=OD/"AUTHORITY_LEDGER_V1.csv"

SOURCES=[
 D/"SPLATOON_OFFICIAL_HOME_V1.csv",
 D/"EXACT_ROOT_SEMANTIC_BATCH02_V1.csv",
 D/"HIGH_YIELD_OFFICIAL_ROOT_BATCH03_V1.csv",
 D/"OFFICIAL_ROOT_BATCH04_V1.csv",
 D/"DIRECT_OFFICIAL_CHARACTER_ROSTER_BATCH05_V1.csv",
 D/"OFFICIAL_ROOT_BATCH06_V1.csv",
]
EXPECTED_SOURCE_PASS={
 "SPLATOON_OFFICIAL_HOME_V1.csv":47,
 "EXACT_ROOT_SEMANTIC_BATCH02_V1.csv":315,
 "HIGH_YIELD_OFFICIAL_ROOT_BATCH03_V1.csv":438,
 "OFFICIAL_ROOT_BATCH04_V1.csv":90,
 "DIRECT_OFFICIAL_CHARACTER_ROSTER_BATCH05_V1.csv":36,
 "OFFICIAL_ROOT_BATCH06_V1.csv":167,
}
EXPECTED_TOTAL=sum(EXPECTED_SOURCE_PASS.values())

def main():
 ledger=[];seen={};source_counts={}
 for p in SOURCES:
  if not p.exists():
   raise SystemExit("missing authority source "+str(p))
  accepted=0
  for r in csv.DictReader(p.open(encoding="utf-8-sig",newline="")):
   if r.get("second_review")!="PASS" or not r.get("candidate_root_hint"):
    continue
   tag=r.get("canonical_tag","");home=r["candidate_root_hint"]
   if not tag:
    raise SystemExit("empty canonical tag in "+p.name)
   if tag in seen and seen[tag]!=home:
    raise SystemExit("HOME conflict "+tag)
   if tag in seen:
    # Same HOME from an earlier reviewed source is corroboration, not a conflict.
    # Count it for the source gate but keep one canonical ledger row.
    accepted+=1
    continue
   seen[tag]=home
   accepted+=1
   ledger.append({
    "canonical_tag":tag,
    "home_copyright":home,
    "evidence_url":r.get("evidence_url",""),
    "evidence_type":r.get("evidence_type",""),
    "source_file":p.name,
    "second_review":"PASS",
    "production_approved":"false",
   })
  source_counts[p.name]=accepted
  expected=EXPECTED_SOURCE_PASS[p.name]
  if accepted!=expected:
   raise SystemExit(f"authority source count drift {p.name}: expected {expected}, got {accepted}")

 if len(ledger)!=len(seen):
  raise SystemExit(f"ledger uniqueness drift: rows {len(ledger)}, unique {len(seen)}")
 if len(ledger)>EXPECTED_TOTAL:
  raise SystemExit(f"ledger exceeds validated source rows: {len(ledger)} > {EXPECTED_TOTAL}")

 OD.mkdir(parents=True,exist_ok=True)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=ledger[0].keys(),lineterminator="\n")
  w.writeheader();w.writerows(ledger)

 x={
  "authority_ledger_rows":len(ledger),
  "unique_characters":len(seen),
  "source_counts":source_counts,
  "conflicts":0,
  "auto_inferred":0,
  "accepted_source_modified":False,
  "production_modified":False,
 }
 (OD/"authority_ledger_v1_summary.json").write_text(
  json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"
 )
 print(json.dumps(x,ensure_ascii=False,indent=2))

if __name__=="__main__":
 main()
