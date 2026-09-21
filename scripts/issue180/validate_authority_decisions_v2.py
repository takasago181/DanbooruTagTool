#!/usr/bin/env python3
"""Validate persistent autonomous decisions before compiling Issue #180 v2."""
from __future__ import annotations
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

R=Path(__file__).resolve().parents[2]
COMPAT=R/"docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
SHARDS=R/"docs/issue180/autonomous/decisions"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CENSUS=R/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
FAMILY_WORK=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/FAMILY_WORK_QUEUE_V2.csv"
UNQUALIFIED_GROUPS=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/UNQUALIFIED_DISCOVERY_GROUPS_V2.csv"
VARIANT_GROUPS=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/VARIANT_PATTERN_GROUPS_V2.csv"
EXPECTED_FIELDS=[
 "scope","key","home_copyright","base_character","authority_type","evidence_url",
 "evidence_claim","validation_state","officiality_state","notes",
]
VALID_SCOPES={"FAMILY_QUALIFIER","DISCOVERY_GROUP","VARIANT_PATTERN","DIRECT_CHARACTER","VARIANT_CHARACTER","NOT_OFFICIAL_CHARACTER","BLOCK_CHARACTER"}
VALID_STATES={"PASS","UNRESOLVED","PENDING","NEEDS_HIGHER_REASONING"}
POLICY_PATH=R/"docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"
POLICY=json.loads(POLICY_PATH.read_text(encoding="utf-8"))
if POLICY.get("version")!=2:
 raise SystemExit("unsupported autonomous policy version")
BROAD_PASS_TYPES=set(POLICY["broad_pass_types"])
BROAD_FAMILIES=set(POLICY["broad_families"])
NON_HOME_FAMILIES=set(POLICY["non_home_families"])
ALLOW_AUTONOMOUS_NOT_OFFICIAL=bool(POLICY["allow_autonomous_not_official_pass"])
ALLOW_AUTONOMOUS_BROAD_FAMILY=bool(POLICY["allow_autonomous_broad_family_pass"])


def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def decision_paths():
 paths=[COMPAT] if COMPAT.exists() else []
 if SHARDS.exists():
  paths.extend(sorted(SHARDS.glob("*.csv")))
 return paths


def read_decisions():
 rows=[]
 for path in decision_paths():
  with path.open(encoding="utf-8-sig",newline="") as f:
   reader=csv.DictReader(f)
   if reader.fieldnames!=EXPECTED_FIELDS:
    raise SystemExit(f"decision ledger schema drift in {path}: {reader.fieldnames}")
   for line,row in enumerate(reader,2):
    row["__source_file"]=str(path.relative_to(R))
    row["__source_line"]=str(line)
    rows.append(row)
 return rows


def evidence_gate(row):
 url=(row.get("evidence_url") or "").strip()
 claim=(row.get("evidence_claim") or "").strip()
 notes=(row.get("notes") or "").strip()
 if url.startswith(("https://","http://")):
  if len(claim) < 12 or claim.startswith("REPO:"):
   return False, "external evidence_url requires a descriptive evidence_claim"
  return True, ""
 if claim.startswith("REPO:"):
  raw=claim[len("REPO:"):].strip().split("#",1)[0].strip()
  if not raw:
   return False, "blank REPO evidence path"
  path=(R/raw).resolve()
  try:
   path.relative_to(R.resolve())
  except ValueError:
   return False, "REPO evidence escapes repository"
  if not path.exists():
   return False, "REPO evidence path does not exist"
  if len(notes) < 8:
   return False, "REPO evidence requires notes describing what the file proves"
  return True, ""
 return False, "PASS requires http(s) evidence_url or REPO:<existing repository path>"


