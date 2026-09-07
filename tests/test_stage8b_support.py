import csv
from dataclasses import fields, replace
from pathlib import Path

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage7a_session import Stage7ASession
from danbooru_tag_tool.stage7a_warnings import Stage7AWarningPresenter
from danbooru_tag_tool.stage8b_support import (
    PROFILE_FIELDS,
    SemanticSupportCandidate,
    SupportKnowledgeStore,
    load_family_support_rules,
    load_special_support_profiles,
)


ROOT = Path(__file__).resolve().parents[1]
PILOT_IDS = ("161", "416", "312", "325", "173", "16", "385", "488", "88", "122")


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def profile_store(knowledge):
    return knowledge.load_generation_profile_store(ROOT)


@pytest.fixture(scope="module")
def store(knowledge, profile_store):
    return SupportKnowledgeStore.load(ROOT, knowledge, profile_store)


def _production_row():
    path = ROOT / "data/semantic/semantic_support_profiles.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return next(csv.DictReader(handle))


def _write_special_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["special_id", *PROFILE_FIELDS])
        writer.writeheader()
        writer.writerows(rows)


def test_production_profiles_load_and_pilot_coverage(store, knowledge):
    assert len(store.special_rows) == 58
    assert len(store.family_rows) == 1
    # Exit Pilot may reorder the ledger, so select the original Stage8B rows by
    # stable owner identity instead of assuming they remain a physical prefix.
    stage8b_rows = tuple(row for row in store.special_rows if row.owner_id in PILOT_IDS)
    assert len(stage8b_rows) == 39
    assert {row.owner_id for row in stage8b_rows} == set(PILOT_IDS)
    assert store.family_rows[0].owner_id == "GFR_SELF_ACTION"
    for special_id in PILOT_IDS:
        assert special_id in knowledge.special
        candidates = store.candidates((special_id,))
        assert 3 <= len(candidates) <= 5
        assert all(candidate.canonical in knowledge.canonical for candidate in candidates)
        assert all(
            relation.support_class in {"CORE_SUPPORT", "OPTIONAL_VARIATION"}
            for candidate in candidates for relation in candidate.relations
        )


def test_pilot_identity_and_current_production_family_are_rechecked(knowledge, profile_store):
    expected_terms = {
        "161": "anal training", "416": "bdsm", "312": "sex machine",
        "325": "tentacle sex", "173": "double penetration",
        "16": "cooperative footjob", "385": "cumdrip from penis",
        "488": "xray sex", "88": "masturbation", "122": "missionary",
    }
    expected_family = {
        "161": "SEMANTIC_SUPPORT", "416": "CONTEXT_MODIFIER",
        "312": "MACHINE_STRUCTURED", "325": "NONHUMAN_INTERACTION",
        "173": "INSERTION_STRUCTURED", "16": "MULTI_ACTOR_INTERACTION",
        "385": "FLUID_STATE_ACTION", "488": "SEMANTIC_SUPPORT",
        "88": "SELF_ACTION", "122": "POSE_COMPOSITION",
    }
    for special_id, term in expected_terms.items():
        assert knowledge.special[special_id].term == term
        profile = profile_store.profiles[special_id]
        observed = profile.GenerationFamily or profile.MeaningStatus
        assert observed == expected_family[special_id]


@pytest.mark.parametrize(("field", "value", "message"), (
    ("special_id", "999999", "unknown special_id"),
    ("candidate_canonical", "not_a_real_canonical", "unknown candidate canonical"),
    ("support_slot", "NOT_A_SLOT", "invalid support_slot"),
    ("support_class", "NOT_A_CLASS", "invalid support_class"),
    ("intent_axis", "NOT_AN_AXIS", "invalid intent_axis"),
    ("intent_direction", "SIDEWAYS", "invalid intent_direction"),
    ("combination_mode", "MAGICAL", "invalid combination_mode"),
))
def test_special_profile_loader_rejects_invalid_identity_and_enums(
        tmp_path, knowledge, field, value, message):
    row = _production_row()
    row[field] = value
    path = tmp_path / "invalid.csv"
    _write_special_csv(path, [row])
    with pytest.raises(ValueError, match=message):
        load_special_support_profiles(path, knowledge)


