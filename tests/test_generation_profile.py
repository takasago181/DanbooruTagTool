import csv
from collections import Counter
from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path

import pytest

from danbooru_tag_tool.generation_profile import (
    APPROVED_STATUSES, AUDIT_ONLY_STATUSES, FAMILY_RULE_COLUMNS,
    OBSERVATION_COLUMNS, PROFILE_COLUMNS, GenerationFamilyRule,
    GenerationModelObservation, GenerationProfile, GenerationProfileStore,
    join_generation_profiles, load_generation_family_rules,
    load_generation_model_observations, load_generation_profiles,
)
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.models import CoreTagSet
from danbooru_tag_tool.prompt_session import PromptSession
from danbooru_tag_tool.search import TagSearchEngine
from tests.test_stage6_recommendations import make_overlay


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv"
PROFILE = ROOT / "data/generation/special2788_generation_profile.csv"
FAMILIES = ROOT / "data/generation/generation_family_rules.csv"
OBSERVATIONS = ROOT / "data/generation/generation_model_observations.csv"
PLAN = ROOT / "data/generation/audit/PROMOTION_PLAN_v1.csv"
FAMILY_AUDIT = ROOT / "data/generation/audit/FAMILY_RULE_AUDIT_25_v1.csv"
CORRECTIONS = ROOT / "data/generation/audit/HIGH_CONFIDENCE_CORRECTIONS_v1.csv"
STRUCTURAL_OVERRIDES = ROOT / "data/generation/audit/EXPLICIT_STRUCTURAL_OVERRIDES_240_v1.csv"
STATIC_REVIEW = ROOT / "data/generation/audit/APPROVED_STATIC_1352_REVIEW_v1.csv"
EXPECTED_COUNTS = {
    "APPROVED_STATIC": 1352,
    "APPROVED_IDENTITY_ONLY": 778,
    "APPROVED_SEMANTIC_ROLE": 336,
    "APPROVED_CORRECTION_METADATA": 13,
    "PROVISIONAL": 294,
    "PROVISIONAL_CORRECTION": 1,
    "REVIEW_REQUIRED": 14,
}
DEPRECATED_STATIC_COLUMNS = {
    "GenerationClass", "StandaloneVisuality", "BodypartClarity", "ActionClarity",
    "ActorClarity", "CoexistenceScore", "SupportDependency", "NeedsActor",
    "NeedsBodypart", "NeedsImplement", "NeedsPose", "NeedsCamera", "ExpansionHint",
    "KnownFailureModes", "ConflictNotes", "AuditStatus", "AuditEvidence",
    "ModelProfile", "Confidence",
}
STATIC_SEMANTIC_FIELDS = (
    "MeaningStatus", "MeaningConfidence", "SourceGlossQuality", "GenerationFamily",
    "GenerationRole", "PromptUseMode", "FamilyRuleId", "CompositionRoleOverride",
    "ActorRequirementOverride", "BodypartRequirementOverride",
    "ImplementRequirementOverride", "PoseRequirementOverride",
    "CameraRequirementOverride", "SpatialAssignmentOverride", "ShapeConflictGroup",
    "RecommendedHandling",
)


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def store(knowledge):
    return knowledge.load_generation_profile_store(ROOT)


def write_rows(tmp_path, filename, columns, rows):
    path = tmp_path / filename
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return path


def profile_row(special_id="1"):
    with PROFILE.open(encoding="utf-8", newline="") as stream:
        return next(row for row in csv.DictReader(stream) if row["SpecialID"] == special_id)


def core(ids):
    return CoreTagSet("test", "核", tuple(ids), "", "2026-09-06T12:00:00+09:00")


def test_v2_static_snapshot_status_counts_and_identity(knowledge, store):
    assert len(knowledge.special) == len(store.profiles) == len(store.joined) == 2788
    assert Counter(profile.PromotionStatus for profile in store.profiles.values()) == EXPECTED_COUNTS
    assert store.profiles.keys() == knowledge.special.keys()
    assert all(store.joined[sid].special is knowledge.special[sid] for sid in knowledge.special)
    assert all(profile.Tag == knowledge.special[sid].term for sid, profile in store.profiles.items())
    assert not (set(PROFILE_COLUMNS) & DEPRECATED_STATIC_COLUMNS)
    with pytest.raises(TypeError):
        store.profiles["new"] = store.profiles["1"]


