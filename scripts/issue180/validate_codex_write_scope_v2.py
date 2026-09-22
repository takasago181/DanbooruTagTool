#!/usr/bin/env python3
"""Final write-scope lock for the Issue #180 Codex autonomous execution.

The marker is created only after the harness is frozen. From that base onward,
Codex may change decision shard CSVs only. Deliberate harness repair is performed
outside the autonomous run and must be followed by a new freeze marker.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[2]
MARKER=R/"docs/issue180/autonomous/CODEX_EXECUTION_BASE_V2.json"
MARKER_REL=MARKER.relative_to(R).as_posix()
DECISION_PREFIX="docs/issue180/autonomous/decisions/"
PROTECTED_DECISION_FILES={
 "docs/issue180/autonomous/decisions/AUTHORITY_DECISIONS_BASE_V2.csv",
}


def git(args):
 p=subprocess.run(["git",*args],cwd=R,text=True,capture_output=True)
 if p.returncode!=0:
  raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
 return p.stdout.strip()


def allowed(path: str) -> bool:
 path=path.replace("\\","/")
 if path==MARKER_REL:
  return True
 if path in PROTECTED_DECISION_FILES:
  return False
 return path.startswith(DECISION_PREFIX) and path.endswith(".csv")


def decision_files_at(ref: str) -> list[str]:
 rows=[
  x.replace("\\","/") for x in git(["ls-tree","-r","--name-only",ref,"--",DECISION_PREFIX]).splitlines()
  if x
 ]
 return sorted(
  x for x in rows
  if x.endswith(".csv")
  and x not in PROTECTED_DECISION_FILES
  and not Path(x).name.startswith("__SMOKE_")
 )


def current_decision_files() -> list[str]:
 rows=[
  x.replace("\\","/") for x in git(["ls-files","--",DECISION_PREFIX]).splitlines()
  if x
 ]
 return sorted(
  x for x in rows
  if x.endswith(".csv")
  and x not in PROTECTED_DECISION_FILES
  and not Path(x).name.startswith("__SMOKE_")
 )


def main():
 if not MARKER.exists():
  raise SystemExit("Codex execution base marker is missing; freeze the harness before final autonomous execution")
 meta=json.loads(MARKER.read_text(encoding="utf-8"))
 if meta.get("status")!="HARNESS_FROZEN_FOR_CODEX_AUTONOMOUS_DECISIONS":
  raise SystemExit(f"Codex execution marker is not frozen: status={meta.get('status')!r}")

 base=str(meta.get("base_sha","")).strip()
 if not re.fullmatch(r"[0-9a-f]{40}",base):
  raise SystemExit("Codex execution base_sha is malformed")
 git(["cat-file","-e",base+"^{commit}"])

 marker_commits=int(git(["rev-list","--count",f"{base}..HEAD","--",MARKER_REL]) or "0")
 if marker_commits!=1:
  raise SystemExit(f"Codex execution marker must be created exactly once after base; commits={marker_commits}")

 tracked_dirty=git(["status","--porcelain","--untracked-files=no"])
 if tracked_dirty:
  raise SystemExit("Codex final state has uncommitted tracked changes; commit decision shards and restore harness changes before final report:\n"+tracked_dirty)
 untracked_decisions=git(["ls-files","--others","--exclude-standard","--",DECISION_PREFIX])
 if untracked_decisions:
  raise SystemExit("Codex final state has untracked decision files; commit them before final report:\n"+untracked_decisions)

 changed={x.replace("\\","/") for x in git(["diff","--name-only",f"{base}..HEAD"]).splitlines() if x}
 bad=sorted(x for x in changed if not allowed(x))
 if bad:
  raise SystemExit(
   "Codex autonomous write-scope violation; harness/policy files changed after freeze:\n"
   +"\n".join("  "+x for x in bad)
  )

 decision_changes=sorted(
  x for x in changed
  if x.startswith(DECISION_PREFIX) and x.endswith(".csv") and x not in PROTECTED_DECISION_FILES
 )

 snapshot=str(meta.get("decision_snapshot_sha","")).strip()
 snapshot_files=[]
 if snapshot:
  if not re.fullmatch(r"[0-9a-f]{40}",snapshot):
   raise SystemExit("decision_snapshot_sha is malformed")
  git(["cat-file","-e",snapshot+"^{commit}"])
  merge_base=git(["merge-base",snapshot,base])
  if merge_base!=snapshot:
   raise SystemExit("decision_snapshot_sha must be an ancestor of the frozen harness base")
  snapshot_files=decision_files_at(snapshot)
  declared=sorted(str(x).replace("\\","/") for x in meta.get("decision_snapshot_files",[]))
  if declared and declared!=snapshot_files:
   raise SystemExit(f"decision snapshot file list mismatch declared={declared} actual={snapshot_files}")

 current_files=current_decision_files()
 if not current_files:
  raise SystemExit("Codex autonomous write-scope has no persistent decision shards")
 if not decision_changes and not snapshot_files:
  raise SystemExit("Codex autonomous write-scope has neither post-freeze decision changes nor a validated pre-refreeze decision snapshot")

 print(json.dumps({
  "base_sha":base,
  "decision_snapshot_sha":snapshot,
  "marker_commits":marker_commits,
  "changed_paths":len(changed),
  "decision_shard_changes":decision_changes,
  "decision_snapshot_files":snapshot_files,
  "current_decision_files":current_files,
  "outside_allowed_scope":0,
  "gate":"PASS",
 },ensure_ascii=False,indent=2))


if __name__=="__main__":main()
