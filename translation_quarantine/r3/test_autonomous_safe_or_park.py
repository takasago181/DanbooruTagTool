"""Focused safety tests for the Issue #36 autonomous campaign."""
from __future__ import annotations

import json

from exact_semantic_evidence import FrozenEvidence, freeze_payload, process_frozen_rows
from r3_autonomous_safe_or_park import _terminal_state, _wording_is_natural


def _evidence(canonical: str, body: str, *, title: str | None = None, exact: bool = True) -> FrozenEvidence:
    raw = json.dumps({"title": title or canonical, "body": body}, sort_keys=True).encode("utf-8")
    return freeze_payload(
        canonical=canonical,
        adapter_id="fixture_exact_canonical",
        source_url=f"https://example.test/{canonical}",
        revision="fixture-rev-1",
        raw_response=raw,
        title=title or canonical,
        body=body,
        exact_title_match=exact,
        http_status=200,
    )


def test_cached_frozen_source_can_be_replayed_without_an_adapter():
    rows = [_evidence("cat", "An image of a cat.")]
    assert process_frozen_rows(rows, {"cat": "LOW"}) == process_frozen_rows(rows, {"cat": "LOW"})


def test_a_second_exact_source_is_not_substituted_for_a_title_mismatch():
    first = _evidence("cat", "An image of a cat.", title="other_tag", exact=False)
    second = _evidence("cat", "An image of a cat.", title="cat", exact=True)
    first_result = process_frozen_rows([first], {"cat": "CRITICAL"})
    second_result = process_frozen_rows([second], {"cat": "CRITICAL"})
    assert first_result["risk_gates"][0]["decision"] == "REVIEW"
    assert second_result["risk_gates"][0]["decision"] == "READY"


def test_explanatory_uncensored_wording_is_parked():
    assert not _wording_is_natural("無修正を示す語")


def test_narrowing_or_added_actor_wording_is_parked():
    assert not _wording_is_natural("グレートソード")
    assert not _wording_is_natural("玉つき筋肉ショタ")


def test_title_mismatch_cannot_be_authority():
    item = _evidence("canonical_tag", "An image of a cat.", title="other_tag", exact=False)
    result = process_frozen_rows([item], {"canonical_tag": "CRITICAL"})
    assert result["risk_gates"][0]["decision"] == "REVIEW"


def test_high_risk_incomplete_proposition_stays_review():
    item = _evidence("between_two_characters", "An image of characters.")
    result = process_frozen_rows([item], {"between_two_characters": "CRITICAL"})
    assert result["risk_gates"][0]["decision"] == "REVIEW"


def test_wording_safe_but_search_unsafe_is_not_final():
    # The campaign's final state requires an independently proven search gate.
    assert _wording_is_natural("エプロン")
    assert _terminal_state(semantic_ready=True, wording_ready=True, search_ready=False) == ("PARK", "REVIEW")


def test_contradiction_is_not_ready():
    assert _terminal_state(semantic_ready=True, wording_ready=True, search_ready=True, contradiction=True) == ("PARK", "CONTRADICTION")
