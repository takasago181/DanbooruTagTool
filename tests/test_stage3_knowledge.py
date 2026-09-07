import csv
from collections import Counter
from dataclasses import asdict, fields
from pathlib import Path

import pytest

from danbooru_tag_tool.knowledge import (
    TagKnowledgeCore, load_aliases, load_canonical, load_semantic,
)
from danbooru_tag_tool.models import (
    AUXILIARY_ROLES, AuxiliaryTag, CanonicalTag, CoreTagSet, LoRA,
    SemanticCandidate, Translation,
)
from danbooru_tag_tool.normalization import normalize_lookup, split_prompt_input
from danbooru_tag_tool.prompt_formatter import PromptFormatter

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


def test_canonical_snapshot_and_prompt(knowledge):
    assert len(knowledge.canonical) == 124016
    tag = knowledge.canonical["school_uniform"]
    assert tag.lookup_key == "school uniform"
    assert knowledge.resolve_exact(" ＳＣＨＯＯＬ_ uniform ").resolved_canonical == "school_uniform"
    assert PromptFormatter.format_tag(tag).text == "school uniform"
    assert tag.canonical_tag == "school_uniform"
    assert "runtime_global_count" not in {f.name for f in fields(tag)}


def test_normalization_and_token_boundaries():
    assert normalize_lookup(" ＬＯＮＧ_  HAIR\t") == "long hair"
    assert split_prompt_input("school uniform, long_hair\r\n1girl") == ("school uniform", "long_hair", "1girl")


def test_normalized_alias_collision_keeps_both_targets(knowledge):
    assert len(knowledge.aliases) == 34416
    assert sum(len(v) > 1 for v in knowledge.aliases.values()) == 45
    result = knowledge.resolve_exact("nagatoro")
    assert set(result.canonical_candidates) == {"ijiranaide_nagatoro-san", "nagatoro_hayase"}
    assert result.resolved_canonical is None


def test_all_stage3_input_hashes_unchanged():
    import hashlib
    import json
    manifest = json.loads((ROOT / "FILE_HASHES.json").read_text(encoding="utf-8"))
    for name in ("data/derived/special2788_VERIFIED_LINKAGE.csv",
                 "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
                 "data/semantic/semantic_bridge_v1.csv",
                 "data/derived/special2788_translation_review_candidates_676.csv"):
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == manifest[name]["sha256"]


def test_all_verified_aliases_and_precedence(knowledge):
    with (ROOT / "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 34417
    assert sum(int(r["TargetCount"]) > 1 for r in rows) == 44
    assert sum(bool(r["CanonicalPrecedenceTag"]) for r in rows) == 140
    for row in rows:
        result = knowledge.resolve_exact(row["NormalizedAlias"])
        if row["CanonicalPrecedenceTag"]:
            assert result.resolved_canonical == row["CanonicalPrecedenceTag"]
        elif int(row["TargetCount"]) > 1:
            assert result.resolved_canonical is None
        else:
            assert row["CanonicalTargets"] in result.canonical_candidates
    assert knowledge.resolve_exact("sole_female").resolved_canonical == "1girl"
    assert knowledge.resolve_exact("cum on leg").resolved_canonical is None
    assert knowledge.resolve_exact("descensored").resolved_canonical is None
    assert knowledge.special["1578"].chosen_canonical == "uncensored"


def test_special_snapshot(knowledge):
    tags = list(knowledge.special.values())
    assert len(tags) == 2788
    assert Counter(t.layer for t in tags) == {"Core": 759, "Extended": 915, "Alias": 778, "Semantic": 336}
    assert Counter(t.match_type for t in tags) == {
        "canonical": 1674, "alias_unique": 767, "alias_ambiguous_curated": 2,
        "alias_ambiguous_multiple": 9, "semantic_unmapped": 336,
    }
    assert sum(t.chosen_canonical is not None for t in tags) == 2443
    assert all(t.is_special for t in tags)
    assert knowledge.resolve_exact(tags[0].japanese).special_ids


def test_semantic_unmapped_and_exact(knowledge):
    assert len(knowledge.semantic) == 336
    assert all(s.candidate_canonical is None for s in knowledge.semantic.values())
    assert not any("count" in f.name for f in fields(SemanticCandidate))
    item = knowledge.semantic["SEM0001"]
    for term in (item.semantic_term, item.ja_label):
        result = knowledge.resolve_exact(term)
        assert item.semantic_id in result.semantic_ids
        assert result.resolved_canonical is None


def test_japanese_resolution_uses_special_to_semantic_lookup(knowledge):
    special = knowledge.special["4"]
    assert knowledge.special_to_semantic_ids["4"] == ("SEM0001",)
    # Proves the Japanese branch does not scan self.semantic.values().
    core = TagKnowledgeCore(knowledge.canonical, knowledge.aliases, knowledge.special, knowledge.semantic)
    core.semantic = ()
    result = core.resolve_exact(special.japanese)
    assert result.semantic_ids == ("SEM0001",)


def write_semantic(tmp_path, rows):
    path = tmp_path / "semantic.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.mark.parametrize("change", [
    {"relation_type": "fake"}, {"review_status": "APPROVED"},
    {"candidate_canonical": "missing", "relation_type": "related"},
    {"candidate_canonical": "school_uniform"}, {"special_id": "missing"},
    {"post_count": "100"}, {"relation_type": "related"},
])
def test_semantic_rejects_invalid_rows(knowledge, tmp_path, change):
    row = asdict(knowledge.semantic["SEM0001"])
    row.update(change)
    with pytest.raises(ValueError):
        load_semantic(write_semantic(tmp_path, [row]), knowledge.canonical, knowledge.special)


