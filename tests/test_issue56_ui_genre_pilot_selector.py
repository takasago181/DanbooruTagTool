import csv
import json
from collections import Counter
from pathlib import Path

from tools.issue56_ui_genre_pilot_selector import (
    OTHER_PREFIX,
    build_tag_lookup,
    load_prompt_reference,
    resolve_alias_target,
    select_pilot,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "special2788" / "prompt_reference"
TAXONOMY = ROOT / "docs" / "issue56" / "pilot" / "issue56_ui_genre_taxonomy_candidate_v1_2.json"
CLASSIFICATION_MAP = ROOT / "docs" / "issue56" / "pilot" / "issue56_ui_genre_pilot_v1_classification_map.csv"


def _pilot_rows(pilot):
    return [item["row"] for item in pilot]


def _taxonomy_indexes():
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    genres = {genre["id"]: genre for genre in taxonomy["genres"]}
    subgenres = {
        genre_id: {subgenre["id"]: subgenre for subgenre in genre["subgenres"]}
        for genre_id, genre in genres.items()
    }
    return taxonomy, genres, subgenres


def _classification_rows():
    with CLASSIFICATION_MAP.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_prompt_reference_materializes_all_2788_unique_special_ids():
    rows, source_hashes = load_prompt_reference(SOURCE_DIR)
    assert len(rows) == 2788
    assert len({row.special_id for row in rows}) == 2788
    assert {row.special_id for row in rows} == set(range(1, 2789))
    assert source_hashes
    assert any(name.startswith(OTHER_PREFIX) for name in source_hashes)


def test_pilot_is_exactly_150_unique_rows_with_expected_strata():
    rows, _ = load_prompt_reference(SOURCE_DIR)
    pilot = select_pilot(rows)
    selected = _pilot_rows(pilot)

    assert len(pilot) == 150
    assert len({row.special_id for row in selected}) == 150

    counts = Counter(str(item["selection_stratum"]) for item in pilot)
    assert counts == {
        "HIGH_USAGE_OTHER": 50,
        "ALIAS": 15,
        "ALIAS_CANONICAL_CONTROL": 15,
        "BOUNDARY_BODY_EXPOSURE": 6,
        "BOUNDARY_ACTIVITY_CONTACT": 6,
        "BOUNDARY_TOOLS_BDSM": 6,
        "BOUNDARY_ROLE_META_CONTEXT": 6,
        "BOUNDARY_INJURY_BODY_BDSM": 6,
        "RARE_NUMERIC": 10,
        "RARE_NONCOUNT": 10,
        "RANDOM": 20,
    }


def test_high_usage_stratum_is_global_across_all_other_parts_not_file_order():
    rows, _ = load_prompt_reference(SOURCE_DIR)
    pilot = select_pilot(rows)

    actual = [
        item["row"].special_id
        for item in pilot
        if item["selection_stratum"] == "HIGH_USAGE_OTHER"
    ]
    expected_rows = sorted(
        (
            row
            for row in rows
            if row.source_file.startswith(OTHER_PREFIX)
            and not row.is_alias
            and row.post_count is not None
        ),
        key=lambda row: (-int(row.post_count or 0), row.special_id),
    )[:50]
    assert actual == [row.special_id for row in expected_rows]
    assert len({row.source_file for row in expected_rows}) > 1


def test_alias_controls_are_resolvable_pairs_and_keep_pair_groups_together():
    rows, _ = load_prompt_reference(SOURCE_DIR)
    pilot = select_pilot(rows)
    lookup = build_tag_lookup(rows)

    alias_items = [item for item in pilot if item["selection_stratum"] == "ALIAS"]
    controls = {
        str(item["pair_group"]): item["row"]
        for item in pilot
        if item["selection_stratum"] == "ALIAS_CANONICAL_CONTROL"
    }

    assert len(alias_items) == 15
    assert len(controls) == 15
    for item in alias_items:
        alias = item["row"]
        group = str(item["pair_group"])
        target = resolve_alias_target(alias, lookup)
        assert target is not None
        assert group in controls
        assert controls[group].special_id == target.special_id


def test_rare_numeric_and_noncount_are_distinct_and_correctly_typed():
    rows, _ = load_prompt_reference(SOURCE_DIR)
    pilot = select_pilot(rows)

    rare_numeric = [
        item["row"] for item in pilot if item["selection_stratum"] == "RARE_NUMERIC"
    ]
    rare_noncount = [
        item["row"] for item in pilot if item["selection_stratum"] == "RARE_NONCOUNT"
    ]

    assert len(rare_numeric) == 10
    assert all(row.post_count is not None and not row.is_alias for row in rare_numeric)
    assert len(rare_noncount) == 10
    assert all(row.post_count is None and not row.is_alias for row in rare_noncount)
    assert not ({row.special_id for row in rare_numeric} & {row.special_id for row in rare_noncount})


def test_selection_is_deterministic():
    rows, _ = load_prompt_reference(SOURCE_DIR)
    first = [item["row"].special_id for item in select_pilot(rows)]
    second = [item["row"].special_id for item in select_pilot(rows)]
    assert first == second


def test_taxonomy_has_unique_ids_and_mandatory_japanese_labels():
    taxonomy, genres, subgenres = _taxonomy_indexes()
    assert taxonomy["display_contract"]["normal_ui_genre_language"] == "ja"
    assert taxonomy["display_contract"]["special_row"] == "ja_plus_en"
    assert len(genres) == 14
    assert all(genre["label_ja"].strip() for genre in genres.values())
    for genre_id, items in subgenres.items():
        assert len(items) == len(genres[genre_id]["subgenres"])
        assert all(item["label_ja"].strip() for item in items.values())


def test_reviewed_classification_map_matches_exact_formal_pilot_ids():
    source_rows, _ = load_prompt_reference(SOURCE_DIR)
    pilot_ids = [str(item["row"].special_id) for item in select_pilot(source_rows)]
    reviewed = _classification_rows()
    reviewed_ids = [row["special_id"] for row in reviewed]

    assert len(reviewed) == 150
    assert len(set(reviewed_ids)) == 150
    assert set(reviewed_ids) == set(pilot_ids)


def test_reviewed_paths_reference_only_defined_taxonomy_ids():
    _, genres, subgenres = _taxonomy_indexes()
    reviewed = _classification_rows()

    def validate_path(path: str):
        if not path:
            return
        parts = path.split(">", 1)
        genre_id = parts[0].strip()
        subgenre_id = parts[1].strip() if len(parts) == 2 else ""
        assert genre_id in genres
        if subgenre_id:
            assert subgenre_id in subgenres[genre_id]

    for row in reviewed:
        status = row["classification_status"]
        assert status in {"HUMAN_REVIEWED", "AUTO_INHERITED_ALIAS", "REVIEW_REQUIRED", "AMBIGUOUS"}

        genre_id = row["primary_genre_id"].strip()
        subgenre_id = row["primary_subgenre_id"].strip()
        if status in {"REVIEW_REQUIRED", "AMBIGUOUS"} and not genre_id:
            assert row["ambiguity_note"].strip()
        else:
            assert genre_id in genres
            if subgenre_id:
                assert subgenre_id in subgenres[genre_id]

        for secondary_path in row["secondary_paths"].split("|"):
            validate_path(secondary_path.strip())


def test_reviewed_map_keeps_unresolved_cases_exceptional():
    reviewed = _classification_rows()
    unresolved = [
        row for row in reviewed if row["classification_status"] in {"REVIEW_REQUIRED", "AMBIGUOUS"}
    ]
    assert 0 < len(unresolved) <= 5
