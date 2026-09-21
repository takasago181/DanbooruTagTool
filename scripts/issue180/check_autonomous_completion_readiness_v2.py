#!/usr/bin/env python3
"""Check whether Issue #180 autonomous work has exhausted mandatory fast lanes."""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[2]
D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
FAMILY=D/"REMAINING_FAMILY_WORK_V2.csv"
OFFICIALITY=D/"REMAINING_OFFICIALITY_WORK_V2.csv"
UNQUALIFIED=D/"REMAINING_UNQUALIFIED_WORK_V2.csv"
SUMMARY=D/"character_home_master_v2_summary.json"
OUT=D/"autonomous_completion_readiness_v2.json"
ORIGIN_META=R/"docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.meta.json"
ISSUE179_REF="refs/heads/research/issue179-character-quality-audit"

MANDATORY_FAMILY_LANES={
 "FAST_REVALIDATE_NORMALIZATION",
 "FAST_ROOT_POLICY_REVIEW",
 "FAST_REVIEW_NEW_EXACT",
 "REVIEW_NORMALIZATION",
 "ALREADY_FASTPATH_SHOULD_NOT_REMAIN",
 "BROAD_LEGACY_REVIEW",
}


def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def check_issue179_freshness():
 meta=json.loads(ORIGIN_META.read_text(encoding="utf-8"))
 saved=str(meta.get("source_sha","")).strip()
 p=subprocess.run(["git","ls-remote","origin",ISSUE179_REF],cwd=R,text=True,capture_output=True)
 if p.returncode!=0:
  return False, saved, "", "git ls-remote failed: "+p.stderr.strip()
 line=(p.stdout or "").strip().splitlines()
 if len(line)!=1 or not line[0].split():
  return False, saved, "", "Issue179 remote ref not found or ambiguous"
 live=line[0].split()[0]
 return live==saved, saved, live, "" if live==saved else "Issue179 origin handoff snapshot is stale"


def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--final",action="store_true",help="fail when mandatory autonomous review work remains")
 args=ap.parse_args()

 fam=read(FAMILY)
 officiality=read(OFFICIALITY)
 unq=read(UNQUALIFIED)
 summary=json.loads(SUMMARY.read_text(encoding="utf-8"))
 lanes=Counter(r.get("work_lane","") for r in fam)
 mandatory_family={k:lanes[k] for k in sorted(MANDATORY_FAMILY_LANES) if lanes[k]}
 direct_roster=sum(r.get("work_state")=="DIRECT_ROSTER_REVIEW" for r in unq)
 pending=int(summary.get("autonomous_pending_rows",0))
 decisions=int(summary.get("autonomous_decision_rows",0))

 blockers={
  "officiality_rows":len(officiality),
  "mandatory_family_families":sum(mandatory_family.values()),
  "direct_roster_rows":direct_roster,
  "pending_decision_rows":pending,
 }
 ready=all(v==0 for v in blockers.values()) and decisions>0
 freshness={"checked":False,"fresh":None,"saved_sha":"","live_sha":"","error":""}
 if args.final:
  fresh,saved,live,error=check_issue179_freshness()
  freshness={"checked":True,"fresh":fresh,"saved_sha":saved,"live_sha":live,"error":error}
  ready=ready and fresh

 result={
  "ready_for_final_autonomous_report":ready,
  "issue179_handoff_freshness":freshness,
  "autonomous_decision_rows":decisions,
  "blockers":blockers,
  "mandatory_family_lane_counts":mandatory_family,
  "residual_family_families":len(fam),
  "residual_variant_rows":summary.get("remaining_work",{}).get("variant_rows",0),
  "residual_unqualified_rows":len(unq),
  "deferred_character_rows":summary.get("remaining_work",{}).get("deferred_character_rows",0),
  "deferred_family_rows":summary.get("remaining_work",{}).get("deferred_family_rows",0),
  "note":"Residual discovery/variant work may remain unresolved, but mandatory fast/officiality/direct-roster lanes must be resolved or explicitly deferred.",
 }
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if args.final and not ready:
  if not freshness["fresh"]:
   raise SystemExit("final readiness failed: Issue179 handoff freshness check failed: "+freshness["error"])
  if decisions==0:
   raise SystemExit("final readiness failed: no autonomous decisions were recorded")
  raise SystemExit("final readiness failed: mandatory active work remains")


if __name__=="__main__":main()
