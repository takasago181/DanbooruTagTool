"""Stage 2 reproducible benchmark for true AND and candidate aggregation.

This is deliberately a prototype runner.  It never writes a production index
and it only reads the Stage 1 approved, revision-pinned Parquet source.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import os
import pickle
import statistics
import subprocess
import sys
import time
import urllib.request
from array import array
from collections import Counter
from io import RawIOBase
from pathlib import Path
from typing import Iterable

import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "stage2"
APPROVED_URL = (
    "https://huggingface.co/datasets/nyanko-devs/danbooru2026/resolve/"
    "ebb02a630201c7b51487e45fb90b3fcf4cbedc20/metadata/posts-snapshot.parquet"
)
POPULATION_RULE = "is_deleted IS NOT TRUE"


def rss_bytes(peak: bool = False) -> int:
    """Windows process working set, including native Arrow allocations."""
    class COUNTERS(ctypes.Structure):
        # PROCESS_MEMORY_COUNTERS_EX is required here: passing the shortened
        # prefix causes GetProcessMemoryInfo to fail on Windows.
        _fields_ = [
            ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]
    counters = COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    memory_info = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
    memory_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(COUNTERS), wintypes.DWORD]
    memory_info.restype = wintypes.BOOL
    if not memory_info(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(counters.PeakWorkingSetSize if peak else counters.WorkingSetSize)


class HttpRangeFile(RawIOBase):
    """Small read-only seekable HTTP file for pyarrow; fetches only requested ranges."""
    def __init__(self, url: str):
        self.url, self.pos, self.size = url, 0, None

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos

    def seek(self, offset, whence=0):
        if whence == 0: self.pos = offset
        elif whence == 1: self.pos += offset
        elif whence == 2:
            if self.size is None: self._length()
            self.pos = self.size + offset
        else: raise ValueError("invalid whence")
        return self.pos

    def _length(self):
        req = urllib.request.Request(self.url, headers={"Range": "bytes=0-0"})
        with urllib.request.urlopen(req) as response:
            self.size = int(response.headers["Content-Range"].split("/")[-1])

    def readinto(self, buffer):
        if not buffer: return 0
        end = self.pos + len(buffer) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        with urllib.request.urlopen(req) as response:
            data = response.read()
        count = len(data)
        buffer[:count] = data
        self.pos += count
        return count


def extract_subset(path: Path, max_id: int) -> dict:
    """Extract the approved population into a small JSONL benchmark fixture."""
    started, before = time.perf_counter(), rss_bytes()
    source = pq.ParquetFile(HttpRangeFile(APPROVED_URL))
    rows = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as out:
        # The source is ID-ordered.  Stop only after a row group whose minimum ID
        # exceeds max_id; filtering remains explicit so the selection is auditable.
        for group in range(source.metadata.num_row_groups):
            meta = source.metadata.row_group(group).column(0).statistics
            if meta and meta.min is not None and int(meta.min) > max_id:
                break
            table = source.read_row_group(group, columns=["id", "is_deleted", "tag_string_general"])
            for post_id, deleted, tags in zip(
                table["id"].to_pylist(), table["is_deleted"].to_pylist(),
                table["tag_string_general"].to_pylist(), strict=True
            ):
                if post_id <= max_id and deleted is not True:
                    out.write(json.dumps({"id": post_id, "tags": tags or ""}, separators=(",", ":")) + "\n")
                    rows += 1
    return {"rows": rows, "elapsed_seconds": time.perf_counter() - started,
            "peak_rss_bytes": rss_bytes(True), "rss_delta_bytes": rss_bytes() - before,
            "population_rule": POPULATION_RULE, "max_post_id": max_id}


def load_posts(path: Path):
    with path.open(encoding="utf-8") as stream:
        return [(r["id"], r["tags"].split() if r["tags"] else [])
                for r in map(json.loads, stream)]


def build(posts, bidirectional: bool):
    names: dict[str, int] = {}
    postings: list[list[int]] = []
    post_tags: list[array] | None = [] if bidirectional else None
    for ordinal, (_, tags) in enumerate(posts):
        ids = array("I")
        for tag in tags:
            tag_id = names.setdefault(tag, len(names))
            if tag_id == len(postings): postings.append([])
            postings[tag_id].append(ordinal)
            if bidirectional: ids.append(tag_id)
        if bidirectional: post_tags.append(ids)
    return {"names": names, "postings": [array("I", x) for x in postings], "post_tags": post_tags}


def build_from_jsonl(path: Path, bidirectional: bool):
    """Streaming variant so build peak does not retain a second raw-post copy."""
    names: dict[str, int] = {}
    postings: list[list[int]] = []
    post_tags: list[array] | None = [] if bidirectional else None
    with path.open(encoding="utf-8") as stream:
        for ordinal, line in enumerate(stream):
            record = json.loads(line)
            ids = array("I")
            for tag in record["tags"].split():
                tag_id = names.setdefault(tag, len(names))
                if tag_id == len(postings): postings.append([])
                postings[tag_id].append(ordinal)
                if bidirectional: ids.append(tag_id)
            if bidirectional: post_tags.append(ids)
    return {"names": names, "postings": [array("I", x) for x in postings], "post_tags": post_tags, "post_count": ordinal + 1}


def intersect(a: Iterable[int], b: Iterable[int]) -> array:
    result, i, j = array("I"), 0, 0
    while i < len(a) and j < len(b):
        left, right = a[i], b[j]
        if left == right: result.append(left); i += 1; j += 1
        elif left < right: i += 1
        else: j += 1
    return result


def and_posts(index, tags: list[str]) -> array:
    lists = sorted((index["postings"][index["names"][tag]] for tag in tags), key=len)
    base = array("I", lists[0])
    for posting in lists[1:]: base = intersect(base, posting)
    return base


def aggregate_forward(index, base: array, selected: set[int]) -> dict[int, int]:
    # A posting-only index has no post->tag traversal.  It must discover every
    # candidate by scanning every posting; a transient base hash set prevents a
    # quadratic repeated merge while preserving that architectural constraint.
    base_set = set(base)
    counts = {}
    for tag_id, posting in enumerate(index["postings"]):
        if tag_id not in selected:
            count = sum(post in base_set for post in posting)
            if count: counts[tag_id] = count
    return counts


def aggregate_bidir(index, base: array, selected: set[int]) -> dict[int, int]:
    counts = Counter()
    for post in base:
        counts.update(tag for tag in index["post_tags"][post] if tag not in selected)
    return dict(counts)


def select_queries(index):
    # Deterministic one-tag base-size conditions; exact achieved sizes are recorded.
    tag_by_id = [None] * len(index["names"])
    for name, tag_id in index["names"].items(): tag_by_id[tag_id] = name
    conditions = {}
    for target in (1, 100, 10_000, 100_000):
        tag_id = min(range(len(tag_by_id)), key=lambda n: abs(len(index["postings"][n]) - target))
        conditions[str(target)] = [tag_by_id[tag_id]]
    popular = sorted(range(len(tag_by_id)), key=lambda n: len(index["postings"][n]), reverse=True)
    and_queries = {"1": [tag_by_id[popular[0]]]}
    used = set(and_queries["1"])
    for count in (2, 3, 5):
        query = []
        for tag_id in popular:
            if tag_by_id[tag_id] not in used:
                query.append(tag_by_id[tag_id])
                if len(query) == count: break
        and_queries[str(count)] = query
    return conditions, and_queries


def median_seconds(action, repeat=5):
    values = []
    for _ in range(repeat):
        started = time.perf_counter(); action(); values.append(time.perf_counter() - started)
    return statistics.median(values)


def bench(index, architecture):
    conditions, and_queries = select_queries(index)
    and_times = {n: median_seconds(lambda q=q: and_posts(index, q)) for n, q in and_queries.items()}
    aggregation = {}
    for target, query in conditions.items():
        base, selected = and_posts(index, query), {index["names"][tag] for tag in query}
        fn = aggregate_bidir if architecture == "bidirectional" else aggregate_forward
        aggregation[target] = {"query": query, "base_count": len(base),
                               "seconds_median_5": median_seconds(lambda: fn(index, base, selected))}
    return {"and_seconds_median_5": and_times, "candidate_aggregation": aggregation}


def index_path(name: str) -> Path: return OUT / f"{name}.pickle"


def child_build(args):
    before, started = rss_bytes(), time.perf_counter()
    index = build_from_jsonl(Path(args.input), args.architecture == "bidirectional")
    build_seconds, peak = time.perf_counter() - started, rss_bytes(True)
    with index_path(args.architecture).open("wb") as out: pickle.dump(index, out, protocol=5)
    payload = {"architecture": args.architecture, "build_seconds": build_seconds,
               "build_peak_rss_bytes": peak, "build_rss_delta_bytes": rss_bytes() - before,
               "index_size_bytes": index_path(args.architecture).stat().st_size,
               "tag_count": len(index["names"]), "post_count": index.pop("post_count"), **bench(index, args.architecture)}
    print(json.dumps(payload))


def child_open(args):
    started = time.perf_counter()
    with index_path(args.architecture).open("rb") as stream: index = pickle.load(stream)
    print(json.dumps({"cold_open_seconds": time.perf_counter() - started,
                      "resident_rss_bytes": rss_bytes(), "loaded_tag_count": len(index["names"])}))


def run(args):
    OUT.mkdir(parents=True, exist_ok=True)
    input_path = OUT / "approved_a_id_1_1000000_not_deleted.jsonl"
    result_path = OUT / "results.json"
    if args.extract or not input_path.exists():
        prep = extract_subset(input_path, 1_000_000)
    elif result_path.exists():
        prep = json.loads(result_path.read_text(encoding="utf-8")).get("preprocessing", {"reused": True})
    else:
        prep = {"reused": True}
    results = {"approved_source": "nyanko-devs/danbooru2026", "revision": "ebb02a630201c7b51487e45fb90b3fcf4cbedc20",
               "population_rule": POPULATION_RULE, "subset": "1 <= id <= 1,000,000", "preprocessing": prep, "architectures": {}}
    for name in ("forward_only", "bidirectional"):
        build_result = subprocess.run([sys.executable, __file__, "build", "--input", str(input_path), "--architecture", name],
                                       check=True, capture_output=True, text=True)
        open_result = subprocess.run([sys.executable, __file__, "open", "--architecture", name],
                                      check=True, capture_output=True, text=True)
        results["architectures"][name] = {**json.loads(build_result.stdout), **json.loads(open_result.stdout)}
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run"); runner.add_argument("--extract", action="store_true")
    build_p = sub.add_parser("build"); build_p.add_argument("--input", required=True); build_p.add_argument("--architecture", required=True, choices=("forward_only", "bidirectional"))
    open_p = sub.add_parser("open"); open_p.add_argument("--architecture", required=True, choices=("forward_only", "bidirectional"))
    args = parser.parse_args()
    if args.command == "run": run(args)
    elif args.command == "build": child_build(args)
    else: child_open(args)


if __name__ == "__main__": main()
