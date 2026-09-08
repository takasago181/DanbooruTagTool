"""Deterministic contract tests for the reusable exact evidence boundary."""
from __future__ import annotations

import json

from exact_semantic_evidence import (
    FrozenEvidence,
    extract_propositions,
    freeze_payload,
    process_frozen_rows,
    risk_gate,
    validate_propositions,
)


def evidence(canonical: str, body: str, *, title: str | None = None, exact: bool = True) -> FrozenEvidence:
    raw = json.dumps({"title": title or canonical, "body": body}, sort_keys=True).encode("utf-8")
    return freeze_payload(
        canonical=canonical, adapter_id="fixture_exact_canonical", source_url=f"https://example.test/{canonical}",
        revision="fixture-rev-1", raw_response=raw, title=title or canonical, body=body,
        exact_title_match=exact, http_status=200,
    )


def test_simple_entity_and_attribute_entity_are_validated():
    for item in (evidence("cat", "An image of a cat."), evidence("pink_hair", "Pink hair.")):
        props = extract_propositions(item)
        validation = validate_propositions(item, props)
        assert validation.status == "VALIDATED"
        assert props.fields["entity_scope"]


def test_actor_target_body_site_direction_and_relation_are_explicit():
    item = evidence("character_holding_sword_on_left", "A character's hand is holding a sword on the left.")
    props = extract_propositions(item)
    assert props.fields["ownership"] == "A character"
    assert props.fields["target"] == "sword on the left"
    assert props.fields["direction"] == "left"
    assert "on" in props.fields["intrinsic_relation"]

    site = evidence("hand_on_head", "A hand on the head.")
    site_props = extract_propositions(site)
    assert site_props.fields["body_site"] == "head"
    assert site_props.fields["spatial_requirement"] is True


def test_count_and_action_state_distinction():
    counted = evidence("3boys", "An image depicting three male characters.")
    counted_props = extract_propositions(counted)
    assert counted_props.fields["count"] == 3
    assert counted_props.fields["required_modifier"] == ["male"]

    action = evidence("holding_sword", "A character holding a sword.")
    state = evidence("closed_eyes", "Closed eyes.")
    assert extract_propositions(action).fields["action_state"] == "action"
    assert extract_propositions(state).fields["action_state"] == "state"


def test_high_critical_require_exact_authority_and_required_propositions():
    item = evidence("holding_sword", "A character holding a sword.")
    props = extract_propositions(item)
    validation = validate_propositions(item, props)
    gate = risk_gate(item, props, validation, "HIGH_POSE_ACTION")
    assert gate["decision"] == "READY"

    incomplete = evidence("between_two_characters", "An image of characters.")
    incomplete_props = extract_propositions(incomplete)
    incomplete_validation = validate_propositions(incomplete, incomplete_props)
    incomplete_gate = risk_gate(incomplete, incomplete_props, incomplete_validation, "CRITICAL")
    assert incomplete_gate["decision"] == "REVIEW"


def test_ambiguous_underspecified_unavailable_and_title_mismatch_are_not_ready():
    ambiguous = evidence("holding_standing", "A character is holding and standing.")
    assert validate_propositions(ambiguous, extract_propositions(ambiguous)).status == "AMBIGUOUS"

    unavailable = freeze_payload(
        canonical="unknown_tag", adapter_id="fixture_exact_canonical", source_url="https://example.test/unknown_tag",
        revision="", raw_response=b"", title="", body="", exact_title_match=False, http_status=429,
    )
    unavailable_props = extract_propositions(unavailable)
    assert risk_gate(unavailable, unavailable_props, validate_propositions(unavailable, unavailable_props), "LOW")["decision"] == "REVIEW"

    mismatch = evidence("canonical_tag", "An image of a cat.", title="other_tag", exact=False)
    mismatch_props = extract_propositions(mismatch)
    assert risk_gate(mismatch, mismatch_props, validate_propositions(mismatch, mismatch_props), "CRITICAL")["decision"] == "REVIEW"


def test_frozen_replay_is_deterministic_and_handoff_is_gated():
    items = [evidence("cat", "An image of a cat."), evidence("unknown", "")]
    first = process_frozen_rows(items, {"cat": "LOW", "unknown": "CRITICAL"})
    second = process_frozen_rows(items, {"cat": "LOW", "unknown": "CRITICAL"})
    assert first == second
    assert first["handoff"][0]["semantic_status"] == "READY"
    assert first["handoff"][1]["wording_route"] == "PARKED"
