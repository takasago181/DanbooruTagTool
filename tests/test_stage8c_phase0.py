import csv
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.stage8c_audit import (
    APPLICABILITY_FIELDS, EVIDENCE_EVENT_FIELDS, FAMILY_PROPOSAL_FIELDS, FAMILY_REVIEW_FIELDS,
    MODEL_FAMILIARITY_FIELDS, NON_TAG_FIELDS, PRACTICAL_USE_FIELDS,
    RESEARCH_SOURCE_FIELDS, REVIEW_FIELDS, TEST_SLOT_FIELDS, family_members,
    read_rows, validate_evidence_events, validate_family_applicability, validate_family_proposals,
    validate_family_review, validate_family_state, validate_model_familiarity, validate_non_tag,
    validate_practical_use, validate_research_sources, validate_review_ledger,
    validate_test_slots, effective_relation_records,
)

ROOT = Path(__file__).resolve().parents[1]
SEMANTIC = ROOT / "data/semantic"
PILOT_IDS = {"161", "416", "312", "325", "173", "16", "385", "488", "88", "122"}
PILOT001_SUPPORT_IDS = PILOT_IDS | {
    "85", "86", "89", "90", "92", "93", "94", "95", "310", "313", "314",
    "512", "679", "704", "705", "778", "938", "1159",
}
EXIT_PILOT_SUPPORT_IDS = {"17", "19", "129", "362", "365", "1823", "1839"}


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def profiles(knowledge):
    return knowledge.load_generation_profile_store(ROOT)


@pytest.fixture(scope="module")
def support(knowledge, profiles):
    return SupportKnowledgeStore.load(ROOT, knowledge, profiles)


def _hash(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_stage8b_resolver_and_accepted_stage8c_production_hashes_are_protected():
    assert _hash("data/semantic/semantic_support_profiles.csv") == "33f9142333db867d53096cf2f11ba411aefa13996560326fa174803a2d8c2755"
    assert _hash("data/semantic/family_support_rules.csv") == "59609aadc82f9f4be97b82008159b55e4d738f41dbb9625c59be8a826fe7c4fd"
    assert _hash("danbooru_tag_tool/stage8b_support.py") == "83f5617a36d48dfb730e21e2ac2957c8e4f6c00857b0971f6af6724f4e105dd2"
    assert _hash("danbooru_tag_tool/ui.py") == "5c83f6ca7dae2f164403cb13d3112a8ad85a8f201de351354c980daf31f98450"
    assert _hash("tests/test_stage8b_support.py") == "ceafd9916a9b09fe093a527dbd985042af46be1558f7414801a05f018bc0a34f"


def test_review_ledger_is_exact_special_id_coverage(knowledge, support):
    rows = read_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS)
    counts = validate_review_ledger(rows, knowledge, support)
    assert len(rows) == 2788
    assert counts == {
        "SUPPORT_DEFINED": 35, "NO_SUGGESTION": 4,
        "UNRESOLVED": 2, "UNREVIEWED": 2747,
    }
    assert {r["special_id"] for r in rows
            if r["review_decision"] == "SUPPORT_DEFINED"} == (
        PILOT001_SUPPORT_IDS | EXIT_PILOT_SUPPORT_IDS
    )


def test_family_rule_inventory_uses_production_ids_and_counts(profiles):
    rows = read_rows(SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS)
    validate_family_review(rows, profiles)
    members = family_members(profiles)
    assert len(rows) == 25
    assert all(row["family_rule_id"].startswith("GFR_") for row in rows)
    assert {row["review_decision"] for row in rows} == {
        "UNREVIEWED", "NOT_APPLICABLE_NO_MEMBERS", "RULES_DEFINED", "NO_COMMON_RULE",
    }
    assert {row["family_rule_id"] for row in rows if row["review_decision"] == "NOT_APPLICABLE_NO_MEMBERS"} == {
        "GFR_ALIAS_REFERENCE", "GFR_SEMANTIC_SUPPORT"
    }
    assert {row["family_rule_id"]: int(row["member_count"]) for row in rows} == {
        key: len(value) for key, value in members.items()
    }


