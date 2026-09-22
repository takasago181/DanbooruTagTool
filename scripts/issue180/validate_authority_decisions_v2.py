#!/usr/bin/env python3
"""Validate persistent autonomous decisions before compiling Issue #180 v2."""
from __future__ import annotations
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

R=Path(__file__).resolve().parents[2]
COMPAT=R/"docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
SHARDS=R/"docs/issue180/autonomous/decisions"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CENSUS=R/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"
FAMILY_WORK=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/FAMILY_WORK_QUEUE_V2.csv"
UNQUALIFIED_GROUPS=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/UNQUALIFIED_DISCOVERY_GROUPS_V2.csv"
STATIC_VARIANT_GROUPS=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/VARIANT_PATTERN_GROUPS_V2.csv"
DYNAMIC_VARIANT_GROUPS=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/DYNAMIC_VARIANT_PATTERN_GROUPS_V2.csv"
VARIANT_WORK=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/VARIANT_WORK_QUEUE_V2.csv"
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


def repo_evidence_supports(row, path, rel_posix):
 scope=(row.get("scope") or "").strip()
 key=(row.get("key") or "").strip()
 lookup_key=key.lower() if scope in {"FAMILY_QUALIFIER","DISCOVERY_GROUP"} else key
 home=(row.get("home_copyright") or "").strip()
 state=(row.get("validation_state") or "").strip()

 if rel_posix=="docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json":
  policy=json.loads(path.read_text(encoding="utf-8"))
  root_map={str(k).lower():str(v) for k,v in policy.get("root_policy_normalization",{}).items()}
  if state=="PASS":
   return (
    scope=="FAMILY_QUALIFIER"
    and bool(home)
    and root_map.get(lookup_key.lower())==home
   )

  # Policy may justify a structural/policy hold only when the policy itself
  # explicitly says this key is non-HOME or a named Character needs a policy
  # decision.  Broad-family membership alone is not proof that external
  # research was completed.
  non_home={str(x).lower() for x in policy.get("non_home_families",[])}
  piapro={str(x).lower() for x in policy.get("piapro_policy_characters",[])}
  if scope in {"FAMILY_QUALIFIER","DISCOVERY_GROUP"}:
   return lookup_key.lower() in non_home
  if scope in {"DIRECT_CHARACTER","BLOCK_CHARACTER"}:
   return key.lower() in piapro
  return False

 if rel_posix=="docs/issue180/AUTHORITY_POLICY_V1.md":
  # This is a methodology document, not row-level factual evidence.
  return False

 if not rel_posix.startswith("docs/issue180/evidence/"):
  return False
 if path.suffix.lower()!=".csv":
  return False

 rows=read(path)
 for ev in rows:
  family=(ev.get("family") or "").strip().lower()
  ev_home=(ev.get("home_copyright") or "").strip()
  canonical=(ev.get("canonical_tag") or "").strip()
  canonical_base=(ev.get("canonical_base") or "").strip()
  pattern=(ev.get("pattern_id") or "").strip()

  # Evidence is scope-bound.  A row that merely names the same HOME is not
  # sufficient to promote an entire family, and base-character evidence is
  # not sufficient to prove a variant Character.
  matched=False
  if scope in {"FAMILY_QUALIFIER","DISCOVERY_GROUP"}:
   matched=bool(family) and family==lookup_key.lower()
  elif scope=="DIRECT_CHARACTER":
   matched=(canonical==key) or (canonical_base==key)
  elif scope in {"VARIANT_CHARACTER","BLOCK_CHARACTER","NOT_OFFICIAL_CHARACTER"}:
   matched=bool(canonical) and canonical==key
  elif scope=="VARIANT_PATTERN":
   matched=bool(pattern) and pattern==key

  if not matched:
   continue

  if state=="PASS" and scope in {"FAMILY_QUALIFIER","DIRECT_CHARACTER","VARIANT_CHARACTER"}:
   if not ev_home or not home or ev_home!=home:
    continue
  return True
 return False

def evidence_gate(row):
 url=(row.get("evidence_url") or "").strip()
 claim=(row.get("evidence_claim") or "").strip()
 notes=(row.get("notes") or "").strip()
 if url.startswith(("https://","http://")):
  own_repo_markers=(
   "github.com/takasago181/DanbooruTagTool",
   "raw.githubusercontent.com/takasago181/DanbooruTagTool",
   "api.github.com/repos/takasago181/DanbooruTagTool",
  )
  if any(marker.lower() in url.lower() for marker in own_repo_markers):
   return False, "this repository cannot be reintroduced as external URL authority; use only approved REPO evidence paths"
  if len(claim) < 12 or claim.startswith("REPO:"):
   return False, "external evidence_url requires a descriptive evidence_claim"
  return True, ""
 if claim.startswith("REPO:"):
  raw=claim[len("REPO:"):].strip().split("#",1)[0].strip()
  if not raw:
   return False, "blank REPO evidence path"
  path=(R/raw).resolve()
  try:
   rel=path.relative_to(R.resolve())
  except ValueError:
   return False, "REPO evidence escapes repository"
  rel_posix=rel.as_posix()
  if rel_posix.startswith("docs/issue180/autonomous/decisions/"):
   return False, "decision shards cannot be used as their own REPO evidence"
  if rel_posix=="docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv":
   return False, "compatibility decision ledger cannot be used as REPO evidence"
  allowed_repo_evidence = (
   rel_posix.startswith("docs/issue180/evidence/")
   or rel_posix=="docs/issue180/AUTHORITY_POLICY_V1.md"
   or rel_posix=="docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"
  )
  if not allowed_repo_evidence:
   return False, "REPO evidence must come from approved evidence/policy paths; generated artifacts and review outputs are discovery/context only"
  if not path.exists():
   return False, "REPO evidence path does not exist"
  if not repo_evidence_supports(row,path,rel_posix):
   return False, "approved REPO evidence does not contain/support this decision key and HOME"
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
 valid_variant_patterns={r["pattern_id"].strip() for r in read(STATIC_VARIANT_GROUPS) if r.get("pattern_id","").strip()}
 if DYNAMIC_VARIANT_GROUPS.exists():
  valid_variant_patterns.update(r["pattern_id"].strip() for r in read(DYNAMIC_VARIANT_GROUPS) if r.get("pattern_id","").strip())
 variant_shapes={
  (((r.get("outer_ip_qualifier") or "").strip() or "-"),(r.get("variant_qualifier") or "").strip())
  for r in read(VARIANT_WORK)
  if (r.get("variant_qualifier") or "").strip()
 }

 def structurally_valid_dynamic_variant_pattern(key):
  parts=key.split("::")
  if len(parts)!=5:
   return False
  home,outer,variant_q,count_token,member_hash=parts
  if not home or not variant_q or not root_resolves(home):
   return False
  if not re.fullmatch(r"n[1-9][0-9]*",count_token):
   return False
  if not re.fullmatch(r"[0-9a-f]{12}",member_hash):
   return False
  return (outer or "-",variant_q) in variant_shapes

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
   if key not in valid_variant_patterns and not structurally_valid_dynamic_variant_pattern(key):
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
   terminal_evidence_ok,terminal_evidence_error=evidence_gate(r)
   if not terminal_evidence_ok:
    raise SystemExit(f"{where}: terminal {scope} review requires grounded evidence: {terminal_evidence_error}")
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

  if scope=="BLOCK_CHARACTER":
   block_note=(r.get("notes") or "").strip()
   if len(block_note)<20:
    raise SystemExit(f"{where}: BLOCK_CHARACTER PASS requires notes (>=20 chars) describing why HOME must remain blocked")

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
