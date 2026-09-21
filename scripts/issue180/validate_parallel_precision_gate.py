#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FILES=[
 ("artifacts/issue180-full-preflight/NEXT_ROOT_P1_SHARDS_X2.csv","review_shard"),
 ("artifacts/issue180-full-preflight/NEXT_ROOT_P3_SHARDS_X2.csv","research_shard"),
 ("artifacts/issue180-full-preflight/UNQUALIFIED_AUTHORITY_SHARDS_X2.csv","review_shard"),
]
OUT=ROOT/"artifacts/issue180-full-preflight/PARALLEL_PRECISION_GATE.json"
def main():
 seen={}; dup=[]; total=0; pending_ok=True
 for rel,shardcol in FILES:
  rows=list(csv.DictReader((ROOT/rel).open("r",encoding="utf-8-sig",newline="")))
  for r in rows:
   key=(rel,r.get("qualifier") or r.get("canonical_tag")); total+=1
   if key in seen: dup.append(key)
   seen[key]=r[shardcol]
   # Parallel scheduling must not silently approve anything.
   vals="|".join(str(v) for v in r.values())
   if "PASS_RESEARCH_ONLY" in vals or "HOME_CONFIRMED" in vals: pending_ok=False
 result={"rows_checked":total,"duplicate_assignments":len(dup),"silent_approval_detected":not pending_ok,
  "gate":"PASS" if not dup and pending_ok else "FAIL","production_modified":False}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
 if result["gate"]!="PASS": raise SystemExit(1)
if __name__=="__main__":main()
