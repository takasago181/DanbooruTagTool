from dataclasses import asdict
from pathlib import Path

import pytest

from danbooru_tag_tool.recommendations import RecommendationCandidate
from danbooru_tag_tool.stage8a_semantics import (
    Stage8ASemantics, load_generation_hint_rules, load_semantic_labels,
)


ROOT = Path(__file__).resolve().parents[1]


def candidate(canonical, *, co=8, base=10, lift=2.0):
    return RecommendationCandidate(
        canonical=canonical,
        role="other",
        base_count=base,
        co_count=co,
        conditional_rate=co / base,
        runtime_global_count=100,
        global_rate=.1,
        raw_lift=lift,
        wilson_lower_bound=.2,
        shrunk_lift=1.5,
    )


@pytest.fixture(scope="module")
def semantics():
    return Stage8ASemantics.load(ROOT)


def test_production_sidecars_load_with_reviewed_counts_and_roles(semantics):
    assert len(semantics.labels) == 34
    assert len(semantics.rules) == 12
    expected = {
        "1girl": ("SUBJECT_BASIC", "人物・人数"),
        "ass": ("BODY_PART", "身体部位"),
        "sex_toy": ("IMPLEMENT", "器具・物体"),
        "object_insertion": ("ACTION_SUPPORT", "行為補強"),
        "on_back": ("POSE", "姿勢・体位"),
        "cross_section": ("CAMERA_COMPOSITION", "構図・見せ方"),
        "gaping": ("STATE_REACTION", "状態・反応"),
        "nude": ("APPEARANCE_CLOTHING", "外見・衣装"),
        "hetero": ("SITUATION_RELATION", "状況・関係"),
    }
    for canonical, (role, label) in expected.items():
        decorated = semantics.decorate(
            candidate(canonical), core_canonicals=("core",), bucket="common"
        )
        assert (decorated.semantic_role, decorated.semantic_label_ja) == (role, label)


def test_semantic_loader_rejects_invalid_role_and_duplicate_canonical(tmp_path):
    invalid = tmp_path / "invalid.csv"
    invalid.write_text(
        "canonical_tag,semantic_role,source,note\n1girl,NOT_A_ROLE,test,x\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid semantic_role"):
        load_semantic_labels(invalid)

    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text(
        "canonical_tag,semantic_role,source,note\n"
        "1girl,SUBJECT_BASIC,test,x\n1girl,SUBJECT_BASIC,test,y\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate canonical_tag"):
        load_semantic_labels(duplicate)


