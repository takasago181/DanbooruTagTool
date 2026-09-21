#!/usr/bin/env python3
"""Adversarial smoke tests for Issue #180 autonomous decision validation."""
from __future__ import annotations
import csv
import subprocess
import sys
from pathlib import Path

R=Path(__file__).resolve().parents[2]
D=R/"docs/issue180/autonomous/decisions"
VALIDATOR=R/"scripts/issue180/validate_authority_decisions_v2.py"
FIELDS=[
 "scope","key","home_copyright","base_character","authority_type","evidence_url",
 "evidence_claim","validation_state","officiality_state","notes",
]


def write(path: Path, rows):
 with path.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n");w.writeheader();w.writerows(rows)


def expect_fail(name, files, expected):
 paths=[]
 try:
  for suffix,rows in files:
   p=D/f"__SMOKE_{name}_{suffix}.csv";write(p,rows);paths.append(p)
  p=subprocess.run([sys.executable,str(VALIDATOR)],cwd=R,text=True,capture_output=True)
  out=(p.stdout or "")+(p.stderr or "")
  if p.returncode==0:
   raise SystemExit(f"{name}: validator unexpectedly accepted adversarial input")
  if expected not in out:
   raise SystemExit(f"{name}: wrong failure; expected {expected!r}, got {out[-800:]!r}")
  print(f"{name}: rejected as expected")
 finally:
  for p in paths:
   p.unlink(missing_ok=True)


def main():
 evidence="REPO:docs/issue180/AUTHORITY_POLICY_V1.md"
 expect_fail("project_voltage", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"project_voltage","home_copyright":"project_voltage",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"",
 }])], "non-HOME collaboration/project family")

 expect_fail("broad_lightweight", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"final_fantasy","home_copyright":"final_fantasy",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"",
 }])], "broad family PASS requires")

 expect_fail("fake_repo_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"blue_archive",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/DOES_NOT_EXIST.md","validation_state":"PASS",
  "officiality_state":"","notes":"",
 }])], "PASS requires http(s) evidence_url or evidence_claim REPO:<existing repository path>")

 row={
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"blue_archive",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"",
 }
 expect_fail("cross_shard_duplicate", [("a",[row]),("b",[row])], "multiple decisions for same scope/key")

 print("Issue #180 autonomous decision adversarial smoke: PASS")


if __name__=="__main__":main()
