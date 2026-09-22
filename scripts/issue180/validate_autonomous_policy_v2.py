#!/usr/bin/env python3
"""Validate the centralized Issue #180 autonomous semantic policy."""
from __future__ import annotations
import csv
import json
from collections import defaultdict
from pathlib import Path

R=Path(__file__).resolve().parents[2]
P=R/"docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CENSUS=R/"artifacts/issue180-full-preflight/CHARACTER_QUALIFIER_CENSUS.csv"

REQUIRED={
 "version","attribute_families","variant_qualifier_families","ordinal_costume_regex","broad_families","non_home_families",
 "broad_pass_types","piapro_policy_characters","root_policy_normalization",
 "root_policy_review_hint_prefixes","root_policy_review_hint_exact",
 "official_origin_classes","not_official_origin_classes","allow_autonomous_not_official_pass","allow_autonomous_broad_family_pass",
 "mandatory_unqualified_group_min_rows","mandatory_variant_pattern_min_rows","mandatory_family_discovery_min_rows",
}


def read_csv(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def unique_list(name,values):
 if len(values)!=len(set(values)):
  raise SystemExit(f"{name}: duplicate values")


def main():
 policy=json.loads(P.read_text(encoding="utf-8"))
 if set(policy)!=REQUIRED:
  raise SystemExit(f"policy schema drift missing={sorted(REQUIRED-set(policy))} extra={sorted(set(policy)-REQUIRED)}")
 if policy["version"]!=2:
  raise SystemExit("unsupported policy version")
 if not isinstance(policy["allow_autonomous_not_official_pass"], bool):
  raise SystemExit("allow_autonomous_not_official_pass: expected boolean")
 if not isinstance(policy["allow_autonomous_broad_family_pass"], bool):
  raise SystemExit("allow_autonomous_broad_family_pass: expected boolean")
 if not isinstance(policy["mandatory_unqualified_group_min_rows"], int) or policy["mandatory_unqualified_group_min_rows"] < 1:
  raise SystemExit("mandatory_unqualified_group_min_rows: expected positive integer")
 if not isinstance(policy["mandatory_variant_pattern_min_rows"], int) or policy["mandatory_variant_pattern_min_rows"] < 1:
  raise SystemExit("mandatory_variant_pattern_min_rows: expected positive integer")
 if not isinstance(policy["mandatory_family_discovery_min_rows"], int) or policy["mandatory_family_discovery_min_rows"] < 1:
  raise SystemExit("mandatory_family_discovery_min_rows: expected positive integer")
 for name in ("attribute_families","variant_qualifier_families","broad_families","non_home_families","broad_pass_types","piapro_policy_characters","official_origin_classes","not_official_origin_classes"):
  if not isinstance(policy[name],list): raise SystemExit(f"{name}: expected list")
  unique_list(name,policy[name])

 attrs=set(policy["attribute_families"]); variants=set(policy["variant_qualifier_families"]); broad=set(policy["broad_families"]); nonhome=set(policy["non_home_families"])
 official_origins=set(policy["official_origin_classes"]); nonofficial_origins=set(policy["not_official_origin_classes"])
 if official_origins & nonofficial_origins: raise SystemExit(f"official/non-official origin overlap: {sorted(official_origins & nonofficial_origins)}")
 if attrs & variants: raise SystemExit(f"attribute/variant overlap: {sorted(attrs & variants)}")
 if variants & broad: raise SystemExit(f"variant/broad overlap: {sorted(variants & broad)}")
 if variants & nonhome: raise SystemExit(f"variant/non-home overlap: {sorted(variants & nonhome)}")
 if attrs & broad: raise SystemExit(f"attribute/broad overlap: {sorted(attrs & broad)}")
 if attrs & nonhome: raise SystemExit(f"attribute/non-home overlap: {sorted(attrs & nonhome)}")

 catalog=read_csv(CAT)
 chars={r["canonical_tag"] for r in catalog if r.get("category_name")=="Character"}
 roots={r["canonical_tag"] for r in catalog if r.get("category_name")=="Copyright"}
 alias_index=defaultdict(set)
 for r in catalog:
  if r.get("category_name")!="Copyright":continue
  alias_index[r["canonical_tag"].lower()].add(r["canonical_tag"])
  for a in (r.get("aliases","") or "").split("|"):
   a=a.strip().lower()
   if a:alias_index[a].add(r["canonical_tag"])
 def resolves(root):
  return root in roots or len(alias_index.get(root.lower(),set()))==1

 census=read_csv(CENSUS)
 qualifiers={(r.get("final_qualifier") or "").strip().lower() for r in census if (r.get("final_qualifier") or "").strip()}

 for tag in policy["piapro_policy_characters"]:
  if tag not in chars: raise SystemExit(f"policy Character absent from catalog: {tag}")
 for fam in policy["non_home_families"]:
  if fam not in qualifiers: raise SystemExit(f"non-home family absent from census: {fam}")
 for fam,root in policy["root_policy_normalization"].items():
  if fam not in qualifiers: raise SystemExit(f"root policy family absent from census: {fam}")
  if not resolves(root): raise SystemExit(f"root policy HOME does not resolve: {fam} -> {root}")
 hints=policy["root_policy_review_hint_prefixes"]
 if len(hints)!=len({tuple(x) for x in hints}): raise SystemExit("duplicate root-policy hint prefixes")
 for x in hints:
  if not isinstance(x,list) or len(x)!=2 or not all(isinstance(v,str) and v for v in x):
   raise SystemExit(f"invalid root-policy hint prefix row: {x!r}")
  if not resolves(x[1]): raise SystemExit(f"hint root does not resolve: {x}")
 for fam,root in policy["root_policy_review_hint_exact"].items():
  if fam not in qualifiers: raise SystemExit(f"exact root-policy hint family absent from census: {fam}")
  if not resolves(root): raise SystemExit(f"exact hint root does not resolve: {fam} -> {root}")

 print(json.dumps({
  "version":policy["version"],
  "attribute_families":len(attrs),
  "variant_qualifier_families":len(variants),
  "broad_families":len(broad),
  "non_home_families":len(nonhome),
  "root_policy_normalizations":len(policy["root_policy_normalization"]),
  "root_policy_hint_prefixes":len(hints),
  "root_policy_hint_exact":len(policy["root_policy_review_hint_exact"]),
  "official_origin_classes":len(policy["official_origin_classes"]),
  "not_official_origin_classes":len(policy["not_official_origin_classes"]),
  "allow_autonomous_not_official_pass":policy["allow_autonomous_not_official_pass"],
  "mandatory_unqualified_group_min_rows":policy["mandatory_unqualified_group_min_rows"],
  "mandatory_variant_pattern_min_rows":policy["mandatory_variant_pattern_min_rows"],
  "mandatory_family_discovery_min_rows":policy["mandatory_family_discovery_min_rows"],
  "allow_autonomous_broad_family_pass":policy["allow_autonomous_broad_family_pass"],
  "gate":"PASS",
 },ensure_ascii=False,indent=2))


if __name__=="__main__":main()