@pytest.mark.parametrize(("field", "old", "new", "message"), (
    ("role", "SUBJECT_BASIC", "NOT_A_ROLE", "invalid semantic role"),
    ("bucket", ",common,", ",sometimes,", "invalid bucket"),
    ("kind", ",CORE_BASIS,", ",NOT_A_KIND,", "invalid hint kind"),
))
def test_hint_loader_rejects_invalid_enums(tmp_path, field, old, new, message):
    source = (
        "rule_id,priority,when_semantic_role,when_same_stat_canonical,when_bucket,"
        "when_low_support,kind,message_ja,source,note\n"
        "rule,10,SUBJECT_BASIC,,common,,CORE_BASIS,説明,test,x\n"
    )
    path = tmp_path / f"invalid_{field}.csv"
    path.write_text(source.replace(old, new), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_generation_hint_rules(path)


def test_default_generation_hints(semantics):
    expected = {
        "1girl": ("CORE_BASIS", "生成の主体や人数を明示する基礎タグ"),
        "sex_toy": ("IMPLEMENT_SPECIFIER", "使用する器具・物体を明示しやすいタグ"),
        "object_insertion": (
            "ACTION_CLARIFIER", "選択中の内容をより具体的にしやすい行為補強タグ"
        ),
    }
    for canonical, hint in expected.items():
        decorated = semantics.decorate(
            candidate(canonical), core_canonicals=("core",), bucket="common"
        )
        assert (decorated.generation_hint_kind, decorated.generation_hint_ja) == hint


def test_generation_hint_and_evidence_notes_are_independent(semantics):
    body = semantics.decorate(
        candidate("breasts"), core_canonicals=("core",), bucket="common"
    )
    assert body.generation_hint_kind == "BODY_TARGET"
    assert body.generation_hint_ja == "対象部位を明示しやすいタグ"
    assert body.evidence_notes_ja == ()

    rare_classified = semantics.decorate(
        candidate("sex_toy", co=4), core_canonicals=("core",), bucket="rare"
    )
    assert rare_classified.generation_hint_kind == "IMPLEMENT_SPECIFIER"
    assert rare_classified.generation_hint_ja == "使用する器具・物体を明示しやすいタグ"
    assert rare_classified.evidence_note_kinds == ("DISCOVERY_CANDIDATE",)
    assert rare_classified.evidence_notes_ja == ("少し珍しい組み合わせの発見に向く候補",)

    rare_low = semantics.decorate(
        candidate("unclassified_tag", co=2),
        core_canonicals=("core",), bucket="rare",
    )
    assert rare_low.semantic_role == "UNCLASSIFIED"
    assert rare_low.semantic_label_ja is None
    assert rare_low.generation_hint_kind is None
    assert rare_low.generation_hint_ja is None
    assert rare_low.evidence_note_kinds == ("DISCOVERY_CANDIDATE",)
    assert rare_low.evidence_notes_ja == ("珍しい候補ですが、件数が少ないため偶然の可能性もあります",)

    same = semantics.decorate(
        candidate("anal_object_insertion"),
        core_canonicals=("anal_object_insertion",), bucket="rare",
    )
    assert same.relation_flags == ("SAME_STAT_CANONICAL",)
    assert same.generation_hint_kind == "ACTION_CLARIFIER"
    assert same.generation_hint_ja == "選択中の内容をより具体的にしやすい行為補強タグ"
    assert same.evidence_note_kinds == ("LOW_ADDITIONAL_VALUE", "DISCOVERY_CANDIDATE")
    assert same.evidence_notes_ja == (
        "選択済みSpecialと統計上同じタグです",
        "少し珍しい組み合わせの発見に向く候補",
    )


@pytest.mark.parametrize(("canonical", "kind", "message"), (
    ("ass", "BODY_TARGET", "対象部位を明示しやすいタグ"),
    ("gaping", "STATE_EXPRESSION", "状態や反応を表しやすいタグ"),
    ("nude", "APPEARANCE_BASIS", "外見や衣装を指定する基礎タグ"),
))
def test_common_role_does_not_imply_indirect_support(semantics, canonical, kind, message):
    decorated = semantics.decorate(
        candidate(canonical), core_canonicals=("core",), bucket="common"
    )
    assert decorated.generation_hint_kind == kind
    assert decorated.generation_hint_ja == message
    assert decorated.evidence_notes_ja == ()


def test_decoration_preserves_stage6_candidates_order_count_and_raw_values(semantics):
    rows = (
        candidate("1girl", co=9, base=10, lift=.8),
        candidate("adult_niche_example", co=1, base=10, lift=20),
        candidate("unclassified_example", co=3, base=10, lift=4),
    )
    decorated = semantics.decorate_many(
        rows, core_canonicals=("core",), bucket="rare"
    )
    assert len(decorated) == len(rows)
    assert [item.candidate.canonical for item in decorated] == [item.canonical for item in rows]
    assert [asdict(item.candidate) for item in decorated] == [asdict(item) for item in rows]
    assert decorated[1].candidate.co_count == 1
    assert decorated[2].semantic_role == "UNCLASSIFIED"


def test_semantic_runtime_is_local_and_offline(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("network access is not allowed")

    monkeypatch.setattr("socket.create_connection", fail)
    semantics = Stage8ASemantics.load(ROOT)
    assert semantics.decorate(
        candidate("1girl"), core_canonicals=("core",), bucket="common"
    ).generation_hint_ja