def test_non_pilot_audit_only_ledgers_remain_empty():
    for name, fields in (
        ("stage8c_model_familiarity.csv", MODEL_FAMILIARITY_FIELDS),
        ("stage8c_non_tag_strategy.csv", NON_TAG_FIELDS),
        ("stage10_test_slots.csv", TEST_SLOT_FIELDS),
        ("stage8c_practical_use.csv", PRACTICAL_USE_FIELDS),
        ("stage8c_relation_evidence_events.csv", EVIDENCE_EVENT_FIELDS),
    ):
        assert read_rows(SEMANTIC / name, fields) == ()


def _proposal(family_id, canonical):
    row = dict.fromkeys(FAMILY_PROPOSAL_FIELDS, "")
    row.update({"proposal_id": "PROP_TEST", "family_rule_id": family_id,
                "support_slot": "BODY_PART", "support_class": "CORE_SUPPORT",
                "candidate_canonical": canonical, "priority": "1", "reason_ja": "synthetic",
                "evidence_level": "SEMANTIC_CURATED", "evidence_source": "SRC_TEST",
                "combination_mode": "ADDITIVE", "evidence_ref": "TEST",
                "proposal_status": "UNIVERSAL_PASS"})
    return row


def _applicability_rows(proposal, members, knowledge, fit="APPLIES_SAME_RELATION"):
    return tuple({
        "proposal_id": proposal["proposal_id"], "special_id": sid,
        "special_term_snapshot": knowledge.special[sid].term, "relation_fit": fit,
        "review_reason_ja": "synthetic complete relation review",
        "evidence_ref": "TEST", "review_batch_id": "TEST", "note": "",
    } for sid in members)


def test_family_relation_requires_every_member_same_relation(knowledge, profiles, support):
    source = support.special_rows[0]
    family_id = "GFR_META_CONTEXT"
    proposed = replace(source, owner_kind="family", owner_id=family_id)
    members = family_members(profiles)[family_id]
    proposal = _proposal(family_id, proposed.candidate_canonical)
    proposal.update({
        "support_slot": proposed.support_slot, "support_class": proposed.support_class or "",
        "priority": str(proposed.priority), "reason_ja": proposed.reason_ja,
        "evidence_level": proposed.evidence_level, "evidence_source": proposed.evidence_source,
        "intent_axis": proposed.intent_axis or "", "intent_direction": proposed.intent_direction or "",
        "combination_mode": proposed.combination_mode or "", "choice_group": proposed.choice_group or "",
        "evidence_ref": proposed.evidence_ref or "", "test_profile_id": proposed.test_profile_id or "",
        "model_scope": proposed.model_scope or "",
    })
    proposals = validate_family_proposals((proposal,), knowledge, profiles, {proposal["evidence_source"]})
    complete = _applicability_rows(proposal, members, knowledge)
    accepted = validate_family_applicability(complete, proposals, (proposed,), knowledge, profiles)
    assert accepted.enabled_family_relations == 1 and accepted.universally_applicable == 1

    with pytest.raises(ValueError, match="UNIVERSAL_PASS requires exact complete"):
        validate_family_applicability(complete[:-1], proposals, (proposed,), knowledge, profiles)

    differs = list(complete)
    differs[0] = {**differs[0], "relation_fit": "METADATA_DIFFERS"}
    with pytest.raises(ValueError, match="UNIVERSAL_PASS requires all"):
        validate_family_applicability(differs, proposals, (proposed,), knowledge, profiles)


def test_applicability_rejects_nonmember(knowledge, profiles):
    family_id = "GFR_META_CONTEXT"
    nonmember = next(sid for sid, p in profiles.profiles.items() if p.FamilyRuleId != family_id)
    proposal = _proposal(family_id, "anus")
    rows = _applicability_rows(proposal, (nonmember,), knowledge)
    with pytest.raises(ValueError, match="not a FamilyRuleId member"):
        validate_family_applicability(rows, {"PROP_TEST": proposal}, (), knowledge, profiles)


