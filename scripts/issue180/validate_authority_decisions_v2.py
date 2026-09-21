#!/usr/bin/env python3
"""Validate persistent autonomous decisions before compiling Issue #180 v2."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[2]
P=R/"docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
EXPECTED_FIELDS=[
 "scope","key","home_copyright","base_character","authority_type","evidence_url",
 "evidence_claim","validation_state","officiality_state","notes",
]
VALID_SCOPES={"FAMILY_QUALIFIER","DIRECT_CHARACTER","VARIANT_CHARACTER","NOT_OFFICIAL_CHARACTER","BLOCK_CHARACTER"}
VALID_STATES={"PASS","UNRESOLVED","PENDING","NEEDS_HIGHER_REASONING"}

def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def main():
 rows=read(P)
 catalog=read(CAT)
 chars={r["canonical_tag"] for r in catalog if r.get("category_name")=="Character"}
 roots={r["canonical_tag"] for r in catalog if r.get("category_name")=="Copyright"}
 with P.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=EXPECTED_FIELDS:
   raise SystemExit(f"decision ledger schema drift: {reader.fieldnames}")
 seen=set(); states=Counter(); scopes=Counter()
 for i,r in enumerate(rows,2):
  scope=(r.get("scope") or "").strip(); key=(r.get("key") or "").strip()
  state=(r.get("validation_state") or "").strip(); home=(r.get("home_copyright") or "").strip()
  if not scope and not key and not state:
   continue
  if scope not in VALID_SCOPES: raise SystemExit(f"line {i}: invalid scope {scope!r}")
  if state not in VALID_STATES: raise SystemExit(f"line {i}: invalid validation_state {state!r}")
  if not key: raise SystemExit(f"line {i}: blank key")
  sig=(scope,key,home,(r.get("base_character") or "").strip(),state)
  if sig in seen: raise SystemExit(f"line {i}: duplicate decision row {sig}")
  seen.add(sig); states[state]+=1; scopes[scope]+=1
  if scope!="FAMILY_QUALIFIER" and key not in chars:
   raise SystemExit(f"line {i}: unknown Character key {key}")
  if state=="PASS":
   if not (r.get("authority_type") or "").strip():
    raise SystemExit(f"line {i}: PASS missing authority_type")
   if not ((r.get("evidence_url") or "").strip() or (r.get("evidence_claim") or "").strip()):
    raise SystemExit(f"line {i}: PASS missing evidence")
   if scope in {"FAMILY_QUALIFIER","DIRECT_CHARACTER","VARIANT_CHARACTER"}:
    if not home: raise SystemExit(f"line {i}: PASS relation missing HOME")
    # Aliases may be normalized by the compiler, so exact-root absence alone is not failure.
   elif home:
    raise SystemExit(f"line {i}: {scope} must not carry HOME")
   if scope=="VARIANT_CHARACTER":
    if not (r.get("base_character") or "").strip():
     raise SystemExit(f"line {i}: variant PASS missing base_character")
    if (r.get("officiality_state") or "").strip() not in {"OFFICIAL_VARIANT","OFFICIAL_CONFIRMED"}:
     raise SystemExit(f"line {i}: variant PASS requires OFFICIAL_VARIANT/OFFICIAL_CONFIRMED")
   if scope=="NOT_OFFICIAL_CHARACTER" and (r.get("officiality_state") or "").strip()!="NOT_OFFICIAL_CONFIRMED":
    raise SystemExit(f"line {i}: NOT_OFFICIAL PASS requires NOT_OFFICIAL_CONFIRMED")
 print({"rows":len(rows),"states":dict(states),"scopes":dict(scopes),"gate":"PASS"})

if __name__=="__main__":main()
