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


def _pilot_rows(pilot):
    return [item["row"] for item in pilot]


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
