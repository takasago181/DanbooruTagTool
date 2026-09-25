#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from codex_runtime import (
    last_codex_qa,
    load_runtime,
    qa_epoch_size,
    read_csv,
)

ROOT = Path(__file__).resolve().parents[2]
WINDOW_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")

FAMILY_PATTERNS = {
    "COSPLAY_COSTUME": re.compile(r"(?:^|_)cosplay(?:_|$)|costume"),
    "NAMED_PROP_WEAPON": re.compile(
        r"(?:^|_)(?:sword|gun|rifle|pistol|katana|spear|staff|wand|shield|weapon|blade|device)(?:_|$)"
    ),
    "CLOTHING_STATE": re.compile(
        r"(?:^|_)(?:torn|unworn|wet|removed|displaced|pulled|lifted|open|soiled)(?:_|$)"
    ),
    "ACTION_POSE_RELATION": re.compile(
        r"(?:^|_)(?:holding|pulling|touching|using|sitting|standing|lying|kneeling|straddling|hugging|kissing|dominant|submissive)(?:_|$)"
    ),
    "BODY_HAIR_NAIL": re.compile(
        r"(?:pubic_hair|armpit_hair|nipple_hair|testicle_hair|nails)"
    ),
    "OBJECT_SCENE": re.compile(r"(?:^|_)(?:door|window|counter|fixture)(?:_|$)"),
}


def validator_snapshot() -> dict:
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
            return json.loads(line[len(marker):])
    raise SystemExit("flat validator did not emit snapshot")


def load_direct_entries(
    lane: int, start: int, end: int
) -> dict[int, tuple[str, dict]]:
    stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
    result: dict[int, tuple[str, dict]] = {}
    for path in sorted(stage_dir.glob("window_*.json")):
        match = WINDOW_RE.match(path.name)
        if not match:
            continue
        a, b = map(int, match.groups())
        if b < start or a > end:
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        for row in obj.get("rows", []):
            idx = int(row["lane_local_index"])
            if start <= idx <= end:
                if idx in result:
                    raise SystemExit(f"duplicate direct QA slot {idx}")
                result[idx] = ("row", row)
        for hold in obj.get("holds", []):
            idx = int(hold["lane_local_index"])
            if start <= idx <= end:
                if idx in result:
                    raise SystemExit(f"duplicate direct QA slot {idx}")
                result[idx] = ("hold", hold)
    return result


def selection_reasons(identity: str, row: dict) -> list[str]:
    reasons: list[str] = []
    if row.get("review_depth") == "RESEARCHED":
        reasons.append("RESEARCHED")
    if row.get("discovery_mode") == "MIXED":
        reasons.append("MIXED")
    if row.get("discovery_mode") == "SEMANTIC_UNRESOLVED":
        reasons.append("SEMANTIC_UNRESOLVED")
    if row.get("route_vocabulary_gap") == "YES":
        reasons.append("VOCABULARY_GAP")
    routes = row.get("routes", [])
    if len(routes) > 1:
        reasons.append("MULTI_ROUTE")
    if any(r.get("strength") == "SUPPORTING" for r in routes if isinstance(r, dict)):
        reasons.append("SUPPORTING")
    if row.get("body_site_ids"):
        reasons.append("BODY_FACET")
    if row.get("theme_ids"):
        reasons.append("THEME_FACET")
    for name, pattern in FAMILY_PATTERNS.items():
        if pattern.search(identity):
            reasons.append(name)
    return reasons


def build_packet(lane: int) -> dict:
    authority, _, qa, runtime_errors = load_runtime(ROOT)
    if runtime_errors:
        raise SystemExit("runtime errors: " + "; ".join(runtime_errors))

    snapshot = validator_snapshot()
    lane_key = str(lane)
    lane_length = int(authority["fixed"]["lane_lengths"][lane_key])
    cursor = last_codex_qa(qa, lane)
    start = cursor + 1
    frontier = snapshot["frontiers"][lane_key]
    processed_end = lane_length if frontier is None else int(frontier) - 1

    if start > lane_length:
        return {
            "schema_version": "issue132-codex-qa-packet-v1",
            "lane": lane,
            "status": "LANE_QA_COMPLETE",
            "rows": [],
        }

    epoch = qa_epoch_size(qa)
    target = min(start + epoch - 1, lane_length)
    lane_complete = frontier is None
    if processed_end < target and not lane_complete:
        return {
            "schema_version": "issue132-codex-qa-packet-v1",
            "lane": lane,
            "status": "NOT_DUE",
            "qa_start": start,
            "next_full_epoch_end": target,
            "processed_end": processed_end,
            "rows": [],
        }

    end = min(target, processed_end)
    entries = load_direct_entries(lane, start, end)
    expected = set(range(start, end + 1))
    if set(entries) != expected:
        raise SystemExit(
            f"QA epoch coverage mismatch missing={sorted(expected-set(entries))[:50]}"
        )

    neutral = read_csv(ROOT / authority["fixed"]["neutral_path"])
    assigned = [
        row for row in neutral
        if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
    ]

    selected: dict[int, dict] = {}
    ordinary: list[tuple[str, int, dict]] = []
    for idx in range(start, end + 1):
        kind, item = entries[idx]
        identity = assigned[idx - 1]["identity_key"]
        source_surfaces = assigned[idx - 1].get("source_surfaces", "")
        try:
            source_surfaces = json.loads(source_surfaces)
        except Exception:
            pass

        if kind == "hold":
            reasons = ["HOLD"]
        else:
            reasons = selection_reasons(identity, item)

        record = {
            "lane_local_index": idx,
            "review_seq": int(assigned[idx - 1]["review_seq"]),
            "identity_key": identity,
            "source_surfaces": source_surfaces,
            "current_kind": kind,
            "current_decision": item,
            "selection_reasons": reasons,
        }
        if reasons:
            selected[idx] = record
        else:
            digest = hashlib.sha256(
                f"{lane}:{idx}:{identity}".encode("utf-8")
            ).hexdigest()
            ordinary.append((digest, idx, record))

    sample_n = min(
        int(qa["ordinary_checked_sample_per_epoch"]),
        len(ordinary),
    )
    for _, idx, record in sorted(ordinary)[:sample_n]:
        record["selection_reasons"] = ["ORDINARY_CHECKED_SAMPLE"]
        selected[idx] = record

    packet = {
        "schema_version": "issue132-codex-qa-packet-v1",
        "lane": lane,
        "status": "READY",
        "lane_local_start": start,
        "lane_local_end": end,
        "epoch_slot_count": end - start + 1,
        "selected_count": len(selected),
        "risk_selected_count": len(selected) - sample_n,
        "ordinary_sample_count": sample_n,
        "rows": [selected[idx] for idx in sorted(selected)],
    }
    payload = json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    packet["packet_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return packet


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    packet = build_packet(args.lane)
    text = json.dumps(packet, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(json.dumps({
            "lane": args.lane,
            "status": packet["status"],
            "selected_count": len(packet.get("rows", [])),
            "out": args.out,
        }, ensure_ascii=False))
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
