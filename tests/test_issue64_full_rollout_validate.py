import csv

from tools.issue64_full_rollout_validate import (
    FULL_ROOT,
    REPO_ROOT,
    normalize_row,
    parse_path,
    parse_secondary,
    validate_effective,
)
from tools.issue64_full_rollout_rework import _apply_semantic_corrections, _correct_path


TAXONOMY = {
    "genres": {
        "CLOTHING": {"label_ja": "衣装", "subgenres": {"UNIFORM": "制服・ユニフォーム"}},
        "OBJECT_PROP": {"label_ja": "道具・小物", "subgenres": {"WEAPON": "武器・戦闘道具", "DAILY": "日用品"}},
        "LIVING_NATURE": {"label_ja": "生き物・植物", "subgenres": {"CREATURE": "生き物"}},
        "ACTION_CONTACT": {"label_ja": "行為・接触", "subgenres": {"INTERACTION": "接触", "OBJECT_USE": "物を使う"}},
        "POSE_MOVEMENT": {"label_ja": "ポーズ・動き", "subgenres": {}},
        "STYLE_QUALITY_META": {"label_ja": "画風・加工・画面表現", "subgenres": {}},
    }
}


def test_parse_primary_paths_and_empty_path():
    assert parse_path("CLOTHING/UNIFORM") == ("CLOTHING", "UNIFORM")
    assert parse_path("PERSON_COUNT") == ("PERSON_COUNT", None)
    assert parse_path("") is None


def test_reject_malformed_path_depth():
    try:
        parse_path("A/B/C")
    except ValueError as exc:
        assert "invalid path syntax" in str(exc)
    else:
        raise AssertionError("path deeper than genre/subgenre must be rejected")


def test_parse_secondary_json_and_path_strings():
    assert parse_secondary('["CLOTHING/UNIFORM", "PERSON_COUNT"]') == [
        ("CLOTHING", "UNIFORM"),
        ("PERSON_COUNT", None),
    ]
    assert parse_secondary('[{"genre_id":"OBJECT_PROP","subgenre_id":"FOOD"}]') == [
        ("OBJECT_PROP", "FOOD")
    ]


def test_parse_historical_japanese_secondary_paths_and_legacy_case():
    assert parse_secondary("画風・加工・画面表現", TAXONOMY) == [("STYLE_QUALITY_META", None)]
    assert parse_secondary("道具・小物 → 武器・戦闘道具", TAXONOMY) == [("OBJECT_PROP", "WEAPON")]
    assert parse_secondary("衣装 → 制服・ユニフォーム | 道具・小物 → 武器・戦闘道具", TAXONOMY) == [
        ("CLOTHING", "UNIFORM"),
        ("OBJECT_PROP", "WEAPON"),
    ]
    assert normalize_row(
        {
            "canonical": "tank",
            "classification_status": "PROPOSED",
            "primary_path": "object_prop/vehicle",
            "confidence": "HIGH",
        },
        1,
        TAXONOMY,
    )["primary_path"] == ("OBJECT_PROP", "VEHICLE")


def test_normalize_legacy_and_late_batch_schemas():
    legacy = normalize_row(
        {
            "global_row": "15",
            "canonical": "blue_hair",
            "classification_status": "PROPOSED",
            "primary_genre_id": "HAIR_FACE",
            "primary_subgenre_id": "",
            "secondary_paths": "[]",
            "confidence": "HIGH",
        },
        implied_global_row=10,
    )
    late = normalize_row(
        {
            "canonical": "blue_hair",
            "classification_status": "PROPOSED",
            "primary_path": "HAIR_FACE",
            "secondary_path": "",
            "confidence": "HIGH",
        },
        implied_global_row=16,
    )
    assert legacy["global_row"] == 15
    assert late["global_row"] == 16
    assert legacy["primary_path"] == late["primary_path"] == ("HAIR_FACE", None)


def test_invalid_subgenre_uses_only_explicit_alias_or_honest_top_level():
    assert _correct_path(("LIVING_NATURE", "ANIMAL"), TAXONOMY) == (
        ("LIVING_NATURE", "CREATURE"),
        "explicit_alias:ANIMAL->CREATURE",
    )
    assert _correct_path(("OBJECT_PROP", "DEVICE"), TAXONOMY) == (
        ("OBJECT_PROP", None),
        "top_level_fallback:DEVICE",
    )


