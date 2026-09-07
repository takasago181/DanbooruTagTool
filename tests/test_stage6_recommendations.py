import json

import pytest

from danbooru_tag_tool.canonical_overlay import CanonicalOverlay, OVERLAY_FORMAT_VERSION
from danbooru_tag_tool.models import CanonicalTag
from danbooru_tag_tool.recommendations import (
    RecommendationEngine, support_aware_shrunk_lift, wilson_lower_bound,
)
from danbooru_tag_tool.runtime_index import RuntimeIndex
from tests.test_stage5_runtime_index import make_index, SNAPSHOT


class Knowledge:
    def __init__(self):
        self.canonical = {
            "a": CanonicalTag("a", 0, 999999), "b": CanonicalTag("b", 0, 999999),
            "c": CanonicalTag("c", 0, 999999), "d": CanonicalTag("d", 0, 999999),
            "non_general": CanonicalTag("non_general", 4, 999999),
        }


def make_overlay(tmp_path):
    directory = make_index(tmp_path)
    document = {
        "metadata": {"overlay_format_version": OVERLAY_FORMAT_VERSION,
                     "statistics_dataset_snapshot_id": SNAPSHOT},
        "source_tag_identities": [
            {"source_tag": "a", "identity": "exact_current_general", "canonical": "a"},
            {"source_tag": "b", "identity": "exact_current_general", "canonical": "b"},
            {"source_tag": "c", "identity": "unique_alias_to_current_general", "canonical": "c"},
            {"source_tag": "d", "identity": "runtime_only", "canonical": None},
        ],
        "canonical_to_source_tag_ids": {"a": [0], "b": [1], "c": [2]},
    }
    path = directory / "canonical_overlay.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return CanonicalOverlay(RuntimeIndex(directory), path)


def test_raw_statistics_and_core_and_runtime_only_exclusion(tmp_path):
    engine = RecommendationEngine(make_overlay(tmp_path), Knowledge())
    candidates = engine.candidates(["a", "b"])
    assert [item.canonical for item in candidates] == ["c"]
    item = candidates[0]
    assert item.base_count == 3 and item.co_count == 1
    assert item.conditional_rate == pytest.approx(1 / 3)
    assert item.runtime_global_count == 3 and item.global_rate == pytest.approx(3 / 5)
    assert item.raw_lift == pytest.approx(5 / 9)
    assert item.role == "other"


def test_wilson_shrinkage_edge_cases_and_ranking():
    assert wilson_lower_bound(0, 0) == 0
    assert wilson_lower_bound(0, 100) == 0
    assert wilson_lower_bound(1, 1) < 1
    assert support_aware_shrunk_lift(0, 100, 0.5) > 0
    assert support_aware_shrunk_lift(1, 1, 0.01) < 100  # raw lift is 100
    with pytest.raises(ValueError):
        wilson_lower_bound(2, 1)
    with pytest.raises(ValueError):
        support_aware_shrunk_lift(1, 0, 0.1)


def test_drop_one_and_combination_specificity(tmp_path):
    engine = RecommendationEngine(make_overlay(tmp_path), Knowledge())
    drops = engine.drop_one(["a", "b", "c"])
    assert [(row.canonical, row.full_base_count, row.without_base_count) for row in drops] == [
        ("a", 1, 2), ("b", 1, 2), ("c", 1, 3),
    ]
    specificity = engine.combination_specificity(["a", "b"], "c")
    assert specificity.full_conditional_rate == pytest.approx(1 / 3)
    assert dict(specificity.singleton_conditional_rates) == {"a": pytest.approx(1 / 2), "b": pytest.approx(1 / 2)}


def test_alias_logical_merge_deduplicates_and_semantic_is_never_candidate(tmp_path):
    overlay = make_overlay(tmp_path)
    document = json.loads(overlay.path.read_text(encoding="utf-8"))
    # Make c an alias union of two raw source tags.  Source b appears alongside
    # a in two posts, so its contribution must be counted per post only once.
    document["source_tag_identities"][1]["canonical"] = "c"
    document["canonical_to_source_tag_ids"] = {"a": [0], "c": [1, 2]}
    overlay.path.write_text(json.dumps(document), encoding="utf-8")
    merged = CanonicalOverlay(RuntimeIndex(tmp_path), overlay.path)
    engine = RecommendationEngine(merged, Knowledge())
    candidate = engine.candidates(["a"])[0]
    assert candidate.canonical == "c" and candidate.co_count == 4
    with pytest.raises(ValueError, match="General"):
        engine.candidates(["non_general"])
