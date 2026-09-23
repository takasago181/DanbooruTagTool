#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

CHECKPOINT_PAT = re.compile(r"^checkpoint_(\d{6})_(\d{6})\.csv$")
CORRECTION_PAT = re.compile(r"^correction_(\d{6})_[A-Za-z0-9_.-]+\.json$")
SCHEMA = "issue132-pass-a-correction-v1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_checkpoint_union(root: Path, lane: int, fields: list[str]):
    errors: list[str] = []
    rows: list[dict[str, str]] = []
    ranges: list[tuple[int, int, Path]] = []
    expect = 1
    checkpoint_dir = root / f"docs/issue132/parallel/lane-{lane}/checkpoints"
    if checkpoint_dir.exists():
        for path in sorted(checkpoint_dir.glob("checkpoint_*.csv")):
            m = CHECKPOINT_PAT.match(path.name)
            if not m:
                errors.append(f"lane {lane}: invalid checkpoint filename {path.name}")
                continue
            a, b = map(int, m.groups())
            if a != expect:
                errors.append(f"lane {lane}: checkpoint {path.name} starts {a}, expected {expect}")
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames or []
                data = list(reader)
            if header != fields:
                errors.append(f"lane {lane}: {path.name} header mismatch")
            if not data:
                errors.append(f"lane {lane}: {path.name} empty")
            if b - a + 1 != len(data):
                errors.append(f"lane {lane}: {path.name} range/count mismatch")
            rows.extend(data)
            ranges.append((a, b, path))
            expect = b + 1
    return rows, ranges, errors


def _source_checkpoint_for_local_index(ranges, local_index: int):
    for a, b, path in ranges:
        if a <= local_index <= b:
            return path
    return None


def apply_corrections(
    root: Path,
    lane: int,
    raw_rows: list[dict[str, str]],
    ranges,
    fields: list[str],
):
    errors: list[str] = []
    effective = [dict(row) for row in raw_rows]
    by_seq: dict[int, tuple[int, dict[str, str]]] = {}
    for idx, row in enumerate(effective):
        try:
            seq = int(row["review_seq"])
        except Exception:
            continue
        by_seq[seq] = (idx, row)

    immutable_fields = {"review_seq", "identity_key"}
    seen_patch_fields: set[tuple[int, str]] = set()
    applied = 0
    correction_dir = root / f"docs/issue132/parallel/lane-{lane}/corrections"
    if not correction_dir.exists():
        return effective, applied, errors

    for path in sorted(correction_dir.glob("correction_*.json")):
        m = CORRECTION_PAT.match(path.name)
        if not m:
            errors.append(f"lane {lane}: invalid correction filename {path.name}")
            continue
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"lane {lane}: {path.name} invalid JSON: {e}")
            continue

        if obj.get("schema_version") != SCHEMA:
            errors.append(f"lane {lane}: {path.name} schema mismatch")
            continue
        if obj.get("lane") != lane:
            errors.append(f"lane {lane}: {path.name} lane mismatch")
            continue

        try:
            review_seq = int(obj["review_seq"])
            local_index = int(obj["lane_local_index"])
        except Exception:
            errors.append(f"lane {lane}: {path.name} invalid review_seq/lane_local_index")
            continue

        if review_seq != int(m.group(1)):
            errors.append(f"lane {lane}: {path.name} filename review_seq mismatch")
        target = by_seq.get(review_seq)
        if target is None:
            errors.append(f"lane {lane}: {path.name} target review_seq not in checkpoint union")
            continue
        idx, row = target
        if row.get("identity_key") != obj.get("identity_key"):
            errors.append(f"lane {lane}: {path.name} identity mismatch")
            continue

        if local_index < 1 or local_index > len(raw_rows):
            errors.append(f"lane {lane}: {path.name} lane_local_index out of current prefix")
            continue
        raw_target = raw_rows[local_index - 1]
        if raw_target.get("review_seq") != str(review_seq) or raw_target.get("identity_key") != obj.get("identity_key"):
            errors.append(f"lane {lane}: {path.name} lane_local_index target mismatch")
            continue

        source = _source_checkpoint_for_local_index(ranges, local_index)
        if source is None or source.name != obj.get("source_checkpoint"):
            errors.append(f"lane {lane}: {path.name} source_checkpoint mismatch")
            continue

        reason = str(obj.get("reason", "")).strip()
        if not reason:
            errors.append(f"lane {lane}: {path.name} blank reason")

        expected_before = obj.get("expected_before", {})
        patch = obj.get("patch", {})
        if not isinstance(expected_before, dict) or not isinstance(patch, dict) or not patch:
            errors.append(f"lane {lane}: {path.name} expected_before/patch invalid")
            continue

        bad_keys = [k for k in patch if k not in fields or k in immutable_fields]
        if bad_keys:
            errors.append(f"lane {lane}: {path.name} invalid patch fields {bad_keys}")
            continue
        if any(not isinstance(v, str) for v in patch.values()):
            errors.append(f"lane {lane}: {path.name} patch values must be strings")
            continue

        ok = True
        for field, expected in expected_before.items():
            if field not in patch:
                errors.append(f"lane {lane}: {path.name} expected_before field {field} not patched")
                ok = False
                continue
            if not isinstance(expected, str):
                errors.append(f"lane {lane}: {path.name} expected_before values must be strings")
                ok = False
                continue
            if raw_target.get(field, "") != expected:
                errors.append(
                    f"lane {lane}: {path.name} expected_before mismatch for {field}: "
                    f"{raw_target.get(field, '')!r} != {expected!r}"
                )
                ok = False
        if not ok:
            continue

        for field, value in patch.items():
            key = (review_seq, field)
            if key in seen_patch_fields:
                errors.append(f"lane {lane}: duplicate correction for review_seq {review_seq} field {field}")
                ok = False
            seen_patch_fields.add(key)
            row[field] = value
        if ok:
            effective[idx] = row
            applied += 1

    return effective, applied, errors
