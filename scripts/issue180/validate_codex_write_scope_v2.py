#!/usr/bin/env python3
"""Final write-scope lock for the Issue #180 Codex autonomous execution.

The marker is created only after the harness is frozen.  From that base onward,
Codex may change decision shard CSVs only.  This prevents an autonomous run
from "fixing" failures by weakening compiler/validator/policy code.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[2]
MARKER=R/"docs/issue180/autonomous/CODEX_EXECUTION_BASE_V2.json"
MARKER_REL=str(MARKER.relative_to(R))
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
 if path==MARKER_REL:
  return True
 if path in PROTECTED_DECISION_FILES:
  return False
 return path.startswith(DECISION_PREFIX) and path.endswith(".csv")


def main():
 if not MARKER.exists():
  raise SystemExit("Codex execution base marker is missing; freeze the harness before final autonomous execution")
 meta=json.loads(MARKER.read_text(encoding="utf-8"))
 base=str(meta.get("base_sha","")).strip()
 if not re.fullmatch(r"[0-9a-f]{40}",base):
  raise SystemExit("Codex execution base_sha is malformed")
 git(["cat-file","-e",base+"^{commit}"])

 marker_commits=int(git(["rev-list","--count",f"{base}..HEAD","--",MARKER_REL]) or "0")
 if marker_commits!=1:
  raise SystemExit(f"Codex execution marker must be created exactly once after base; commits={marker_commits}")

 changed={x for x in git(["diff","--name-only",f"{base}..HEAD"]).splitlines() if x}
 bad=sorted(x for x in changed if not allowed(x))
 if bad:
  raise SystemExit(
   "Codex autonomous write-scope violation; harness/policy files changed after freeze:\n"
   +"\n".join("  "+x for x in bad)
  )

 # The marker commit itself is expected.  All other tracked changes must be
 # decision shards.  Require at least one real decision shard before a final
 # autonomous report can pass.
 decision_changes=sorted(x for x in changed if x.startswith(DECISION_PREFIX) and x.endswith(".csv") and x not in PROTECTED_DECISION_FILES)
 if not decision_changes:
  raise SystemExit("Codex autonomous write-scope has no decision-shard changes after freeze")

 print(json.dumps({
  "base_sha":base,
  "marker_commits":marker_commits,
  "changed_paths":len(changed),
  "decision_shard_changes":decision_changes,
  "outside_allowed_scope":0,
  "gate":"PASS",
 },ensure_ascii=False,indent=2))


if __name__=="__main__":main()