def test_promotion_status_is_available_through_existing_left_join(knowledge):
    joined = knowledge.load_generation_profile(PROFILE)
    assert joined["1"].generation_profile.PromotionStatus == "APPROVED_STATIC"
    assert joined["1117"].generation_profile.PromotionStatus == "REVIEW_REQUIRED"


def test_only_approved_rows_promote_static_semantics(store):
    for profile in store.profiles.values():
        assert profile.is_approved == (profile.PromotionStatus in APPROVED_STATUSES)
        assert profile.is_audit_only == (profile.PromotionStatus in AUDIT_ONLY_STATUSES)
        if profile.is_audit_only:
            assert all(getattr(profile, name) in ("", None) for name in STATIC_SEMANTIC_FIELDS)
            assert profile.SpecialFlags == "AUDIT_ONLY_DO_NOT_AUTO_EXPAND"
        else:
            assert profile.PromotionStatus.startswith("APPROVED_")


def test_family_defaults_are_unknown_and_per_tag_override_wins(knowledge, store):
    assert len(store.family_rules) == 25
    profile = store.profiles["192"]
    assert profile.FamilyRuleId == "GFR_INSERTION_STRUCTURED"
    effective = store.effective_profile("192")
    assert profile.ActorRequirementOverride is True
    assert effective.NeedsActor is True and effective.NeedsBodypart is True
    assert effective.NeedsSpatialAssignment is None
    assert effective.AllowsAutomaticExpansion is False
    overridden = replace(profile, ActorRequirementOverride=False, CameraRequirementOverride=False)
    custom = dict(store.profiles)
    custom[profile.SpecialID] = overridden
    replaced = GenerationProfileStore(
        knowledge.special, custom, store.family_rules, store.observations
    ).effective_profile(profile.SpecialID)
    assert replaced.NeedsActor is False and replaced.NeedsCamera is False
    assert replaced.NeedsBodypart is True


def test_all_family_physical_defaults_are_unknown(store):
    assert len(store.family_rules) == 25
    for rule in store.family_rules.values():
        assert rule.DefaultNeedsActor is None
        assert rule.DefaultNeedsBodypart is None
        assert rule.DefaultNeedsImplement is None
        assert rule.DefaultNeedsPose is None
        assert rule.DefaultNeedsCamera is None
        assert rule.DefaultNeedsSpatialAssignment is None
        assert rule.DefaultCompositionRole == ""


def test_false_and_unknown_remain_distinct(knowledge, store):
    piledriver = store.effective_profile("793")
    assert piledriver.NeedsPose is True
    camera_focus = store.effective_profile("515")
    assert camera_focus.NeedsPose is False
    assert camera_focus.NeedsCamera is True
    assert store.effective_profile("10").NeedsPose is None
    assert store.effective_profile("10").CompositionRole is None
    assert piledriver.CompositionRole == "pose"
    assert store.effective_profile("2003").CompositionRole == "camera"


def test_all_approved_static_family_links_are_valid(store):
    for profile in store.profiles.values():
        if profile.PromotionStatus == "APPROVED_STATIC":
            rule = store.family_rules[profile.FamilyRuleId]
            assert rule.GenerationFamily == profile.GenerationFamily
            assert store.effective_profile(profile.SpecialID).PromptUseMode == profile.PromptUseMode


def test_observations_are_separate_and_preserve_unknown_settings(knowledge, store):
    assert len(store.observations) == 17
    local = [item for key, item in store.observations.items() if key.startswith("PROMOTION-V1-LOCAL-")]
    assert len(local) == 16
    assert all(item.ModelProfile == "current_illustrious_test_profile" for item in local)
    assert all(item.Checkpoint == "unknown" for item in local)
    combination = store.observations["PHASE1-USER-COMBINATION-01"]
    assert combination.TestType == "COMBINATION"
    assert combination.SpecialIDs == ("192", "545")
    before = store.profiles["192"]
    assert combination.Notes
    assert store.profiles["192"] is before
    assert not (set(PROFILE_COLUMNS) & {"ModelProfile", "Checkpoint", "Result"})


def test_alias_prompt_identity_preserved_for_all_778(knowledge, store):
    aliases = [profile for profile in store.profiles.values()
               if profile.PromotionStatus == "APPROVED_IDENTITY_ONLY"]
    assert len(aliases) == 778
    for profile in aliases:
        tag = knowledge.special[profile.SpecialID]
        assert tag.layer == "Alias" and profile.PromptUseMode == "ALIAS_PRESERVE"
        assert PromptSession.from_core(core([profile.SpecialID]), knowledge).export_prompt() == \
            tag.term.replace("_", " ")


