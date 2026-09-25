#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from staging_v2 import (
    HOLD_REASON_CODES,
    RESEARCH_ATTEMPT_CODES,
)

ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = "issue132-pass-a-write-request-v1"
OUTPUT_SCHEMA = "issue132-pass-a-staging-window-v2"
EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19b9a3f86b22f294135f96a707c"
# overwritten below from the pinned manifest to avoid accidental drift
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"
REQ_RE = re.compile(r"^request_(\d{6})_(\d{6})\.json$")

ROW_FIELDS = {
    "lane_local_index",
    "review_seq",
    "discovery_mode",
    "routes",
    "local_refinement_ids",
    "body_site_ids",
    "theme_ids",
    "route_vocabulary_gap",
    "review_depth",
    "evidence_urls",
}
HOLD_FIELDS = {
    "lane_local_index",
    "review_seq",
    "reason_code",
    "research_attempt_codes",
}


def read_neutral(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def identity_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_vocab(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "route_ids",
        "local_refinement_parent",
        "body_site_ids",
        "theme_ids",
        "allowed_discovery_modes",
        "allowed_route_strengths",
        "allowed_review_depths",
    }
    missing = sorted(required - set(obj))
    if missing:
        raise ValueError(f"vocabulary manifest missing keys: {missing}")
    return obj


def validate_row(row: dict, expected: dict, local_index: int, vocab: dict) -> dict:
    if set(row) != ROW_FIELDS:
        raise ValueError(f"row {local_index}: field-set mismatch")
    if int(row["lane_local_index"]) != local_index:
        raise ValueError(f"row {local_index}: lane_local_index mismatch")
    if int(row["review_seq"]) != int(expected["review_seq"]):
        raise ValueError(f"row {local_index}: review_seq mismatch")

    mode = row["discovery_mode"]
    if mode not in set(vocab["allowed_discovery_modes"]):
        raise ValueError(f"row {local_index}: invalid discovery_mode")

    depth = row["review_depth"]
    if depth not in set(vocab["allowed_review_depths"]):
        raise ValueError(f"row {local_index}: invalid review_depth")

    if row["route_vocabulary_gap"] not in {"YES", "NO"}:
        raise ValueError(f"row {local_index}: invalid route_vocabulary_gap")

    routes = row["routes"]
    if not isinstance(routes, list) or len(routes) > 3:
        raise ValueError(f"row {local_index}: invalid routes")
    route_ids = set(vocab["route_ids"])
    strengths = set(vocab["allowed_route_strengths"])
    selected = set()
    for route in routes:
        if not isinstance(route, dict) or set(route) != {"id", "strength"}:
            raise ValueError(f"row {local_index}: route field-set mismatch")
        if route["id"] not in route_ids or route["strength"] not in strengths:
            raise ValueError(f"row {local_index}: invalid route code")
        selected.add(route["id"])

    locals_ = row["local_refinement_ids"]
    bodies = row["body_site_ids"]
    themes = row["theme_ids"]
    evidence = row["evidence_urls"]
    for name, values in (
        ("local_refinement_ids", locals_),
        ("body_site_ids", bodies),
        ("theme_ids", themes),
        ("evidence_urls", evidence),
    ):
        if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
            raise ValueError(f"row {local_index}: {name} must be string list")

    local_parent = vocab["local_refinement_parent"]
    for local in locals_:
        if local not in local_parent:
            raise ValueError(f"row {local_index}: invalid local refinement")
        if local_parent[local] not in selected:
            raise ValueError(f"row {local_index}: local refinement parent route missing")

    if any(x not in set(vocab["body_site_ids"]) for x in bodies):
        raise ValueError(f"row {local_index}: invalid body site")
    if any(x not in set(vocab["theme_ids"]) for x in themes):
        raise ValueError(f"row {local_index}: invalid theme")

    if mode in {"SEARCH_ORIENTED", "SEMANTIC_UNRESOLVED"} and (routes or locals_ or bodies or themes):
        raise ValueError(f"row {local_index}: mode must not carry browse facets")
    if depth == "RESEARCHED" and not evidence:
        raise ValueError(f"row {local_index}: RESEARCHED requires evidence")

    out = dict(row)
    out["identity_sha256"] = identity_sha(expected["identity_key"])
    return out


def validate_hold(hold: dict, expected: dict, local_index: int) -> dict:
    if set(hold) != HOLD_FIELDS:
        raise ValueError(f"hold {local_index}: field-set mismatch")
    if int(hold["lane_local_index"]) != local_index:
        raise ValueError(f"hold {local_index}: lane_local_index mismatch")
    if int(hold["review_seq"]) != int(expected["review_seq"]):
        raise ValueError(f"hold {local_index}: review_seq mismatch")
    if hold["reason_code"] not in HOLD_REASON_CODES:
        raise ValueError(f"hold {local_index}: invalid reason_code")
    attempts = hold["research_attempt_codes"]
    if not isinstance(attempts, list) or not attempts or any(x not in RESEARCH_ATTEMPT_CODES for x in attempts):
        raise ValueError(f"hold {local_index}: invalid research_attempt_codes")
    out = dict(hold)
    out["identity_sha256"] = identity_sha(expected["identity_key"])
    return out


def materialize_request(path: Path, neutral: list[dict[str, str]], vocab: dict, parallel_root: Path) -> tuple[Path, bool]:
    m = REQ_RE.match(path.name)
    if not m:
        raise ValueError(f"{path}: invalid request filename")
    file_start, file_end = map(int, m.groups())

    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != REQUEST_SCHEMA:
        raise ValueError(f"{path}: schema mismatch")
    lane = int(obj["lane"])
    start = int(obj["lane_local_start"])
    end = int(obj["lane_local_end"])
    if (start, end) != (file_start, file_end):
        raise ValueError(f"{path}: filename/range mismatch")
    if end < start or end - start + 1 > 25:
        raise ValueError(f"{path}: request size must be 1..25")
    if obj.get("parent_neutral_sha256") != EXPECTED_PARENT_SHA:
        raise ValueError(f"{path}: parent neutral SHA mismatch")
    if obj.get("parent_identity_order_sha256") != EXPECTED_ORDER_SHA:
        raise ValueError(f"{path}: parent identity-order SHA mismatch")

    assigned = [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
    if start < 1 or end > len(assigned):
        raise ValueError(f"{path}: range outside lane")

    rows = obj.get("rows")
    holds = obj.get("holds")
    if not isinstance(rows, list) or not isinstance(holds, list):
        raise ValueError(f"{path}: rows/holds must be lists")

    by_index: dict[int, tuple[str, dict]] = {}
    out_rows = []
    for row in rows:
        idx = int(row["lane_local_index"])
        if idx < start or idx > end or idx in by_index:
            raise ValueError(f"{path}: duplicate/out-of-range row {idx}")
        out = validate_row(row, assigned[idx - 1], idx, vocab)
        by_index[idx] = ("row", out)
        out_rows.append(out)

    out_holds = []
    for hold in holds:
        idx = int(hold["lane_local_index"])
        if idx < start or idx > end or idx in by_index:
            raise ValueError(f"{path}: duplicate/out-of-range hold {idx}")
        out = validate_hold(hold, assigned[idx - 1], idx)
        by_index[idx] = ("hold", out)
        out_holds.append(out)

    expected_indices = set(range(start, end + 1))
    if set(by_index) != expected_indices:
        raise ValueError(f"{path}: incomplete coverage")

    output = {
        "schema_version": OUTPUT_SCHEMA,
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "parent_neutral_sha256": EXPECTED_PARENT_SHA,
        "parent_identity_order_sha256": EXPECTED_ORDER_SHA,
        "rows": sorted(out_rows, key=lambda x: int(x["lane_local_index"])),
        "holds": sorted(out_holds, key=lambda x: int(x["lane_local_index"])),
    }

    out_path = parallel_root / f"lane-{lane}" / "staging" / f"window_{start:06d}_{end:06d}.json"
    if out_path.exists():
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        if existing != output:
            raise ValueError(f"{path}: canonical staging already exists with different content")
        return out_path, False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return out_path, True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parallel-dir", default="docs/issue132/parallel")
    ap.add_argument("--neutral", default="docs/issue132/parallel/input/luna_neutral_review_input_v2.csv")
    ap.add_argument("--vocab", default="docs/issue132/parallel/pass_a_contract_manifest_v1.json")
    args = ap.parse_args()

    parallel_root = ROOT / args.parallel_dir
    neutral = read_neutral(ROOT / args.neutral)
    vocab = load_vocab(ROOT / args.vocab)

    created = []
    checked = []
    for lane in (1, 2, 3):
        req_dir = parallel_root / f"lane-{lane}" / "write-requests"
        if not req_dir.exists():
            continue
        for path in sorted(req_dir.glob("request_*.json")):
            out_path, was_created = materialize_request(path, neutral, vocab, parallel_root)
            checked.append(str(path.relative_to(ROOT)))
            if was_created:
                created.append(str(out_path.relative_to(ROOT)))

    print(json.dumps({
        "schema_version": "issue132-write-materialization-summary-v1",
        "requests_checked": len(checked),
        "staging_created": created,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
