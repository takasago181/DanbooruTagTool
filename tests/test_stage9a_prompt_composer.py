"""Stage9 specification section 14 and safe input-boundary regressions."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.prompt_composer import (
    BLOCK_ORDER, ComposerInput, ComposerProfile, NegativeRule, PromptComposer, SupportOverride,
)
from danbooru_tag_tool.prompt_formatter import PromptFormatter
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def store(knowledge):
    return SupportKnowledgeStore.load(ROOT, knowledge, knowledge.load_generation_profile_store(ROOT))


@pytest.fixture(scope="module")
def composer(knowledge, store):
    return PromptComposer(knowledge, store)


def atom(result, canonical):
    return next(a for a in result.plan.candidate_atoms if a.canonical == canonical)


def codes(result):
    return {warning.code for warning in result.warnings}


def synthetic(knowledge, store, rows, specials=None):
    # A separate knowledge container prevents production fixture mutation.
    k = TagKnowledgeCore(knowledge.canonical, knowledge.aliases,
                         specials or knowledge.special, {})
    return PromptComposer(k, SupportKnowledgeStore(rows, (), SimpleNamespace(profiles={})))


def row(store, sid="311", canonical="solo", **changes):
    template = next(r for r in store.special_rows if r.owner_id == "88" and r.candidate_canonical == "solo")
    return replace(template, owner_id=sid, candidate_canonical=canonical, **changes)


def test_01_special_survives_generic_support(composer, knowledge):
    result = composer.compose(("312",))
    assert result.plan.selected_special_ids == ("312",)
    assert PromptFormatter.format_special(knowledge.special["312"]).text in result.positive_prompt
    assert "machine" in result.provenance_map
    assert result.provenance_map["sex machine"].special_owners == ("312",)


def test_02_same_special_identity_dedupes(composer):
    result = composer.compose(("88", "88"))
    assert result.plan.selected_special_ids == ("88",)
    assert result.positive_prompt.split(", ").count("masturbation") == 1


def test_03_shared_support_keeps_all_relations(composer):
    result = composer.compose(("161", "173"))
    a = result.provenance_map["anus"]
    assert {r.owner_special_id for r in a.support_relations} == {"161", "173"}
    assert {r.support_class for r in a.support_relations} == {"CORE_SUPPORT", "OPTIONAL_VARIATION"}
    assert result.positive_prompt.split(", ").count("anus") == 1


def test_04_explicit_id88_precedes_family(composer):
    a = atom(composer.compose(("88",)), "solo")
    assert a.selected and len(a.support_relations) == 1
    assert a.support_relations[0].source_kind == "special"
    assert a.support_relations[0].support_class == "CORE_SUPPORT"
    assert a.support_relations[0].combination_mode == "ADDITIVE"


def test_05_family_optional_contextual_is_only_suggested(composer):
    result = composer.compose(("85",))
    a = atom(result, "solo")
    assert not a.selected and a.support_relations[0].source_kind == "family"
    assert "solo" not in result.provenance_map


def test_06_unresolved_special_only(composer):
    result = composer.compose(("311",))
    assert result.positive_prompt == "riding machine"
    assert len(result.plan.selected_atoms) == 1


def test_07_no_core_additive_count_cap(knowledge, store):
    names = ("solo", "anus", "penis", "feet", "sitting", "nude", "sex", "blush")
    core = synthetic(knowledge, store, [row(store, canonical=c, priority=i) for i, c in enumerate(names)])
    result = core.compose(("311",))
    assert len(result.plan.selected_atoms) == len(names) + 1


def test_08_alternatives_require_choice_and_multiple_warn(composer):
    initial = composer.compose(("312",))
    assert not atom(initial, "dildo").selected and not atom(initial, "vibrator").selected
    chosen = composer.compose(("312",), overrides=(SupportOverride("dildo", "INCLUDE"),
                                                   SupportOverride("vibrator", "INCLUDE")))
    assert "CHOICE_GROUP_MULTIPLE" in codes(chosen)
    assert {"dildo", "vibrator"} <= chosen.provenance_map.keys()


def test_09_exact_negative_collision_non_destructive(composer):
    negative = "SOLO\n bad_hands, nsfw"
    result = composer.compose(("88",), negative_prompt=negative)
    assert "POSITIVE_NEGATIVE_EXACT" in codes(result)
    assert result.negative_prompt == negative and "solo" in result.provenance_map


def test_10_adult_negative_rule_is_profile_aware(composer):
    profile = ComposerProfile(negative_rule_set=(NegativeRule("project_adult", "GENERIC"),))
    result = composer.compose(("311",), negative_prompt="nsfw", adult_intent=True, profile=profile)
    assert "ADULT_NEGATIVE_CONFLICT" in codes(result)
    assert "ADULT_NEGATIVE_CONFLICT" not in codes(composer.compose(
        ("311",), negative_prompt="nsfw", adult_intent=False, profile=profile))


def test_11_anima_rule_cannot_leak(composer):
    rule = NegativeRule("synthetic_anima_rule", "ANIMA", profile_id="anima_test")
    anima = ComposerProfile("anima_test", "ANIMA", negative_rule_set=(rule,))
    wai = ComposerProfile("wai_test", "WAI_ILLUSTRIOUS", negative_rule_set=(rule,))
    assert "ADULT_NEGATIVE_CONFLICT" in codes(composer.compose(
        ("311",), profile=anima, negative_prompt="nsfw", adult_intent=True))
    wrong = composer.compose(("311",), profile=wai, negative_prompt="nsfw", adult_intent=True)
    assert "RULE_SCOPE_MISMATCH" in codes(wrong)
    assert "ADULT_NEGATIVE_CONFLICT" not in codes(wrong)
    assert "PROFILE_SCOPE_MISMATCH" in codes(composer.compose(
        ("311",), profile=anima, model_family="WAI_ILLUSTRIOUS"))


def test_12_baseline_block_order(composer):
    result = composer.compose(("311",), inputs=(
        ComposerInput("identity", text="character", block="IDENTITY"),
        ComposerInput("relation", text="relation token", block="RELATION"),
        ComposerInput("count", canonical="2girls", block="COUNT"),
    ))
    assert result.block_order == BLOCK_ORDER
    assert result.positive_prompt == "2girls, relation token, character, riding machine"


def test_13_profile_moves_special_without_semantic_changes(composer):
    result = composer.compose(("88",), profile=ComposerProfile(special_slot_position=9))
    assert result.block_order[-1] == "SPECIAL"
    assert result.positive_prompt.endswith("masturbation")
    assert atom(result, "solo").selected


def test_14_explicit_exclusion_records_reason(composer):
    result = composer.compose(("88",), overrides=(SupportOverride("solo", "EXCLUDE", "user decision"),))
    a = atom(result, "solo")
    assert not a.selected and a.user_override == "EXCLUDE" and a.reason == "user decision"
    assert "solo" not in result.provenance_map


def test_15_conflicting_include_retained(composer):
    result = composer.compose(("85",), overrides=(SupportOverride("solo", "INCLUDE"),),
                              negative_prompt="solo")
    assert atom(result, "solo").user_override == "INCLUDE"
    assert "solo" in result.provenance_map and "POSITIVE_NEGATIVE_EXACT" in codes(result)


def test_16_support_satisfied_by_special_preserves_provenance(knowledge, store):
    special = replace(knowledge.special["311"], term="solo")
    core = synthetic(knowledge, store, [row(store)], {"311": special})
    result = core.compose(("311",))
    assert result.positive_prompt == "solo"
    assert result.provenance_map["solo"].special_owners == ("311",)
    assert len(result.provenance_map["solo"].support_relations) == 1
    assert result.plan.suppressed_atoms[0].reason == "satisfied_by_special"


def test_17_repeat_determinism(composer):
    assert composer.compose(("173", "161", "312")) == composer.compose(("173", "161", "312"))


def test_18_no_network_or_llm_runtime(monkeypatch, composer):
    def forbidden(*args, **kwargs):
        raise AssertionError("Runtime network forbidden")
    monkeypatch.setattr("socket.socket", forbidden)
    monkeypatch.setattr("socket.create_connection", forbidden)
    assert composer.compose(("88",)).positive_prompt
    source = (ROOT / "danbooru_tag_tool/prompt_composer.py").read_text(encoding="utf-8")
    assert not any(name in source for name in ("import requests", "import openai", "urllib", "httpx"))


def test_distinct_specials_same_token_keep_both_identities(knowledge, store):
    specials = {sid: replace(knowledge.special[sid], term="same token") for sid in ("311", "312")}
    result = synthetic(knowledge, store, [], specials).compose(("312", "311", "312"))
    assert result.plan.selected_special_ids == ("312", "311")
    assert result.positive_prompt == "same token"
    assert result.provenance_map["same token"].special_owners == ("312", "311")


def test_alias_inputs_use_authority_and_ambiguous_alias_rejected(knowledge, composer):
    alias, targets = next((a, ts) for a, ts in knowledge.aliases.items()
                          if len(ts) == 1 and a not in knowledge.canonical_lookup)
    result = composer.compose((), inputs=(ComposerInput("alias", canonical=alias),
                                         ComposerInput("canonical", canonical=targets[0])))
    assert len(result.plan.selected_atoms) == 1
    ambiguous = next(a for a, ts in knowledge.aliases.items()
                     if len(ts) > 1 and a not in knowledge.canonical_lookup)
    with pytest.raises(ValueError):
        composer.compose((), inputs=(ComposerInput("ambiguous", canonical=ambiguous),))


def test_lora_separate_and_negative_passthrough(composer):
    result = composer.compose(("311",), inputs=(
        ComposerInput("style", text="artist style"),
        ComposerInput("lora", text="<lora:test:0.8>", block="LORA"),
    ), negative_prompt="artist style")
    assert result.positive_prompt == "riding machine, artist style, <lora:test:0.8>"
    assert "POSITIVE_NEGATIVE_EXACT" in codes(result)
    assert all(a.weight is None for a in result.plan.candidate_atoms)


def test_user_order_and_lane_evidence_are_preserved(composer):
    evidence = (("co_count", 2), ("base_count", 3), ("conditional_rate", 2/3), ("snapshot", "test"))
    result = composer.compose(("311",), inputs=(
        ComposerInput("b", text="b token"), ComposerInput("a", text="a token"),
        ComposerInput("stats", canonical="solo", lane="COOCCURRENCE", selected=False, evidence=evidence),
    ))
    assert result.positive_prompt.endswith("b token, a token")
    assert atom(result, "solo").evidence == evidence
    assert not atom(result, "solo").selected


def test_optional_support_satisfied_by_explicit_input(composer):
    result = composer.compose(("85",), inputs=(ComposerInput("solo", canonical="solo"),))
    assert len(result.provenance_map["solo"].support_relations) == 1
    assert "SEMANTIC_OPTIONAL" in result.provenance_map["solo"].source_lanes


def test_invalid_inputs_fail_clearly(composer):
    with pytest.raises(ValueError):
        composer.compose(("unknown",))
    with pytest.raises(ValueError):
        composer.compose(("311",), overrides=(SupportOverride("solo", "INCLUDE"),))
    with pytest.raises(ValueError):
        ComposerProfile(block_order=("SPECIAL",))
    with pytest.raises(ValueError):
        ComposerInput("fake_special", text="x", block="SPECIAL")


@pytest.mark.parametrize("lane", ("SEMANTIC_AUX", "COOCCURRENCE", "SEMANTIC_OPTIONAL"))
def test_supplied_suggestion_lanes_default_off(composer, lane):
    result = composer.compose(("311",), inputs=(ComposerInput("suggestion", canonical="solo", lane=lane),))
    assert result.positive_prompt == "riding machine"
    assert not atom(result, "solo").selected