def test_zero_member_family_can_never_universally_pass(knowledge, profiles, support):
    proposal = _proposal("GFR_ALIAS_REFERENCE", "anus")
    proposal["proposal_status"] = "UNIVERSAL_PASS"
    with pytest.raises(ValueError, match="Zero-member family cannot"):
        validate_family_proposals((proposal,), knowledge, profiles, {"SRC_TEST"})


def _family_proposal_from_source(source, family_id, status="UNIVERSAL_PASS", proposal_id="PROP_TEST"):
    proposal = _proposal(family_id, source.candidate_canonical)
    proposal.update({"proposal_id": proposal_id, "proposal_status": status,
                     "support_slot": source.support_slot, "support_class": source.support_class or "",
                     "priority": str(source.priority), "reason_ja": source.reason_ja,
                     "evidence_level": source.evidence_level, "evidence_source": source.evidence_source,
                     "intent_axis": source.intent_axis or "", "intent_direction": source.intent_direction or "",
                     "combination_mode": source.combination_mode or "", "choice_group": source.choice_group or "",
                     "evidence_ref": source.evidence_ref or "", "test_profile_id": source.test_profile_id or "",
                     "model_scope": source.model_scope or ""})
    return proposal


def test_explicit_lifecycle_blocking_paths(knowledge, profiles, support):
    family_id = "GFR_META_CONTEXT"
    source = replace(support.special_rows[0], owner_kind="family", owner_id=family_id)
    members = family_members(profiles)[family_id]
    complete = _applicability_rows(_family_proposal_from_source(source, family_id), members, knowledge)

    for fit in ("DOES_NOT_APPLY", "UNRESOLVED"):
        proposal = _family_proposal_from_source(source, family_id)
        rows = _applicability_rows(proposal, members, knowledge, fit)
        proposals = validate_family_proposals((proposal,), knowledge, profiles, {source.evidence_source})
        with pytest.raises(ValueError, match="UNIVERSAL_PASS requires all"):
            validate_family_applicability(rows, proposals, (), knowledge, profiles)

    proposal = _family_proposal_from_source(source, family_id)
    proposals = validate_family_proposals((proposal,), knowledge, profiles, {source.evidence_source})
    duplicate = _applicability_rows(proposal, members, knowledge) + (_applicability_rows(proposal, (members[0],), knowledge)[0],)
    with pytest.raises(ValueError, match="Duplicate applicability"):
        validate_family_applicability(duplicate, proposals, (), knowledge, profiles)

    drift = dict(complete[0]); drift["special_term_snapshot"] = "drifted"
    with pytest.raises(ValueError, match="Special term mismatch"):
        validate_family_applicability((drift,), proposals, (), knowledge, profiles)

    with pytest.raises(ValueError, match="exact complete"):
        validate_family_applicability((), proposals, (), knowledge, profiles)

    promoted = _family_proposal_from_source(source, family_id, "PROMOTED")
    promoted_map = validate_family_proposals((promoted,), knowledge, profiles, {source.evidence_source})
    with pytest.raises(ValueError, match="exact enabled production"):
        validate_family_applicability(_applicability_rows(promoted, members, knowledge), promoted_map, (), knowledge, profiles)

    with pytest.raises(ValueError, match="one exact proven"):
        validate_family_applicability((), {}, (source,), knowledge, profiles)

    duplicate_map = {"P1": {**proposal, "proposal_id": "P1"}, "P2": {**proposal, "proposal_id": "P2"}}
    with pytest.raises(ValueError, match="Duplicate active"):
        validate_family_applicability((), duplicate_map, (), knowledge, profiles)


def test_family_terminal_state_cross_validation(knowledge, profiles, support):
    rows = [dict(row) for row in read_rows(SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS)]
    target = next(row for row in rows if row["family_rule_id"] == "GFR_META_CONTEXT")
    target.update({"review_decision": "RULES_DEFINED", "reviewed_member_count": target["member_count"],
                   "review_reason_ja": "synthetic", "evidence_ref": "TEST"})
    with pytest.raises(ValueError, match="RULES_DEFINED"):
        validate_family_state(rows, {}, (), knowledge, profiles)
    target["review_decision"] = "NO_COMMON_RULE"
    source = replace(support.special_rows[0], owner_kind="family", owner_id="GFR_META_CONTEXT")
    with pytest.raises(ValueError, match="NO_COMMON_RULE"):
        validate_family_state(rows, {}, (source,), knowledge, profiles)
    target["review_decision"] = "UNRESOLVED"
    promoted = _family_proposal_from_source(source, "GFR_META_CONTEXT", "PROMOTED")
    with pytest.raises(ValueError, match="UNRESOLVED"):
        validate_family_state(rows, {"P": promoted}, (source,), knowledge, profiles)


