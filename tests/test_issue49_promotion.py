import csv
from pathlib import Path

import pytest

from tools.issue49_promotion import (
    PromotionError,
    _assert_profile_gate,
    load_candidates,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data/generation/special2788_generation_profile.csv"
SPECIAL_SOURCE = ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv"


def test_issue49_quarantine_materializes_effective_subset_from_live_evidence():
    candidates, source_files = load_candidates()
    _, _, effective, gate = _assert_profile_gate(PROFILE, SPECIAL_SOURCE, candidates)

    assert len(source_files) == 36
    assert gate["counts"] == {
        "profile_rows": 2788,
        "profile_unique_identities": 2788,
        "source_special_rows": 2788,
        "candidate_source_active_rows": 228,
        "candidate_source_excluded_rows": 4,
        "candidate_source_active_field_assignments": 259,
        "candidate_source_excluded_field_assignments": 4,
        "source_non_effective_candidate_rows": 6,
        "effective_field_assignments": 253,
        "affected_specials": 173,
        "conflicting_effective_assignments": 0,
        "target_specials_exactly_once": 173,
    }
    assert len(effective) == 253
    assert len({candidate["special_id"] for candidate in effective}) == 173
    assert all(candidate["status"] in {"QUARANTINED_CANDIDATE", "QUARANTINE_CANDIDATE"}
               for candidate in effective)


def test_issue49_excludes_provisional_target_as_non_effective():
    candidates, _ = load_candidates()
    _, _, effective, gate = _assert_profile_gate(PROFILE, SPECIAL_SOURCE, candidates)
    assert not any(candidate["special_id"] == "779" for candidate in effective)
    parked = gate["non_effective_candidates"]
    assert len(parked) == 6
    assert {candidate["special_id"] for candidate in parked} == {"779"}


def test_issue49_rejects_conflicting_effective_assignments():
    candidate = {
        "special_id": "1", "tag": "anus", "field": "ActorRequirementOverride",
        "current_value": "", "proposed_value": "true", "status": "QUARANTINED_CANDIDATE",
        "source_path": "candidate_fixes.csv", "source_line": 2,
    }
    other = dict(candidate, proposed_value="false", source_line=3)
    with pytest.raises(PromotionError, match="Conflicting effective assignment"):
        _assert_profile_gate(PROFILE, SPECIAL_SOURCE, [candidate, other])


def test_issue49_compact_block_expands_named_fields_only():
    from tools.issue49_promotion import _compact_candidates

    rows = [{
        "sequence": "1", "special_id": "1", "tag": "tag", "rule_version": "R2",
        "risk_priority": "A", "problem_fields": "ActorRequirementOverride+BodypartRequirementOverride",
        "proposed_change": "actor=true; bodypart=true", "reason": "reason",
        "evidence_refs": "evidence", "status": "QUARANTINE_CANDIDATE",
    }]
    candidates = _compact_candidates(rows, "block.csv")
    assert [(row["field"], row["proposed_value"]) for row in candidates] == [
        ("ActorRequirementOverride", "true"),
        ("BodypartRequirementOverride", "true"),
    ]
