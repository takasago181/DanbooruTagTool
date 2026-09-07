import csv
import json
from pathlib import Path

from danbooru_tag_tool.japanese_overlay import JapaneseOverlay, JapaneseTerm, load_japanese_terms
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.search import TagSearchEngine


ROOT = Path(__file__).resolve().parents[1]


def test_schema_filters_candidate_and_rejected_from_runtime():
    terms = (
        JapaneseTerm("school_uniform", "制服", "display", "test"),
        JapaneseTerm("school_uniform", "学生服", "search", "test"),
        JapaneseTerm("school_uniform", "制服候補", "candidate", "test"),
        JapaneseTerm("school_uniform", "誤訳", "rejected", "test"),
    )
    overlay = JapaneseOverlay.from_terms(terms, {"school_uniform": object()})
    assert overlay.display_by_canonical["school_uniform"] == "制服"
    assert overlay.search_by_canonical["school_uniform"] == ("制服", "学生服")
    assert "制服候補" not in overlay.lookup()
    assert "誤訳" not in overlay.lookup()


def test_runtime_overlay_canonical_integrity_and_usage_counts():
    knowledge = TagKnowledgeCore.load(ROOT)
    terms = load_japanese_terms(ROOT / "data/japanese/japanese_terms.csv")
    overlay = knowledge.japanese_overlay
    assert set(overlay.search_by_canonical) <= set(knowledge.canonical)
    assert all(isinstance(term, str)
               for values in overlay.search_by_canonical.values() for term in values)
    assert sum(term.usage == "candidate" for term in terms) > 0
    assert sum(term.usage == "rejected" for term in terms) > 0
    audit = json.loads((ROOT / "benchmarks/stage6_5/japanese_import_audit.json").read_text(encoding="utf-8"))
    assert audit["terms"]["display"] == 0
    assert audit["runtime"]["term_count"] == audit["terms"]["search"]


def test_source_manifest_license_and_usage_counts():
    manifest = json.loads((ROOT / "data/japanese/japanese_sources.json").read_text(encoding="utf-8"))
    assert all(source["license"] for source in manifest["sources"])
    assert next(source for source in manifest["sources"]
                if source["source_id"] == "newtextdoc1111_alias_fdf2772")["license"] == "MIT"
    audit = json.loads((ROOT / "benchmarks/stage6_5/japanese_import_audit.json").read_text(encoding="utf-8"))
    for report in audit["sources"].values():
        counts = report["source_term_usage_counts"]
        assert set(counts) == {"display", "search", "candidate", "rejected"}
        assert all(isinstance(value, int) and value >= 0 for value in counts.values())


def test_alias_only_is_audit_only():
    audit = json.loads((ROOT / "benchmarks/stage6_5/japanese_import_audit.json").read_text(encoding="utf-8"))
    assert sum(item["alias_only_count"] for item in audit["sources"].values()) > 0
    terms = {(term.canonical_tag, term.ja_term) for term in load_japanese_terms(
        ROOT / "data/japanese/japanese_terms.csv")}
    examples = list(csv.DictReader((ROOT / "benchmarks/stage6_5/japanese_import_examples.csv").open(encoding="utf-8")))
    for row in examples:
        if row["disposition"] == "alias_only":
            assert not any(canonical == row["canonical_tag"] for canonical, _ in terms)


def test_examples_cover_audit_boundaries_without_runtime_leakage():
    rows = list(csv.DictReader((ROOT / "benchmarks/stage6_5/japanese_import_examples.csv").open(encoding="utf-8")))
    assert {row["usage"] for row in rows} >= {"search", "candidate", "rejected"}
    assert {row["disposition"] for row in rows} >= {"alias_only", "unmatched"}
    runtime = json.loads((ROOT / "data/runtime/japanese_overlay.json").read_text(encoding="utf-8"))
    runtime_terms = {term for entry in runtime["entries"].values() for term in entry["search_ja"]}
    for row in rows:
        if row["usage"] == "rejected" or row["disposition"] in {"alias_only", "unmatched"}:
            assert row["ja_term"] == "" or row["ja_term"] not in runtime_terms


def test_special_japanese_identity_and_stage4_order_are_preserved():
    with_overlay = TagKnowledgeCore.load(ROOT)
    without_overlay = TagKnowledgeCore.load(ROOT, japanese_overlay_path=ROOT / "missing-overlay.json")
    special = with_overlay.special["1"]
    assert special.japanese == without_overlay.special["1"].japanese
    assert TagSearchEngine(with_overlay).search_one(special.japanese)[0].canonical == \
        TagSearchEngine(without_overlay).search_one(special.japanese)[0].canonical
    for query in ("twintails", "sole_female", "long h", "ng hai", "hair", "a", "nagatoro"):
        old = TagSearchEngine(without_overlay).search_one(query, limit=100)
        new = TagSearchEngine(with_overlay).search_one(query, limit=100)
        assert [(item.canonical, item.match_type) for item in new] == \
            [(item.canonical, item.match_type) for item in old]


def test_overlay_lookup_provenance_and_rollback():
    knowledge = TagKnowledgeCore.load(ROOT)
    term = next(iter(knowledge.japanese_overlay.lookup()))
    result = TagSearchEngine(knowledge).search_one(term)[0]
    assert "japanese_overlay" in result.provenance
    old = TagKnowledgeCore.load(ROOT, japanese_overlay_path=ROOT / "missing-overlay.json")
    assert old.resolve_exact("school_uniform").match_type == "canonical"
    assert old.resolve_exact("sole_female").match_type == "alias"