def test_relation_boundary_scan_moves_object_contact_but_keeps_body_posture():
    rows = {
        name: {
            "status": "PROPOSED",
            "primary_path": ("POSE_MOVEMENT", None),
            "secondary_paths": [],
            "confidence": "HIGH",
            "source_correction_ids": [],
            "reason": "",
        }
        for name in ("standing_on_box", "standing_on_one_leg")
    }
    changes = _apply_semantic_corrections(rows, TAXONOMY)
    assert rows["standing_on_box"]["primary_path"] == ("ACTION_CONTACT", "INTERACTION")
    assert rows["standing_on_one_leg"]["primary_path"] == ("POSE_MOVEMENT", None)
    assert [change["canonical"] for change in changes] == ["standing_on_box"]


def test_effective_rollout_validates_all_30629_rows():
    report = validate_effective(REPO_ROOT)
    assert report["pass"] is True, report["errors"]
    assert report["population_count"] == 30_629
    assert report["effective_row_count"] == 30_629
    assert report["batch_count"] == 36
    assert report["recovered_rows"] == 1_200
    assert report["batch034_path_correction_rows"] == 721
    assert report["residual_candidate_review_rows"] == 76
    assert report["invalid_path_counts"] == {}
    assert report["source_hash_verification"] == "PASS"
    assert report["warnings"] == []


def test_targeted_review_corrections_and_ambiguous_rows_are_preserved():
    sidecar = REPO_ROOT / FULL_ROOT / "effective_sidecar.csv"
    with sidecar.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = {row["canonical"]: row for row in csv.DictReader(stream)}

    assert rows["pink_nails"]["primary_path"] == "BODY_PART"
    for canonical in (
        "cropped_arm",
        "cropped_arms",
        "cropped_head",
        "cropped_legs",
        "cropped_shoulders",
        "cropped_torso",
    ):
        assert rows[canonical]["primary_path"] == "COMPOSITION_CAMERA"
    assert rows["cropped_cardigan"]["primary_path"] == "CLOTHING/ACCESSORY"
    assert rows["cropped_hoodie"]["primary_path"] == "CLOTHING/EVERYDAY"
    assert rows["studio_microphone"]["primary_path"] == "OBJECT_PROP/DAILY"
    assert rows["vocaloid_boxart_pose"]["primary_path"] == "POSE_MOVEMENT"
    assert rows["standing_on_chair"]["primary_path"] == "ACTION_CONTACT/INTERACTION"
    assert rows["sarcophagus"]["primary_path"] == "OBJECT_PROP"
    assert rows["waiter"]["primary_path"] == "PERSON_COUNT"
    assert rows["waitress"]["classification_status"] == "UNRESOLVED"
    assert rows["headshot"]["classification_status"] == "UNRESOLVED"


def test_final_residual_review_is_bounded_and_matches_effective_sidecar():
    review_path = REPO_ROOT / FULL_ROOT / "corrections/residual_candidate_review.csv"
    sidecar_path = REPO_ROOT / FULL_ROOT / "effective_sidecar.csv"
    with review_path.open("r", encoding="utf-8-sig", newline="") as stream:
        candidates = list(csv.DictReader(stream))
    with sidecar_path.open("r", encoding="utf-8-sig", newline="") as stream:
        effective = {row["canonical"]: row for row in csv.DictReader(stream)}

    assert len(candidates) == 76
    assert len({row["canonical"] for row in candidates}) == 76
    assert sum(row["candidate_family"].startswith("relation_contact_") for row in candidates) == 48
    assert sum(row["candidate_family"] == "batch034_water_identity" for row in candidates) == 25
    assert sum(row["candidate_family"] == "calendar_event_boundary" for row in candidates) == 2

    unresolved = {row["canonical"] for row in candidates if row["disposition"] == "UNRESOLVED"}
    assert unresolved == {
        "2011",
        "father's_day",
        "water_drop",
        "water_on_glass",
        "water_stream",
        "water_type_theme_(pokemon)",
    }
    assert effective["two-tone_leg_warmers"]["primary_path"] == "CLOTHING"
    assert effective["water_drop_hair_ornament"]["primary_path"] == "CLOTHING/ACCESSORY"
    for canonical in unresolved:
        assert effective[canonical]["classification_status"] == "UNRESOLVED"
        assert effective[canonical]["primary_path"] == ""
