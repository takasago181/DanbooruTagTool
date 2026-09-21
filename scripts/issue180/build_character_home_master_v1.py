#!/usr/bin/env python3
"""Issue #180 full-population HOME master pipeline.

Research-only. Produces one deterministic row for every Character and overlays
only second-reviewed authority. Anything not proven stays HOME_UNRESOLVED.
No accepted/production source is mutated.
"""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW"
OD=D/"MASTER_HOME"; OUT=OD/"CHARACTER_HOME_MASTER_V1.csv"
BASE=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
LEDGER=D/"MEGABATCH_AUTHORITY/AUTHORITY_LEDGER_V1.csv"
EXPECTED=35890

def read(p):
 return list(csv.DictReader(p.open(encoding="utf-8-sig",newline="")))

def main():
 # Prefer the normalized 35,890-row Character population; fail closed if shape drifts.
 if not BASE.exists(): raise SystemExit("missing normalized Character population")
 rows=[r for r in read(BASE) if r.get("category_name")=="Character"]
 if len(rows)!=EXPECTED: raise SystemExit(f"Character population drift: expected {EXPECTED}, got {len(rows)}")
 ledger=read(LEDGER) if LEDGER.exists() else []
 auth={}
 for r in ledger:
  tag=r.get("canonical_tag",""); home=r.get("home_copyright","")
  if not tag or not home: raise SystemExit("invalid authority ledger row")
  if tag in auth and auth[tag]!=home: raise SystemExit("multi-home authority conflict "+tag)
  auth[tag]=home
 out=[]; counts={"HOME_CONFIRMED":0,"HOME_UNRESOLVED":0,"NOT_OFFICIAL_CHARACTER":0}
 seen=set()
 for r in rows:
  tag=r.get("canonical_tag","")
  if not tag or tag in seen: raise SystemExit("empty/duplicate Character tag "+tag)
  seen.add(tag)
  # Authority ledger is the only confirmation source in v1. Fan/non-official
  # classification remains unresolved until a reviewed NOT_OFFICIAL authority exists.
  if tag in auth:
   state="HOME_CONFIRMED"; home=auth[tag]; reason="SECOND_REVIEWED_AUTHORITY_LEDGER"
  else:
   state="HOME_UNRESOLVED"; home=""; reason="NO_SECOND_REVIEWED_HOME_AUTHORITY"
  counts[state]+=1
  out.append({"canonical_tag":tag,"final_state":state,"home_copyright":home,
              "decision_reason":reason,"production_approved":"false"})
 if len(out)!=EXPECTED or sum(counts.values())!=EXPECTED: raise SystemExit("master population accounting failure")
 if counts["HOME_CONFIRMED"]!=len(auth): raise SystemExit(f"authority coverage mismatch: {counts['HOME_CONFIRMED']} vs {len(auth)}")
 OD.mkdir(parents=True,exist_ok=True)
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 summary={"character_population":EXPECTED,"states":counts,"authority_ledger_rows":len(ledger),
          "unique_authority_characters":len(auth),"multi_home_conflicts":0,"silent_approval":0,
          "accepted_source_modified":False,"production_modified":False}
 (OD/"character_home_master_v1_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