def test_semantic_duplicate_and_multiple_candidates(knowledge, tmp_path):
    row = asdict(knowledge.semantic["SEM0001"])
    with pytest.raises(ValueError):
        load_semantic(write_semantic(tmp_path, [row, row]), knowledge.canonical, knowledge.special)
    row.update(candidate_canonical="school_uniform", relation_type="related", review_status="UNREVIEWED")
    other = dict(row, semantic_id="SEM0001-C2", candidate_canonical="long_hair", review_status="REJECTED")
    loaded = load_semantic(write_semantic(tmp_path, [row, other]), knowledge.canonical, knowledge.special)
    assert len(loaded) == 2
    core = TagKnowledgeCore(knowledge.canonical, {}, knowledge.special, loaded)
    assert core.resolve_exact(row["semantic_term"]).resolved_canonical is None


def core_fields():
    return dict(core_set_id="core-1", core_set_name="核", special_tag_ids=["1", "4"],
                memo="", created_at="2026-09-05T12:00:00+09:00")


def test_core_roundtrip_and_boundaries(knowledge):
    core = knowledge.create_core_set(**core_fields())
    assert CoreTagSet.from_json(core.to_json(knowledge.special), knowledge.special) == core
    assert core.special_tag_ids == ("1", "4")  # Unmapped Special is still a valid Core member.
    auxiliary = AuxiliaryTag(knowledge.canonical["school_uniform"])
    assert auxiliary.role == "other"
    assert {"body", "action"} <= AUXILIARY_ROLES
    assert AuxiliaryTag(knowledge.canonical["long_hair"], "body").role == "body"
    assert AuxiliaryTag(knowledge.canonical["holding"], "action").role == "action"
    assert isinstance(LoRA("example"), LoRA)


@pytest.mark.parametrize("role", ["device", "restraint", "fluid", "contact", "anatomy"])
def test_auxiliary_role_rejects_unapproved_subroles(knowledge, role):
    with pytest.raises(ValueError):
        AuxiliaryTag(knowledge.canonical["school_uniform"], role)


@pytest.mark.parametrize("change", [
    {"special_tag_ids": ["1", "1"]}, {"special_tag_ids": ["school_uniform"]},
    {"special_tag_ids": []}, {"special_tag_ids": "1"}, {"special_tag_ids": [1]},
    {"created_at": "yesterday"}, {"core_set_name": " "},
])
def test_core_invalid(knowledge, change):
    with pytest.raises(ValueError):
        knowledge.create_core_set(**(core_fields() | change))


def test_loaders_reject_corruption(tmp_path):
    path = tmp_path / "tags.csv"
    path.write_text("a,0,1,\na,0,2,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_canonical(path)
    path.write_text("NormalizedAlias,CanonicalTargets,TargetCount\nx,missing,1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_aliases(path, {"a": CanonicalTag("a", 0, 1)})


def test_translation_boundary_and_priority(knowledge):
    translations = [Translation("long_hair", "長い髪", "test-seed", "UNREVIEWED"),
                    Translation("long_hair", "school_uniform", "test-seed", "UNREVIEWED")]
    core = TagKnowledgeCore(knowledge.canonical, knowledge.aliases, knowledge.special, knowledge.semantic, translations)
    assert core.resolve_exact("長い髪").resolved_canonical == "long_hair"
    assert core.resolve_exact("school_uniform").resolved_canonical == "school_uniform"
    assert knowledge.translations == ()


@pytest.mark.parametrize("change", [
    {"canonical_tag": ""}, {"canonical_tag": "  "},
    {"japanese": ""}, {"japanese": "  "},
    {"translation_status": "APPROVED"},
])
def test_translation_rejects_invalid_required_values(change):
    fields = {
        "canonical_tag": "long_hair",
        "japanese": "長い髪",
        "translation_source": "test-seed",
        "translation_status": "UNREVIEWED",
    } | change
    with pytest.raises(ValueError):
        Translation(**fields)


def test_translation_rejects_unknown_canonical(knowledge):
    translation = Translation("not_a_canonical", "未知", "test-seed", "UNREVIEWED")
    with pytest.raises(ValueError, match="Unknown translation canonical"):
        TagKnowledgeCore(knowledge.canonical, knowledge.aliases, knowledge.special, knowledge.semantic, [translation])
