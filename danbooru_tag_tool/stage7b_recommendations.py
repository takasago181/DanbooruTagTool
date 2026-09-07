"""Stage 7B UI adapter for the existing Stage 6 recommendation math.

This module deliberately does not define a new score.  It only runs the
existing :class:`RecommendationEngine` away from Tk's event loop and turns
its raw candidates into the two UI views required by Stage 7B.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
from typing import Callable, Iterable

from .recommendations import RecommendationCandidate, RecommendationEngine


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    request_id: int
    core_canonicals: tuple[str, ...]
    base_count: int | None
    common: tuple[RecommendationCandidate, ...] = ()
    rare: tuple[RecommendationCandidate, ...] = ()
    status: str = "ready"
    message: str = ""


class RecommendationController:
    """Debounced-by-caller, cached, stale-safe Stage 7B worker.

    Tk owns the debounce timer.  The controller owns request identity, the
    order-independent cache, and the background worker.  A callback receives
    only the newest request's result; an old worker completion is discarded.
    """

    def __init__(self, engine: RecommendationEngine | None,
                 *, max_common: int = 8, max_rare: int = 5):
        self.engine = engine
        self.max_common = max_common
        self.max_rare = max_rare
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="stage7b")
        self._cache: dict[tuple[str, ...], RecommendationResult] = {}
        self._lock = Lock()
        self._request_id = 0
        self._pending = None
        self._worker_running = False
        self._closed = False

    @staticmethod
    def cache_key(core_canonicals: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted(set(core_canonicals)))

    @property
    def request_id(self) -> int:
        with self._lock:
            return self._request_id

    def invalidate(self) -> int:
        """Invalidate an in-flight worker when the core is not computable."""
        with self._lock:
            self._request_id += 1
            self._pending = None
            return self._request_id

    def request(self, core_canonicals: Iterable[str], callback: Callable[[RecommendationResult], None]) -> int:
        key = self.cache_key(core_canonicals)
        with self._lock:
            if self._closed:
                raise RuntimeError("RecommendationController is closed")
            self._request_id += 1
            request_id = self._request_id
            cached = self._cache.get(key)
            immediate = None
            if not key:
                immediate = RecommendationResult(request_id, key, None, status="empty")
            elif self.engine is None:
                immediate = RecommendationResult(
                request_id, key, None, status="unavailable",
                message="関連候補を利用できません。Promptにはそのまま使用できます。",
                )
            elif cached is not None:
                immediate = RecommendationResult(request_id, key, cached.base_count,
                                                 cached.common, cached.rare,
                                                 cached.status, cached.message)
            if immediate is not None:
                self._pending = None
                start_worker = False
            else:
                # There is intentionally only one queued slot.  A running job
                # may finish, while B/C are overwritten and only latest D runs.
                self._pending = (request_id, key, callback)
                start_worker = not self._worker_running
                if start_worker:
                    self._worker_running = True
        if immediate is not None:
            callback(immediate)
            return request_id
        if start_worker:
            self._executor.submit(self._drain_latest)
        return request_id

    def _calculate(self, request_id: int, key: tuple[str, ...]) -> RecommendationResult:
        try:
            raw = self.engine.candidates(key)
            base_count = raw[0].base_count if raw else self.engine.overlay.intersect(key).base_count
            common = RecommendationEngine.rank(raw, "conditional_rate")[:self.max_common]
            rare = RecommendationEngine.rank(raw, "raw_lift")[:self.max_rare]
            return RecommendationResult(request_id, key, int(base_count), common, rare)
        except (KeyError, ValueError):
            return RecommendationResult(
                request_id, key, None, status="unavailable",
                message="このSpecial組み合わせでは関連候補を計算できません。Promptにはそのまま使用できます。",
            )
        except Exception:
            # Recommendation failure must not disable search, Prompt, or copy.
            return RecommendationResult(
                request_id, key, None, status="error",
                message="関連候補を表示できません。Promptはそのまま使用できます。",
            )

    def _drain_latest(self):
        while True:
            with self._lock:
                pending = self._pending
                self._pending = None
                if pending is None or self._closed:
                    self._worker_running = False
                    return
            request_id, key, callback = pending
            result = self._calculate(request_id, key)
            with self._lock:
                self._cache[key] = result
                deliver = request_id == self._request_id and not self._closed
            if deliver:
                callback(result)

    def close(self):
        with self._lock:
            self._closed = True
            self._pending = None
        self._executor.shutdown(wait=False, cancel_futures=True)