def test_effective_family_summary_fixture_uses_resolver_path(profiles, support):
    family_id = "GFR_META_CONTEXT"
    members = family_members(profiles)[family_id]
    source = next(
        row for row in support.special_rows
        if row.owner_id == "161" and row.candidate_canonical == "anus"
        and row.support_slot == "BODY_PART"
    )
    family_row = replace(source, owner_kind="family", owner_id=family_id)
    explicit_row = replace(source, owner_kind="special", owner_id=members[0])
    synthetic = SupportKnowledgeStore((explicit_row,), (family_row,), profiles)
    records = effective_relation_records(synthetic, members[:2])
    assert len(records) == 2
    assert {record[2].source_kind for record in records} == {"special", "family"}
    assert all(record[1] == "anus" for record in records)
    assert len({(record[0], record[1], record[2].source_kind) for record in records}) == 2
    relations = [record[2] for record in records]
    assert Counter(relation.support_slot for relation in relations) == {"BODY_PART": 2}
    assert Counter(relation.support_class for relation in relations) == {"CORE_SUPPORT": 2}
    assert sum(Counter(relation.intent_axis or "UNASSERTED" for relation in relations).values()) == 2
    assert sum(Counter(relation.combination_mode or "UNASSERTED" for relation in relations).values()) == 2
    assert sum(Counter(relation.evidence_level for relation in relations).values()) == 2


def test_nonempty_context_and_proposal_evidence_guards(knowledge, profiles, support):
    practical = dict.fromkeys(PRACTICAL_USE_FIELDS, "")
    practical.update({"owner_type": "SPECIAL", "owner_id": "161", "candidate_canonical": "anus",
                      "practical_use": "CORE_ESTABLISHMENT", "stage10_test_priority": "HIGH",
                      "review_reason_ja": "synthetic"})
    with pytest.raises(ValueError, match="relation/proposal context"):
        validate_practical_use((practical,), knowledge, profiles)
    proposal = _proposal("GFR_META_CONTEXT", "anus")
    proposal.update({"evidence_level": "MODEL_OBSERVED", "test_profile_id": "", "model_scope": ""})
    with pytest.raises(ValueError, match="Observed family proposal"):
        validate_family_proposals((proposal,), knowledge, profiles, {"SRC_TEST"})


def test_practical_use_requires_active_exact_proposal(knowledge, profiles, support):
    proposal = _proposal("GFR_META_CONTEXT", "anus")
    practical = dict.fromkeys(PRACTICAL_USE_FIELDS, "")
    practical.update({"owner_type": "FAMILY", "owner_id": "GFR_META_CONTEXT",
                      "candidate_canonical": "anus", "proposal_id": "PROP_TEST",
                      "practical_use": "CORE_ESTABLISHMENT", "stage10_test_priority": "HIGH",
                      "review_reason_ja": "synthetic"})
    for status in ("REJECTED", "UNRESOLVED"):
        with pytest.raises(ValueError, match="active family proposal"):
            validate_practical_use((practical,), knowledge, profiles, support,
                                   {"PROP_TEST": {**proposal, "proposal_status": status}})
    validate_practical_use((practical,), knowledge, profiles, support,
                           {"PROP_TEST": {**proposal, "proposal_status": "DRAFT"}})


