"""Independent PyArrow ground truth for the finished Stage 5 index."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from danbooru_tag_tool.runtime_index import RuntimeIndex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    index = RuntimeIndex(args.index, verify_hashes=True)
    counts = index.runtime_global_counts
    target_tags = [index.tags[int(abs(counts.astype('int64') - target).argmin())] for target in (1, 100, 10_000, 100_000)]
    seed = next(i for i in range(index.total_posts) if index.post_tag_offsets[i + 1] - index.post_tag_offsets[i] >= 5)
    a, b, c, d, e = [index.tags[int(x)] for x in index.post_tag_ids[index.post_tag_offsets[seed]:index.post_tag_offsets[seed + 1]][:5]]
    queries = {"one": (a,), "two": (a, b), "three": (a, b, c), "five": (a, b, c, d, e), "small": (target_tags[0],), "medium": (target_tags[2],), "large": (target_tags[3],)}
    direct = {name: {"posts": [], "counts": Counter()} for name in queries}
    globals_direct = Counter()
    reader = pq.ParquetFile(args.source)
    for batch in reader.iter_batches(batch_size=65_536, columns=["id", "is_deleted", "tag_string_general"]):
        for row in batch.to_pylist():
            if row["is_deleted"] is True:
                continue
            tags = tuple(row["tag_string_general"].split()) if row["tag_string_general"] else ()
            globals_direct.update(tags)
            tag_set = set(tags)
            for name, query in queries.items():
                if set(query) <= tag_set:
                    direct[name]["posts"].append(int(row["id"]))
                    direct[name]["counts"].update(tags)
    report = {"pass": True, "queries": {}, "global_count_match": True}
    for tag, count in globals_direct.items():
        if tag in index.tag_to_id and int(index.runtime_global_counts[index.tag_id(tag)]) != count:
            report["global_count_match"] = False
    for name, query in queries.items():
        actual = index.intersect(query)
        actual_counts = index.aggregate(actual, exclude=query)
        expected_counts = {tag: value for tag, value in direct[name]["counts"].items() if tag not in query}
        passed = actual.post_ids.tolist() == direct[name]["posts"] and actual_counts == expected_counts
        report["queries"][name] = {"tags": query, "base_count": actual.base_count, "pass": passed}
        report["pass"] &= passed
    report["pass"] &= report["global_count_match"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
