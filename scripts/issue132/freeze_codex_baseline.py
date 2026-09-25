#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

from parallel_overlay import apply_corrections, load_checkpoint_union
from staging_repair_overlay import resolve_repair_overlay
from staging_v2 import SCHEMA_V2, compact_row_to_full

ROOT = Path(__file__).resolve().parents[2]
BASELINE_END = {1: 1125, 2: 1225, 3: 1200}
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"
STAGE_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")


def load_base():
    path = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    spec = importlib.util.spec_from_file_location("issue132_freeze_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load base validator")
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


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def normalize_v1_row(raw, fields):
    if isinstance(raw, dict):
        if set(raw) != set(fields):
            raise ValueError("v1 field-set mismatch")
        return {field: str(raw[field]) for field in fields}
    if isinstance(raw, list):
        if len(raw) != len(fields):
            raise ValueError("v1 ordered row length mismatch")
        return {field: str(value) for field, value in zip(fields, raw)}
    raise ValueError("v1 row must be dict/list")


def effective_window_rows(path: Path, lane: int, start: int, end: int, assigned, base):
    repaired, _, repair_errors = resolve_repair_overlay(path, lane, start, end)
    if repair_errors:
        raise ValueError("; ".join(repair_errors))
    obj = repaired if repaired is not None else json.loads(path.read_text(encoding="utf-8"))
    if obj.get("lane") != lane:
        raise ValueError("lane mismatch")
    if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
        raise ValueError("range mismatch")
    if obj.get("holds"):
        raise ValueError("baseline source window still contains holds")

    rows_by_index = {}
    schema = obj.get("schema_version")
    for raw in obj.get("rows", []):
        if schema == SCHEMA_V2:
            idx = int(raw["lane_local_index"])
            full = compact_row_to_full(raw, assigned[idx - 1], base.FIELDS)
        elif schema == SCHEMA_V1:
            full = normalize_v1_row(raw, base.FIELDS)
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
        else:
            raise ValueError(f"unsupported staging schema {schema}")

        if idx < start or idx > end or idx in rows_by_index:
            raise ValueError(f"duplicate/out-of-range row {idx}")
        rows_by_index[idx] = full

    expected = set(range(start, end + 1))
    if set(rows_by_index) != expected:
        raise ValueError(
            f"window coverage mismatch missing={sorted(expected-set(rows_by_index))}"
        )
    return rows_by_index


def main() -> None:
    base = load_base()
    neutral_path = ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv"
    neutral = read_csv(neutral_path)
    out_dir = ROOT / "docs/issue132/parallel/codex-baseline"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "issue132-codex-baseline-v1",
        "derived_from_repository_head": git_head(),
        "manual_semantic_audit_head": "5123a13bd574ef50f04f3f7e0fb031d2625dcbaa",
        "parent_neutral_sha256": "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d",
        "parent_identity_order_sha256": "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b",
        "lanes": {},
        "forensic_sources_retained": True,
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
        effective, correction_count, correction_errors = apply_corrections(
            ROOT, lane, raw, checkpoint_ranges, base.FIELDS
        )
        if correction_errors:
            raise SystemExit("; ".join(correction_errors))

        by_index = {idx: dict(row) for idx, row in enumerate(effective, start=1)}
        prefix = len(effective)

        stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
        for path in sorted(stage_dir.glob("window_*.json")):
            match = STAGE_RE.match(path.name)
            if not match:
                continue
            start, end = map(int, match.groups())
            if end <= prefix or start > target_end:
                continue
            if start <= prefix:
                raise SystemExit(f"lane {lane}: staging overlaps checkpoint boundary")
            if end > target_end:
                continue
            try:
                rows = effective_window_rows(path, lane, start, end, assigned, base)
            except Exception as exc:
                raise SystemExit(f"lane {lane} {path.name}: {exc}")
            overlap = set(by_index) & set(rows)
            if overlap:
                raise SystemExit(f"lane {lane}: duplicate effective baseline indices {sorted(overlap)}")
            by_index.update(rows)

        expected_indices = set(range(1, target_end + 1))
        if set(by_index) != expected_indices:
            raise SystemExit(
                f"lane {lane}: baseline coverage mismatch "
                f"missing={sorted(expected_indices-set(by_index))[:50]}"
            )

        ordered = []
        for idx in range(1, target_end + 1):
            row = by_index[idx]
            expected = assigned[idx - 1]
            if (
                row.get("identity_key") != expected["identity_key"]
                or int(row.get("review_seq", "-1")) != int(expected["review_seq"])
            ):
                raise SystemExit(f"lane {lane} local {idx}: identity binding mismatch")
            errors = base.validate_row(row, int(expected["review_seq"]))
            if errors:
                raise SystemExit(
                    f"lane {lane} local {idx}: " + "; ".join(errors)
                )
            ordered.append(row)

        out_path = out_dir / f"lane-{lane}_000001_{target_end:06d}.csv"
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=base.FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(ordered)

        manifest["lanes"][str(lane)] = {
            "lane_local_end": target_end,
            "row_count": len(ordered),
            "checkpoint_seed_count": prefix,
            "corrections_applied": correction_count,
            "path": str(out_path.relative_to(ROOT)),
            "sha256": sha256_file(out_path),
        }

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
