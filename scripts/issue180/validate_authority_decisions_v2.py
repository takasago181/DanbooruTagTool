#!/usr/bin/env python3
"""Validate persistent autonomous decisions before compiling Issue #180 v2."""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

R=Path(__file__).resolve().parents[2]
P=R/"docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CENSUS=R/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
FAMILY_WORK=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/FAMILY_WORK_QUEUE_V2.csv"
EXPECTED_FIELDS=[
 "scope","key","home_copyright","base_character","authority_type","evidence_url",
 "evidence_claim","validation_state","officiality_state","notes",
]
VALID_SCOPES={"FAMILY_QUALIFIER","DIRECT_CHARACTER","VARIANT_CHARACTER","NOT_OFFICIAL_CHARACTER","BLOCK_CHARACTER"}
VALID_STATES={"PASS","UNRESOLVED","PENDING","NEEDS_HIGHER_REASONING"}
BROAD_PASS_TYPES={
 "ROOT_POLICY_REVIEWED",
 "OFFICIAL_ROSTER_ROOT_POLICY",
 "FIRST_PARTY_CANONICAL_ROOT",
 "CURATED_ROSTER_ROOT_POLICY",
}


def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def is_grounded_evidence(row):
 url=(row.get("evidence_url") or "").strip()
 claim=(row.get("evidence_claim") or "").strip()
 return url.startswith(("https://","http://")) or claim.startswith(("REPO:","POLICY:"))


def main():
 rows=read(P)
 catalog=read(CAT)
 chars={r["canonical_tag"] for r in catalog if r.get("category_name")=="Character"}
 roots={r["canonical_tag"] for r in catalog if r.get("category_name")=="Copyright"}
 alias_index=defaultdict(set)
 for r in catalog:
  if r.get("category_name")!="Copyright": continue
  alias_index[r["canonical_tag"].lower()].add(r["canonical_tag"])
  for a in (r.get("aliases","") or "").split("|"):
   a=a.strip().lower()
   if a: alias_index[a].add(r["canonical_tag"])

 def root_resolves(value):
  value=(value or "").strip()
  if value in roots:return True
  return len(alias_index.get(value.lower(),set()))==1

 census=read(CENSUS)
 valid_families={(r.get("final_qualifier") or "").strip().lower() for r in census if (r.get("final_qualifier") or "").strip()}
 family_lane={r["family"]:r.get("work_lane","") for r in read(FAMILY_WORK)}

 with P.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=EXPECTED_FIELDS:
   raise SystemExit(f"decision ledger schema drift: {reader.fieldnames}")

 seen_rows=set(); seen_scope_key=set(); states=Counter(); scopes=Counter()
 for i,r in enumerate(rows,2):
  scope=(r.get("scope") or "").strip(); key=(r.get("key") or "").strip()
  state=(r.get("validation_state") or "").strip(); home=(r.get("home_copyright") or "").strip()
  if not scope and not key and not state:
   continue
  if scope not in VALID_SCOPES: raise SystemExit(f"line {i}: invalid scope {scope!r}")
  if state not in VALID_STATES: raise SystemExit(f"line {i}: invalid validation_state {state!r}")
  if not key: raise SystemExit(f"line {i}: blank key")
  sig=(scope,key,home,(r.get("base_character") or "").strip(),state)
  if sig in seen_rows: raise SystemExit(f"line {i}: duplicate decision row {sig}")
  seen_rows.add(sig)
  scope_key=(scope,key)
  if scope_key in seen_scope_key:
   raise SystemExit(f"line {i}: multiple decisions for same scope/key {scope_key}; consolidate evidence into one row")
  seen_scope_key.add(scope_key)
  states[state]+=1; scopes[scope]+=1

  if scope=="FAMILY_QUALIFIER":
   key=key.lower()
   if key not in valid_families:
    raise SystemExit(f"line {i}: unknown qualifier family {key}")
  elif key not in chars:
   raise SystemExit(f"line {i}: unknown Character key {key}")

  if state!="PASS":
   continue

  authority_type=(r.get("authority_type") or "").strip()
  officiality=(r.get("officiality_state") or "").strip()
  if not authority_type:
   raise SystemExit(f"line {i}: PASS missing authority_type")
  if not is_grounded_evidence(r):
   raise SystemExit(f"line {i}: PASS requires http(s) evidence_url or evidence_claim beginning REPO:/POLICY:")

  if scope in {"FAMILY_QUALIFIER","DIRECT_CHARACTER","VARIANT_CHARACTER"}:
   if not home: raise SystemExit(f"line {i}: PASS relation missing HOME")
   if not root_resolves(home): raise SystemExit(f"line {i}: HOME does not resolve uniquely in Copyright catalog: {home}")
  elif home:
   raise SystemExit(f"line {i}: {scope} must not carry HOME")

  if scope=="FAMILY_QUALIFIER":
   lane=family_lane.get(key,"")
   if lane=="HIGHER_REASONING_NON_HOME_SEMANTICS":
    raise SystemExit(f"line {i}: {key} is a non-HOME collaboration/project family; use direct/variant evidence, not FAMILY_QUALIFIER")
   if lane.startswith("HIGHER_REASONING_BROAD") and authority_type not in BROAD_PASS_TYPES:
    raise SystemExit(f"line {i}: broad family PASS requires explicit root-policy/roster authority_type")

  if scope=="DIRECT_CHARACTER" and officiality not in {"OFFICIAL_CONFIRMED","OFFICIAL_IDENTITY"}:
   raise SystemExit(f"line {i}: DIRECT_CHARACTER PASS requires OFFICIAL_CONFIRMED/OFFICIAL_IDENTITY")

  if scope=="VARIANT_CHARACTER":
   base=(r.get("base_character") or "").strip()
   if not base: raise SystemExit(f"line {i}: variant PASS missing base_character")
   if base not in chars: raise SystemExit(f"line {i}: variant PASS base is not a Character: {base}")
   if officiality not in {"OFFICIAL_VARIANT","OFFICIAL_CONFIRMED"}:
    raise SystemExit(f"line {i}: variant PASS requires OFFICIAL_VARIANT/OFFICIAL_CONFIRMED")

  if scope=="NOT_OFFICIAL_CHARACTER" and officiality!="NOT_OFFICIAL_CONFIRMED":
   raise SystemExit(f"line {i}: NOT_OFFICIAL PASS requires NOT_OFFICIAL_CONFIRMED")

 print({"rows":len(rows),"states":dict(states),"scopes":dict(scopes),"gate":"PASS"})


if __name__=="__main__":main()
