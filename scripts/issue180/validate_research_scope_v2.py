#!/usr/bin/env python3
"""Fail closed if Issue #180 autonomous work escapes its research lane."""
from __future__ import annotations
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[2]
BASE="82ccb264e27cd72d140d910294efb7460a233a99"
EXACT_ALLOWED={".github/workflows/issue180_single_home_pilot.yml","AGENTS.md"}
PREFIX_ALLOWED=("docs/issue180/","scripts/issue180/")
EXACT_PREFIX_ALLOWED=("tests/issue180/",)


def git_paths(args):
 p=subprocess.run(["git",*args],cwd=R,text=True,capture_output=True)
 if p.returncode!=0:
  raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
 return {x.strip() for x in p.stdout.splitlines() if x.strip()}


def allowed(path):
 return path in EXACT_ALLOWED or path.startswith(PREFIX_ALLOWED) or path.startswith(EXACT_PREFIX_ALLOWED)


def main():
 # BASE is the saved pre-audit checkpoint. Everything after it belongs to
 # this autonomous Issue #180 lane and must remain inside the allow-list.
 try:
  subprocess.run(["git","cat-file","-e",BASE+"^{commit}"],cwd=R,check=True,capture_output=True)
 except subprocess.CalledProcessError:
  raise SystemExit(f"scope base commit unavailable: {BASE}; use full branch history/fetch-depth 0")

 committed=git_paths(["diff","--name-only",f"{BASE}..HEAD"])
 unstaged=git_paths(["diff","--name-only"])
 staged=git_paths(["diff","--cached","--name-only"])
 changed=committed|unstaged|staged
 bad=sorted(p for p in changed if not allowed(p))
 if bad:
  raise SystemExit("Issue #180 research-scope violation:\n" + "\n".join("  "+p for p in bad))
 print(f"Issue #180 research-scope gate PASS: changed={len(changed)} outside=0 base={BASE}")


if __name__=="__main__":main()
