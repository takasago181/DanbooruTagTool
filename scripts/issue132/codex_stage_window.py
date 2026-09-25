#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from codex_runtime import (
    allowed_forward_end,
    direct_start,
    load_runtime,
    policy_blob,
    policy_id,
    read_csv,
)
from codex_semantic import (
    HOLD_REASON_CODES,
    RESEARCH_ATTEMPT_CODES,
    identity_sha256,
    validate_compact_hold,
    validate_compact_row,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_SCHEMA = "issue132-codex-decision-window-v1"
STAGING_SCHEMA = "issue132-pass-a-staging-window-v2"
WINDOW_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")

DECISION_ROW_FIELDS = {
    "lane_local_index",
    "discovery_mode",
    "routes",
    "local_refinement_ids",
    "body_site_ids",
    "theme_ids",
    "route_vocabulary_gap",
    "review_depth",
    "evidence_urls",
}
DECISION_HOLD_FIELDS = {
    "lane_local_index",
    "reason_code",
    "research_attempt_codes",
}


def current_forward_frontier(
    stage_dir: Path, direct_boundary: int, lane_length: int
) -> int | None:
    covered: set[int] = set()
    for path in stage_dir.glob("window_*.json"):
        match = WINDOW_RE.match(path.name)
        if not match:
            continue
        start, end = map(int, match.groups())
        if start >= direct_boundary:
            covered.update(range(start, end + 1))
    for idx in range(direct_boundary, lane_length + 1):
        if idx not in covered:
            return idx
    return None


def make_compact_row(raw: dict, expected: dict, idx: int) -> dict:
    return {
        "lane_local_index": idx,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha256(expected["identity_key"]),
        "discovery_mode": raw["discovery_mode"],
        "routes": raw["routes"],
        "local_refinement_ids": raw["local_refinement_ids"],
        "body_site_ids": raw["body_site_ids"],
        "theme_ids": raw["theme_ids"],
        "route_vocabulary_gap": raw["route_vocabulary_gap"],
        "review_depth": raw["review_depth"],
        "evidence_urls": raw["evidence_urls"],
    }


def make_compact_hold(raw: dict, expected: dict, idx: int) -> dict:
    return {
        "lane_local_index": idx,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha256(expected["identity_key"]),
        "reason_code": raw["reason_code"],
        "research_attempt_codes": raw["research_attempt_codes"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    authority, contract, qa, runtime_errors = load_runtime(ROOT)
    if runtime_errors:
        raise SystemExit("runtime errors: " + "; ".join(runtime_errors))

    obj = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    if set(obj) != {
        "schema_version", "lane", "lane_local_start", "lane_local_end", "rows", "holds"
    }:
        raise SystemExit("decision top-level field-set mismatch")
    if obj.get("schema_version") != DECISION_SCHEMA:
        raise SystemExit("decision schema mismatch")

    lane = int(obj["lane"])
    start = int(obj["lane_local_start"])
    end = int(obj["lane_local_end"])
    if lane not in (1, 2, 3):
        raise SystemExit("invalid lane")

    lane_length = int(authority["fixed"]["lane_lengths"][str(lane)])
    boundary = direct_start(authority, lane)
    if start < boundary:
        raise SystemExit(f"decision window starts before direct boundary {boundary}")
    if end < start or end - start + 1 > int(authority["fixed"]["forward_window_max"]):
        raise SystemExit("decision window size must be 1..100")
    if end > allowed_forward_end(qa, lane):
        raise SystemExit(
            f"decision window exceeds ChatGPT QA watermark {allowed_forward_end(qa, lane)}"
        )
    if end > lane_length:
        raise SystemExit("decision window exceeds lane length")

    stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
    frontier = current_forward_frontier(stage_dir, boundary, lane_length)
    if frontier is None:
        raise SystemExit("lane already has direct staging coverage through lane end")
    if start != frontier:
        raise SystemExit(f"decision window must start at current direct frontier {frontier}")

    neutral = read_csv(ROOT / authority["fixed"]["neutral_path"])
    assigned = [
        row for row in neutral
        if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
    ]

    rows = obj["rows"]
    holds = obj["holds"]
    if not isinstance(rows, list) or not isinstance(holds, list):
        raise SystemExit("rows/holds must be lists")

    by_index: dict[int, str] = {}
    out_rows: list[dict] = []
    out_holds: list[dict] = []
    errors: list[str] = []

    for raw in rows:
        if not isinstance(raw, dict) or set(raw) != DECISION_ROW_FIELDS:
            errors.append("decision row field-set mismatch")
            continue
        try:
            idx = int(raw["lane_local_index"])
        except Exception:
            idx = -1
        if idx < start or idx > end or idx in by_index:
            errors.append(f"duplicate/out-of-range row {idx}")
            continue

        compact = make_compact_row(raw, assigned[idx - 1], idx)
        errors.extend(
            f"local {idx}: {err}"
            for err in validate_compact_row(compact, assigned[idx - 1], idx, contract)
        )
        by_index[idx] = "row"
        out_rows.append(compact)

    for raw in holds:
        if not isinstance(raw, dict) or set(raw) != DECISION_HOLD_FIELDS:
            errors.append("decision hold field-set mismatch")
            continue
        try:
            idx = int(raw["lane_local_index"])
        except Exception:
            idx = -1
        if idx < start or idx > end or idx in by_index:
            errors.append(f"duplicate/out-of-range hold {idx}")
            continue
        if raw.get("reason_code") not in HOLD_REASON_CODES:
            errors.append(f"local {idx}: invalid hold reason_code")
        attempts = raw.get("research_attempt_codes")
        if (
            not isinstance(attempts, list)
            or not attempts
            or any(x not in RESEARCH_ATTEMPT_CODES for x in attempts)
        ):
            errors.append(f"local {idx}: invalid research_attempt_codes")
        compact = make_compact_hold(raw, assigned[idx - 1], idx)
        errors.extend(
            f"hold local {idx}: {err}"
            for err in validate_compact_hold(compact, assigned[idx - 1], idx)
        )
        by_index[idx] = "hold"
        out_holds.append(compact)

    expected = set(range(start, end + 1))
    if set(by_index) != expected:
        errors.append(
            f"coverage mismatch missing={sorted(expected-set(by_index))} "
            f"extra={sorted(set(by_index)-expected)}"
        )

    if errors:
        for error in errors[:100]:
            print("ERROR:", error)
        raise SystemExit(1)

    output = {
        "schema_version": STAGING_SCHEMA,
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "parent_neutral_sha256": authority["fixed"]["parent_neutral_sha256"],
        "parent_identity_order_sha256": authority["fixed"]["parent_identity_order_sha256"],
        "semantic_policy_id": policy_id(authority),
        "semantic_policy_git_blob_sha": policy_blob(authority),
        "rows": sorted(out_rows, key=lambda x: int(x["lane_local_index"])),
        "holds": sorted(out_holds, key=lambda x: int(x["lane_local_index"])),
    }

    out_path = stage_dir / f"window_{start:06d}_{end:06d}.json"
    text_out = json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n"
    if out_path.exists():
        if out_path.read_text(encoding="utf-8") != text_out:
            raise SystemExit(f"canonical staging exists with different content: {out_path}")
        print(json.dumps({"path": str(out_path.relative_to(ROOT)), "created": False}))
        return

    if not args.check_only:
        stage_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text_out, encoding="utf-8")

    print(json.dumps({
        "path": str(out_path.relative_to(ROOT)),
        "created": not args.check_only,
        "rows": len(out_rows),
        "holds": len(out_holds),
        "policy": policy_id(authority),
        "next_frontier": end + 1 if end < lane_length else None,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
