import csv
import json
from pathlib import Path

import pytest

from danbooru_tag_tool.japanese_overlay import JapaneseOverlay
from tools.issue55_promote_japanese_overlay import (
    EXPECTED_SOURCE_ROWS,
    SOURCE_COLUMNS,
    build_document,
    load_source_table,
    validate_document,
    validate_temp_with_loader,
)


def _rows(path: Path, count: int = EXPECTED_SOURCE_ROWS):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SOURCE_COLUMNS)
        writer.writeheader()
        for index in range(count):
            writer.writerow({
                "canonical": f"tag_{index:05d}",
                "display_ja": f"表示{index}",
                "search_ja": f"検索{index}",
                "source_state": "",
                "decision": "KEEP",
                "display_verdict": "ACCEPT",
                "search_verdict": "ACCEPT",
                "risk_class": "LOW",
                "review_mode": "TEST",
                "language_sanity_provenance": "TEST",
            })


def test_v5_mapping_is_exact_and_loader_compatible(tmp_path):
    source = tmp_path / "v5.csv"
    _rows(source)
    rows = load_source_table(source)
    canonical = {row.canonical: object() for row in rows}
    document = build_document(rows)
    validate_document(document, rows, canonical)

    output = tmp_path / "japanese_overlay.json"
    output.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    overlay = validate_temp_with_loader(output, rows, canonical)

    first = rows[0]
    assert document["entries"][first.canonical] == {
        "display_ja": first.display_ja,
        "search_ja": [first.search_ja],
    }
    assert overlay.search_by_canonical[first.canonical] == (
        first.display_ja,
        first.search_ja,
    )


def test_v5_duplicate_canonical_fails_closed(tmp_path):
    source = tmp_path / "v5.csv"
    _rows(source)
    rows = list(csv.DictReader(source.open(encoding="utf-8")))
    rows[-1]["canonical"] = rows[0]["canonical"]
    with source.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SOURCE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match="Duplicate V5 canonical"):
        load_source_table(source)


def test_production_unknown_canonical_fails_closed(tmp_path):
    source = tmp_path / "v5.csv"
    _rows(source)
    rows = load_source_table(source)
    document = build_document(rows)
    canonical = {row.canonical: object() for row in rows[1:]}

    with pytest.raises(ValueError, match="unknown canonicals"):
        validate_document(document, rows, canonical)


def test_loader_rejects_unrelated_entry_fields(tmp_path):
    source = tmp_path / "v5.csv"
    _rows(source)
    rows = load_source_table(source)
    document = build_document(rows)
    document["entries"][rows[0].canonical]["extra"] = "forbidden"

    with pytest.raises(ValueError, match="Unexpected production entry fields"):
        validate_document(document, rows, {row.canonical: object() for row in rows})
