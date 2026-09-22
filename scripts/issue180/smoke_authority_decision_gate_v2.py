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
 expect_fail("original_family", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"original","home_copyright":"original",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"",
  "notes":"Generic original qualifier must never be bulk HOME authority.",
 }])], "non-HOME collaboration/project family")

 expect_fail("project_voltage", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"project_voltage","home_copyright":"project_voltage",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"Repository policy evidence for smoke test.",
 }])], "non-HOME collaboration/project family")

 expect_fail("broad_lightweight", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"final_fantasy","home_copyright":"final_fantasy",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"Repository policy evidence for smoke test.",
 }])], "autonomous broad-family FAMILY_QUALIFIER PASS is disabled")

 expect_fail("fake_repo_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"blue_archive",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/DOES_NOT_EXIST.md","validation_state":"PASS",
  "officiality_state":"","notes":"Repository evidence should not exist.",
 }])], "REPO evidence path does not exist")

 row_pass={
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"blue_archive",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"Repository policy evidence for smoke test.",
 }
 row_unresolved={
  "scope":"FAMILY_QUALIFIER","key":"Blue_Archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED","officiality_state":"","notes":"conflicting review state",
 }
 expect_fail("cross_shard_duplicate", [("a",[row_pass]),("b",[row_unresolved])], "multiple decisions for same scope/key")

 expect_fail("blank_terminal_unresolved", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED","officiality_state":"","notes":"too short",
 }])], "terminal UNRESOLVED decision requires notes")

 expect_fail("discovery_group_pass", [("a",[{
  "scope":"DISCOVERY_GROUP","key":"pokemon","home_copyright":"",
  "base_character":"","authority_type":"ROSTER_GROUP_RESEARCH","evidence_url":"https://www.pokemon.co.jp/",
  "evidence_claim":"Official Pokemon source used for group review.","validation_state":"PASS",
  "officiality_state":"","notes":"Group review progress must never create HOME authority.",
 }])], "DISCOVERY_GROUP is review-progress only")

 expect_fail("discovery_group_no_evidence", [("a",[{
  "scope":"DISCOVERY_GROUP","key":"pokemon","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED",
  "officiality_state":"","notes":"Reviewed the group but deliberately omitted grounded evidence for this smoke case.",
 }])], "terminal DISCOVERY_GROUP review requires grounded evidence")

 expect_fail("variant_pattern_pass", [("a",[{
  "scope":"VARIANT_PATTERN","key":"blue_archive::blue_archive::swimsuit","home_copyright":"",
  "base_character":"","authority_type":"VARIANT_PATTERN_REVIEW","evidence_url":"https://bluearchive.jp/",
  "evidence_claim":"Official Blue Archive source used to review the swimsuit variant pattern.",
  "validation_state":"PASS","officiality_state":"",
  "notes":"Pattern progress must never grant HOME directly.",
 }])], "VARIANT_PATTERN is review-progress only")

 expect_fail("autonomous_not_official", [("a",[{
  "scope":"NOT_OFFICIAL_CHARACTER","key":"harmony_(pokemon)","home_copyright":"",
  "base_character":"","authority_type":"AUTONOMOUS_NON_OFFICIAL","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"NOT_OFFICIAL_CONFIRMED",
  "notes":"Single-pass autonomous exclusion must be rejected.",
 }])], "autonomous NOT_OFFICIAL_CHARACTER PASS is disabled")

 print("Issue #180 autonomous decision adversarial smoke: PASS")


if __name__=="__main__":main()
