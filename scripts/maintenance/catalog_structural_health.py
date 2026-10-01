"""Generic read-only health check for the current full runtime catalog."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from contextlib import closing
from collections import Counter
from pathlib import Path
from typing import Any

VALIDATOR_ID = "dtt.catalog-structural-health"
VALIDATOR_VERSION = "2.0.0"
VALID_CATEGORIES = {"General", "Special", "Character", "Copyright", "Artist"}
REQUIRED_COLUMNS = {"id", "canonical", "ordinal", "payload"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def validate(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        quick = db.execute("PRAGMA quick_check").fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchall()
        foreign = db.execute("PRAGMA foreign_key_check").fetchall()
        if quick != [("ok",)] or integrity != [("ok",)] or foreign:
            raise ValueError(f"SQLite integrity failure: quick={quick[:3]} integrity={integrity[:3]} foreign={len(foreign)}")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version != 1:
            raise ValueError(f"unsupported catalog schema version {version!r}")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"entries", "metadata"}.issubset(tables):
            raise ValueError(f"required catalog tables missing: {sorted({'entries', 'metadata'} - tables)}")
        columns = {row[1] for row in db.execute("PRAGMA table_info(entries)")}
        if not REQUIRED_COLUMNS.issubset(columns):
            raise ValueError(f"entries schema missing columns: {sorted(REQUIRED_COLUMNS - columns)}")
        id_definition = next((row for row in db.execute("PRAGMA table_info(entries)") if row[1] == "id"), None)
        if id_definition is None or id_definition[5] != 1:
            raise ValueError("entries.id must remain the primary identity key")
        metadata_columns = {row[1] for row in db.execute("PRAGMA table_info(metadata)")}
        if "provenance" not in metadata_columns:
            raise ValueError("metadata.provenance is required")
        total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        if not total:
            raise ValueError("catalog has no entries")
        distinct_ids = db.execute("SELECT COUNT(DISTINCT id) FROM entries").fetchone()[0]
        if distinct_ids != total:
            raise ValueError("catalog contains duplicate entry IDs")
        categories: Counter[str] = Counter()
        for index, (entry_id, canonical, ordinal, raw) in enumerate(db.execute("SELECT id, canonical, ordinal, payload FROM entries ORDER BY ordinal")):
            if not isinstance(entry_id, str) or not entry_id:
                raise ValueError(f"empty entry id at ordinal {index}: {entry_id!r}")
            if ordinal != index:
                raise ValueError(f"ordinal sequence must be contiguous from 0; row {index} has {ordinal!r}")
            try:
                payload = json.loads(raw)
            except (TypeError, json.JSONDecodeError) as error:
                raise ValueError(f"invalid payload JSON at ordinal {index}: {error}") from error
            if not isinstance(payload, dict):
                raise ValueError(f"payload at ordinal {index} must be an object")
            if payload.get("Id") != entry_id or payload.get("Canonical") != canonical:
                raise ValueError(f"database identity columns disagree with payload at ordinal {index}")
            category = payload.get("TagCategory") or ("Special" if payload.get("IsSpecial") is True else "General")
            if category not in VALID_CATEGORIES:
                raise ValueError(f"unknown category at ordinal {index}: {category!r}")
            if not isinstance(payload.get("IsSpecial"), bool) or not isinstance(payload.get("English"), str) or not isinstance(payload.get("Aliases"), list):
                raise ValueError(f"catalog reader required fields invalid at ordinal {index}")
            categories[category] += 1
    return {
        "ok": True,
        "validator": {"id": VALIDATOR_ID, "version": VALIDATOR_VERSION, "sha256": sha256(Path(__file__).resolve())},
        "path": str(path.resolve()), "schema_version": version,
        "quick_check": "ok", "integrity_check": "ok", "foreign_key_rows": 0,
        "total": total, "category_counts": dict(sorted(categories.items())),
        "ids_unique": True, "ordinals_contiguous": True, "payloads_valid": True,
        "catalog_sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only structural health for a full runtime catalog")
    parser.add_argument("--catalog", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.catalog), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as error:  # concise CLI failure
        print(json.dumps({"ok": False, "validator": VALIDATOR_ID, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
