#!/usr/bin/env python3
"""Render tracked Issue #180 Forward dispatch snapshots from the current generated campaign queue."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGNS = ROOT / "artifacts/issue180-v3/parallel_authority_campaigns_v2.csv"
SOURCE_LEDGER = ROOT / "docs/issue180/parallel/SOURCE_REVIEW_LEDGER_V2.csv"
TRACKED_DIR = ROOT / "docs/issue180/parallel/dispatch"
DEFAULT_PACKET_LIMIT = 200

FIELDS = [
    "queue_id",
    "campaign_id",
    "owner_slot",
    "owner_branch",
    "campaign_key",
    "campaign_fingerprint",
    "research_state",
    "work_buckets",
    "member_count",
    "member_ids/tags",
    "source_units",
    "priority",
    "source_hint_urls",
    "source_hint_review_ids",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_campaign_keys(raw: str) -> list[str]:
    try:
        value = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid campaign_keys JSON in source ledger: {raw!r}") from exc
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise SystemExit(f"campaign_keys must be a JSON string list: {raw!r}")
    return value


def accepted_source_hints(source_rows: list[dict[str, str]]) -> dict[str, list[tuple[str, str]]]:
    hints: dict[str, list[tuple[str, str]]] = {}
    for row in source_rows:
        if row.get("review_status") != "ACCEPTED":
            continue
        for key in parse_campaign_keys(row.get("campaign_keys", "")):
            hints.setdefault(key, []).append((row["source_review_id"], row["source_url"]))
    return hints


def build_rows(
    campaigns: list[dict[str, str]], source_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    hints = accepted_source_hints(source_rows)
    out: list[dict[str, str]] = []
    for row in campaigns:
        if row.get("owner_role") != "FORWARD":
            continue
        key = row["campaign_key"]
        matched = sorted(set(hints.get(key, []) + hints.get("*", [])))
        urls = [u for _, u in matched]
        review_ids = [rid for rid, _ in matched]
        out.append(
            {
                "queue_id": row["queue_id"],
                "campaign_id": row["campaign_id"],
                "owner_slot": row["owner_slot"],
                "owner_branch": row["owner_branch"],
                "campaign_key": key,
                "campaign_fingerprint": row["campaign_fingerprint"],
                "research_state": row["research_state"],
                "work_buckets": row["work_buckets"],
                "member_count": row["member_count"],
                "member_ids/tags": row["member_ids/tags"],
                "source_units": row["source_units"],
                "priority": row["priority"],
                "source_hint_urls": json.dumps(urls, ensure_ascii=False, separators=(",", ":")),
                "source_hint_review_ids": json.dumps(review_ids, ensure_ascii=False, separators=(",", ":")),
            }
        )
    return sorted(
        out,
        key=lambda r: (
            int(r["owner_slot"]),
            r["research_state"] != "OPEN",
            {"P1": 1, "P2": 2, "P3": 3}.get(r["priority"], 9),
            -int(r["member_count"]),
            r["campaign_key"],
        ),
    )


def render(rows: list[dict[str, str]]) -> str:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def expected_files(rows: list[dict[str, str]], packet_limit: int = DEFAULT_PACKET_LIMIT) -> dict[str, str]:
    files: dict[str, str] = {}
    summary = {
        "queue_ids": sorted({r["queue_id"] for r in rows}),
        "packet_limit_per_lane": packet_limit,
        "total_forward_campaigns": len(rows),
        "total_open_campaigns": sum(r["research_state"] == "OPEN" for r in rows),
        "lanes": {},
    }
    for slot in range(4):
        lane_all = [r for r in rows if r["owner_slot"] == str(slot)]
        lane_open = [r for r in lane_all if r["research_state"] == "OPEN"]
        packet = lane_open[:packet_limit]
        files[f"fwd-{slot}.csv"] = render(packet)
        summary["lanes"][str(slot)] = {
            "total_campaigns": len(lane_all),
            "open_campaigns": len(lane_open),
            "dispatched_open_campaigns": len(packet),
        }
    files["DISPATCH_SUMMARY_V2.json"] = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return files


def write_dir(root: Path, files: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (root / name).write_text(content, encoding="utf-8", newline="")


def check_tracked(files: dict[str, str]) -> None:
    errors: list[str] = []
    for name, expected in files.items():
        path = TRACKED_DIR / name
        if not path.exists():
            errors.append(f"missing tracked dispatch: {path.relative_to(ROOT)}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"stale tracked dispatch: {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-tracked", action="store_true")
    parser.add_argument("--check-tracked", action="store_true")
    parser.add_argument("--export-dir", type=Path)
    parser.add_argument("--packet-limit", type=int, default=DEFAULT_PACKET_LIMIT)
    args = parser.parse_args()

    if not CAMPAIGNS.exists():
        raise SystemExit("missing generated campaign queue; run run_issue180_v3.py and build_parallel_campaigns_v2.py first")
    if not SOURCE_LEDGER.exists():
        raise SystemExit("missing SOURCE_REVIEW_LEDGER_V2.csv")

    rows = build_rows(read_csv(CAMPAIGNS), read_csv(SOURCE_LEDGER))
    if args.packet_limit < 1:
        raise SystemExit("--packet-limit must be >= 1")
    files = expected_files(rows, args.packet_limit)

    if args.write_tracked:
        write_dir(TRACKED_DIR, files)
    if args.export_dir:
        export_root = args.export_dir if args.export_dir.is_absolute() else ROOT / args.export_dir
        write_dir(export_root, files)
    if args.check_tracked:
        check_tracked(files)

    counts = {str(slot): sum(r["owner_slot"] == str(slot) for r in rows) for slot in range(4)}
    open_counts = {
        str(slot): sum(r["owner_slot"] == str(slot) and r["research_state"] == "OPEN" for r in rows)
        for slot in range(4)
    }
    queue_ids = sorted({r["queue_id"] for r in rows})
    print(json.dumps({
        "queue_id": queue_ids[0] if len(queue_ids) == 1 else queue_ids,
        "forward_campaign_count": len(rows),
        "campaign_counts_by_slot": counts,
        "open_counts_by_slot": open_counts,
        "packet_limit_per_lane": args.packet_limit,
        "dispatched_open_counts_by_slot": {str(slot): min(open_counts[str(slot)], args.packet_limit) for slot in range(4)},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
