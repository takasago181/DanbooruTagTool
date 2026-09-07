"""Run from project root: python -m tools.stage4_search_benchmark.

Measures complete search_one calls (including scan, ranking and dedup), not
isolated lookups. Outputs JSON to stdout; never changes source data.
"""
import json
import math
import platform
import statistics
from pathlib import Path
from time import perf_counter

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.search import TagSearchEngine


def main():
    started = perf_counter()
    knowledge = TagKnowledgeCore.load(Path(__file__).resolve().parents[1])
    loaded = perf_counter()
    engine = TagSearchEngine(knowledge)
    initialized = perf_counter()
    queries = [
        ("canonical exact", "twintails", "twintails", "canonical"),
        ("alias exact", "sole_female", "1girl", "alias"),
        ("Japanese exact", knowledge.special["1"].japanese, "anus", "japanese"),
        ("prefix", "long h", "long_hair", "prefix"),
        ("partial", "ng hai", "long_hair", "partial"),
        ("partial broad", "hair", None, None),
        ("partial short stress", "a", None, None),
    ]
    samples = {label: [] for label, *_ in queries}
    for label, query, canonical, match_type in queries:
        result = engine.search_one(query)
        if canonical is not None:
            assert any(r.canonical == canonical and r.match_type == match_type
                       for r in result), (label, query)
        for _ in range(20):
            engine.search_one(query)
    # Interleave queries to reduce drift bias. GC stays enabled, default limit=50.
    for _ in range(200):
        for label, query, *_ in queries:
            start = perf_counter()
            engine.search_one(query)
            samples[label].append((perf_counter() - start) * 1000)
    report = {
        "python": platform.python_version(), "platform": platform.platform(),
        "canonical_count": len(knowledge.canonical),
        "special_count": len(knowledge.special), "semantic_count": len(knowledge.semantic),
        "alias_keys": len(knowledge.aliases), "translations": len(knowledge.translations),
        "entry_count": len(engine._entries),
        "load_ms": round((loaded - started) * 1000, 3),
        "search_init_ms": round((initialized - loaded) * 1000, 3),
        "warmups_per_query": 20, "iterations_per_query": 200, "limit": 50,
        "queries": [{
            "type": label, "query": query,
            "median_ms": round(statistics.median(samples[label]), 3),
            "p95_ms": round(sorted(samples[label])[math.ceil(len(samples[label]) * .95) - 1], 3),
        } for label, query, *_ in queries],
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