def test_enabled_row_requires_support_class_and_duplicate_is_error(tmp_path, knowledge):
    row = _production_row()
    row["support_class"] = ""
    path = tmp_path / "missing_class.csv"
    _write_special_csv(path, [row])
    with pytest.raises(ValueError, match="requires support_class"):
        load_special_support_profiles(path, knowledge)

    row = _production_row()
    path = tmp_path / "duplicate.csv"
    _write_special_csv(path, [row, row])
    with pytest.raises(ValueError, match="duplicate candidate canonical"):
        load_special_support_profiles(path, knowledge)


@pytest.mark.parametrize("evidence_level", ("MODEL_OBSERVED", "USER_ENV_VERIFIED"))
def test_observed_evidence_requires_test_profile_and_model_scope(
        tmp_path, knowledge, evidence_level):
    row = _production_row()
    row["evidence_level"] = evidence_level
    row["test_profile_id"] = ""
    row["model_scope"] = ""
    path = tmp_path / "untraceable.csv"
    _write_special_csv(path, [row])
    with pytest.raises(ValueError, match="requires test_profile_id and model_scope"):
        load_special_support_profiles(path, knowledge)


def test_disabled_row_is_loaded_for_audit_but_hidden_at_runtime(
        tmp_path, knowledge, profile_store):
    row = _production_row()
    row["enabled"] = "false"
    row["support_class"] = ""
    path = tmp_path / "disabled.csv"
    _write_special_csv(path, [row])
    rows = load_special_support_profiles(path, knowledge)
    assert len(rows) == 1 and rows[0].enabled is False
    isolated = SupportKnowledgeStore(rows, (), profile_store)
    assert isolated.candidates((row["special_id"],)) == ()


def test_family_loader_requires_existing_stage6_family(tmp_path, knowledge, profile_store):
    row = _production_row()
    family_row = {"family_rule_id": "GFR_NOT_REAL", **{
        field: row[field] for field in PROFILE_FIELDS
    }}
    path = tmp_path / "family.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["family_rule_id", *PROFILE_FIELDS])
        writer.writeheader()
        writer.writerow(family_row)
    with pytest.raises(ValueError, match="unknown family_rule_id"):
        load_family_support_rules(path, knowledge, profile_store)


def test_no_profile_and_substring_never_generate_candidates(store, knowledge):
    no_profile = next(
        special_id for special_id, special in knowledge.special.items()
        if special_id not in PILOT_IDS and "anal" in special.term
    )
    assert store.candidates((no_profile,)) == ()
    assert store.candidates(()) == ()


def test_support_metadata_is_preserved_without_statistics_or_runtime_ranking(store):
    rows = store.candidates(("312",))
    assert [item.canonical for item in rows] == [
        "machine", "sex_toy", "dildo", "vibrator", "object_insertion"
    ]
    assert rows[0].relations[0].support_class == "CORE_SUPPORT"
    assert rows[2].relations[0].support_class == "OPTIONAL_VARIATION"
    assert rows[2].relations[0].combination_mode == "ALTERNATIVE"
    assert rows[2].relations[0].choice_group == "sex_machine_attachment"
    assert rows[2].relations[0].intent_axis == "SPECIFICITY"
    assert not ({"base_count", "co_count", "conditional_rate", "raw_lift"}
                & {field.name for field in fields(SemanticSupportCandidate)})


def test_union_deduplicates_and_special_profile_precedes_family(store, profile_store):
    explicit = next(row for row in store.special_rows
                    if row.owner_id == "312" and row.candidate_canonical == "machine")
    family_id = profile_store.profiles["312"].FamilyRuleId
    family_same = replace(
        explicit, owner_kind="family", owner_id=family_id,
        reason_ja="family reason must not replace explicit", priority=1,
    )
    family_other = replace(
        family_same, candidate_canonical="dildo", reason_ja="family-only candidate", priority=2,
    )
    isolated = SupportKnowledgeStore((explicit,), (family_same, family_other), profile_store)
    candidates = isolated.candidates(("312",))
    assert [item.canonical for item in candidates] == ["machine", "dildo"]
    machine = next(item for item in candidates if item.canonical == "machine")
    assert len(machine.relations) == 1
    assert machine.relations[0].reason_ja == explicit.reason_ja
    assert machine.relations[0].provenance.startswith("special:312")