@pytest.mark.parametrize("special_id", ["309", "1117"])
def test_audit_only_tag_is_selectable_exportable_and_never_auto_expands(
    knowledge, store, special_id
):
    profile = store.profiles[special_id]
    assert profile.PromotionStatus in AUDIT_ONLY_STATUSES
    session = PromptSession.from_core(core([special_id]), knowledge)
    assert session.export_prompt() == knowledge.special[special_id].term.replace("_", " ")
    effective = store.effective_profile(special_id)
    assert effective.AllowsAutomaticExpansion is False
    assert effective.PromptUseMode is None
    assert effective.NeedsActor is None and effective.NeedsSpatialAssignment is None


def test_search_session_and_export_unchanged_by_v2_metadata(knowledge, store):
    engine = TagSearchEngine(knowledge)
    ids = ("192", "1578", "4", "1117")
    queries = [value for sid in ids for value in
               (knowledge.special[sid].term, knowledge.special[sid].japanese)]
    before = [engine.search_one(query) for query in queries]
    session = PromptSession.from_core(core(ids), knowledge)
    saved = session.core.to_json(knowledge.special)
    expected = session.export_prompt()
    assert [engine.search_one(query) for query in queries] == before
    assert all(before)
    loaded = CoreTagSet.from_json(saved, knowledge.special)
    assert PromptSession.from_core(loaded, knowledge).export_prompt() == expected
    assert "descensored" in expected and "uncensored" not in expected
    # Ruleset2 keeps this curated Alias target as related evidence only.  It
    # must not enter default full-semantic statistics or replace Prompt text.
    assert "uncensored" not in session.statistics_canonicals
    assert "1578" in session.unresolved_statistics_special_ids
    assert store.profiles["1117"].PromotionStatus == "REVIEW_REQUIRED"


