import csv
from collections import Counter
import hashlib
import json
from pathlib import Path

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.stage8c_audit import (
    APPLICABILITY_FIELDS, FAMILY_PROPOSAL_FIELDS, FAMILY_REVIEW_FIELDS, REVIEW_FIELDS,
    family_members, read_rows, validate_family_applicability, validate_family_proposals,
    validate_family_review, validate_family_state, validate_review_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC = ROOT / "data/semantic"
SELF_ACTION = ("85", "86", "88", "89", "90", "92", "93", "94", "95",
               "512", "679", "704", "705", "778", "938")
MACHINE = ("310", "311", "312", "313", "314", "1159")
TARGETS = frozenset((*SELF_ACTION, *MACHINE))
PREEXISTING_SUPPORT_IDS = {"16", "88", "122", "161", "173", "312", "325", "385", "416", "488"}
EXIT_PILOT_IDS = frozenset({
    "17", "19", "129", "177", "178", "179", "362", "365", "934", "1078",
    "1823", "1839",
})


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def profiles(knowledge):
    return knowledge.load_generation_profile_store(ROOT)


@pytest.fixture(scope="module")
def support(knowledge, profiles):
    return SupportKnowledgeStore.load(ROOT, knowledge, profiles)


def _row_hash(rows):
    payload = json.dumps(tuple(rows), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def test_frozen_request_and_exact_family_membership(profiles):
    frozen = json.loads((SEMANTIC / "stage8c_pilot001_frozen_expectations.json").read_text(
        encoding="utf-8"
    ))
    assert frozen["target_specials"] == 21 and frozen["family_rule_ids"] == 2
    members = family_members(profiles)
    assert members["GFR_SELF_ACTION"] == SELF_ACTION
    assert members["GFR_MACHINE_STRUCTURED"] == MACHINE


def test_pilot001_acceptance_counts_are_derived(knowledge, support):
    reviews = read_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS)
    counts = validate_review_ledger(reviews, knowledge, support)
    assert counts == {
        "SUPPORT_DEFINED": 35, "NO_SUGGESTION": 4,
        "UNRESOLVED": 2, "UNREVIEWED": 2747,
    }
    assert len(reviews) == len({row["special_id"] for row in reviews}) == 2788
    assert len(support.special_rows) == 58 and len(support.family_rows) == 1
    pilot001 = Counter(
        row["review_decision"] for row in reviews if row["special_id"] in TARGETS
    )
    assert pilot001 == {"SUPPORT_DEFINED": 20, "UNRESOLVED": 1}


def test_only_intended_review_rows_changed_from_phase0():
    rows = read_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS)
    changed = {row["special_id"] for row in rows
               if row["review_batch_id"] == "STAGE8C_PHASE1_PILOT001"}
    assert changed == TARGETS - {"88", "312"}
    assert _row_hash(
        row for row in rows if row["special_id"] not in TARGETS | EXIT_PILOT_IDS
    ) == (
        "11ada7372c46230ec99ba9c80402359b7d4dee20b7ecac5a896510ca9bfed38a"
    )


def test_stage8b_39_rows_and_id312_five_rows_are_unchanged():
    path = SEMANTIC / "semantic_support_profiles.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = tuple(reader)
    baseline = tuple(sorted(
        (row for row in rows if row["special_id"] in PREEXISTING_SUPPORT_IDS),
        key=lambda row: (
            int(row["special_id"]), row["candidate_canonical"], row["support_slot"]
        ),
    ))
    assert len(baseline) == 39
    assert _row_hash(baseline) == (
        "d106939801b00fcd4bd10a950eb9a3e78bf02865e94da034cbe16e007679015e"
    )
    id312 = tuple(row for row in rows if row["special_id"] == "312")
    assert len(id312) == 5
    assert _row_hash(id312) == "b36b10933efe58b58a10c0c1390938093695fd7600298e6b0f84d08cff10f2a2"


def test_machine_special_rows_and_unresolved_boundary(support):
    rows = [row for row in support.special_rows if row.owner_id in MACHINE]
    counts = Counter(row.owner_id for row in rows)
    assert {sid: counts[sid] for sid in MACHINE} == {
        "310": 2, "311": 0, "312": 5, "313": 4, "314": 3, "1159": 2,
    }
    assert {row.candidate_canonical for row in rows if row.owner_id == "310"} == {
        "breast_pump", "lactation",
    }
    assert {row.candidate_canonical for row in rows if row.owner_id == "313"} == {
        "vibrator", "sex_toy", "sitting", "straddling",
    }
    assert {row.candidate_canonical for row in rows if row.owner_id == "314"} == {
        "robot", "sex", "android",
    }
    assert {row.candidate_canonical for row in rows if row.owner_id == "1159"} == {
        "beads", "anal_beads",
    }
    review = {row["special_id"]: row for row in read_rows(
        SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS
    )}
    assert review["311"]["review_decision"] == "UNRESOLVED"
    assert not support.candidates(("311",))


