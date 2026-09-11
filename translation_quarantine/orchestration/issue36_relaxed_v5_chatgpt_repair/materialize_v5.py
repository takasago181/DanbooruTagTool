#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
V4_TABLE = REPO_ROOT / "translation_quarantine/orchestration/issue36_relaxed_closeout_v3_language_sanity_v4/final_translation_table.csv"
OVERRIDE_DIR = SCRIPT_DIR / "overrides"
PROGRESS_PATH = SCRIPT_DIR / "progress.json"
OUTPUT_DIR = SCRIPT_DIR / "materialized"
OUTPUT_TABLE = OUTPUT_DIR / "final_translation_table_v5.csv"
REPORT_PATH = OUTPUT_DIR / "materialization_report.json"

REQUIRED_OVERRIDE_COLUMNS = {"canonical", "old_display_ja", "new_display_ja", "reason"}


def fail(message: str) -> None:
    raise SystemExit(f"MATERIALIZE_FAIL: {message}")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            fail(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def main() -> None:
    progress = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    expected_rows = int(progress["total_rows"])
    expected_overrides = int(progress["override_rows"])

    source_fields, source_rows = read_csv(V4_TABLE)
    if "canonical" not in source_fields or "display_ja" not in source_fields:
        fail(f"V4 table must contain canonical/display_ja; got {source_fields}")
    if len(source_rows) != expected_rows:
        fail(f"V4 row count {len(source_rows)} != expected {expected_rows}")

    source_canonicals = [row["canonical"] for row in source_rows]
    source_counts = Counter(source_canonicals)
    duplicate_source = sorted(k for k, v in source_counts.items() if v != 1)
    if duplicate_source:
        fail(f"V4 canonical must be unique; examples={duplicate_source[:10]}")

    source_by_canonical = {row["canonical"]: row for row in source_rows}

    # Source-shard repairs and post-shard cross-audit repairs are both durable V5 overrides.
    # Keep the namespaces distinct for provenance, but materialize both through the same
    # fail-closed validation path.
    override_files = sorted(
        list(OVERRIDE_DIR.glob("audit_shard_*.csv"))
        + list(OVERRIDE_DIR.glob("cross_shard_*.csv"))
    )
    if not override_files:
        fail("no override CSV files found")

    overrides: list[dict[str, str]] = []
    override_file_rows: dict[str, int] = {}
    for path in override_files:
        fields, rows = read_csv(path)
        missing = REQUIRED_OVERRIDE_COLUMNS - set(fields)
        if missing:
            fail(f"{path.name}: missing columns {sorted(missing)}")
        override_file_rows[path.name] = len(rows)
        for row in rows:
            row["__file"] = path.name
            overrides.append(row)

    if len(overrides) != expected_overrides:
        fail(f"override row count {len(overrides)} != progress override_rows {expected_overrides}")

    override_counts = Counter(row["canonical"] for row in overrides)
    duplicate_override = sorted(k for k, v in override_counts.items() if v != 1)
    if duplicate_override:
        fail(f"override canonical duplicated; examples={duplicate_override[:20]}")

    missing_from_source: list[str] = []
    old_value_mismatches: list[dict[str, str]] = []
    empty_new_values: list[str] = []
    override_by_canonical: dict[str, dict[str, str]] = {}
    for row in overrides:
        canonical = row["canonical"]
        if canonical not in source_by_canonical:
            missing_from_source.append(canonical)
            continue
        if row["old_display_ja"] != source_by_canonical[canonical]["display_ja"]:
            old_value_mismatches.append({
                "canonical": canonical,
                "file": row["__file"],
                "source_display_ja": source_by_canonical[canonical]["display_ja"],
                "override_old_display_ja": row["old_display_ja"],
            })
        if not row["new_display_ja"].strip():
            empty_new_values.append(canonical)
        override_by_canonical[canonical] = row

    if missing_from_source:
        fail(f"override canonical missing from V4; examples={missing_from_source[:20]}")
    if old_value_mismatches:
        sample = old_value_mismatches[:5]
        fail(f"old_display_ja mismatch count={len(old_value_mismatches)} sample={sample}")
    if empty_new_values:
        fail(f"empty new_display_ja; examples={empty_new_values[:20]}")

    output_rows: list[dict[str, str]] = []
    applied = 0
    for source_row in source_rows:
        row = dict(source_row)
        override = override_by_canonical.get(row["canonical"])
        if override is not None:
            row["display_ja"] = override["new_display_ja"]
            applied += 1
        output_rows.append(row)

    if applied != expected_overrides:
        fail(f"applied {applied} overrides != expected {expected_overrides}")
    if [r["canonical"] for r in output_rows] != source_canonicals:
        fail("canonical identity/order changed during materialization")
    if any(not r["display_ja"].strip() for r in output_rows):
        fail("materialized table contains empty display_ja")

    non_display_columns = [c for c in source_fields if c != "display_ja"]
    for before, after in zip(source_rows, output_rows):
        for column in non_display_columns:
            if before[column] != after[column]:
                fail(f"non-display column changed: canonical={before['canonical']} column={column}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_TABLE.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=source_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    report = {
        "status": "PASS",
        "source_table": str(V4_TABLE.relative_to(REPO_ROOT)),
        "output_table": str(OUTPUT_TABLE.relative_to(REPO_ROOT)),
        "source_rows": len(source_rows),
        "materialized_rows": len(output_rows),
        "override_files": len(override_files),
        "override_rows": len(overrides),
        "applied_overrides": applied,
        "canonical_unique": True,
        "canonical_identity_preserved": True,
        "canonical_order_preserved": True,
        "non_display_columns_preserved": True,
        "display_ja_nonempty": True,
        "old_display_ja_matches_v4": True,
        "duplicate_override_canonicals": 0,
        "override_file_rows": override_file_rows,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
