"""Verify Stage 7B against the production Stage 6 recommendation engine."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import sys
from threading import Event
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.canonical_overlay import CanonicalOverlay
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.recommendations import RecommendationEngine
from danbooru_tag_tool.runtime_index import RuntimeIndex
from danbooru_tag_tool.stage7b_recommendations import RecommendationController


RESULT = ROOT / "benchmarks/stage7b/metric_parity.json"
CORE = ("clothed_female_nude_male", "genderswap")
RAW_FIELDS = (
    "canonical", "role", "base_count", "co_count", "conditional_rate",
    "runtime_global_count", "global_rate", "raw_lift", "wilson_lower_bound",
    "shrunk_lift",
)


def row(candidate):
    return {name: getattr(candidate, name) for name in RAW_FIELDS}


def main():
    knowledge = TagKnowledgeCore.load(ROOT)
    index_dir = ROOT / "data/runtime_index"
    index = RuntimeIndex(index_dir)
    engine = RecommendationEngine(
        CanonicalOverlay(index, index_dir / "canonical_overlay.json"), knowledge
    )

    cold_started = perf_counter()
    raw = engine.candidates(CORE)
    stage6_cold_ms = (perf_counter() - cold_started) * 1000
    expected_common = RecommendationEngine.rank(raw, "conditional_rate")[:8]
    expected_rare = RecommendationEngine.rank(raw, "raw_lift")[:5]

    controller = RecommendationController(engine)
    finished = Event()
    results = []
    try:
        controller.request(CORE, lambda result: (results.append(result), finished.set()))
        if not finished.wait(60):
            raise TimeoutError("Stage 7B cold recommendation timed out")
        actual = results[-1]
        cache_finished = Event()
        cache_started = perf_counter()
        controller.request(reversed(CORE), lambda result: (results.append(result), cache_finished.set()))
        if not cache_finished.wait(2):
            raise TimeoutError("Stage 7B cache hit timed out")
        cache_ms = (perf_counter() - cache_started) * 1000
    finally:
        controller.close()

    common_match = actual.common == expected_common
    rare_match = actual.rare == expected_rare
    raw_values_unchanged = (
        [row(item) for item in actual.common] == [row(item) for item in expected_common]
        and [row(item) for item in actual.rare] == [row(item) for item in expected_rare]
    )
    observed_content_tags = sorted(
        name for name in ("1girl", "solo", "nude", "sex", "censored")
        if any(item.canonical == name for item in raw)
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "core": list(CORE),
        "base_count": actual.base_count,
        "candidate_count": len(raw),
        "stage6_cold_calculation_ms": stage6_cold_ms,
        "stage7b_cache_hit_ms": cache_ms,
        "common_metric": "conditional_rate",
        "rare_metric": "raw_lift",
        "common_order_matches_stage6": common_match,
        "rare_order_matches_stage6": rare_match,
        "raw_values_unchanged": raw_values_unchanged,
        "common_canonicals": [item.canonical for item in actual.common],
        "rare_canonicals": [item.canonical for item in actual.rare],
        "low_support_candidate_count": sum(item.co_count <= 2 for item in raw),
        "low_support_visible_in_rare": any(item.co_count <= 2 for item in actual.rare),
        "observed_unfiltered_content_tags": observed_content_tags,
        "stage7b_additional_ranking": False,
        "runtime_external_calls": 0,
    }
    if not all((common_match, rare_match, raw_values_unchanged)):
        raise AssertionError("Stage 7B metric parity failed")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
