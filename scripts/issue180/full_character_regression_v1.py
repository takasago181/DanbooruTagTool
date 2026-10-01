#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
PREF=ROOT/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
GATE=ROOT/"artifacts/issue180-full-preflight/P1_P3_CATALOG_SEMANTIC_GATE_V1.csv"
JP=ROOT/"artifacts/issue180-full-preflight/P1_P3_JAPANESE_DISPLAY_AUDIT_V1.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/FULL_CHARACTER_REGRESSION_V1.json"
def read(path):
 with path.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
 cat=read(CAT); chars=read(PREF); gate=read(GATE); jp=read(JP)
 copyright={r["canonical_tag"] for r in cat if r["category_name"]=="Copyright"}
 candidate=[r for r in gate if r["gate_state"]!="HOME_UNRESOLVED"]
 missing=[r for r in candidate if r["candidate_root"] not in copyright]
 dup={}
 for r in candidate:
  dup.setdefault((r["lane"],r["qualifier"]),set()).add(r["candidate_root"])
 conflicts=[k for k,v in dup.items() if len(v)>1]
 silent=[r for r in candidate if str(r.get("authority_approved","")).lower()=="true"]
 jp_missing=[r for r in jp if r["gate_state"]!="HOME_UNRESOLVED" and r["japanese_review_required"]=="true"]
 result={"character_rows":len(chars),"candidate_families":len(candidate),"candidate_roots_missing_from_copyright":len(missing),
  "multi_home_conflicts":len(conflicts),"silent_authority_approvals":len(silent),"candidate_families_needing_japanese_review":len(jp_missing),
  "accepted_source_modified":False,"production_modified":False,
  "gate":"PASS" if len(chars)==35890 and not missing and not conflicts and not silent else "FAIL"}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,ensure_ascii=False,indent=2))
 if result["gate"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
