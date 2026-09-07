"""Build reviewed v2 generation metadata from PROMOTION_PLAN v1.

This does not edit the immutable Special2788 dictionary.  Audit-only rows keep
identity/status/evidence but do not receive production semantic fields.
"""
from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from danbooru_tag_tool.generation_profile import (
    FAMILY_RULE_COLUMNS, OBSERVATION_COLUMNS, PROFILE_COLUMNS,
)


SOURCE = ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv"
PLAN = ROOT / "data/generation/audit/PROMOTION_PLAN_v1.csv"
COUNTS = ROOT / "data/generation/audit/PROMOTION_COUNTS_v1.json"
FAMILY_AUDIT = ROOT / "data/generation/audit/FAMILY_RULE_AUDIT_25_v1.csv"
CORRECTIONS = ROOT / "data/generation/audit/HIGH_CONFIDENCE_CORRECTIONS_v1.csv"
STRUCTURAL_OVERRIDES = ROOT / "data/generation/audit/EXPLICIT_STRUCTURAL_OVERRIDES_240_v1.csv"
STATIC_REVIEW = ROOT / "data/generation/audit/APPROVED_STATIC_1352_REVIEW_v1.csv"
OUT = ROOT / "data/generation"

EXPECTED_COUNTS = {
    "APPROVED_STATIC": 1352,
    "APPROVED_IDENTITY_ONLY": 778,
    "APPROVED_SEMANTIC_ROLE": 336,
    "APPROVED_CORRECTION_METADATA": 13,
    "PROVISIONAL": 294,
    "PROVISIONAL_CORRECTION": 1,
    "REVIEW_REQUIRED": 14,
}

