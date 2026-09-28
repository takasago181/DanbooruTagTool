#!/usr/bin/env python3
"""Repair only unquoted CSV separators in the six frozen Issue #180 decision shards.

The repair recovers free-text boundaries from the unique validation_state followed
by officiality_state anchor. It does not edit any recovered field value. All files
are preflighted and round-tripped before any write; an audit records each repaired
row and the exact pre/post semantic values.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISION_DIR = ROOT / "docs/issue180/autonomous/decisions"
AUDIT_PATH = ROOT / "docs/issue180/serial/DECISION_SHARD_SERIALIZATION_REPAIR_V1.json"
SCHEMA = (
    "scope", "key", "home_copyright", "base_character", "authority_type",
    "evidence_url", "evidence_claim", "validation_state", "officiality_state", "notes",
)
SHARDS = (
    "direct_and_exceptions_v2.csv", "discovery_roster_reviews_v2.csv",
    "family_terminal_reviews_v2.csv", "roster_verified_v4.csv",
    "variant_pattern_reviews_v2.csv", "variants_verified_v4.csv",
)
EXPECTED_REPAIRS = {
    "direct_and_exceptions_v2.csv": 6,
    "discovery_roster_reviews_v2.csv": 1,
    "family_terminal_reviews_v2.csv": 59,
    "roster_verified_v4.csv": 0,
    "variant_pattern_reviews_v2.csv": 19,
    "variants_verified_v4.csv": 6,
}
VALID_STATES = {"PASS", "UNRESOLVED", "PENDING", "NEEDS_HIGHER_REASONING"}
VALID_OFFICIALITY = {"", "OFFICIAL_CONFIRMED", "OFFICIAL_IDENTITY", "OFFICIAL_VARIANT", "NOT_OFFICIAL_CONFIRMED"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def semantic_digest(values: list[str]) -> str:
    data = json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return digest(data)


def decode_record(values: list[str], source: str, line: int) -> tuple[list[str], bool]:
    if len(values) == len(SCHEMA):
        result = values
        repaired = False
    else:
        candidates = [
            index for index in range(7, len(values) - 1)
            if values[index] in VALID_STATES and values[index + 1] in VALID_OFFICIALITY
        ]
        if len(values) < len(SCHEMA) or len(candidates) != 1:
            raise ValueError(f"{source}:{line}: cannot uniquely recover exact decision fields; candidates={candidates}")
        state_index = candidates[0]
        result = values[:6] + [
            ",".join(values[6:state_index]), values[state_index], values[state_index + 1],
            ",".join(values[state_index + 2:]),
        ]
        repaired = True
    if len(result) != len(SCHEMA) or not result[0].strip() or not result[1].strip():
        raise ValueError(f"{source}:{line}: recovered row violates exact schema or has blank scope/key")
    return result, repaired


def parse_file(raw: bytes, source: str) -> tuple[list[list[str]], list[tuple[int, int, list[str], bytes]]]:
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    header = next(reader, None)
    if tuple(header or ()) != SCHEMA:
        raise ValueError(f"{source}: unexpected schema")
    rows: list[list[str]] = []
    repairs: list[tuple[int, int, list[str], bytes]] = []
    prior_end = reader.line_num
    for record_number, values in enumerate(reader, start=2):
        start = prior_end
        end = reader.line_num
        semantic, repaired = decode_record(values, source, start + 1)
        rows.append(semantic)
        if repaired:
            raw_record = "".join(lines[start:end]).encode("utf-8")
            repairs.append((record_number, start, semantic, raw_record))
        prior_end = end
    return rows, repairs


def serialize_record(values: list[str], ending: str) -> str:
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator=ending).writerow(values)
    return stream.getvalue()


def main() -> None:
    prepared: dict[Path, tuple[bytes, bytes, list[list[str]], list[dict[str, object]]]] = {}
    for name in SHARDS:
        path = DECISION_DIR / name
        original = path.read_bytes()
        before_rows, repairs = parse_file(original, name)
        if len(repairs) != EXPECTED_REPAIRS[name]:
            raise ValueError(f"{name}: expected {EXPECTED_REPAIRS[name]} serialization defects, found {len(repairs)}")
        text = original.decode("utf-8-sig")
        lines = text.splitlines(keepends=True)
        for record_number, start, values, raw_record in reversed(repairs):
            end_marker = "\r\n" if raw_record.endswith(b"\r\n") else "\n" if raw_record.endswith(b"\n") else "\r" if raw_record.endswith(b"\r") else ""
            physical_count = len(raw_record.decode("utf-8").splitlines(keepends=True))
            lines[start:start + physical_count] = [serialize_record(values, end_marker)]
        repaired_text = "".join(lines)
        bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
        repaired = bom + repaired_text.encode("utf-8")
        after_rows, remaining = parse_file(repaired, name)
        if remaining or before_rows != after_rows:
            raise ValueError(f"{name}: semantic or schema round-trip changed during repair")
        row_audit = []
        for record_number, _start, values, raw_record in repairs:
            row_audit.append({
                "record_number": record_number,
                "original_serialization_sha256": digest(raw_record),
                "semantic_values_before": dict(zip(SCHEMA, values)),
                "semantic_values_after": dict(zip(SCHEMA, after_rows[record_number - 2])),
                "semantic_sha256_before": semantic_digest(values),
                "semantic_sha256_after": semantic_digest(after_rows[record_number - 2]),
                "semantic_values_identical": values == after_rows[record_number - 2],
            })
        prepared[path] = (original, repaired, after_rows, row_audit)

    changed: list[Path] = []
    try:
        for path, (original, repaired, _rows, _audit) in prepared.items():
            if original != repaired:
                path.write_bytes(repaired)
                changed.append(path)
        files = []
        for path, (original, repaired, rows, row_audit) in prepared.items():
            strict_rows, leftover = parse_file(path.read_bytes(), path.name)
            if leftover or rows != strict_rows:
                raise ValueError(f"{path.name}: on-disk semantic round-trip mismatch")
            files.append({
                "path": path.relative_to(ROOT).as_posix(),
                "original_file_sha256": digest(original),
                "repaired_file_sha256": digest(repaired),
                "row_count": len(rows),
                "repaired_row_count": len(row_audit),
                "semantic_values_identical_for_all_rows": True,
                "repaired_rows": row_audit,
            })
        if sum(item["repaired_row_count"] for item in files) != 91:
            raise ValueError("expected exactly 91 serialization-only repairs")
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        audit = {
            "schema_version": 1,
            "repair_kind": "CSV serialization only; recovered semantic field values are immutable",
            "field_schema": list(SCHEMA),
            "boundary_rule": "unique validation_state followed by allowed officiality_state; free-text commas retained verbatim",
            "decision_contents_changed": False,
            "repaired_row_count": 91,
            "files": files,
        }
        AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:
        for path in changed:
            path.write_bytes(prepared[path][0])
        raise
    print(json.dumps({"repaired_rows": 91, "files": [{"path": f["path"], "repaired_rows": f["repaired_row_count"]} for f in files],
                      "audit": AUDIT_PATH.relative_to(ROOT).as_posix()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
