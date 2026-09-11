"""Promote the audited Issue #36 V5 table into the local runtime overlay."""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from danbooru_tag_tool.japanese_overlay import JapaneseOverlay
from danbooru_tag_tool.knowledge import TagKnowledgeCore


SOURCE_COLUMNS = (
    "canonical",
    "display_ja",
    "search_ja",
    "source_state",
    "decision",
    "display_verdict",
    "search_verdict",
    "risk_class",
    "review_mode",
    "language_sanity_provenance",
)
PROFILE_COLUMNS = "SpecialID"
EXPECTED_SOURCE_ROWS = 30_629
EXPECTED_PROFILE_ROWS = 2_788


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class SourceRow:
    canonical: str
    display_ja: str
    search_ja: str


def load_source_table(path: Path) -> tuple[SourceRow, ...]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != SOURCE_COLUMNS:
            raise ValueError("Unexpected V5 source columns/order")
        rows = tuple(
            SourceRow(
                canonical=row["canonical"],
                display_ja=row["display_ja"],
                search_ja=row["search_ja"],
            )
            for row in reader
        )
    if len(rows) != EXPECTED_SOURCE_ROWS:
        raise ValueError(f"Unexpected V5 source row count: {len(rows)}")
    canonicals = [row.canonical for row in rows]
    if any(not value for value in canonicals):
        raise ValueError("Blank V5 canonical")
    if len(set(canonicals)) != len(canonicals):
        raise ValueError("Duplicate V5 canonical")
    if any(not row.display_ja.strip() for row in rows):
        raise ValueError("Blank V5 display_ja")
    if any(not row.search_ja.strip() for row in rows):
        raise ValueError("Blank V5 search_ja")
    return rows


def build_document(rows: tuple[SourceRow, ...]) -> dict:
    return {
        "format_version": 1,
        "entries": {
            row.canonical: {
                "display_ja": row.display_ja,
                "search_ja": [row.search_ja],
            }
            for row in rows
        },
    }


def validate_document(document: dict, rows: tuple[SourceRow, ...], canonical) -> None:
    if set(document) != {"format_version", "entries"} or document["format_version"] != 1:
        raise ValueError("Unexpected production document schema")
    entries = document["entries"]
    if not isinstance(entries, dict) or len(entries) != len(rows):
        raise ValueError("Production entry count mismatch")
    expected_order = [row.canonical for row in rows]
    if list(entries) != expected_order:
        raise ValueError("Production canonical identity/order mismatch")
    unknown = set(entries).difference(canonical)
    if unknown:
        raise ValueError(f"V5 source contains {len(unknown)} unknown canonicals")
    for row in rows:
        value = entries[row.canonical]
        if set(value) != {"display_ja", "search_ja"}:
            raise ValueError("Unexpected production entry fields")
        if value["display_ja"] != row.display_ja:
            raise ValueError("display_ja mapping mismatch")
        if value["search_ja"] != [row.search_ja]:
            raise ValueError("search_ja mapping mismatch")


def validate_profile(path: Path, expected_hash: str) -> dict:
    actual_hash = sha256(path)
    if actual_hash != expected_hash:
        raise ValueError("Issue #49 profile SHA-256 mismatch")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if PROFILE_COLUMNS not in (reader.fieldnames or ()):
            raise ValueError("Issue #49 profile identity column missing")
        identities = [row[PROFILE_COLUMNS] for row in reader]
    if len(identities) != EXPECTED_PROFILE_ROWS:
        raise ValueError("Issue #49 profile row count mismatch")
    if len(set(identities)) != EXPECTED_PROFILE_ROWS:
        raise ValueError("Issue #49 profile duplicate identity")
    if identities != [str(index) for index in range(1, EXPECTED_PROFILE_ROWS + 1)]:
        raise ValueError("Issue #49 profile identity/order mismatch")
    return {
        "path": str(path),
        "sha256": actual_hash,
        "rows": len(identities),
        "unique_identities": len(set(identities)),
        "identity_order_preserved": True,
    }


def write_temp_document(path: Path, document: dict) -> None:
    payload = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    if path.read_text(encoding="utf-8") != payload:
        raise ValueError("UTF-8 roundtrip mismatch")


def validate_temp_with_loader(
    path: Path,
    rows: tuple[SourceRow, ...],
    canonical,
) -> JapaneseOverlay:
    document = json.loads(path.read_text(encoding="utf-8"))
    validate_document(document, rows, canonical)
    overlay = JapaneseOverlay.load(path, canonical)
    if len(overlay.display_by_canonical) != len(rows):
        raise ValueError("Loader display count mismatch")
    if len(overlay.search_by_canonical) != len(rows):
        raise ValueError("Loader search count mismatch")
    for row in rows:
        if overlay.display_by_canonical[row.canonical] != row.display_ja:
            raise ValueError("Loader display mapping mismatch")
        expected_search = tuple(dict.fromkeys((row.display_ja, row.search_ja)))
        if overlay.search_by_canonical[row.canonical] != expected_search:
            raise ValueError("Loader search mapping mismatch")
    return overlay


def atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def promote(args: argparse.Namespace) -> dict:
    runtime_root = args.runtime_root.resolve()
    source = args.source.resolve()
    overlay_path = runtime_root / "data/runtime/japanese_overlay.json"
    profile_path = runtime_root / "data/generation/special2788_generation_profile.csv"
    backup_dir = args.backup_dir.resolve()
    backup_path = backup_dir / "original_japanese_overlay.json"

    if backup_dir == overlay_path.parent or overlay_path.parent in backup_dir.parents:
        raise ValueError("Backup directory must be outside data/runtime")
    if not overlay_path.is_file():
        raise ValueError("Production overlay is missing")
    if backup_path.exists():
        raise ValueError("Rollback backup already exists")
    source_hash = sha256(source)
    if source_hash != args.expected_source_sha256:
        raise ValueError("Audited V5 source SHA-256 mismatch")

    knowledge = TagKnowledgeCore.load(runtime_root)
    rows = load_source_table(source)
    document = build_document(rows)
    validate_document(document, rows, knowledge.canonical)

    original_hash = sha256(overlay_path)
    if original_hash != args.expected_overlay_sha256:
        raise ValueError("Production overlay changed before promotion")
    original_size = overlay_path.stat().st_size
    if original_size != args.expected_overlay_size:
        raise ValueError("Production overlay size changed before promotion")
    original_document = json.loads(overlay_path.read_text(encoding="utf-8"))
    JapaneseOverlay.load(overlay_path, knowledge.canonical)
    profile_before = validate_profile(profile_path, args.expected_profile_sha256)

    descriptor, temporary_name = tempfile.mkstemp(
        dir=overlay_path.parent,
        prefix=".issue55-japanese-overlay-",
        suffix=".tmp",
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    replaced = False
    rollback_performed = False
    try:
        write_temp_document(temporary, document)
        validate_temp_with_loader(temporary, rows, knowledge.canonical)
        temporary_hash = sha256(temporary)
        temporary_size = temporary.stat().st_size

        if sha256(overlay_path) != original_hash:
            raise ValueError("Production overlay changed concurrently before backup")
        backup_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy2(overlay_path, backup_path)
        if sha256(backup_path) != original_hash:
            raise ValueError("Rollback backup hash mismatch")
        if sha256(overlay_path) != original_hash:
            raise ValueError("Production overlay changed concurrently before replace")

        os.replace(temporary, overlay_path)
        replaced = True
        try:
            promoted_document = json.loads(overlay_path.read_text(encoding="utf-8"))
            validate_document(promoted_document, rows, knowledge.canonical)
            promoted_overlay = validate_temp_with_loader(overlay_path, rows, knowledge.canonical)
            post_hash = sha256(overlay_path)
            if post_hash != temporary_hash:
                raise ValueError("Atomic replacement hash mismatch")
            profile_after = validate_profile(profile_path, args.expected_profile_sha256)
        except Exception:
            restore_descriptor, restore_name = tempfile.mkstemp(
                dir=overlay_path.parent,
                prefix=".issue55-rollback-",
                suffix=".tmp",
            )
            os.close(restore_descriptor)
            restore_temp = Path(restore_name)
            try:
                shutil.copy2(backup_path, restore_temp)
                os.replace(restore_temp, overlay_path)
                rollback_performed = True
            finally:
                if restore_temp.exists():
                    restore_temp.unlink()
            raise
    finally:
        if temporary.exists():
            temporary.unlink()

    report = {
        "format_version": 1,
        "verdict": "PRODUCTION_WRITE_COMPLETE_AWAITING_UI_ACCEPTANCE",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_root": str(runtime_root),
        "source": {
            "path": str(source),
            "sha256": source_hash,
            "rows": len(rows),
            "unique_canonicals": len({row.canonical for row in rows}),
        },
        "mapping": {
            "canonical_identity_exact": True,
            "canonical_order_preserved": True,
            "display_ja_exact": True,
            "search_ja_exact_single_item_list": True,
            "unknown_canonical_count": 0,
            "duplicate_canonical_count": 0,
            "unrelated_entry_fields": 0,
            "utf8_roundtrip": True,
            "production_loader_validation": True,
        },
        "overlay": {
            "path": str(overlay_path),
            "pre_sha256": original_hash,
            "pre_size": original_size,
            "pre_entries": len(original_document["entries"]),
            "temporary_sha256": temporary_hash,
            "temporary_size": temporary_size,
            "post_sha256": post_hash,
            "post_size": overlay_path.stat().st_size,
            "post_entries": len(document["entries"]),
            "loader_display_count": len(promoted_overlay.display_by_canonical),
            "loader_search_count": len(promoted_overlay.search_by_canonical),
            "atomic_replace": replaced,
        },
        "rollback": {
            "path": str(backup_path),
            "sha256": sha256(backup_path),
            "available": backup_path.is_file(),
            "automatic_rollback_performed": rollback_performed,
        },
        "issue49_profile_before": profile_before,
        "issue49_profile_after": profile_after,
        "issue49_profile_unchanged": profile_before == profile_after,
    }
    atomic_write_json(args.report.resolve(), report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-overlay-sha256", required=True)
    parser.add_argument("--expected-overlay-size", type=int, required=True)
    parser.add_argument("--expected-profile-sha256", required=True)
    return parser.parse_args()


def main() -> None:
    print(json.dumps(promote(parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
