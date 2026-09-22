#!/usr/bin/env python3
"""Check whether Issue #180 autonomous work has exhausted mandatory fast lanes."""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[2]
D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
FAMILY=D/"REMAINING_FAMILY_WORK_V2.csv"
OFFICIALITY=D/"REMAINING_OFFICIALITY_WORK_V2.csv"
UNQUALIFIED=D/"REMAINING_UNQUALIFIED_WORK_V2.csv"
UNQUALIFIED_GROUPS=D/"UNQUALIFIED_DISCOVERY_GROUPS_V2.csv"
REVIEWED_GROUPS=D/"REVIEWED_DISCOVERY_GROUPS_V2.csv"
VARIANT_GROUPS=D/"DYNAMIC_VARIANT_PATTERN_GROUPS_V2.csv"
REVIEWED_VARIANT_PATTERNS=D/"REVIEWED_VARIANT_PATTERNS_V2.csv"
DEFERRED_CHAR=D/"DEFERRED_CHARACTER_REVIEW_V2.csv"
WEAK=D/"LEGACY_WEAK_DIRECT_REVIEW_V2.csv"
MASTER=D/"CHARACTER_HOME_MASTER_V2.csv"
SUMMARY=D/"character_home_master_v2_summary.json"
OUT=D/"autonomous_completion_readiness_v2.json"
ORIGIN_META=R/"docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.meta.json"
ISSUE179_REF="refs/heads/research/issue179-character-quality-audit"
WRITE_SCOPE_GATE=R/"scripts/issue180/validate_codex_write_scope_v2.py"
POLICY_PATH=R/"docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"

MANDATORY_FAMILY_LANES={
 "FAST_REVALIDATE_NORMALIZATION",
 "FAST_ROOT_POLICY_REVIEW",
 "FAST_REVIEW_NEW_EXACT",
 "REVIEW_NORMALIZATION",
 "ALREADY_FASTPATH_SHOULD_NOT_REMAIN",
 "BROAD_LEGACY_REVIEW",
 "HIGHER_REASONING_BROAD",
}


def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def check_issue179_freshness():
 meta=json.loads(ORIGIN_META.read_text(encoding="utf-8"))
 saved_commit=str(meta.get("source_sha","")).strip()
 saved_blob=str(meta.get("source_blob_sha","")).strip()
 source_path=str(meta.get("source_path","")).strip()
 p=subprocess.run(["git","ls-remote","origin",ISSUE179_REF],cwd=R,text=True,capture_output=True)
 if p.returncode!=0:
  return False, saved_commit, "", saved_blob, "", "git ls-remote failed: "+p.stderr.strip()
 line=(p.stdout or "").strip().splitlines()
 if len(line)!=1 or not line[0].split():
  return False, saved_commit, "", saved_blob, "", "Issue179 remote ref not found or ambiguous"
 live_commit=line[0].split()[0]
 if live_commit==saved_commit:
  return True, saved_commit, live_commit, saved_blob, saved_blob, ""
 fetch=subprocess.run(["git","fetch","--quiet","--no-tags","--depth=1","origin",live_commit],cwd=R,text=True,capture_output=True)
 if fetch.returncode!=0:
  return False, saved_commit, live_commit, saved_blob, "", "Issue179 live commit fetch failed: "+fetch.stderr.strip()
 blob=subprocess.run(["git","rev-parse",f"{live_commit}:{source_path}"],cwd=R,text=True,capture_output=True)
 if blob.returncode!=0:
  return False, saved_commit, live_commit, saved_blob, "", "Issue179 origin review blob lookup failed: "+blob.stderr.strip()
 live_blob=blob.stdout.strip()
 tree=subprocess.run(
  ["git","ls-tree","-r","--name-only",live_commit,"--","docs/issue179/reviews"],
  cwd=R,text=True,capture_output=True
 )
 if tree.returncode!=0:
  return False, saved_commit, live_commit, saved_blob, live_blob, "Issue179 review tree lookup failed: "+tree.stderr.strip()
 origin_review_files=sorted(
  x.strip() for x in tree.stdout.splitlines()
  if x.strip().endswith("_ORIGIN_REVIEW.csv")
 )
 unexpected=[x for x in origin_review_files if x!=source_path]
 fresh=bool(saved_blob) and live_blob==saved_blob and not unexpected
 if live_blob!=saved_blob:
  error="Issue179 origin review file changed; refresh handoff snapshot"
 elif unexpected:
  error="Issue179 has new origin review files not present in the handoff: "+", ".join(unexpected)
 else:
  error=""
 return fresh, saved_commit, live_commit, saved_blob, live_blob, error


