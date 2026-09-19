"""Read-only SQLite/catalog checks used by the local maintenance scripts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_VERSION = "ordinary-catalog-v2-33688-special3059"

STATUS_NAMES = {
    0: "AutoCandidate",
    1: "HumanResolved",
    2: "ReferenceOnlyNoDirectBrowse",
    3: "DeferProductFitReview",
    4: "OutOfScopeNoBrowse",
}
EXPECTED_STATUS = {
    "AutoCandidate": 2718,
    "HumanResolved": 315,
    "ReferenceOnlyNoDirectBrowse": 21,
    "DeferProductFitReview": 5,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def checker_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "contract_version": CONTRACT_VERSION,
    }


def check_db(path: Path, *, catalog: bool) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = f"file:{path.resolve()}?mode=ro&immutable=1"
    with sqlite3.connect(uri, uri=True) as connection:
        quick = connection.execute("PRAGMA quick_check").fetchone()[0]
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
        if quick != "ok" or integrity != "ok" or foreign:
            raise RuntimeError(
                f"SQLite check failed for {path}: quick={quick}, integrity={integrity}, foreign={foreign}"
            )

        if catalog:
            rows = connection.execute(
                "SELECT id, canonical, ordinal, payload FROM entries ORDER BY ordinal"
            ).fetchall()
            if not rows:
                raise RuntimeError("catalog has no entries")
            payloads = [json.loads(row[3]) for row in rows]
            ids = [row[0] for row in rows]
            ordinals = [row[2] for row in rows]
            special = [payload for payload in payloads if payload.get("IsSpecial") is True]
            general = [payload for payload in payloads if payload.get("IsSpecial") is False]
            special_v2 = [payload.get("SpecialBrowseV2") for payload in special]
            statuses = Counter(
                STATUS_NAMES.get(item.get("Status"), f"Unknown({item.get('Status')})")
                for item in special_v2
                if item is not None
            )
            general_product_fit = Counter(payload.get("ProductFit") for payload in general)
            categories = Counter(payload.get("EffectiveCategory") for payload in payloads)
            result: dict[str, Any] = {
                "path": str(path),
                "quick_check": quick,
                "integrity_check": integrity,
                "foreign_key_rows": len(foreign),
                "total": len(rows),
                "special": len(special),
                "general": len(general),
                "special_browse_v2": len([item for item in special_v2 if item is not None]),
                "special_status": dict(statuses),
                "general_product_fit": dict(general_product_fit),
                "ordinals_contiguous": ordinals == list(range(len(rows))),
                "ids_unique": len(set(ids)) == len(ids),
                "general_canonical_unique": len({payload.get("Canonical") for payload in general}) == len(general),
                "character": categories.get("Character", 0),
                "copyright": categories.get("Copyright", 0),
                "artist": categories.get("Artist", 0),
            }
            expected = {
                "total": 33688,
                "special": 3059,
                "general": 30629,
                "special_browse_v2": 3059,
            }
            for key, value in expected.items():
                if result[key] != value:
                    raise RuntimeError(f"catalog invariant {key}={result[key]!r}, expected {value!r}")
            for key in ("character", "copyright", "artist"):
                if result[key] != 0:
                    raise RuntimeError(f"ordinary catalog category {key}={result[key]!r}, expected 0")
            if result["special_status"] != EXPECTED_STATUS:
                raise RuntimeError(f"#76 status distribution changed: {result['special_status']}")
            if not result["ordinals_contiguous"] or not result["ids_unique"] or not result["general_canonical_unique"]:
                raise RuntimeError("catalog identity/ordinal invariant failed")
            result["ok"] = True
            return result

        row = connection.execute("SELECT version, payload FROM user_state WHERE id = 1").fetchone()
        if row is None:
            raise RuntimeError("user.db has no id=1 state")
        payload = json.loads(row[1])
        result = {
            "path": str(path),
            "quick_check": quick,
            "integrity_check": integrity,
            "foreign_key_rows": len(foreign),
            "version": row[0],
            "payload_json": True,
            "ok": True,
        }
        if row[0] != 1:
            raise RuntimeError(f"unexpected user state version: {row[0]}")
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only catalog and UserData SQLite health check")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--userdb", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = {
            "catalog": check_db(args.catalog, catalog=True),
            "userdb": check_db(args.userdb, catalog=False),
            "read_only": True,
            "checker": checker_metadata(),
        }
    except Exception as error:  # noqa: BLE001 - concise CLI failure is intentional
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