def test_source_bytes_unchanged_and_v2_load_is_read_only(knowledge):
    before = SOURCE.read_bytes()
    original = dict(knowledge.special)
    knowledge.load_generation_profile_store(ROOT)
    assert knowledge.special == original and SOURCE.read_bytes() == before
    manifest = json.loads((ROOT / "FILE_HASHES.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(before).hexdigest() == manifest[SOURCE.relative_to(ROOT).as_posix()]["sha256"]


def test_absent_empty_and_unknown_profile_are_left_joins(knowledge, tmp_path):
    for path in (None, tmp_path / "missing.csv",
                 write_rows(tmp_path, "empty.csv", PROFILE_COLUMNS, [])):
        joined = knowledge.load_generation_profile(path)
        assert len(joined) == 2788
        assert all(item.generation_profile is None for item in joined.values())
    row = profile_row() | {"SpecialID": "unknown-existing-in-other-version"}
    profiles = load_generation_profiles(write_rows(tmp_path, "unknown.csv", PROFILE_COLUMNS, [row]))
    joined = join_generation_profiles(knowledge.special, profiles)
    assert len(joined) == 2788 and joined["1"].generation_profile is None


@pytest.mark.parametrize("change", [
    {"SpecialID": ""}, {"Tag": ""}, {"PromotionStatus": "AUTO_APPROVED"},
    {"PromptUseMode": "AUTO_EXPAND"}, {"ActorRequirementOverride": "yes"},
])
def test_malformed_profiles_rejected(tmp_path, change):
    with pytest.raises(ValueError):
        load_generation_profiles(write_rows(
            tmp_path, "profile.csv", PROFILE_COLUMNS, [profile_row() | change]
        ))


def test_audit_only_semantic_promotion_is_rejected(tmp_path):
    row = profile_row("1117") | {"GenerationRole": "guessed", "PromptUseMode": "MODEL_DEPENDENT"}
    with pytest.raises(ValueError, match="Audit-only"):
        load_generation_profiles(write_rows(tmp_path, "profile.csv", PROFILE_COLUMNS, [row]))


def test_profile_columns_duplicates_and_tag_drift_rejected(knowledge, tmp_path):
    row = profile_row()
    with pytest.raises(ValueError, match="Duplicate"):
        load_generation_profiles(write_rows(tmp_path, "duplicate.csv", PROFILE_COLUMNS, [row, row]))
    with pytest.raises(ValueError, match="columns"):
        load_generation_profiles(write_rows(tmp_path, "columns.csv", (*PROFILE_COLUMNS, "extra"), []))
    with pytest.raises(ValueError, match="mismatch"):
        knowledge.load_generation_profile(write_rows(
            tmp_path, "drift.csv", PROFILE_COLUMNS, [row | {"Tag": "different"}]
        ))


def test_family_and_observation_validation(knowledge, store, tmp_path):
    family = next(csv.DictReader(FAMILIES.open(encoding="utf-8", newline="")))
    loaded_family = load_generation_family_rules(write_rows(
        tmp_path, "family.csv", FAMILY_RULE_COLUMNS,
        [family | {"DefaultNeedsActor": "false"}],
    ))
    assert loaded_family[family["FamilyRuleId"]].DefaultNeedsActor is False
    with pytest.raises(ValueError, match="blank/true/false"):
        load_generation_family_rules(write_rows(
            tmp_path, "invalid-family.csv", FAMILY_RULE_COLUMNS,
            [family | {"DefaultNeedsActor": "unknown"}],
        ))
    observation = next(csv.DictReader(OBSERVATIONS.open(encoding="utf-8", newline="")))
    multiple = observation | {
        "ObservationID": "test-combination", "TestType": "COMBINATION",
        "SpecialIDs": "192;545",
    }
    loaded = load_generation_model_observations(write_rows(
        tmp_path, "observations.csv", OBSERVATION_COLUMNS, [multiple]
    ))
    assert loaded["test-combination"].SpecialIDs == ("192", "545")
    unknown = replace(loaded["test-combination"], SpecialIDs=("missing",))
    with pytest.raises(ValueError, match="unknown SpecialID"):
        GenerationProfileStore(knowledge.special, store.profiles, store.family_rules,
                               {unknown.ObservationID: unknown})


@pytest.mark.parametrize("special_id", ["192", "1578", "1117"])
def test_v2_metadata_does_not_change_fixture_statistics(knowledge, tmp_path, special_id):
    overlay = make_overlay(tmp_path)
    document = json.loads(overlay.path.read_text(encoding="utf-8"))
    tag = knowledge.special[special_id]
    if tag.statistics_canonical is None:
        # Unmapped/ambiguous and Ruleset2 non-default Alias statistics remain unresolved.
        assert PromptSession.from_core(core([special_id]), knowledge).unresolved_statistics_special_ids
        return
    document["canonical_to_source_tag_ids"] = {tag.statistics_canonical: [0]}
    document["source_tag_identities"][0]["canonical"] = tag.statistics_canonical
    overlay.path.write_text(json.dumps(document), encoding="utf-8")
    from danbooru_tag_tool.canonical_overlay import CanonicalOverlay
    overlay = CanonicalOverlay(overlay.index, overlay.path)
    session = PromptSession.from_core(core([special_id]), knowledge)
    before = overlay.intersect(session.statistics_canonicals)
    counts = overlay.aggregate(before, exclude=session.statistics_canonicals)
    knowledge.load_generation_profile_store(ROOT)
    after = overlay.intersect(session.statistics_canonicals)
    assert after.base_count == before.base_count == 4
    assert overlay.aggregate(after, exclude=session.statistics_canonicals) == counts


def test_plan_and_production_counts_are_independently_reproducible(store):
    with PLAN.open(encoding="utf-8-sig", newline="") as stream:
        plan = list(csv.DictReader(stream))
    assert len(plan) == 2788
    assert Counter(row["PromotionStatus"] for row in plan) == EXPECTED_COUNTS
    assert Counter(profile.PromotionStatus for profile in store.profiles.values()) == EXPECTED_COUNTS


def test_v2_1_review_sets_match_production_exactly(store):
    with CORRECTIONS.open(encoding="utf-8-sig", newline="") as stream:
        corrections = list(csv.DictReader(stream))
    with STRUCTURAL_OVERRIDES.open(encoding="utf-8-sig", newline="") as stream:
        overrides = list(csv.DictReader(stream))
    with STATIC_REVIEW.open(encoding="utf-8-sig", newline="") as stream:
        review = list(csv.DictReader(stream))
    assert len(corrections) == 177
    assert sum(row["CurrentFamily"] != row["ProposedFamily"] for row in corrections) == 153
    assert sum(row["CurrentRole"] != row["ProposedRole"] for row in corrections) == 162
    assert sum(row["CurrentPromptUseMode"] != row["ProposedPromptUseMode"]
               for row in corrections) == 116
    assert len(overrides) == 240
    assert len(review) == 1352
    assert all(store.profiles[row["SpecialID"]].PromotionStatus == "APPROVED_STATIC"
               for row in review)
    for row in review:
        profile = store.profiles[row["SpecialID"]]
        assert (profile.GenerationFamily, profile.GenerationRole, profile.PromptUseMode) == (
            row["ProposedFamily"], row["ProposedRole"], row["ProposedPromptUseMode"]
        )
    explicit_ids = {row["SpecialID"] for row in overrides}
    actual_ids = {
        profile.SpecialID for profile in store.profiles.values()
        if profile.PromotionStatus == "APPROVED_STATIC" and any((
            profile.ActorRequirementOverride is not None,
            profile.BodypartRequirementOverride is not None,
            profile.ImplementRequirementOverride is not None,
            profile.PoseRequirementOverride is not None,
            profile.CameraRequirementOverride is not None,
            profile.SpatialAssignmentOverride is not None,
            bool(profile.CompositionRoleOverride), bool(profile.SpecialFlags),
        ))
    }
    assert actual_ids == explicit_ids


@pytest.mark.parametrize("special_id", ["10", "169", "297", "1991"])
def test_context_tags_do_not_inherit_physical_requirements(store, special_id):
    profile = store.profiles[special_id]
    effective = store.effective_profile(special_id)
    assert profile.GenerationFamily == "CONTEXT_MODIFIER"
    assert effective.PromptUseMode == "SUPPORT"
    assert all(value is None for value in (
        effective.NeedsActor, effective.NeedsBodypart, effective.NeedsImplement,
        effective.NeedsPose, effective.NeedsCamera, effective.NeedsSpatialAssignment,
    ))


def test_audited_examples_and_actor_separation_are_explicit(store):
    for special_id in ("1023", "2521", "2522", "2523"):
        assert store.profiles[special_id].GenerationFamily != "FLUID_STATE_ACTION"
    big_belly = store.profiles["2364"]
    assert (big_belly.GenerationFamily, big_belly.PromptUseMode) == ("BODY_ATTRIBUTE", "DIRECT")
    piledriver = store.effective_profile("793")
    assert piledriver.PromptUseMode == "STRUCTURED"
    assert piledriver.NeedsPose is True and piledriver.CompositionRole == "pose"
    cross_section = store.effective_profile("2003")
    assert cross_section.NeedsCamera is True and cross_section.CompositionRole == "camera"
    separated = [profile for profile in store.profiles.values()
                 if profile.SpecialFlags == "ACTOR_SEPARATION_REQUIRED"]
    assert len(separated) == 35
    assert all(profile.ActorRequirementOverride is True
               and profile.SpatialAssignmentOverride is True for profile in separated)
    self_actor = next(profile for profile in store.profiles.values()
                      if profile.SpecialFlags == "SELF_ACTOR_ROLE")
    assert self_actor.ActorRequirementOverride is True
    assert "ACTOR_SEPARATION_REQUIRED" not in self_actor.SpecialFlags


def test_chatgpt_final_audit_multi_target_corrections(store):
    multiple_anal = store.profiles["152"]
    assert (multiple_anal.GenerationFamily, multiple_anal.GenerationRole,
            multiple_anal.PromptUseMode, multiple_anal.FamilyRuleId) == (
                "INSERTION_STRUCTURED", "bodypart_action", "STRUCTURED",
                "GFR_INSERTION_STRUCTURED"
            )
    assert multiple_anal.ActorRequirementOverride is True
    assert multiple_anal.BodypartRequirementOverride is True
    assert multiple_anal.SpatialAssignmentOverride is True
    assert multiple_anal.SpecialFlags == ""
    multiple_fellatio = store.profiles["697"]
    assert (multiple_fellatio.GenerationFamily, multiple_fellatio.GenerationRole,
            multiple_fellatio.PromptUseMode, multiple_fellatio.FamilyRuleId) == (
                "ACTION_INTERACTION", "action", "STRUCTURED", "GFR_ACTION_INTERACTION"
            )
    assert multiple_fellatio.ActorRequirementOverride is True
    assert multiple_fellatio.BodypartRequirementOverride is None
    assert multiple_fellatio.SpatialAssignmentOverride is True
    assert multiple_fellatio.SpecialFlags == ""
