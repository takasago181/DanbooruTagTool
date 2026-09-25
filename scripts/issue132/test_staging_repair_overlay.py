#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from staging_repair_overlay import SCHEMA, git_blob_sha, resolve_repair_overlay


def make_overlay(source: Path, lane: int, start: int, end: int, supersedes=None):
    window = {
        "schema_version": "issue132-pass-a-staging-window-v2",
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "parent_neutral_sha256": "x",
        "parent_identity_order_sha256": "y",
        "rows": [],
        "holds": [],
    }
    return {
        "schema_version": SCHEMA,
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "source_staging_path": source.as_posix(),
        "source_staging_blob_sha": git_blob_sha(source.read_bytes()),
        "repair_reason_codes": ["STRUCTURAL_REBUILD"],
        "supersedes": list(supersedes or []),
        "effective_window": window,
    }


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source = root / "window_000001_000025.json"
        source.write_text('{"raw":"source"}\n', encoding="utf-8")
        repair_dir = root / "repairs"
        repair_dir.mkdir()

        # One valid active overlay.
        p1 = repair_dir / "repair_000001_000025_v001.json"
        p1.write_text(json.dumps(make_overlay(source, 1, 1, 25)), encoding="utf-8")
        window, name, errors = resolve_repair_overlay(source, 1, 1, 25)
        assert not errors, errors
        assert name == p1.name
        assert window is not None

        # A malformed older overlay must be recoverable when a newer valid
        # overlay explicitly supersedes it.
        p1.write_text("{", encoding="utf-8")
        p2 = repair_dir / "repair_000001_000025_v002.json"
        p2.write_text(
            json.dumps(make_overlay(source, 1, 1, 25, [p1.name])),
            encoding="utf-8",
        )
        window, name, errors = resolve_repair_overlay(source, 1, 1, 25)
        assert not errors, errors
        assert name == p2.name
        assert window is not None

        # A second unsuperseded leaf must fail closed.
        p3 = repair_dir / "repair_000001_000025_v003.json"
        p3.write_text(json.dumps(make_overlay(source, 1, 1, 25)), encoding="utf-8")
        window, name, errors = resolve_repair_overlay(source, 1, 1, 25)
        assert window is None
        assert name is None
        assert errors

    print("PASS: staging repair overlay supersession")


if __name__ == "__main__":
    main()