def test_membership_drift_after_applicability_review_is_rejected(knowledge, profiles, support):
    family_id = "GFR_META_CONTEXT"
    source = replace(support.special_rows[0], owner_kind="family", owner_id=family_id)
    proposal = _family_proposal_from_source(source, family_id)
    members = family_members(profiles)[family_id]
    proposals = validate_family_proposals((proposal,), knowledge, profiles, {source.evidence_source})
    rows = _applicability_rows(proposal, members, knowledge)
    new_member = next(sid for sid, profile in profiles.profiles.items() if profile.FamilyRuleId != family_id)
    changed_profiles = dict(profiles.profiles)
    changed_profiles[new_member] = replace(changed_profiles[new_member], FamilyRuleId=family_id)
    drifted_store = SimpleNamespace(profiles=changed_profiles, family_rules=profiles.family_rules)
    with pytest.raises(ValueError, match="exact complete current member"):
        validate_family_applicability(rows, proposals, (), knowledge, drifted_store)


def test_terminal_family_review_requires_all_members_and_reason(profiles):
    rows = [dict(row) for row in read_rows(SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS)]
    target = next(row for row in rows if row["family_rule_id"] == "GFR_META_CONTEXT")
    target.update({"review_decision": "RULES_DEFINED", "review_reason_ja": "synthetic", "evidence_ref": "TEST"})
    with pytest.raises(ValueError, match="Incomplete terminal"):
        validate_family_review(rows, profiles)


def test_research_registry_and_current_model_policy(knowledge):
    rows = read_rows(SEMANTIC / "stage8c_research_sources.csv", RESEARCH_SOURCE_FIELDS)
    validate_research_sources(rows)
    ids = {row["source_id"] for row in rows}
    assert {"SRC_WAI_V17_CURRENT", "SRC_NOOBAI_V11_EPS_CURRENT", "SRC_NOOBAI_VPRED_V10_CURRENT", "SRC_STAGE8B_PILOT_CURATION"} <= ids
    assert not read_rows(SEMANTIC / "stage8c_model_familiarity.csv", MODEL_FAMILIARITY_FIELDS)


def test_unknown_wai_v17_cutoff_cannot_be_filled(knowledge):
    sources = read_rows(SEMANTIC / "stage8c_research_sources.csv", RESEARCH_SOURCE_FIELDS)
    row = dict.fromkeys(MODEL_FAMILIARITY_FIELDS, "")
    row.update({
        "model_scope": "WAI_ILLUSTRIOUS_SDXL", "exact_model_version": "v17",
        "source_checked_date": "2026-09-06", "latest_version_status": "CURRENT_CONFIRMED",
        "training_cutoff_status": "UNKNOWN", "training_cutoff_value": "2024-06",
        "candidate_canonical": "anus", "familiarity_status": "UNKNOWN",
        "evidence_source_id": "SRC_WAI_V17_CURRENT", "test_priority": "HIGH",
        "reason_ja": "synthetic invalid inherited cutoff",
    })
    with pytest.raises(ValueError, match="cutoff must remain blank"):
        validate_model_familiarity((row,), knowledge, {r["source_id"] for r in sources})
    arbitrary = {**row, "training_cutoff_status": "MAYBE", "training_cutoff_value": ""}
    with pytest.raises(ValueError, match="version/cutoff status"):
        validate_model_familiarity((arbitrary,), knowledge, {r["source_id"] for r in sources})


def test_schema_validators_accept_empty_phase0_files(knowledge, profiles):
    source_ids = {r["source_id"] for r in read_rows(
        SEMANTIC / "stage8c_research_sources.csv", RESEARCH_SOURCE_FIELDS
    )}
    validate_model_familiarity((), knowledge, source_ids)
    validate_non_tag((), knowledge, source_ids)
    validate_test_slots(())
    validate_practical_use((), knowledge, profiles)
    validate_evidence_events((), knowledge, profiles, source_ids)


