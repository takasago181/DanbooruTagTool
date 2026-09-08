from translation_quarantine.r3.r3_common import (
    bridge_conflict,
    issue32_fingerprint,
    issue32_propositions,
    json_hash,
)


def test_issue32_v2_translation_visible_semantics_are_native_propositions():
    semantics = {
        "identity_scope": "an exact frozen meaning scope",
        "action_vs_state": "sexual_action",
        "actor_or_ownership": None,
        "target_or_body_site": "target",
        "count_or_cardinality": None,
        "intrinsic_relation_or_spatial_requirement": "relation",
        "defining_qualifiers": ["qualifier"],
    }
    row = {"translation_visible_semantics": semantics}
    assert issue32_propositions(row) == semantics


def test_issue32_v2_fingerprint_uses_exact_semantics_and_sha256_prefix():
    semantics = {
        "identity_scope": "scope",
        "action_vs_state": "state",
        "defining_qualifiers": ["a", "b"],
    }
    row = {"translation_visible_semantics": semantics}
    assert issue32_fingerprint(row) == f"sha256:{json_hash(semantics)}"


def test_issue32_v2_conflict_signal_is_explicit_conflict():
    assert bridge_conflict({"conflict_signal": True}) is True
    assert bridge_conflict({"conflict_signal": False}) is False
