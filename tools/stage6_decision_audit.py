"""Read-only Stage 6 evidence replay and bounded timing audit; no new ranking."""
import csv
from fractions import Fraction
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.runtime_index import RuntimeIndex
from danbooru_tag_tool.canonical_overlay import CanonicalOverlay
from danbooru_tag_tool.recommendations import RecommendationEngine, RANKING_METHODS
from tools.stage6_ranking_evaluation import split_candidates, top_summary


def timed(fn):
    fn()  # explicit warm-up, including logical posting cache
    samples = []
    for _ in range(3):
        start = time.perf_counter()
        fn()
        samples.append(1000 * (time.perf_counter() - start))
    return {"samples_ms": samples, "median_ms": statistics.median(samples)}


def main():
    folder = ROOT / "benchmarks/stage6"
    data = json.loads((folder / "ranking_evaluation.json").read_text(encoding="utf-8"))
    with (folder / "top20_by_method.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    paths = [ROOT / name for name in (
        "docs/stage_reports/RECOMMENDATION_RANKING_EVALUATION.md", "danbooru_tag_tool/recommendations.py",
        "tests/test_stage6_recommendations.py", "danbooru_tag_tool/canonical_overlay.py",
        "tools/stage6_ranking_evaluation.py", "benchmarks/stage6/ranking_evaluation.json",
        "benchmarks/stage6/top20_by_method.csv")]
    def hashes():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    before = hashes()
    stored_hashes = json.loads((folder / "input_hashes.json").read_text(encoding="utf-8"))
    for name, expected in stored_hashes.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    index = RuntimeIndex(ROOT / "data/runtime_index", expected_snapshot_id=data["snapshot_id"])
    assert data["total_posts"] == index.total_posts == 11218362
    overlay = CanonicalOverlay(index, ROOT / "data/runtime_index/canonical_overlay.json")
    overlay.validate()
    knowledge = TagKnowledgeCore.load(ROOT)
    engine = RecommendationEngine(overlay, knowledge)
    output = {"source_hashes": before, "recorded_input_hashes_match": True,
              "snapshot_id": index.snapshot_id, "csv_rows": len(rows), "cases": {}}
    assert len(rows) == 480
    for name, case in data["cases"].items():
        core = case["core"]
        candidates = engine.candidates(core)
        assert len(candidates) == case["candidate_count"]
        assert overlay.intersect(core).base_count == case["base_count"]
        ids = [[s.special_id for s in knowledge.special.values()
                if s.layer != "Semantic" and s.chosen_canonical == t] for t in core]
        assert all(ids) and len(set(core)) == len(core)
        for method in RANKING_METHODS:
            # Includes all raw fields, role, score, top20 order, and support metrics.
            assert top_summary(candidates, method) == case["methods"][method]
            selected = [r for r in rows if r["case"] == name and r["ranking_method"] == method]
            assert len(selected) == 20
            for csv_row, expected in zip(selected, case["methods"][method]["top20"]):
                for key, value in expected.items():
                    actual = csv_row[key]
                    assert (float(actual) == value) if isinstance(value, (int, float)) else actual == value
        # Independently check the raw-field equations and shrinkage identity.
        for row in candidates:
            assert row.canonical not in core and row.co_count <= row.base_count
            assert math.isclose(row.conditional_rate, row.co_count / row.base_count)
            assert math.isclose(row.global_rate, row.runtime_global_count / index.total_posts)
            assert math.isclose(row.raw_lift, row.conditional_rate / row.global_rate)
            assert math.isclose(row.shrunk_lift, (row.base_count * row.raw_lift + 20) / (row.base_count + 20))
        orders = {m: [r.canonical for r in engine.rank(candidates, m)] for m in RANKING_METHODS}
        # The proof concerns mathematical ordering; exact floating-point ties
        # may differ. Record full-list equality rather than assuming it.
        equal = {"rate_wilson": orders["conditional_rate"] == orders["wilson_lower_bound"],
                 "lift_shrunk": orders["raw_lift"] == orders["shrunk_lift"]}
        by_name = {r.canonical: r for r in candidates}
        def exact_lift_order_key(tag):
            r = by_name[tag]
            return Fraction(r.co_count, r.runtime_global_count)
        tie_only = all(exact_lift_order_key(a) == exact_lift_order_key(b)
                       for a, b in zip(orders["raw_lift"], orders["shrunk_lift"]))
        assert tie_only
        drops = engine.drop_one(core)
        assert [asdict(d) for d in drops] == case["drop_one"]
        target = case["combination_specificity_example"]["candidate"]
        diag = engine.combination_specificity(core, target)
        assert diag.full_conditional_rate == case["combination_specificity_example"]["full_conditional_rate"]
        assert dict(diag.singleton_conditional_rates) == case["combination_specificity_example"]["singleton_conditional_rates"]
        split = [split_candidates(engine, core, p) for p in (0, 1)]
        stability = {m: len(set(r.canonical for r in engine.rank(split[0], m)[:20]) &
                             set(r.canonical for r in engine.rank(split[1], m)[:20])) / 20
                     for m in RANKING_METHODS}
        assert stability == data["stability"][name]
        output["cases"][name] = {
            "core": core, "special_ids_per_core_item": ids,
            "all_candidate_order_equal": equal,
            "lift_full_list_differences_only_exact_rational_ties": tie_only,
            "replayed_statistics_top20_diagnostics_stability": "PASS",
            "warm_candidates_including_AND_aggregation_all_scores": timed(lambda: engine.candidates(core)),
            "warm_sort_only": {m: timed(lambda m=m: engine.rank(candidates, m)) for m in RANKING_METHODS},
            "warm_drop_one": timed(lambda: engine.drop_one(core)),
            "warm_specificity_one_candidate": timed(lambda: engine.combination_specificity(core, target)),
        }
        print(name, "PASS", flush=True)
    assert hashes() == before
    output["inputs_unchanged"] = True
    (folder / "decision_audit.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
