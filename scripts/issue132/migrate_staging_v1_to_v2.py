#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from staging_v2 import SCHEMA_V2, identity_sha256

ROOT = Path(__file__).resolve().parents[2]
STAGE_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"
EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_list(value: str, field: str):
    obj = json.loads(value or "[]")
    if not isinstance(obj, list) or any(not isinstance(x, str) for x in obj):
        raise ValueError(f"{field} must be a string list")
    return obj


def reason_code(reason: str) -> str:
    s = reason.lower()
    if "ルート" in reason or "route" in s:
        return "ROUTE_AMBIGUOUS"
    if any(x in reason for x in ("固有参照", "対象を", "対象・", "同定", "identity")):
        return "IDENTITY_AMBIGUOUS"
    if any(x in reason for x in ("意味", "範囲", "定義", "scope")):
        return "SEMANTIC_SCOPE_AMBIGUOUS"
    if any(x in reason for x in ("直接", "根拠", "確認でき", "確定でき")):
        return "DIRECT_EVIDENCE_NOT_FOUND"
    return "OTHER_UNRESOLVED"


def attempt_codes(attempts) -> list[str]:
    out: list[str] = []
    for item in attempts if isinstance(attempts, list) else []:
        text = str(item)
        low = text.lower()
        if "danbooru" in low and "DANBOORU_EXACT" not in out:
            out.append("DANBOORU_EXACT")
        if "safebooru" in low and "SAFEBOORU_EXACT" not in out:
            out.append("SAFEBOORU_EXACT")
        if ("公式" in text or "official" in low) and "OFFICIAL_SOURCE" not in out:
            out.append("OFFICIAL_SOURCE")
        if any(x in low for x in ("http", "web", "search")) and "DIRECT_WEB_SOURCE" not in out:
            out.append("DIRECT_WEB_SOURCE")
    if not out:
        out.append("OTHER_DIRECT_SOURCE")
    return out


def convert_window(path: Path, assigned: list[dict[str, str]]):
    m = STAGE_RE.match(path.name)
    if not m:
        return None, "invalid filename"
    start, end = map(int, m.groups())
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != SCHEMA_V1:
        return None, "not-v1"
    if obj.get("parent_neutral_sha256") != EXPECTED_PARENT_SHA:
        return None, "parent neutral SHA mismatch"
    if obj.get("parent_identity_order_sha256") != EXPECTED_ORDER_SHA:
        return None, "parent order SHA mismatch"

    expected_by_pair = {
        (str(assigned[i - 1]["review_seq"]), assigned[i - 1]["identity_key"]): i
        for i in range(start, end + 1)
    }
    covered: set[int] = set()
    rows_v2 = []

    for row in obj.get("rows", []):
        if not isinstance(row, dict):
            return None, "non-object v1 row"
        pair = (str(row.get("review_seq", "")), str(row.get("identity_key", "")))
        local_index = expected_by_pair.get(pair)
        if local_index is None:
            return None, f"row not exact window identity: {pair[0]}"
        if local_index in covered:
            return None, f"duplicate local index {local_index}"
        covered.add(local_index)
        routes = []
        for i in range(1, 4):
            rid = str(row.get(f"route_{i}_id", "")).strip()
            strength = str(row.get(f"route_{i}_strength", "")).strip()
            if rid:
                routes.append({"id": rid, "strength": strength})
        rows_v2.append({
            "lane_local_index": local_index,
            "review_seq": int(row["review_seq"]),
            "identity_sha256": identity_sha256(row["identity_key"]),
            "discovery_mode": row["discovery_mode"],
            "routes": routes,
            "local_refinement_ids": parse_list(row.get("local_refinement_ids", "[]"), "local_refinement_ids"),
            "body_site_ids": parse_list(row.get("body_site_ids", "[]"), "body_site_ids"),
            "theme_ids": parse_list(row.get("theme_ids", "[]"), "theme_ids"),
            "route_vocabulary_gap": row["route_vocabulary_gap"],
            "review_depth": row["review_depth"],
            "evidence_urls": parse_list(row.get("evidence_urls", "[]"), "evidence_urls"),
        })

    holds_v2 = []
    for hold in obj.get("holds", []):
        if not isinstance(hold, dict):
            return None, "non-object v1 hold"
        try:
            local_index = int(hold["lane_local_index"])
            seq = int(hold["review_seq"])
        except Exception:
            return None, "invalid hold indices"
        if local_index < start or local_index > end:
            return None, f"hold outside window {local_index}"
        expected = assigned[local_index - 1]
        if int(expected["review_seq"]) != seq or expected["identity_key"] != hold.get("identity_key"):
            return None, f"hold identity mismatch {local_index}"
        if local_index in covered:
            return None, f"duplicate row/hold local index {local_index}"
        covered.add(local_index)
        holds_v2.append({
            "lane_local_index": local_index,
            "review_seq": seq,
            "identity_sha256": identity_sha256(expected["identity_key"]),
            "reason_code": reason_code(str(hold.get("reason", ""))),
            "research_attempt_codes": attempt_codes(hold.get("research_attempts", [])),
        })

    expected_indices = set(range(start, end + 1))
    if covered != expected_indices:
        return None, f"coverage mismatch missing={sorted(expected_indices-covered)} extra={sorted(covered-expected_indices)}"

    rows_v2.sort(key=lambda x: x["lane_local_index"])
    holds_v2.sort(key=lambda x: x["lane_local_index"])
    out = {
        "schema_version": SCHEMA_V2,
        "lane": obj["lane"],
        "lane_local_start": start,
        "lane_local_end": end,
        "parent_neutral_sha256": obj["parent_neutral_sha256"],
        "parent_identity_order_sha256": obj["parent_identity_order_sha256"],
        "rows": rows_v2,
        "holds": holds_v2,
    }
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parallel-dir", default="docs/issue132/parallel")
    ap.add_argument("--neutral", default="docs/issue132/parallel/input/luna_neutral_review_input_v2.csv")
    ap.add_argument("--report", default="docs/issue132/parallel/staging_v2_migration_report.json")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    neutral = read_csv(ROOT / args.neutral)
    converted = []
    skipped = []
    already_v2 = []

    for lane in (1, 2, 3):
        assigned = [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        stage_dir = ROOT / args.parallel_dir / f"lane-{lane}" / "staging"
        for path in sorted(stage_dir.glob("window_*.json")):
            obj = json.loads(path.read_text(encoding="utf-8"))
            if obj.get("schema_version") == SCHEMA_V2:
                already_v2.append(str(path.relative_to(ROOT)))
                continue
            if obj.get("schema_version") != SCHEMA_V1:
                skipped.append({"path": str(path.relative_to(ROOT)), "reason": "unknown schema"})
                continue
            try:
                new_obj, error = convert_window(path, assigned)
            except Exception as exc:
                new_obj, error = None, str(exc)
            if error:
                skipped.append({"path": str(path.relative_to(ROOT)), "reason": error})
                continue
            assert new_obj is not None
            converted.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(
                    json.dumps(new_obj, ensure_ascii=False, separators=(",", ":")) + "\n",
                    encoding="utf-8",
                )

    report = {
        "schema_version": "issue132-staging-v2-migration-report-v1",
        "converted_count": len(converted),
        "already_v2_count": len(already_v2),
        "skipped_count": len(skipped),
        "converted": converted,
        "already_v2": already_v2,
        "skipped": skipped,
    }
    report_path = ROOT / args.report
    if not args.check:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
