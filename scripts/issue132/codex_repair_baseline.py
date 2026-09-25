#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from codex_runtime import (
    load_baseline_lane,
    load_baseline_manifest,
    load_runtime,
    policy_blob,
    policy_id,
    read_csv,
)
from codex_semantic import identity_sha256, validate_compact_row

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "issue132-codex-baseline-repair-v1"
REPAIR_FIELDS = {
    "lane_local_index",
    "expected_state",
    "discovery_mode",
    "routes",
    "local_refinement_ids",
    "body_site_ids",
    "theme_ids",
    "route_vocabulary_gap",
    "review_depth",
    "evidence_urls",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assigned_lane(neutral: list[dict[str, str]], lane: int) -> list[dict[str, str]]:
    return [
        row for row in neutral
        if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
    ]


def make_compact(raw: dict, expected: dict, idx: int) -> dict:
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


def scan_lane_debt(
    baseline: dict,
    lane: int,
    assigned: list[dict[str, str]],
    contract: dict,
) -> tuple[list[dict], list[int]]:
    lints: list[dict] = []
    holds = sorted(int(x["lane_local_index"]) for x in baseline.get("holds", []))
    for row in baseline.get("rows", []):
        idx = int(row["lane_local_index"])
        errors = validate_compact_row(row, assigned[idx - 1], idx, contract)
        if errors:
            lints.append({
                "lane_local_index": idx,
                "review_seq": int(assigned[idx - 1]["review_seq"]),
                "identity_key": assigned[idx - 1]["identity_key"],
                "errors": errors,
            })
    return lints, holds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repairs", required=True)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    authority, contract, _, runtime_errors = load_runtime(ROOT)
    if runtime_errors:
        raise SystemExit("runtime errors: " + "; ".join(runtime_errors))

    request = json.loads(Path(args.repairs).read_text(encoding="utf-8"))
    if set(request) != {"schema_version", "lane", "repairs"}:
        raise SystemExit("repair request top-level field-set mismatch")
    if request.get("schema_version") != SCHEMA:
        raise SystemExit("repair request schema mismatch")

    lane = int(request["lane"])
    if lane not in (1, 2, 3):
        raise SystemExit("invalid lane")
    repairs = request["repairs"]
    if not isinstance(repairs, list) or not repairs or len(repairs) > 100:
        raise SystemExit("repairs must be a non-empty list of at most 100 entries")

    manifest = load_baseline_manifest(ROOT, authority)
    baseline = load_baseline_lane(ROOT, manifest, lane)
    neutral = read_csv(ROOT / authority["fixed"]["neutral_path"])
    assigned = assigned_lane(neutral, lane)

    rows_by_index = {
        int(row["lane_local_index"]): dict(row)
        for row in baseline.get("rows", [])
    }
    holds_by_index = {
        int(hold["lane_local_index"]): dict(hold)
        for hold in baseline.get("holds", [])
    }
    current_lints, _ = scan_lane_debt(baseline, lane, assigned, contract)
    existing_lints = {int(item["lane_local_index"]) for item in current_lints}
    trace = dict(baseline.get("repair_trace", {}))
    seen_request: set[int] = set()
    errors: list[str] = []

    for raw in repairs:
        if not isinstance(raw, dict) or set(raw) != REPAIR_FIELDS:
            errors.append("repair entry field-set mismatch")
            continue
        try:
            idx = int(raw["lane_local_index"])
        except Exception:
            idx = -1
        if idx < 1 or idx > int(baseline["lane_local_end"]) or idx in seen_request:
            errors.append(f"duplicate/out-of-range repair index {idx}")
            continue
        seen_request.add(idx)

        expected_state = raw["expected_state"]
        if expected_state == "HOLD":
            if idx not in holds_by_index:
                errors.append(f"local {idx}: expected HOLD but current slot is not a hold")
                continue
        elif expected_state == "LINT_ROW":
            if idx not in rows_by_index or idx not in existing_lints:
                errors.append(f"local {idx}: expected LINT_ROW but slot is not current lint debt")
                continue
        else:
            errors.append(f"local {idx}: expected_state must be HOLD or LINT_ROW")
            continue

        compact = make_compact(raw, assigned[idx - 1], idx)
        row_errors = validate_compact_row(compact, assigned[idx - 1], idx, contract)
        if row_errors:
            errors.extend(f"local {idx}: {err}" for err in row_errors)
            continue

        holds_by_index.pop(idx, None)
        rows_by_index[idx] = compact
        trace[str(idx)] = {
            "semantic_policy_id": policy_id(authority),
            "semantic_policy_git_blob_sha": policy_blob(authority),
            "replaced_state": expected_state,
        }

    if errors:
        for error in errors[:100]:
            print("ERROR:", error)
        raise SystemExit(1)

    baseline["rows"] = [rows_by_index[idx] for idx in sorted(rows_by_index)]
    baseline["holds"] = [holds_by_index[idx] for idx in sorted(holds_by_index)]
    baseline["repair_trace"] = {
        key: trace[key] for key in sorted(trace, key=lambda value: int(value))
    }

    lints, holds = scan_lane_debt(baseline, lane, assigned, contract)
    lane_entry = manifest["lanes"][str(lane)]
    lane_path = ROOT / lane_entry["path"]
    lane_text = json.dumps(baseline, ensure_ascii=False, separators=(",", ":")) + "\n"

    if args.check_only:
        print(json.dumps({
            "lane": lane,
            "repairs": len(repairs),
            "remaining_holds": len(holds),
            "remaining_lints": len(lints),
            "write": False,
        }))
        return

    lane_path.write_text(lane_text, encoding="utf-8")
    lane_entry["sha256"] = sha256_file(lane_path)
    manifest_path = ROOT / authority["baseline"]["manifest_path"]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "lane": lane,
        "repairs": len(repairs),
        "remaining_holds": len(holds),
        "remaining_lints": len(lints),
        "baseline_path": str(lane_path.relative_to(ROOT)),
        "manifest_path": str(manifest_path.relative_to(ROOT)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