STRUCTURAL_FIELD_MAP = {
    "ActorOverride": "ActorRequirementOverride",
    "BodypartOverride": "BodypartRequirementOverride",
    "ImplementOverride": "ImplementRequirementOverride",
    "PoseOverride": "PoseRequirementOverride",
    "CameraOverride": "CameraRequirementOverride",
    "SpatialOverride": "SpatialAssignmentOverride",
    "CompositionRoleOverride": "CompositionRoleOverride",
    "SpecialFlags": "SpecialFlags",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def static_row(plan):
    row = dict.fromkeys(PROFILE_COLUMNS, "")
    status = plan["PromotionStatus"]
    row.update(SpecialID=plan["SpecialID"], Tag=plan["Tag"], PromotionStatus=status,
               EvidenceClass=plan["EvidenceLevel"], EvidenceRefs=plan["EvidenceURLs"])
    if status == "APPROVED_STATIC":
        row.update(
            MeaningStatus=plan["DeepMeaningStatus"],
            MeaningConfidence=plan["DeepMeaningConfidence"],
            SourceGlossQuality=plan["SourceGlossQuality"],
            GenerationFamily=plan["GenerationFamily"],
            GenerationRole=plan["GenerationRole"],
            PromptUseMode=plan["PromptUseMode"],
            FamilyRuleId=f"GFR_{plan['GenerationFamily']}",
            RecommendedHandling=plan["RecommendedHandling"],
        )
    elif status == "APPROVED_IDENTITY_ONLY":
        row.update(
            MeaningStatus=plan["DeepMeaningStatus"],
            MeaningConfidence=plan["DeepMeaningConfidence"],
            PromptUseMode="ALIAS_PRESERVE",
            SpecialFlags="PRESERVE_PROMPT_IDENTITY",
            RecommendedHandling=plan["RecommendedHandling"],
        )
    elif status == "APPROVED_SEMANTIC_ROLE":
        row.update(
            MeaningStatus="SEMANTIC_SUPPORT",
            MeaningConfidence=plan["DeepMeaningConfidence"],
            GenerationRole="semantic_support",
            PromptUseMode="SUPPORT",
            SpecialFlags="SEMANTIC_NOT_DIRECT_CANONICAL",
            RecommendedHandling=plan["RecommendedHandling"],
        )
    elif status == "APPROVED_CORRECTION_METADATA":
        row.update(
            MeaningStatus=plan["DeepMeaningStatus"],
            MeaningConfidence=plan["DeepMeaningConfidence"],
            SourceGlossQuality=plan["SourceGlossQuality"],
            GenerationRole=plan["GenerationRole"],
            SpecialFlags="CORRECTED_METADATA_OVERLAY",
            RecommendedHandling=plan["RecommendedHandling"],
        )
    else:
        row["SpecialFlags"] = "AUDIT_ONLY_DO_NOT_AUTO_EXPAND"
    return row


def family_rows(audit_rows):
    if len(audit_rows) != 25 or len({row["FamilyRuleId"] for row in audit_rows}) != 25:
        raise ValueError("Expected 25 unique audited family rules")
    rows = []
    for audit in audit_rows:
        proposed_physical = (
            audit["ProposedNeedsActor"], audit["ProposedNeedsBodypart"],
            audit["ProposedNeedsImplement"], audit["ProposedNeedsPose"],
            audit["ProposedNeedsCamera"], audit["ProposedNeedsSpatialAssignment"],
            audit["ProposedCompositionRole"],
        )
        if any(proposed_physical):
            raise ValueError("v2.1 family physical defaults must be blank")
        rows.append(dict(
            FamilyRuleId=audit["FamilyRuleId"],
            GenerationFamily=audit["GenerationFamily"],
            DefaultPromptUseMode=audit["ProposedDefaultPromptUseMode"],
            DefaultNeedsActor="",
            DefaultNeedsBodypart="",
            DefaultNeedsImplement="",
            DefaultNeedsPose="",
            DefaultNeedsCamera="",
            DefaultNeedsSpatialAssignment="",
            DefaultCompositionRole="",
            Notes=audit["Rationale"],
        ))
    return rows


def apply_family_audit(static, source_rows, correction_rows, override_rows, review_rows):
    source_by_id = {row["ID"]: row for row in source_rows}
    static_by_id = {row["SpecialID"]: row for row in static}

    def validate_identity(row, label):
        special_id = row["SpecialID"]
        if special_id not in source_by_id or special_id not in static_by_id:
            raise ValueError(f"{label} references unknown SpecialID: {special_id}")
        if row["Tag"] != source_by_id[special_id]["Tag"] or row["Tag"] != static_by_id[special_id]["Tag"]:
            raise ValueError(f"{label} ID/Tag mismatch: {special_id}")
        if static_by_id[special_id]["PromotionStatus"] != "APPROVED_STATIC":
            raise ValueError(f"{label} references non-APPROVED_STATIC row: {special_id}")

    if len(correction_rows) != 177 or len({row["SpecialID"] for row in correction_rows}) != 177:
        raise ValueError("Expected 177 unique family corrections")
    changed = Counter()
    for correction in correction_rows:
        validate_identity(correction, "Correction")
        profile = static_by_id[correction["SpecialID"]]
        current = {
            "CurrentFamily": profile["GenerationFamily"],
            "CurrentRole": profile["GenerationRole"],
            "CurrentPromptUseMode": profile["PromptUseMode"],
        }
        if any(correction[name] != value for name, value in current.items()):
            raise ValueError(f"Correction current-value mismatch: {correction['SpecialID']}")
        for source_name, target_name, counter_name in (
            ("ProposedFamily", "GenerationFamily", "family"),
            ("ProposedRole", "GenerationRole", "role"),
            ("ProposedPromptUseMode", "PromptUseMode", "mode"),
        ):
            if profile[target_name] != correction[source_name]:
                changed[counter_name] += 1
            profile[target_name] = correction[source_name]
        profile["FamilyRuleId"] = f"GFR_{profile['GenerationFamily']}"
    if changed != Counter(family=153, role=162, mode=116):
        raise ValueError(f"Unexpected correction change counts: {dict(changed)}")

    if len(override_rows) != 240 or len({row["SpecialID"] for row in override_rows}) != 240:
        raise ValueError("Expected 240 unique explicit structural overrides")
    for override in override_rows:
        validate_identity(override, "Structural override")
        profile = static_by_id[override["SpecialID"]]
        proposed = (override["ProposedFamily"], override["ProposedRole"],
                    override["ProposedPromptUseMode"])
        actual = (profile["GenerationFamily"], profile["GenerationRole"],
                  profile["PromptUseMode"])
        if proposed != actual or override["HasExplicitStructuralOverride"] != "True":
            raise ValueError(f"Structural override audit mismatch: {override['SpecialID']}")
        for source_name, target_name in STRUCTURAL_FIELD_MAP.items():
            profile[target_name] = override[source_name]

    if len(review_rows) != 1352 or len({row["SpecialID"] for row in review_rows}) != 1352:
        raise ValueError("Expected 1,352 unique APPROVED_STATIC review rows")
    for review in review_rows:
        validate_identity(review, "APPROVED_STATIC review")
        profile = static_by_id[review["SpecialID"]]
        expected = (review["ProposedFamily"], review["ProposedRole"],
                    review["ProposedPromptUseMode"])
        actual = (profile["GenerationFamily"], profile["GenerationRole"],
                  profile["PromptUseMode"])
        if expected != actual:
            raise ValueError(f"APPROVED_STATIC review mismatch: {review['SpecialID']}")
        for source_name, target_name in STRUCTURAL_FIELD_MAP.items():
            if review[source_name] != profile[target_name]:
                raise ValueError(f"Structural review mismatch: {review['SpecialID']}")


def observation_rows(plan_rows):
    rows = []
    local = [row for row in plan_rows if row["LocalTestEvidence"]]
    if len(local) != 16:
        raise ValueError(f"Expected 16 local observation rows, got {len(local)}")
    stress_ids = {"195", "548"}
    for index, plan in enumerate(local, 1):
        row = dict.fromkeys(OBSERVATION_COLUMNS, "")
        row.update(
            ObservationID=f"PROMOTION-V1-LOCAL-{index:02d}",
            ModelProfile="current_illustrious_test_profile",
            Checkpoint="unknown",
            TestType="STRESS" if plan["SpecialID"] in stress_ids else "SINGLE",
            SpecialIDs=plan["SpecialID"],
            Result="REPORTED",
            Notes=plan["LocalTestEvidence"],
        )
        rows.append(row)
    combination = dict.fromkeys(OBSERVATION_COLUMNS, "")
    combination.update(
        ObservationID="PHASE1-USER-COMBINATION-01",
        ModelProfile="current_illustrious_test_profile",
        Checkpoint="unknown",
        TestType="COMBINATION",
        SpecialIDs="192;545",
        Result="REPORTED",
        FailureModes="Naive multi-Special composition was unstable; fusion or disappearance was reported.",
        Notes=("Phase 1 user report: each Special was recognizable alone, while explicit actor, "
               "body-part and spatial role separation improved coexistence. Exact checkpoint, "
               "seed and generation settings were not recorded."),
    )
    rows.append(combination)
    return rows


def main():
    source = read_csv(SOURCE)
    plan = read_csv(PLAN)
    family_audit = read_csv(FAMILY_AUDIT)
    corrections = read_csv(CORRECTIONS)
    structural_overrides = read_csv(STRUCTURAL_OVERRIDES)
    static_review = read_csv(STATIC_REVIEW)
    if len(source) != 2788 or len(plan) != 2788:
        raise ValueError("Expected exactly 2,788 source/plan rows")
    for source_row, plan_row in zip(source, plan):
        if (source_row["ID"] != plan_row["SpecialID"]
                or source_row["Tag"] != plan_row["Tag"]
                or source_row["Layer"] != plan_row["Layer"]
                or source_row["canonical_target"] != plan_row["CanonicalTarget"]):
            raise ValueError(f"Source/plan identity mismatch: {source_row['ID']}")
    counts = Counter(row["PromotionStatus"] for row in plan)
    recorded = json.loads(COUNTS.read_text(encoding="utf-8"))["counts"]
    if dict(counts) != EXPECTED_COUNTS or recorded != EXPECTED_COUNTS:
        raise ValueError("Promotion status counts do not match the reviewed decision")
    static = [static_row(row) for row in plan]
    apply_family_audit(static, source, corrections, structural_overrides, static_review)
    write_csv(OUT / "special2788_generation_profile.csv", PROFILE_COLUMNS, static)
    write_csv(OUT / "generation_family_rules.csv", FAMILY_RULE_COLUMNS,
              family_rows(family_audit))
    write_csv(OUT / "generation_model_observations.csv", OBSERVATION_COLUMNS,
              observation_rows(plan))
    print(f"generated static={len(static)}, families={len(family_audit)}, observations=17")


if __name__ == "__main__":
    main()
