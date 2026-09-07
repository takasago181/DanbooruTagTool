from threading import Event
import time

from danbooru_tag_tool.recommendations import RecommendationCandidate, RecommendationEngine
from danbooru_tag_tool.stage7b_recommendations import RecommendationController


def candidate(name, *, co=4, base=10, lift=2.0):
    return RecommendationCandidate(name, "other", base, co, co / base, 100, .01,
                                   lift, .1, lift)


class FakeEngine:
    def __init__(self):
        self.calls = []
        self.started = Event()
        self.release = Event()

    def candidates(self, core):
        self.calls.append(tuple(core))
        self.started.set()
        self.release.wait(2)
        return (candidate("common"), candidate("rare", co=1, lift=9.0))


class StaticEngine:
    def __init__(self, rows):
        self.rows = tuple(rows)

    def candidates(self, core):
        return self.rows


def wait_for(results):
    deadline = time.time() + 3
    while time.time() < deadline and not results:
        time.sleep(.01)
    assert results


def test_cache_key_is_order_independent_and_views_use_existing_metrics():
    engine = FakeEngine()
    controller = RecommendationController(engine, max_common=1, max_rare=1)
    results = []
    try:
        controller.request(("b", "a"), results.append)
        engine.release.set()
        wait_for(results)
        first = results[-1]
        assert first.core_canonicals == ("a", "b")
        assert first.common[0].canonical == "common"
        assert first.rare[0].canonical == "rare"
        controller.request(("a", "b"), results.append)
        assert len(engine.calls) == 1
        assert results[-1].request_id != first.request_id
    finally:
        controller.close()


def test_queued_stale_work_is_coalesced_and_only_latest_runs():
    engine = FakeEngine()
    controller = RecommendationController(engine)
    results = []
    try:
        controller.request(("a",), results.append)
        assert engine.started.wait(1)
        controller.request(("b",), results.append)
        controller.request(("c",), results.append)
        controller.request(("d",), results.append)
        engine.release.set()
        wait_for(results)
        assert engine.calls == [("a",), ("d",)]
        assert all(result.core_canonicals == ("d",) for result in results)
    finally:
        controller.close()


def test_empty_or_missing_engine_keeps_prompt_path_available():
    controller = RecommendationController(None)
    results = []
    try:
        controller.request((), results.append)
        assert results[-1].status == "empty"
        controller.request(("a",), results.append)
        assert results[-1].status == "unavailable"
    finally:
        controller.close()


def test_stage7b_views_are_exact_stage6_metric_orders_and_raw_objects():
    rows = (
        candidate("1girl", co=9, lift=.8),
        candidate("solo", co=8, lift=1.1),
        candidate("adult_example", co=3, lift=4.0),
        candidate("niche_example", co=1, lift=20.0),
    )
    controller = RecommendationController(StaticEngine(rows), max_common=20, max_rare=20)
    results = []
    try:
        controller.request(("core",), results.append)
        wait_for(results)
        result = results[0]
        assert result.common == RecommendationEngine.rank(rows, "conditional_rate")
        assert result.rare == RecommendationEngine.rank(rows, "raw_lift")
        assert set(result.common) == set(rows)
        assert set(result.rare) == set(rows)
        assert result.common[0].base_count == rows[0].base_count
        assert result.common[0].co_count == rows[0].co_count
        assert result.common[0].conditional_rate == rows[0].conditional_rate
        assert {row.canonical for row in result.rare} >= {
            "1girl", "solo", "adult_example", "niche_example"
        }
    finally:
        controller.close()
