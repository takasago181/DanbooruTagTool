#!/usr/bin/env python3
"""Adversarial smoke tests for Issue #180 autonomous decision validation."""
from __future__ import annotations
import csv
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

R=Path(__file__).resolve().parents[2]
D=R/"docs/issue180/autonomous/decisions"
VALIDATOR=R/"scripts/issue180/validate_authority_decisions_v2.py"
FIELDS=[
 "scope","key","home_copyright","base_character","authority_type","evidence_url",
 "evidence_claim","validation_state","officiality_state","notes",
]


@contextmanager
def isolated_persistent_decisions():
 """Hide real autonomous shards while synthetic validator fixtures run."""
 persistent=[
  p for p in sorted(D.glob("*.csv"))
  if p.name!="AUTHORITY_DECISIONS_BASE_V2.csv" and not p.name.startswith("__SMOKE_")
 ]
 with tempfile.TemporaryDirectory(prefix="issue180-decision-smoke-") as td:
  stash=Path(td)
  for p in persistent:
   shutil.move(str(p),str(stash/p.name))
  try:
   yield
  finally:
   for p in D.glob("__SMOKE_*.csv"):
    p.unlink(missing_ok=True)
   for p in persistent:
    src=stash/p.name
    if src.exists():
     shutil.move(str(src),str(p))


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


def expect_pass(name, rows):
 path=D/f"__SMOKE_{name}_pass.csv"
 try:
  write(path,rows)
  p=subprocess.run([sys.executable,str(VALIDATOR)],cwd=R,text=True,capture_output=True)
  out=(p.stdout or "")+(p.stderr or "")
  if p.returncode!=0:
   raise SystemExit(f"{name}: validator unexpectedly rejected valid input: {out[-800:]!r}")
  print(f"{name}: accepted as expected")
 finally:
  path.unlink(missing_ok=True)