def test_self_action_promoted_family_rule_and_explicit_precedence(knowledge, profiles, support):
    source_ids = {row["source_id"] for row in csv.DictReader(
        (SEMANTIC / "stage8c_research_sources.csv").open(encoding="utf-8-sig", newline="")
    )}
    proposal_rows = read_rows(
        SEMANTIC / "stage8c_family_relation_proposals.csv", FAMILY_PROPOSAL_FIELDS
    )
    assert len(proposal_rows) == 1
    proposal = proposal_rows[0]
    assert proposal == {
        "proposal_id": "FRP_P1_SELF_ACTION_SOLO_V1", "family_rule_id": "GFR_SELF_ACTION",
        "support_slot": "SUBJECT_BASIC", "support_class": "OPTIONAL_VARIATION",
        "candidate_canonical": "solo", "priority": "10",
        "reason_ja": "自己行為の主体を単独人物として構成する共通の任意補助候補",
        "evidence_level": "SEMANTIC_CURATED", "evidence_source": "SRC_STAGE8B_PILOT_CURATION",
        "intent_axis": "COMPOSITION", "intent_direction": "NEUTRAL",
        "combination_mode": "CONTEXTUAL", "choice_group": "",
        "evidence_ref": "STAGE8C_PILOT001_SELF_ACTION_15_MEMBER_REVIEW",
        "test_profile_id": "", "model_scope": "", "proposal_status": "PROMOTED",
        "note": "NOT_TESTED; explicit Special relation takes precedence for the same canonical",
    }
    proposals = validate_family_proposals(proposal_rows, knowledge, profiles, source_ids)
    applicability = read_rows(
        SEMANTIC / "stage8c_family_candidate_applicability.csv", APPLICABILITY_FIELDS
    )
    assert len(applicability) == 15
    assert {row["special_id"] for row in applicability} == set(SELF_ACTION)
    assert {row["relation_fit"] for row in applicability} == {"APPLIES_SAME_RELATION"}
    result = validate_family_applicability(
        applicability, proposals, support.family_rows, knowledge, profiles
    )
    assert (result.enabled_family_relations, result.universally_applicable,
            result.blocked, result.missing_member_reviews) == (1, 1, 0, 0)

    id88 = next(candidate for candidate in support.candidates(("88",))
                if candidate.canonical == "solo")
    assert len(id88.relations) == 1
    assert id88.relations[0].source_kind == "special"
    assert id88.relations[0].support_class == "CORE_SUPPORT"
    other = next(candidate for candidate in support.candidates(("85",))
                 if candidate.canonical == "solo")
    assert other.relations[0].source_kind == "family"
    assert other.relations[0].support_class == "OPTIONAL_VARIATION"


def test_machine_has_no_common_or_generic_family_rule(knowledge, profiles, support):
    family_reviews = read_rows(
        SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS
    )
    validate_family_review(family_reviews, profiles)
    by_id = {row["family_rule_id"]: row for row in family_reviews}
    assert by_id["GFR_SELF_ACTION"]["review_decision"] == "RULES_DEFINED"
    assert by_id["GFR_SELF_ACTION"]["reviewed_member_count"] == "15"
    assert by_id["GFR_MACHINE_STRUCTURED"]["review_decision"] == "NO_COMMON_RULE"
    assert by_id["GFR_MACHINE_STRUCTURED"]["reviewed_member_count"] == "6"
    assert not [row for row in support.family_rows
                if row.owner_id == "GFR_MACHINE_STRUCTURED"]
    assert not [row for row in support.family_rows
                if row.candidate_canonical in {"machine", "sex_toy"}]

    source_ids = {row["source_id"] for row in csv.DictReader(
        (SEMANTIC / "stage8c_research_sources.csv").open(encoding="utf-8-sig", newline="")
    )}
    proposals = validate_family_proposals(read_rows(
        SEMANTIC / "stage8c_family_relation_proposals.csv", FAMILY_PROPOSAL_FIELDS
    ), knowledge, profiles, source_ids)
    validate_family_state(family_reviews, proposals, support.family_rows, knowledge, profiles)


def test_ruleset2_authorities_and_later_stage_gates_are_unchanged():
    hashes = {
        "01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv": "12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02",
        "06_SEMANTIC336_ROUTING_OVERLAY.csv": "deb17fd928e7af9fed4a3542fd90d83c96c83e4c4cde9a2d9045b85a2f08e624",
        "37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv": "9cb6d667ce4894a8df4e2a9579e0bf9adabd93ccc54ecf28ac57e9dc2581b1d5",
        "38_ALIAS_STATISTICS_POLICY_v3.0.csv": "e092014c196bf2406054f7c78c03e63a1cd8cdfdba59c059d2baf50222e7727d",
    }
    base = ROOT / "data/derived/ruleset2"
    assert all(hashlib.sha256((base / name).read_bytes()).hexdigest() == expected
               for name, expected in hashes.items())
    summary = json.loads((ROOT / "benchmarks/stage8c/pilot001_scope_diff.json").read_text(
        encoding="utf-8"
    ))
    assert summary["pilot001_acceptance"] == "NOT COMPLETE"
    assert summary["stage8c_overall"] == "NOT FINAL"
    assert summary["stage9"] == summary["stage10"] == "NOT STARTED"
    assert summary["runtime_external_calls"] == 0