@pytest.mark.parametrize(("selected", "canonical", "expected"), (
    (("161", "173"), "anus", {
        ("161", "CORE_SUPPORT", "ADDITIVE"),
        ("173", "OPTIONAL_VARIATION", "CONTEXTUAL"),
    }),
    (("312", "173"), "object_insertion", {
        ("312", "OPTIONAL_VARIATION", "CONTEXTUAL"),
        ("173", "CORE_SUPPORT", "ADDITIVE"),
    }),
    (("88", "122"), "on_back", {
        ("88", "OPTIONAL_VARIATION", "ALTERNATIVE"),
        ("122", "CORE_SUPPORT", "ADDITIVE"),
    }),
    (("173", "122"), "spread_legs", {
        ("173", "OPTIONAL_VARIATION", "CONTEXTUAL"),
        ("122", "CORE_SUPPORT", "ADDITIVE"),
    }),
))
def test_deduplicated_candidate_keeps_every_special_relation(
        store, selected, canonical, expected):
    forward = store.candidates(selected)
    reverse = store.candidates(tuple(reversed(selected)))
    candidate = next(item for item in forward if item.canonical == canonical)
    reverse_candidate = next(item for item in reverse if item.canonical == canonical)
    assert sum(item.canonical == canonical for item in forward) == 1
    assert {
        (relation.owner_special_id, relation.support_class, relation.combination_mode)
        for relation in candidate.relations
    } == expected
    assert candidate == reverse_candidate
    assert all(relation.reason_ja and relation.evidence_source
               for relation in candidate.relations)


def test_multi_relation_candidate_adds_manual_auxiliary_once(
        store, knowledge, profile_store):
    session = Stage7ASession(
        knowledge, Stage7AWarningPresenter(knowledge, profile_store)
    )
    assert session.add_special("88")
    assert session.add_special("122")
    candidate = next(
        item for item in store.candidates(session.selected_special_ids)
        if item.canonical == "on_back"
    )
    assert len(candidate.relations) == 2
    assert session.add_auxiliary(candidate.canonical)
    assert not session.add_auxiliary(candidate.canonical)
    assert session.manual_auxiliary_canonicals.count("on_back") == 1
    assert session.prompt_preview.count("on back") == 1


def test_support_is_read_only_until_manual_auxiliary_add(
        store, knowledge, profile_store):
    session = Stage7ASession(
        knowledge, Stage7AWarningPresenter(knowledge, profile_store)
    )
    assert session.add_special("161")
    original_ids = session.selected_special_ids
    original_prompt = session.prompt_preview
    candidates = store.candidates(session.selected_special_ids)
    assert session.selected_special_ids == original_ids
    assert session.prompt_preview == original_prompt
    assert session.automatic_injections == ()
    assert session.add_auxiliary(candidates[0].canonical)
    assert not session.add_auxiliary(candidates[0].canonical)
    assert session.selected_special_ids == original_ids
    assert session.prompt_preview.startswith("anal training, ")


def test_control_profiles_do_not_inject_unrelated_hard_direction(store):
    masturbation = {item.canonical for item in store.candidates(("88",))}
    missionary = {item.canonical for item in store.candidates(("122",))}
    assert masturbation == {"solo", "sitting", "on_back", "kneeling"}
    assert missionary == {"on_back", "lying", "spread_legs", "from_above", "sex"}
    unrelated = {"large_insertion", "multiple_penetration", "bondage", "tentacles"}
    assert not (masturbation & unrelated)
    assert not (missionary & unrelated)


def test_runtime_support_lookup_is_offline(monkeypatch, store):
    def fail(*args, **kwargs):
        raise AssertionError("network access is not allowed")

    monkeypatch.setattr("socket.create_connection", fail)
    assert store.candidates(("161",))
