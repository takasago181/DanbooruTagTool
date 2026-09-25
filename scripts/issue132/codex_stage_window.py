#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
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
    reason_codes,
)
from staging_v2 import (
    HOLD_REASON_CODES,
    RESEARCH_ATTEMPT_CODES,
    SCHEMA_V2,
    compact_row_to_full,
    identity_sha256,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_SCHEMA = "issue132-codex-decision-window-v1"
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
    "decision_reason_codes",
}
DECISION_HOLD_FIELDS = {
    "lane_local_index",
    "reason_code",
    "research_attempt_codes",
}


def load_base():
    path = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    spec = importlib.util.spec_from_file_location("issue132_codex_stage_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load base validator")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_decision_row(
    row: dict,
    local_index: int,
    expected: dict,
    contract: dict,
    base,
) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not isinstance(row, dict) or set(row) != DECISION_ROW_FIELDS:
        return {}, [f"local {local_index}: decision row field-set mismatch"]
    try:
        got = int(row["lane_local_index"])
    except Exception:
        got = -1
    if got != local_index:
        errors.append(f"local {local_index}: lane_local_index mismatch")

    codes = row["decision_reason_codes"]
    allowed_codes = reason_codes(contract)
    if (
        not isinstance(codes, list)
        or not codes
        or any(not isinstance(x, str) for x in codes)
        or any(x not in allowed_codes for x in codes)
        or len(codes) != len(set(codes))
    ):
        errors.append(f"local {local_index}: invalid decision_reason_codes")

    compact = {
        "lane_local_index": local_index,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha256(expected["identity_key"]),
        "discovery_mode": row["discovery_mode"],
        "routes": row["routes"],
        "local_refinement_ids": row["local_refinement_ids"],
        "body_site_ids": row["body_site_ids"],
        "theme_ids": row["theme_ids"],
        "route_vocabulary_gap": row["route_vocabulary_gap"],
        "review_depth": row["review_depth"],
        "evidence_urls": row["evidence_urls"],
    }
    try:
        full = compact_row_to_full(compact, expected, base.FIELDS)
    except Exception as exc:
        errors.append(f"local {local_index}: {exc}")
        return compact, errors

    for err in base.validate_row(full, int(expected["review_seq"])):
        errors.append(f"local {local_index}: {err}")

    return compact, errors


def validate_decision_hold(
    hold: dict,
    local_index: int,
    expected: dict,
) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not isinstance(hold, dict) or set(hold) != DECISION_HOLD_FIELDS:
        return {}, [f"local {local_index}: hold field-set mismatch"]
    try:
        got = int(hold["lane_local_index"])
    except Exception:
        got = -1
    if got != local_index:
        errors.append(f"local {local_index}: hold lane_local_index mismatch")
    if hold.get("reason_code") not in HOLD_REASON_CODES:
        errors.append(f"local {local_index}: invalid hold reason_code")
    attempts = hold.get("research_attempt_codes")
    if (
        not isinstance(attempts, list)
        or not attempts
        or any(x not in RESEARCH_ATTEMPT_CODES for x in attempts)
    ):
        errors.append(f"local {local_index}: invalid research_attempt_codes")
    compact = {
        "lane_local_index": local_index,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha256(expected["identity_key"]),
        "reason_code": hold.get("reason_code"),
        "research_attempt_codes": attempts,
    }
    return compact, errors


def reject_overlap(stage_dir: Path, start: int, end: int, out_path: Path) -> None:
    for path in stage_dir.glob("window_*.json"):
        if path == out_path:
            continue
        match = WINDOW_RE.match(path.name)
        if not match:
            continue
        a, b = map(int, match.groups())
        if max(a, start) <= min(b, end):
            raise SystemExit(f"new window overlaps existing staging {path.name}")


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
    if end < start or end - start + 1 > int(authority["fixed"]["forward_window_max"]):
        raise SystemExit("decision window size must be 1..100")
    if start < direct_start(authority, lane):
        raise SystemExit("decision window is before the Codex direct-staging boundary")
    if end > allowed_forward_end(qa, lane):
        raise SystemExit(
            f"decision window exceeds ChatGPT QA watermark {allowed_forward_end(qa, lane)}"
        )

    neutral = read_csv(ROOT / authority["fixed"]["neutral_path"])
    assigned = [
        row for row in neutral
        if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
    ]
    if end > len(assigned):
        raise SystemExit("decision window exceeds lane length")

    rows = obj["rows"]
    holds = obj["holds"]
    if not isinstance(rows, list) or not isinstance(holds, list):
        raise SystemExit("rows/holds must be lists")

    by_index: dict[int, tuple[str, dict]] = {}
    reason_map: dict[str, list[str]] = {}
    out_rows: list[dict] = []
    out_holds: list[dict] = []
    errors: list[str] = []
    base = load_base()

    for row in rows:
        try:
            idx = int(row.get("lane_local_index"))
        except Exception:
            idx = -1
        if idx < start or idx > end or idx in by_index:
            errors.append(f"row has duplicate/out-of-range lane_local_index {idx}")
            continue
        compact, row_errors = validate_decision_row(
            row, idx, assigned[idx - 1], contract, base
        )
        errors.extend(row_errors)
        by_index[idx] = ("row", compact)
        out_rows.append(compact)
        reason_map[str(idx)] = list(row.get("decision_reason_codes", []))

    for hold in holds:
        try:
            idx = int(hold.get("lane_local_index"))
        except Exception:
            idx = -1
        if idx < start or idx > end or idx in by_index:
            errors.append(f"hold has duplicate/out-of-range lane_local_index {idx}")
            continue
        compact, hold_errors = validate_decision_hold(hold, idx, assigned[idx - 1])
        errors.extend(hold_errors)
        by_index[idx] = ("hold", compact)
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
        "schema_version": SCHEMA_V2,
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "parent_neutral_sha256": authority["fixed"]["parent_neutral_sha256"],
        "parent_identity_order_sha256": authority["fixed"]["parent_identity_order_sha256"],
        "semantic_policy_id": policy_id(authority),
        "semantic_policy_git_blob_sha": policy_blob(authority),
        "decision_reason_codes": {
            key: reason_map[key] for key in sorted(reason_map, key=lambda x: int(x))
        },
        "rows": sorted(out_rows, key=lambda x: int(x["lane_local_index"])),
        "holds": sorted(out_holds, key=lambda x: int(x["lane_local_index"])),
    }

    stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
    out_path = stage_dir / f"window_{start:06d}_{end:06d}.json"
    reject_overlap(stage_dir, start, end, out_path)

    text = json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n"
    if out_path.exists():
        if out_path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"canonical staging already exists with different content: {out_path}")
        print(json.dumps({"path": str(out_path.relative_to(ROOT)), "created": False}))
        return

    if not args.check_only:
        stage_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")

    print(json.dumps({
        "path": str(out_path.relative_to(ROOT)),
        "created": not args.check_only,
        "rows": len(out_rows),
        "holds": len(out_holds),
        "policy": policy_id(authority),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
