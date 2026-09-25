#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

from staging_v2 import (
    compact_row_to_full,
    identity_sha256,
    validate_compact_hold,
    validate_identity_binding,
)

ROOT = Path(__file__).resolve().parents[2]


def load_base():
    p = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    s = importlib.util.spec_from_file_location("issue132_staging_v2_test_base", p)
    if s is None or s.loader is None:
        raise SystemExit("cannot load base validator")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def main():
    base = load_base()
    expected = {"review_seq": "1", "identity_key": "sample_identity"}
    row = {
        "lane_local_index": 1,
        "review_seq": 1,
        "identity_sha256": identity_sha256(expected["identity_key"]),
        "discovery_mode": "BROWSE_WORTHY",
        "routes": [{"id": "CLOTHING_EXPOSURE", "strength": "CORE"}],
        "local_refinement_ids": ["CLOTHING/ACCESSORY"],
        "body_site_ids": [],
        "theme_ids": [],
        "route_vocabulary_gap": "NO",
        "review_depth": "CHECKED",
        "evidence_urls": [],
    }
    assert validate_identity_binding(row, expected, 1) == []
    full = compact_row_to_full(row, expected, base.FIELDS)
    assert full["identity_key"] == "sample_identity"
    assert full["semantic_summary_ja"]
    assert full["route_1_reason_ja"]
    assert base.validate_row(full, 1) == []

    hold = {
        "lane_local_index": 1,
        "review_seq": 1,
        "identity_sha256": identity_sha256(expected["identity_key"]),
        "reason_code": "DIRECT_EVIDENCE_NOT_FOUND",
        "research_attempt_codes": ["DANBOORU_EXACT"],
    }
    assert validate_compact_hold(hold, expected, 1) == []
    print("staging_v2 self-test: PASS")


if __name__ == "__main__":
    main()
