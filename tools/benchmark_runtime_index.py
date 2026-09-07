"""Measure Stage 5 runtime-open, AND, and reverse candidate aggregation."""
from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
import statistics
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from danbooru_tag_tool.runtime_index import RuntimeIndex


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t)]


def rss_bytes():
    counters = _ProcessMemoryCounters(); counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = (ctypes.c_void_p, ctypes.POINTER(_ProcessMemoryCounters), ctypes.c_ulong)
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        return None
    return int(counters.WorkingSetSize)


def percentile(values, p):
    return float(np.percentile(np.asarray(values, dtype=float), p))


def sample(index, operation, repeats=15):
    values = []
    for _ in range(repeats):
        start = time.perf_counter_ns(); operation(); values.append((time.perf_counter_ns() - start) / 1_000_000)
    return {"repeats": repeats, "median_ms": statistics.median(values), "p95_ms": percentile(values, 95), "samples_ms": values}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter(); index = RuntimeIndex(args.index); open_ms = (time.perf_counter() - start) * 1000
    counts = index.runtime_global_counts
    conditions = {}
    for target in (1, 100, 10_000, 100_000):
        candidate = int(np.argmin(np.abs(counts.astype(np.int64) - target)))
        conditions[f"base_target_{target}"] = [index.tags[candidate]]
    # A nonempty 2/3/5-tag core is constructed from an indexed post's own tags.
    seed = next(i for i in range(index.total_posts) if index.post_tag_offsets[i + 1] - index.post_tag_offsets[i] >= 5)
    start_offset, end_offset = index.post_tag_offsets[seed:seed + 2]
    core_tags = [index.tags[int(tag_id)] for tag_id in index.post_tag_ids[int(start_offset):int(end_offset)][:5]]
    and_conditions = {"and_1": core_tags[:1], "and_2": core_tags[:2], "and_3": core_tags[:3], "and_5": core_tags[:5]}
    results = {"open_ms": open_ms, "open_rss_bytes": rss_bytes(), "total_posts": index.total_posts, "conditions": {}, "notes": "Warm-process timings; short operations are repeated. mmap virtual size is not reported as RSS."}
    for name, tags in and_conditions.items():
        result = index.intersect(tags)
        results["conditions"][name] = {"tags": tags, "base_count": result.base_count, "and": sample(index, lambda: index.intersect(tags))}
    for name, tags in conditions.items():
        result = index.intersect(tags)
        and_stats = sample(index, lambda: index.intersect(tags))
        aggregate_stats = sample(index, lambda result=result, tags=tags: index.aggregate(result, exclude=tags))
        total_stats = sample(index, lambda tags=tags: index.aggregate(index.intersect(tags), exclude=tags))
        results["conditions"][name] = {"tags": tags, "base_count": result.base_count, "and": and_stats, "aggregation": aggregate_stats, "and_plus_aggregation": total_stats, "rss_after_aggregation_bytes": rss_bytes()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