def main():
 evidence="REPO:docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"
 policy_text_evidence="REPO:docs/issue180/AUTHORITY_POLICY_V1.md"
 expect_fail("original_family", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"original","home_copyright":"original",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"https://example.com/original-family-semantic-smoke",
  "evidence_claim":"External smoke evidence intentionally reaches the generic-family semantic prohibition.",
  "validation_state":"PASS","officiality_state":"",
  "notes":"Generic original qualifier must never be bulk HOME authority.",
 }])], "non-HOME collaboration/project family")

 expect_fail("project_voltage", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"project_voltage","home_copyright":"project_voltage",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"https://example.com/project-voltage-semantic-smoke",
  "evidence_claim":"External smoke evidence intentionally reaches the non-HOME family semantic gate.",
  "validation_state":"PASS","officiality_state":"","notes":"Repository policy evidence for smoke test.",
 }])], "non-HOME collaboration/project family")

 expect_fail("broad_lightweight", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"final_fantasy","home_copyright":"final_fantasy",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"https://example.com/final-fantasy-broad-smoke",
  "evidence_claim":"External smoke evidence intentionally reaches the broad-family semantic gate.",
  "validation_state":"PASS","officiality_state":"","notes":"Repository policy evidence for smoke test.",
 }])], "autonomous broad-family FAMILY_QUALIFIER PASS is disabled")

 expect_fail("self_referential_repo_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"blue_archive",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/autonomous/decisions/__SMOKE_self_referential_repo_evidence_a.csv",
  "validation_state":"PASS","officiality_state":"",
  "notes":"A decision shard must not be allowed to prove its own authority.",
 }])], "decision shards cannot be used as their own REPO evidence")

 expect_fail("self_repo_external_url", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"https://github.com/takasago181/DanbooruTagTool/blob/main/artifacts/example.csv",
  "evidence_claim":"This intentionally uses the same repository as fake external authority for the smoke test.",
  "validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"Self-repository URLs must not bypass the approved internal evidence allow-list.",
 }])], "this repository cannot be reintroduced as external URL authority")

 expect_fail("generated_artifact_as_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"REPO:artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/FAMILY_WORK_QUEUE_V2.csv",
  "validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"Generated work queues are discovery/context only and must never prove their own terminal review.",
 }])], "REPO evidence must come from approved evidence/policy paths")

 expect_fail("review_output_as_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/autonomous/FINAL_ADVERSARIAL_AUDIT_V2.md",
  "validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"Autonomous review documentation is not factual authority for a family HOME decision.",
 }])], "REPO evidence must come from approved evidence/policy paths")

 expect_fail("fake_repo_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"blue_archive",
  "base_character":"","authority_type":"QUALIFIER_COPYRIGHT","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/DOES_NOT_EXIST.md","validation_state":"PASS",
  "officiality_state":"","notes":"Repository evidence should not exist.",
 }])], "REPO evidence must come from approved evidence/policy paths")

 row_pass={
  "scope":"FAMILY_QUALIFIER","key":"blue_archive_the_animation","home_copyright":"blue_archive",
  "base_character":"","authority_type":"ROOT_POLICY_REVIEWED","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"","notes":"Explicit root-policy normalization used for duplicate-key smoke test.",
 }
 row_unresolved={
  "scope":"FAMILY_QUALIFIER","key":"Blue_Archive_The_Animation","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED","officiality_state":"","notes":"conflicting review state",
 }
 expect_fail("cross_shard_duplicate", [("a",[row_pass]),("b",[row_unresolved])], "multiple decisions for same scope/key")

 expect_fail("blank_terminal_unresolved", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED","officiality_state":"","notes":"too short",
 }])], "terminal UNRESOLVED decision requires notes")

 expect_fail("family_terminal_no_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"Completed family review but intentionally omitted evidence for this smoke case.",
 }])], "terminal FAMILY_QUALIFIER review requires grounded evidence")

 expect_fail("direct_terminal_no_evidence", [("a",[{
  "scope":"DIRECT_CHARACTER","key":"harmony_(pokemon)","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"","validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"Completed direct review but intentionally omitted evidence for this smoke case.",
 }])], "terminal DIRECT_CHARACTER review requires grounded evidence")

 expect_fail("methodology_doc_not_row_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":policy_text_evidence,"validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"A methodology document must not count as evidence that Blue Archive family research was completed.",
 }])], "REPO evidence must come from approved evidence/policy paths")

 expect_pass("family_terminal_with_explicit_family_evidence", [{
  "scope":"FAMILY_QUALIFIER","key":"disney","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/evidence/exact_root_semantic_authority_batch02.csv",
  "validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"The approved evidence CSV contains an explicit Disney family row and records the umbrella as unresolved.",
 }])

 expect_fail("home_only_source_registry_not_family_evidence", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"arknights","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/evidence/official_roster_sources_batch01.csv",
  "validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"A source registry row with only home_copyright must not be promoted to family-level evidence.",
 }])], "approved REPO evidence does not contain/support this decision key and HOME")

 expect_fail("unrelated_policy_mapping", [("a",[{
  "scope":"FAMILY_QUALIFIER","key":"pokemon_go","home_copyright":"fate_(series)",
  "base_character":"","authority_type":"ROOT_POLICY_REVIEWED","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"",
  "notes":"Both tokens exist in policy data, but there is no Pokemon GO to Fate mapping.",
 }])], "approved REPO evidence does not contain/support this decision key and HOME")

 expect_pass("explicit_policy_mapping", [{
  "scope":"FAMILY_QUALIFIER","key":"blue_archive_the_animation","home_copyright":"blue_archive",
  "base_character":"","authority_type":"ROOT_POLICY_REVIEWED","evidence_url":"",
  "evidence_claim":evidence,"validation_state":"PASS","officiality_state":"",
  "notes":"The autonomous policy explicitly maps the anime qualifier to the canonical Blue Archive HOME.",
 }])

 expect_fail("unrelated_internal_csv", [("a",[{
  "scope":"DIRECT_CHARACTER","key":"harmony_(pokemon)","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/evidence/direct_official_character_roster_batch05.csv",
  "validation_state":"UNRESOLVED","officiality_state":"",
  "notes":"The evidence CSV is valid but contains different Character rows, so it must not support Harmony.",
 }])], "approved REPO evidence does not contain/support this decision key and HOME")

 expect_pass("direct_internal_csv_exact_match", [{
  "scope":"DIRECT_CHARACTER","key":"pikachu","home_copyright":"pokemon",
  "base_character":"","authority_type":"POKEMON_OFFICIAL_POKEDEX_EXACT","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/evidence/direct_official_character_roster_batch05.csv",
  "validation_state":"PASS","officiality_state":"OFFICIAL_CONFIRMED",
  "notes":"Exact Pikachu row and Pokemon HOME are both present in the approved official roster evidence CSV.",
 }])

 expect_fail("base_roster_not_variant_evidence", [("a",[{
  "scope":"VARIANT_CHARACTER","key":"callie_(splatoon)","home_copyright":"splatoon_(series)",
  "base_character":"callie_(splatoon)","authority_type":"VARIANT_TEST","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/evidence/splatoon_official_roster_v1.csv",
  "validation_state":"PASS","officiality_state":"OFFICIAL_VARIANT",
  "notes":"A base-character roster row must not prove variant officiality merely through canonical_base.",
 }])], "approved REPO evidence does not contain/support this decision key and HOME")

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

 expect_fail("block_pass_disallowed", [("a",[{
  "scope":"BLOCK_CHARACTER","key":"harmony_(pokemon)","home_copyright":"",
  "base_character":"","authority_type":"OFFICIALITY_BLOCK","evidence_url":"https://example.com/harmony-block-smoke",
  "evidence_claim":"External smoke evidence intentionally reaches the BLOCK_CHARACTER terminal-only gate.",
  "validation_state":"PASS","officiality_state":"",
  "notes":"Even a well-documented block must use a terminal review state rather than PASS.",
 }])], "BLOCK_CHARACTER is terminal review only")

 expect_pass("block_terminal_review", [{
  "scope":"BLOCK_CHARACTER","key":"harmony_(pokemon)","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"https://example.com/harmony-block-review-smoke",
  "evidence_claim":"External smoke evidence represents a reviewed Character-specific HOME hold.",
  "validation_state":"NEEDS_HIGHER_REASONING","officiality_state":"",
  "notes":"Character-specific evidence remains ambiguous, so all HOME inheritance paths must stay blocked pending higher review.",
 }])

 expect_fail("relation_pass_plus_terminal_block", [("a",[{
  "scope":"DIRECT_CHARACTER","key":"pikachu","home_copyright":"pokemon",
  "base_character":"","authority_type":"POKEMON_OFFICIAL_POKEDEX_EXACT","evidence_url":"",
  "evidence_claim":"REPO:docs/issue180/evidence/direct_official_character_roster_batch05.csv",
  "validation_state":"PASS","officiality_state":"OFFICIAL_CONFIRMED",
  "notes":"Exact official Character evidence intentionally conflicts with a terminal block in this smoke.",
 }]),("b",[{
  "scope":"BLOCK_CHARACTER","key":"pikachu","home_copyright":"",
  "base_character":"","authority_type":"","evidence_url":"https://example.com/pikachu-terminal-block-smoke",
  "evidence_claim":"Synthetic external smoke evidence intentionally creates a contradictory all-path Character hold.",
  "validation_state":"NEEDS_HIGHER_REASONING","officiality_state":"",
  "notes":"This terminal block intentionally contradicts the simultaneous direct PASS and must be rejected.",
 }])], "contradictory Character decisions for pikachu")

 expect_fail("autonomous_not_official", [("a",[{
  "scope":"NOT_OFFICIAL_CHARACTER","key":"harmony_(pokemon)","home_copyright":"",
  "base_character":"","authority_type":"AUTONOMOUS_NON_OFFICIAL","evidence_url":"https://example.com/harmony-officiality-smoke",
  "evidence_claim":"External smoke evidence intentionally reaches the NOT_OFFICIAL policy gate.",
  "validation_state":"PASS","officiality_state":"NOT_OFFICIAL_CONFIRMED",
  "notes":"Single-pass autonomous exclusion must be rejected.",
 }])], "autonomous NOT_OFFICIAL_CHARACTER PASS is disabled")

 print("Issue #180 autonomous decision adversarial smoke: PASS")


if __name__=="__main__":
 with isolated_persistent_decisions():
  main()
