"""Reproducible Stage 6 evaluation; writes only benchmarks/stage6/."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from danbooru_tag_tool.canonical_overlay import CanonicalOverlay
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.recommendations import RANKING_METHODS, RecommendationEngine
from danbooru_tag_tool.runtime_index import RuntimeIndex

OUT = ROOT / "benchmarks" / "stage6"
# These are recorded Stage-5 actual Special combinations, deliberately chosen
# to cover two, three, and five Special Core conditions without precomputing
# all pairs/triples.
CASES = {
    "two_special_small": ("clothed_female_nude_male", "genderswap"),
    "two_special_medium": ("erection", "open_clothes"),
    "three_special_small": ("bare_legs", "completely_nude", "uncensored"),
    "three_special_medium": ("ass", "facial", "penis"),
    "five_special_small": ("drooling", "ejaculation", "hetero", "see-through_clothes", "sex"),
    "five_special_medium": ("breasts", "covered_nipples", "groping", "pussy", "spread_legs"),
}


def serialise(candidate):
    return {field: getattr(candidate, field) for field in candidate.__dataclass_fields__}


def top_summary(candidates, method):
    ranked = RecommendationEngine.rank(candidates, method)[:20]
    supports = [row.co_count for row in ranked]
    return {
        "top20": [serialise(row) | {"ranking_method": method, "ranking_score": row.score(method)} for row in ranked],
        "co_count_le_1": sum(value <= 1 for value in supports),
        "co_count_le_5": sum(value <= 5 for value in supports),
        "co_count_le_10": sum(value <= 10 for value in supports),
        "high_lift_low_support": sum(row.raw_lift >= 5 and row.co_count <= 10 for row in ranked),
        "large_support": sum(row.co_count >= 100 for row in ranked),
        "broad_global_rate_ge_10pct": sum(row.global_rate >= .10 for row in ranked),
    }


def split_candidates(engine, core, parity):
    base = engine.overlay.intersect(core)
    selected = base.post_ordinals[engine.overlay.index.post_ids[base.post_ordinals] % 2 == parity]
    if not len(selected):
        return ()
    counts = engine.overlay.aggregate(selected, exclude=core)
    total = len(selected)
    output = []
    for row in engine.candidates(core):
        co = counts.get(row.canonical, 0)
        if not co:
            continue
        # Ranking only needs coherent split conditional values; global snapshot
        # values intentionally remain the same snapshot population.
        output.append(row.__class__(row.canonical, row.role, total, co, co / total,
                                    row.runtime_global_count, row.global_rate,
                                    (co / total) / row.global_rate, __import__("danbooru_tag_tool.recommendations", fromlist=["wilson_lower_bound"]).wilson_lower_bound(co, total),
                                    __import__("danbooru_tag_tool.recommendations", fromlist=["support_aware_shrunk_lift"]).support_aware_shrunk_lift(co, total, row.global_rate)))
    return tuple(output)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = RuntimeIndex(ROOT / "data/runtime_index")
    overlay = CanonicalOverlay(index, ROOT / "data/runtime_index/canonical_overlay.json")
    knowledge = TagKnowledgeCore.load(ROOT)
    engine = RecommendationEngine(overlay, knowledge)
    result = {"snapshot_id": index.snapshot_id, "total_posts": index.total_posts, "cases": {}, "stability": {}}
    flat_rows = []
    for name, core in CASES.items():
        candidates, elapsed = engine.timed_candidates(core)
        drops = engine.drop_one(core)
        details = {"core": list(core), "base_count": candidates[0].base_count if candidates else 0,
                   "candidate_count": len(candidates), "ranking_overhead_ms": elapsed,
                   "drop_one": [row.__dict__ if hasattr(row, "__dict__") else {key: getattr(row, key) for key in row.__dataclass_fields__} for row in drops],
                   "methods": {}}
        for method in RANKING_METHODS:
            summary = top_summary(candidates, method)
            details["methods"][method] = summary
            for row in summary["top20"]:
                flat_rows.append({"case": name} | row)
        # Combination diagnostic for the raw-lift leader: diagnostic only.
        leader = RecommendationEngine.rank(candidates, "raw_lift")[0] if candidates else None
        if leader:
            diagnostic = engine.combination_specificity(core, leader)
            details["combination_specificity_example"] = {
                "candidate": diagnostic.canonical, "full_conditional_rate": diagnostic.full_conditional_rate,
                "singleton_conditional_rates": dict(diagnostic.singleton_conditional_rates),
            }
        result["cases"][name] = details
        left, right = split_candidates(engine, core, 0), split_candidates(engine, core, 1)
        result["stability"][name] = {
            method: len({r.canonical for r in RecommendationEngine.rank(left, method)[:20]} &
                        {r.canonical for r in RecommendationEngine.rank(right, method)[:20]}) / 20
            for method in RANKING_METHODS
        }
    (OUT / "ranking_evaluation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT / "top20_by_method.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat_rows[0]))
        writer.writeheader(); writer.writerows(flat_rows)
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [
        ROOT / "data/runtime_index/canonical_overlay.json", ROOT / "data/runtime_index/BUILD_MANIFEST.json",
        ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv",
    ]}
    (OUT / "input_hashes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({name: data["base_count"] for name, data in result["cases"].items()}))


if __name__ == "__main__":
    main()