def main():
 rows=read_decisions()
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
 valid_discovery_groups={r["discovery_group"].strip().lower() for r in read(UNQUALIFIED_GROUPS) if r.get("discovery_group","").strip()}
 valid_variant_patterns={r["pattern_id"].strip() for r in read(VARIANT_GROUPS) if r.get("pattern_id","").strip()}

 seen_rows=set(); seen_scope_key={}; states=Counter(); scopes=Counter(); files=Counter()
 for r in rows:
  src=r["__source_file"]; line=r["__source_line"]
  scope=(r.get("scope") or "").strip(); key=(r.get("key") or "").strip()
  state=(r.get("validation_state") or "").strip(); home=(r.get("home_copyright") or "").strip()
  if not scope and not key and not state:
   continue
  where=f"{src}:{line}"
  if scope not in VALID_SCOPES: raise SystemExit(f"{where}: invalid scope {scope!r}")
  if state not in VALID_STATES: raise SystemExit(f"{where}: invalid validation_state {state!r}")
  if not key: raise SystemExit(f"{where}: blank key")
  lookup_key=key.lower() if scope in {"FAMILY_QUALIFIER","DISCOVERY_GROUP"} else key
  sig=(scope,lookup_key,home,(r.get("base_character") or "").strip(),state)
  if sig in seen_rows: raise SystemExit(f"{where}: duplicate decision row {sig}")
  seen_rows.add(sig)
  scope_key=(scope,lookup_key)
  if scope_key in seen_scope_key:
   raise SystemExit(f"{where}: multiple decisions for same scope/key {scope_key}; first seen at {seen_scope_key[scope_key]}")
  seen_scope_key[scope_key]=where
  states[state]+=1; scopes[scope]+=1; files[src]+=1

  if scope=="FAMILY_QUALIFIER":
   if lookup_key not in valid_families:
    raise SystemExit(f"{where}: unknown qualifier family {lookup_key}")
  elif scope=="DISCOVERY_GROUP":
   if lookup_key not in valid_discovery_groups:
    raise SystemExit(f"{where}: unknown unqualified discovery group {lookup_key}")
   if home:
    raise SystemExit(f"{where}: DISCOVERY_GROUP must not carry HOME")
   if state=="PASS":
    raise SystemExit(f"{where}: DISCOVERY_GROUP is review-progress only; use DIRECT_CHARACTER rows for HOME PASS")
  elif scope=="VARIANT_PATTERN":
   if key not in valid_variant_patterns:
    raise SystemExit(f"{where}: unknown variant pattern {key}")
   if home:
    raise SystemExit(f"{where}: VARIANT_PATTERN must not carry HOME")
   if state=="PASS":
    raise SystemExit(f"{where}: VARIANT_PATTERN is review-progress only; use VARIANT_CHARACTER rows for HOME PASS")
  elif key not in chars:
   raise SystemExit(f"{where}: unknown Character key {key}")

  if state in {"UNRESOLVED","NEEDS_HIGHER_REASONING"}:
   review_note=(r.get("notes") or "").strip()
   if len(review_note)<20:
    raise SystemExit(f"{where}: terminal {state} decision requires notes (>=20 chars) describing the completed review/remaining uncertainty")
   if scope in {"DISCOVERY_GROUP","VARIANT_PATTERN"}:
    group_evidence_ok,group_evidence_error=evidence_gate(r)
    if not group_evidence_ok:
     raise SystemExit(f"{where}: {scope} terminal review requires grounded evidence: {group_evidence_error}")
  if state!="PASS":
   continue

  authority_type=(r.get("authority_type") or "").strip()
  officiality=(r.get("officiality_state") or "").strip()
  if not authority_type:
   raise SystemExit(f"{where}: PASS missing authority_type")
  evidence_ok,evidence_error=evidence_gate(r)
  if not evidence_ok:
   raise SystemExit(f"{where}: {evidence_error}")

  if scope in {"FAMILY_QUALIFIER","DIRECT_CHARACTER","VARIANT_CHARACTER"}:
   if not home: raise SystemExit(f"{where}: PASS relation missing HOME")
   if not root_resolves(home): raise SystemExit(f"{where}: HOME does not resolve uniquely in Copyright catalog: {home}")
  elif home:
   raise SystemExit(f"{where}: {scope} must not carry HOME")

  if scope=="FAMILY_QUALIFIER":
   lane=family_lane.get(lookup_key,"")
   if lookup_key in NON_HOME_FAMILIES or lane=="HIGHER_REASONING_NON_HOME_SEMANTICS":
    raise SystemExit(f"{where}: {lookup_key} is a non-HOME collaboration/project family; use direct/variant evidence, not FAMILY_QUALIFIER")
   if lookup_key in BROAD_FAMILIES or lane.startswith("HIGHER_REASONING_BROAD"):
    if not ALLOW_AUTONOMOUS_BROAD_FAMILY:
     raise SystemExit(f"{where}: autonomous broad-family FAMILY_QUALIFIER PASS is disabled; use DIRECT_CHARACTER roster evidence or an explicit policy normalization")
    if authority_type not in BROAD_PASS_TYPES:
     raise SystemExit(f"{where}: broad family PASS requires explicit root-policy/roster authority_type")

  if scope=="DIRECT_CHARACTER" and officiality not in {"OFFICIAL_CONFIRMED","OFFICIAL_IDENTITY"}:
   raise SystemExit(f"{where}: DIRECT_CHARACTER PASS requires OFFICIAL_CONFIRMED/OFFICIAL_IDENTITY")

  if scope=="VARIANT_CHARACTER":
   base=(r.get("base_character") or "").strip()
   if not base: raise SystemExit(f"{where}: variant PASS missing base_character")
   if base not in chars: raise SystemExit(f"{where}: variant PASS base is not a Character: {base}")
   if officiality not in {"OFFICIAL_VARIANT","OFFICIAL_CONFIRMED"}:
    raise SystemExit(f"{where}: variant PASS requires OFFICIAL_VARIANT/OFFICIAL_CONFIRMED")

  if scope=="NOT_OFFICIAL_CHARACTER":
   if not ALLOW_AUTONOMOUS_NOT_OFFICIAL:
    raise SystemExit(f"{where}: autonomous NOT_OFFICIAL_CHARACTER PASS is disabled; use BLOCK/NEEDS_HIGHER_REASONING until second-reviewed handoff")
   if officiality!="NOT_OFFICIAL_CONFIRMED":
    raise SystemExit(f"{where}: NOT_OFFICIAL PASS requires NOT_OFFICIAL_CONFIRMED")

 print({"rows":sum(files.values()),"files":dict(files),"states":dict(states),"scopes":dict(scopes),"gate":"PASS"})


if __name__=="__main__":main()
