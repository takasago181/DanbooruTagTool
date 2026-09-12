import csv
import json
from pathlib import Path

import pytest

from tools.issue56_ui_genre_pilot_selector import OTHER_PREFIX, load_prompt_reference
from tools.issue56_ui_genre_rollout import (
    PILOT_MAP_PATH,
    REVIEWED_DIR,
    ROOT,
    RolloutError,
    build_outputs,
    load_taxonomy,
    merge_mapping_sources,
    validate_mapping,
)


def _read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_frozen_taxonomy_is_exact_audited_shape_without_visible_other():
    taxonomy, genres, subgenres = load_taxonomy()
    assert taxonomy["status"] == "FROZEN_FOR_FULL_ROLLOUT"
    assert taxonomy["audit_gate"]["issue"] == 59
    assert taxonomy["audit_gate"]["verdict"] == "PASS"
    assert taxonomy["audit_gate"]["comment_id"] == 5642183508
    assert len(genres) == 14
    assert sum(len(items) for items in subgenres.values()) == 38

    for genre in genres.values():
        assert genre["label_ja"].strip()
        assert "その他" not in genre["label_ja"]
        assert not genre["id"].startswith("OTHER")
        for subgenre in genre["subgenres"]:
            assert subgenre["label_ja"].strip()
            assert "その他" not in subgenre["label_ja"]
            assert not subgenre["id"].startswith("OTHER")


def test_rollout_seed_is_exact_audited_150_pilot_rows():
    pilot = _read_csv(PILOT_MAP_PATH)
    mappings, origins = merge_mapping_sources(PILOT_MAP_PATH, REVIEWED_DIR)
    assert len(pilot) == 150
    assert len({row["special_id"] for row in pilot}) == 150
    assert set(int(row["special_id"]) for row in pilot).issubset(mappings)
    assert all(special_id in origins for special_id in mappings)


def test_partial_rollout_validates_against_frozen_2788_source():
    rows, _ = load_prompt_reference(ROOT / "data" / "special2788" / "prompt_reference")
    _, genres, subgenres = load_taxonomy()
    mappings, _ = merge_mapping_sources()
    meta = validate_mapping(rows, mappings, genres, subgenres)

    assert len(rows) == 2788
    assert {row.special_id for row in rows} == set(range(1, 2789))
    assert meta["mapped_total"] >= 150
    assert meta["unmapped_total"] == 2788 - meta["mapped_total"]
    assert meta["old_other_total"] == sum(
        1 for row in rows if row.source_file.startswith(OTHER_PREFIX)
    )
    assert meta["old_other_mapped"] + meta["old_other_unmapped"] == meta["old_other_total"]


def test_partial_rollout_builds_old_other_review_queue_without_auto_classification(tmp_path):
    meta = build_outputs(tmp_path)
    queue_path = tmp_path / "issue56_old_other_unmapped_v1.csv"
    partial_path = tmp_path / "issue56_ui_genre_mapping_partial_v1.csv"
    meta_path = tmp_path / "issue56_ui_genre_rollout_meta_v1.json"

    assert queue_path.exists()
    assert partial_path.exists()
    assert meta_path.exists()

    queue = _read_csv(queue_path)
    partial = _read_csv(partial_path)
    saved_meta = json.loads(meta_path.read_text(encoding="utf-8"))

    assert len(queue) == meta["old_other_unmapped"]
    assert len(partial) == meta["mapped_total"]
    assert saved_meta["mapped_total"] == meta["mapped_total"]
    assert all(row["source_file"].startswith(OTHER_PREFIX) for row in queue)
    assert not any("primary_genre_id" in row for row in queue)


def test_require_complete_fails_closed_until_all_2788_are_reviewed():
    rows, _ = load_prompt_reference(ROOT / "data" / "special2788" / "prompt_reference")
    _, genres, subgenres = load_taxonomy()
    mappings, _ = merge_mapping_sources()
    with pytest.raises(RolloutError, match="complete rollout required"):
        validate_mapping(rows, mappings, genres, subgenres, require_complete=True)


def test_removed_other_body_site_cannot_reappear_in_frozen_taxonomy():
    _, _, subgenres = load_taxonomy()
    all_subgenre_ids = {item for items in subgenres.values() for item in items}
    assert "OTHER_BODY_SITE" not in all_subgenre_ids
