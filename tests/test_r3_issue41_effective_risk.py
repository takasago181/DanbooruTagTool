from __future__ import annotations

import json
from pathlib import Path

import pytest

from translation_quarantine.r3.r3_issue41_build_blind import BLIND_QUOTAS, select_effective
from translation_quarantine.r3.r3_issue41_effective_risk import (
    apply_effective_risk,
    apply_file,
    load_overrides,
)


def _pilot(canonical: str, ordinal: int, risk: str, *, semantic: bool = True) -> dict:
    return {
        "pilot_ordinal": ordinal,
        "canonical": canonical,
        "risk_class": risk,
        "semantic_evidence_ids": [f"scope:{canonical}"] if semantic else [],
        "display_state": "READY",
        "search_state": "READY",
        "bridge32_state": "READY",
        "row_state": "READY",
        "reason_codes": [],
    }


def _override(
    canonical: str,
    ordinal: int,
    selection: str,
    effective: str,
    **extra,
) -> dict:
    return {
        "canonical": canonical,
        "pilot_ordinal": ordinal,
        "selection_risk_class": selection,
        "effective_risk_class": effective,
        "reason": "fixture",
        "frozen": True,
        **extra,
    }


def test_required_known_underclassifications_are_applied_and_fail_closed_without_scope():
    rows = [
        _pilot("all_fours", 1, "LOW", semantic=False),
        _pilot("fellatio", 2, "LOW", semantic=False),
        _pilot("loli", 3, "LOW", semantic=False),
    ]
    overrides = {
        "all_fours": _override("all_fours", 1, "LOW", "HIGH_POSE_ACTION"),
        "fellatio": _override("fellatio", 2, "LOW", "HIGH_ANATOMY_ADULT"),
        "loli": _override("loli", 3, "LOW", "CRITICAL"),
    }
    out = apply_effective_risk(rows, overrides)
    by_canonical = {row["canonical"]: row for row in out}
    assert by_canonical["all_fours"]["effective_risk_class"] == "HIGH_POSE_ACTION"
    assert by_canonical["fellatio"]["effective_risk_class"] == "HIGH_ANATOMY_ADULT"
    assert by_canonical["loli"]["effective_risk_class"] == "CRITICAL"
    assert all(row["display_state"] == "REVIEW" for row in out)
    assert all(row["row_state"] == "REVIEW" for row in out)
    assert all(
        "EFFECTIVE_HIGH_OR_CRITICAL_MISSING_EXACT_CANONICAL_SCOPE" in row["reason_codes"]
        for row in out
    )


def test_override_validation_rejects_downgrade_duplicate_unknown_and_nonfrozen(
    tmp_path: Path,
):
    path = tmp_path / "overrides.jsonl"
    rows = [_override("x", 1, "CRITICAL", "LOW")]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="forbidden"):
        load_overrides(path)

    duplicate = [
        _override("x", 1, "LOW", "MEDIUM"),
        _override("x", 1, "LOW", "CRITICAL"),
    ]
    path.write_text(
        "\n".join(json.dumps(row) for row in duplicate) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_overrides(path)

    unknown = [_override("x", 1, "LOW", "NOT_A_RISK")]
    path.write_text("\n".join(json.dumps(row) for row in unknown) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown effective risk"):
        load_overrides(path)

    nonfrozen = [_override("x", 1, "LOW", "MEDIUM", frozen=False)]
    path.write_text(
        "\n".join(json.dumps(row) for row in nonfrozen) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not frozen"):
        load_overrides(path)


def test_fixed_membership_and_ordinals_are_preserved(tmp_path: Path):
    output = tmp_path
    pilot = [_pilot("a", 1, "LOW"), _pilot("b", 2, "MEDIUM")]
    (output / "pilot_rows.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in pilot),
        encoding="utf-8",
    )
    overrides_path = output / "overrides.jsonl"
    overrides_path.write_text(
        json.dumps(_override("a", 1, "LOW", "CRITICAL")) + "\n",
        encoding="utf-8",
    )
    manifest = apply_file(output, overrides_path)
    effective = [
        json.loads(line)
        for line in (output / "pilot_rows_effective.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [(row["pilot_ordinal"], row["canonical"]) for row in effective] == [
        (1, "a"),
        (2, "b"),
    ]
    assert manifest["membership_unchanged"] is True
    assert manifest["override_rows"] == 1
    assert len(manifest["override_manifest_sha256"]) == 64


def test_blind_selection_groups_on_effective_risk_not_selection_risk():
    rows = []
    ordinal = 0
    # Every row intentionally preserves LOW as selection risk. The test fails if
    # blind selection accidentally uses the stale class instead of effective risk.
    for risk, count in {
        "LOW": 4,
        "MEDIUM": 5,
        "HIGH_POSE_ACTION": 6,
        "HIGH_ANATOMY_ADULT": 7,
        "CRITICAL": 8,
    }.items():
        for _ in range(count):
            ordinal += 1
            rows.append(
                {
                    "canonical": f"c{ordinal}",
                    "selection_risk_class": "LOW",
                    "effective_risk_class": risk,
                    "issue32_overlap": "NO",
                }
            )
    selected, key = select_effective(rows)
    assert len(selected) == 30
    assert key["achieved_stratum_counts"] == BLIND_QUOTAS
    assert {row["selection_risk_class"] for row in key["selected"]} == {"LOW"}
    assert {row["effective_risk_class"] for row in key["selected"]} == set(BLIND_QUOTAS)