def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--final",action="store_true",help="fail when mandatory autonomous review work remains")
 ap.add_argument("--require-fresh-issue179",action="store_true",help="also fail if the live Issue179 origin evidence moved beyond the frozen snapshot")
 args=ap.parse_args()
 if args.require_fresh_issue179 and not args.final:
  raise SystemExit("--require-fresh-issue179 requires --final")

 fam=read(FAMILY)
 officiality=read(OFFICIALITY)
 unq=read(UNQUALIFIED)
 groups=read(UNQUALIFIED_GROUPS)
 reviewed_groups=read(REVIEWED_GROUPS)
 variant_groups=read(VARIANT_GROUPS)
 reviewed_variant_patterns=read(REVIEWED_VARIANT_PATTERNS)
 deferred_char=read(DEFERRED_CHAR)
 weak=read(WEAK)
 master=read(MASTER)
 master_by={r["canonical_tag"]:r for r in master}
 summary=json.loads(SUMMARY.read_text(encoding="utf-8"))
 policy=json.loads(POLICY_PATH.read_text(encoding="utf-8"))
 group_min=int(policy["mandatory_unqualified_group_min_rows"])
 variant_pattern_min=int(policy["mandatory_variant_pattern_min_rows"])
 family_discovery_min=int(policy["mandatory_family_discovery_min_rows"])
 lanes=Counter(r.get("work_lane","") for r in fam)
 mandatory_family={k:lanes[k] for k in sorted(MANDATORY_FAMILY_LANES) if lanes[k]}
 mandatory_family_discovery=sorted(
  (r["family"],int(r.get("character_rows","0") or 0))
  for r in fam
  if r.get("work_lane")=="DISCOVERY_RESEARCH"
  and int(r.get("character_rows","0") or 0)>=family_discovery_min
 )
 direct_roster=sum(r.get("work_state")=="DIRECT_ROSTER_REVIEW" for r in unq)
 official_origins=set(policy["official_origin_classes"])
 nonofficial_origins=set(policy["not_official_origin_classes"])
 deferred_character_tags={r.get("canonical_tag","").strip() for r in deferred_char}
 explicit_origin_unknown=[
  r["canonical_tag"] for r in master
  if (r.get("origin_class") or "").strip()
  and r.get("origin_class") not in official_origins
  and r.get("origin_class") not in nonofficial_origins
  and r.get("final_state")=="HOME_UNRESOLVED"
  and r["canonical_tag"] not in deferred_character_tags
 ]
 reviewed_group_keys={r.get("discovery_group","").strip().lower() for r in reviewed_groups}
 reviewed_variant_pattern_keys={r.get("pattern_id","").strip() for r in reviewed_variant_patterns}
 mandatory_variant_patterns=[
  r for r in variant_groups
  if r.get("work_state")=="BASE_HOME_READY_OFFICIALITY_REVIEW"
  and int(r.get("character_rows","0") or 0)>=variant_pattern_min
 ]
 missing_mandatory_variant_patterns=sorted(
  (r["pattern_id"],int(r["character_rows"]))
  for r in mandatory_variant_patterns
  if r["pattern_id"].strip() not in reviewed_variant_pattern_keys
 )
 mandatory_groups=[
  r for r in groups
  if int(r.get("character_rows","0") or 0)>=group_min
 ]
 missing_mandatory_groups=sorted(
  (r["discovery_group"],int(r["character_rows"]))
  for r in mandatory_groups
  if r["discovery_group"].strip().lower() not in reviewed_group_keys
 )
 weak_unresolved=[
  r["canonical_tag"] for r in weak
  if master_by.get(r["canonical_tag"],{}).get("final_state") not in {"HOME_CONFIRMED","NOT_OFFICIAL_CHARACTER"}
  and r["canonical_tag"] not in deferred_character_tags
 ]
 pending=int(summary.get("autonomous_pending_rows",0))
 pending_variant_pass=int(summary.get("pending_reviewed_variants_without_confirmed_base",0))
 decisions=int(summary.get("autonomous_decision_rows",0))

 blockers={
  "officiality_rows":len(officiality),
  "issue179_explicit_unknown_rows":len(explicit_origin_unknown),
  "mandatory_family_families":sum(mandatory_family.values()),
  "mandatory_family_discovery_families":len(mandatory_family_discovery),
  "direct_roster_rows":direct_roster,
  "mandatory_unqualified_groups":len(missing_mandatory_groups),
  "mandatory_variant_patterns":len(missing_mandatory_variant_patterns),
  "legacy_weak_direct_rows":len(weak_unresolved),
  "pending_variant_pass_rows":pending_variant_pass,
  "pending_decision_rows":pending,
 }
 ready=all(v==0 for v in blockers.values()) and decisions>0
 freshness={"checked":False,"fresh":None,"saved_sha":"","live_sha":"","saved_blob_sha":"","live_blob_sha":"","error":""}
 write_scope={"checked":False,"pass":None,"error":""}
 if args.final:
  scope=subprocess.run([sys.executable,str(WRITE_SCOPE_GATE)],cwd=R,text=True,capture_output=True)
  write_scope={"checked":True,"pass":scope.returncode==0,"error":(scope.stderr or scope.stdout or "").strip()}
  ready=ready and scope.returncode==0
  fresh,saved_commit,live_commit,saved_blob,live_blob,error=check_issue179_freshness()
  freshness={
   "checked":True,"fresh":fresh,
   "saved_sha":saved_commit,"live_sha":live_commit,
   "saved_blob_sha":saved_blob,"live_blob_sha":live_blob,
   "error":error,
  }
  if args.require_fresh_issue179:
   ready=ready and fresh

 result={
  "ready_for_final_autonomous_report":ready,
  "issue179_handoff_freshness":freshness,
  "issue179_refresh_required_before_freeze": bool(freshness["checked"] and not freshness["fresh"]),
  "codex_write_scope":write_scope,
  "autonomous_decision_rows":decisions,
  "blockers":blockers,
  "mandatory_family_lane_counts":mandatory_family,
  "mandatory_family_discovery_min_rows":family_discovery_min,
  "mandatory_family_discovery_missing":mandatory_family_discovery,
  "issue179_explicit_unknown_unreviewed":sorted(explicit_origin_unknown),
  "legacy_weak_direct_unresolved":weak_unresolved,
  "mandatory_unqualified_group_min_rows":group_min,
  "mandatory_unqualified_groups_total":len(mandatory_groups),
  "mandatory_unqualified_groups_missing":missing_mandatory_groups,
  "reviewed_discovery_groups":len(reviewed_group_keys),
  "mandatory_variant_pattern_min_rows":variant_pattern_min,
  "mandatory_variant_patterns_total":len(mandatory_variant_patterns),
  "mandatory_variant_patterns_missing":missing_mandatory_variant_patterns,
  "reviewed_variant_patterns":len(reviewed_variant_pattern_keys),
  "residual_family_families":len(fam),
  "residual_variant_rows":summary.get("remaining_work",{}).get("variant_rows",0),
  "residual_unqualified_rows":len(unq),
  "deferred_character_rows":summary.get("remaining_work",{}).get("deferred_character_rows",0),
  "deferred_family_rows":summary.get("remaining_work",{}).get("deferred_family_rows",0),
  "note":"Residual long-tail discovery/variant work may remain unresolved, but mandatory fast/officiality/high-yield family-discovery/direct-roster/high-yield discovery-group/high-yield ready-variant-pattern lanes must be resolved or explicitly deferred.",
 }
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if args.final and not ready:
  if not write_scope["pass"]:
   raise SystemExit("final readiness failed: Codex write-scope gate failed: "+write_scope["error"])
  if args.require_fresh_issue179 and not freshness["fresh"]:
   raise SystemExit("final readiness failed: Issue179 handoff freshness check failed: "+freshness["error"])
  if decisions==0:
   raise SystemExit("final readiness failed: no autonomous decisions were recorded")
  raise SystemExit("final readiness failed: mandatory active work remains")


if __name__=="__main__":main()