def test_evidence_history_preserves_negative_and_model_scope(knowledge, profiles, support):
    base = dict.fromkeys(EVIDENCE_EVENT_FIELDS, "")
    base.update({
        "evidence_event_id": "EV_TEST_NEGATIVE", "owner_kind": "SPECIAL",
        "owner_id": "161", "candidate_canonical": "anus",
        "evidence_level": "USER_ENV_VERIFIED",
        "evidence_source": "SRC_STAGE8B_PILOT_CURATION", "evidence_ref": "RESULT_A",
        "test_profile_id": "WAI17_A_B", "model_scope": "WAI-illustrious-SDXL v17",
        "seed_set_ref": "SEEDS_1_4", "generation_condition_hash": "abc",
        "observed_effect": "NEGATIVE", "observed_failures": "visibility loss",
        "result_ref": "RESULT_A", "event_status": "ACTIVE",
    })
    validate_evidence_events((base,), knowledge, profiles, {"SRC_STAGE8B_PILOT_CURATION"}, support, {},
                             {"SRC_STAGE8B_PILOT_CURATION": "USER_TEST"})
    broken = {**base, "model_scope": ""}
    with pytest.raises(ValueError, match="requires reproducible test metadata"):
        validate_evidence_events((broken,), knowledge, profiles, {"SRC_STAGE8B_PILOT_CURATION"}, support, {},
                                 {"SRC_STAGE8B_PILOT_CURATION": "USER_TEST"})


def test_evidence_requires_defined_relation_and_matching_source_kind(knowledge, profiles, support):
    base = dict.fromkeys(EVIDENCE_EVENT_FIELDS, "")
    base.update({
        "evidence_event_id": "EV_DEFINED", "owner_kind": "SPECIAL", "owner_id": "161",
        "candidate_canonical": "anus", "evidence_level": "USER_ENV_VERIFIED",
        "evidence_source": "SRC_USER", "evidence_ref": "RESULT", "test_profile_id": "P",
        "model_scope": "WAI-illustrious-SDXL v17", "seed_set_ref": "S",
        "generation_condition_hash": "H", "observed_effect": "NEUTRAL", "result_ref": "R",
        "event_status": "ACTIVE",
    })
    validate_evidence_events((base,), knowledge, profiles, {"SRC_USER"}, support, {}, {"SRC_USER": "USER_TEST"})
    with pytest.raises(ValueError, match="production relation"):
        validate_evidence_events(({**base, "candidate_canonical": "penis"},), knowledge, profiles,
                                 {"SRC_USER"}, support, {}, {"SRC_USER": "USER_TEST"})
    with pytest.raises(ValueError, match="USER_ENV_VERIFIED requires USER_TEST"):
        validate_evidence_events((base,), knowledge, profiles, {"SRC_USER"}, support, {}, {"SRC_USER": "CONTROLLED_TEST"})


def test_generated_coverage_and_summaries_match_pilot001():
    summary = json.loads((ROOT / "benchmarks/stage8c/validation_summary.json").read_text(encoding="utf-8"))
    assert summary["total_special"] == summary["unique_special_ids"] == 2788
    assert summary["static_family_count"] == summary["family_rule_count"] == 25
    assert summary["static_needs_spatial_yes"] == 216
    assert summary["static_needs_spatial_conditional"] == 677
    assert summary["actual_spatial_relations"] == 0
    assert summary["production_special_relation_rows"] == 50
    assert summary["production_family_relation_rows"] == 1
    assert summary["runtime_external_calls"] == 0
    assert not summary["stage8c_final_decision"] and summary["stage8c_phase1_started"]
    assert summary["pilot001_acceptance"] == "NOT COMPLETE"
    assert summary["pilot001_implementation_complete"] and not summary["pilot002_started"]
    with (ROOT / "benchmarks/stage8c/coverage_audit.csv").open(encoding="utf-8", newline="") as handle:
        assert len(tuple(csv.DictReader(handle))) == 2788
    with (ROOT / "benchmarks/stage8c/static_family_summary.csv").open(encoding="utf-8", newline="") as handle:
        assert len(tuple(csv.DictReader(handle))) == 25
    with (ROOT / "benchmarks/stage8c/family_rule_summary.csv").open(encoding="utf-8", newline="") as handle:
        assert len(tuple(csv.DictReader(handle))) == 25


def test_stage8c_is_not_imported_by_runtime_ui_or_resolver():
    assert "stage8c" not in (ROOT / "danbooru_tag_tool/ui.py").read_text(encoding="utf-8").lower()
    assert "stage8c" not in (ROOT / "danbooru_tag_tool/stage8b_support.py").read_text(encoding="utf-8").lower()
