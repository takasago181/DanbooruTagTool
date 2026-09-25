#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from codex_runtime import allowed_forward_end, load_runtime, read_csv

ROOT = Path(__file__).resolve().parents[2]


def validated_snapshot() -> dict:
    result = subprocess.run(
        [sys.executable, "scripts/issue132/validate_flat_pass_a.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise SystemExit("flat validator failed:\n" + result.stdout[-12000:])
    marker = "FLAT_SNAPSHOT_JSON="
    for line in result.stdout.splitlines():
        if line.startswith(marker):
            snapshot = json.loads(line[len(marker):])
            break
    else:
        raise SystemExit("flat validator did not emit snapshot")

    blocking = {
        "invalid_window_count": snapshot.get("invalid_window_count", 0),
        "duplicate_coverage_count": snapshot.get("duplicate_coverage_count", 0),
        "qa_watermark_violation_count": snapshot.get("qa_watermark_violation_count", 0),
        "fatal_contract_error_count": snapshot.get("fatal_contract_error_count", 0),
    }
    if any(blocking.values()):
        raise SystemExit("forward work blocked by current validation: " + json.dumps(blocking))
    return snapshot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if args.limit < 1 or args.limit > 100:
        raise SystemExit("--limit must be 1..100")

    authority, _, qa, runtime_errors = load_runtime(ROOT)
    if runtime_errors:
        raise SystemExit("runtime errors: " + "; ".join(runtime_errors))

    snapshot = validated_snapshot()
    lane_key = str(args.lane)
    frontier = snapshot["frontiers"][lane_key]
    allowed = allowed_forward_end(qa, args.lane)
    lane_length = int(authority["fixed"]["lane_lengths"][lane_key])

    if frontier is None:
        packet = {
            "schema_version": "issue132-codex-work-packet-v1",
            "lane": args.lane,
            "status": "LANE_COMPLETE",
            "rows": [],
        }
    elif frontier > allowed:
        packet = {
            "schema_version": "issue132-codex-work-packet-v1",
            "lane": args.lane,
            "status": "QA_GATE",
            "frontier": frontier,
            "qa_allowed_forward_end": allowed,
            "rows": [],
        }
    else:
        end = min(frontier + args.limit - 1, allowed, lane_length)
        neutral = read_csv(ROOT / authority["fixed"]["neutral_path"])
        assigned = [
            row
            for row in neutral
            if ((int(row["review_seq"]) - 1) % 3) + 1 == args.lane
        ]
        rows = []
        for idx in range(frontier, end + 1):
            source = assigned[idx - 1]
            surfaces = source.get("source_surfaces", "")
            try:
                surfaces = json.loads(surfaces)
            except Exception:
                pass
            rows.append({
                "lane_local_index": idx,
                "review_seq": int(source["review_seq"]),
                "identity_key": source["identity_key"],
                "source_surfaces": surfaces,
            })

        packet = {
            "schema_version": "issue132-codex-work-packet-v1",
            "lane": args.lane,
            "status": "READY",
            "lane_local_start": frontier,
            "lane_local_end": end,
            "count": len(rows),
            "qa_allowed_forward_end": allowed,
            "rows": rows,
        }

    text = json.dumps(packet, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(json.dumps({
            "status": packet["status"],
            "lane": args.lane,
            "count": len(packet["rows"]),
            "out": args.out,
        }, ensure_ascii=False))
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
