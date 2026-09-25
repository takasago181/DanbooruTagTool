#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path

from parallel_overlay import apply_corrections, load_checkpoint_union
from staging_repair_overlay import resolve_repair_overlay

ROOT = Path(__file__).resolve().parents[2]
BASELINE_END = {1: 1125, 2: 1225, 3: 1200}
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"
SCHEMA_V2 = "issue132-pass-a-staging-window-v2"
STAGE_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")


def load_base():
    path = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    spec = importlib.util.spec_from_file_location("issue132_freeze_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load historical base schema")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def identity_sha(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def full_to_compact(row: dict[str, str], expected: dict[str, str], idx: int) -> dict:
    routes = []
    for n in (1, 2, 3):
        rid = row.get(f"route_{n}_id", "").strip()
        if rid:
            routes.append({"id": rid, "strength": row[f"route_{n}_strength"]})
    return {
        "lane_local_index": idx,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha(expected["identity_key"]),
        "discovery_mode": row["discovery_mode"],
        "routes": routes,
        "local_refinement_ids": json.loads(row.get("local_refinement_ids") or "[]"),
        "body_site_ids": json.loads(row.get("body_site_ids") or "[]"),
        "theme_ids": json.loads(row.get("theme_ids") or "[]"),
        "route_vocabulary_gap": row["route_vocabulary_gap"],
        "review_depth": row["review_depth"],
        "evidence_urls": json.loads(row.get("evidence_urls") or "[]"),
    }


def normalize_v1_row(raw, fields):
    if isinstance(raw, dict) and set(raw) == set(fields):
        return {field: str(raw[field]) for field in fields}
    if isinstance(raw, list) and len(raw) == len(fields):
        return {field: str(value) for field, value in zip(fields, raw)}
    raise ValueError("historical v1 row shape mismatch")


def legacy_hold_to_compact(hold: dict, expected: dict, idx: int) -> dict:
    return {
        "lane_local_index": idx,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha(expected["identity_key"]),
        "reason_code": "OTHER_UNRESOLVED",
        "research_attempt_codes": ["OTHER_DIRECT_SOURCE"],
    }


def effective_window(
    path: Path,
    lane: int,
    start: int,
    end: int,
    assigned: list[dict[str, str]],
    fields: list[str],
) -> tuple[dict[int, dict], dict[int, dict]]:
    repaired, _, repair_errors = resolve_repair_overlay(path, lane, start, end)
    if repair_errors:
        raise ValueError("; ".join(repair_errors))
    obj = repaired if repaired is not None else json.loads(path.read_text(encoding="utf-8"))
    if obj.get("lane") != lane:
        raise ValueError("lane mismatch")
    if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
        raise ValueError("range mismatch")

    rows: dict[int, dict] = {}
    holds: dict[int, dict] = {}
    schema = obj.get("schema_version")

    for raw in obj.get("rows", []):
        if schema == SCHEMA_V2:
            idx = int(raw["lane_local_index"])
            compact = dict(raw)
        elif schema == SCHEMA_V1:
            full = normalize_v1_row(raw, fields)
            seq = int(full["review_seq"])
            matches = [
                idx
                for idx in range(start, end + 1)
                if int(assigned[idx - 1]["review_seq"]) == seq
                and assigned[idx - 1]["identity_key"] == full["identity_key"]
            ]
            if len(matches) != 1:
                raise ValueError("v1 row does not bind uniquely")
            idx = matches[0]
            compact = full_to_compact(full, assigned[idx - 1], idx)
        else:
            raise ValueError(f"unsupported staging schema {schema}")

        if idx < start or idx > end or idx in rows or idx in holds:
            raise ValueError(f"duplicate/out-of-range row {idx}")
        rows[idx] = compact

    for hold in obj.get("holds", []):
        idx = int(hold["lane_local_index"])
        if schema == SCHEMA_V2:
            compact_hold = dict(hold)
        elif schema == SCHEMA_V1:
            expected = assigned[idx - 1]
            if (
                int(hold["review_seq"]) != int(expected["review_seq"])
                or hold.get("identity_key") != expected["identity_key"]
            ):
                raise ValueError(f"legacy hold local {idx}: identity mismatch")
            compact_hold = legacy_hold_to_compact(hold, expected, idx)
        else:
            raise ValueError(f"unsupported staging schema {schema}")

        if idx < start or idx > end or idx in rows or idx in holds:
            raise ValueError(f"duplicate/out-of-range hold {idx}")
        holds[idx] = compact_hold

    expected = set(range(start, end + 1))
    covered = set(rows) | set(holds)
    if covered != expected:
        raise ValueError(
            f"window coverage mismatch missing={sorted(expected-covered)} "
            f"extra={sorted(covered-expected)}"
        )
    return rows, holds


def main() -> None:
    base = load_base()
    neutral = read_csv(
        ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv"
    )
    out_dir = ROOT / "docs/issue132/parallel/codex-baseline"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "issue132-codex-baseline-manifest-v2",
        "manual_semantic_audit_head": "5123a13bd574ef50f04f3f7e0fb031d2625dcbaa",
        "parent_neutral_sha256": "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d",
        "parent_identity_order_sha256": "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b",
        "forensic_sources_retained": True,
        "lanes": {},
    }

    for lane in (1, 2, 3):
        assigned = [
            row for row in neutral
            if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
        ]
        target_end = BASELINE_END[lane]

        raw, checkpoint_ranges, checkpoint_errors = load_checkpoint_union(
            ROOT, lane, base.FIELDS
        )
        if checkpoint_errors:
            raise SystemExit("; ".join(checkpoint_errors))
        effective, _, correction_errors = apply_corrections(
            ROOT, lane, raw, checkpoint_ranges, base.FIELDS
        )
        if correction_errors:
            raise SystemExit("; ".join(correction_errors))

        rows: dict[int, dict] = {}
        holds: dict[int, dict] = {}

        for idx, row in enumerate(effective, start=1):
            if idx > target_end:
                break
            expected = assigned[idx - 1]
            if (
                row.get("identity_key") != expected["identity_key"]
                or int(row.get("review_seq", "-1")) != int(expected["review_seq"])
            ):
                raise SystemExit(f"lane {lane} local {idx}: checkpoint identity mismatch")
            rows[idx] = full_to_compact(row, expected, idx)

        checkpoint_end = min(len(effective), target_end)
        stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
        for path in sorted(stage_dir.glob("window_*.json")):
            match = STAGE_RE.match(path.name)
            if not match:
                continue
            start, end = map(int, match.groups())
            if end <= checkpoint_end or start > target_end:
                continue
            if start <= checkpoint_end:
                raise SystemExit(f"lane {lane}: staging overlaps checkpoint boundary")
            if end > target_end:
                continue
            try:
                win_rows, win_holds = effective_window(
                    path, lane, start, end, assigned, base.FIELDS
                )
            except Exception as exc:
                raise SystemExit(f"lane {lane} {path.name}: {exc}")
            overlap = (set(rows) | set(holds)) & (set(win_rows) | set(win_holds))
            if overlap:
                raise SystemExit(
                    f"lane {lane}: duplicate effective indices {sorted(overlap)}"
                )
            rows.update(win_rows)
            holds.update(win_holds)

        expected_indices = set(range(1, target_end + 1))
        covered = set(rows) | set(holds)
        if covered != expected_indices:
            raise SystemExit(
                f"lane {lane}: baseline coverage mismatch "
                f"missing={sorted(expected_indices-covered)[:50]}"
            )

        baseline = {
            "schema_version": "issue132-codex-baseline-lane-v1",
            "lane": lane,
            "lane_local_start": 1,
            "lane_local_end": target_end,
            "parent_neutral_sha256": manifest["parent_neutral_sha256"],
            "parent_identity_order_sha256": manifest["parent_identity_order_sha256"],
            "rows": [rows[idx] for idx in sorted(rows)],
            "holds": [holds[idx] for idx in sorted(holds)],
        }
        out_path = out_dir / f"lane-{lane}_000001_{target_end:06d}.json"
        out_path.write_text(
            json.dumps(baseline, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        manifest["lanes"][str(lane)] = {
            "lane_local_end": target_end,
            "path": str(out_path.relative_to(ROOT)),
            "sha256": sha256_file(out_path),
        }

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
