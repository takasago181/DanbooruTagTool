"""Issue #97 read-only Special expansion quality audit.

Checks the committed #96 authority sidecars and, when --catalog is supplied,
the built production catalog. The script never opens or mutates UserData/user.db.
Legacy `special2788` path names remain valid compatibility/authority names;
live cardinality is 2,983.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

BASE_SPECIAL_COUNT = 2788
EXPANDED_SPECIAL_COUNT = 2983
PROMOTION_START_ID = BASE_SPECIAL_COUNT + 1
PROMOTION_COUNT = EXPANDED_SPECIAL_COUNT - BASE_SPECIAL_COUNT

PROMOTION = Path("docs/issue96/special_expansion_promotion_proposal_v1.csv")
JA_METADATA = Path("docs/issue96/special_expansion_ja_metadata_v1.csv")
TAXONOMY = Path("docs/issue96/special_expansion_taxonomy_final_v1.csv")
DUPLICATE_VALIDATED = Path("docs/issue96/special_expansion_duplicate_validated_v1.csv")
GENERATION_PROFILE = Path("data/generation/special2788_generation_profile.csv")
PRODUCT_FIT = Path("data/special2788/product_fit_verdicts.csv")

STATUS_NAMES = {
    0: "AutoCandidate",
    1: "HumanResolved",
    2: "ReferenceOnlyNoDirectBrowse",
    3: "DeferProductFitReview",
    4: "OutOfScopeNoBrowse",
}
EXPECTED_STATUS = {
    "AutoCandidate": 2745,
    "HumanResolved": 210,
    "ReferenceOnlyNoDirectBrowse": 21,
    "DeferProductFitReview": 6,
    "OutOfScopeNoBrowse": 1,
}

ACTIVE_2788_SCAN = (
    Path("src/DanbooruTagTool.Data/AcceptedAssetImporter.cs"),
    Path("src/DanbooruTagTool.Data/SpecialBrowseV2Overlay.cs"),
    Path("scripts/maintenance/catalog_health.py"),
    Path("scripts/maintenance/check_local_health.ps1"),
    Path("src/DanbooruTagTool.Tests/ProductionTests.cs"),
    Path("src/DanbooruTagTool.Tests/TechnicalFixTests.cs"),
)


def read_csv(root: Path, relative: Path) -> list[dict[str, str]]:
    path = root / relative
    if not path.is_file():
        raise RuntimeError(f"missing audit input: {relative.as_posix()}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def exact_id_map(
    rows: Iterable[dict[str, str]], *, field: str, expected: range, label: str
) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for row in rows:
        try:
            item_id = int(row[field])
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError(f"{label}: invalid {field}") from error
        if item_id in result:
            raise RuntimeError(f"{label}: duplicate id {item_id}")
        result[item_id] = row
    expected_ids = set(expected)
    actual_ids = set(result)
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)[:20]
        extra = sorted(actual_ids - expected_ids)[:20]
        raise RuntimeError(f"{label}: id coverage mismatch missing={missing} extra={extra}")
    return result


def require_nonblank(row: dict[str, str], fields: Iterable[str], label: str) -> None:
    blank = [field for field in fields if not row.get(field, "").strip()]
    if blank:
        raise RuntimeError(f"{label}: blank fields {blank}")


def check_promoted_authority(root: Path) -> tuple[dict[int, dict[str, str]], dict[str, int]]:
    promoted_ids = range(PROMOTION_START_ID, EXPANDED_SPECIAL_COUNT + 1)
    promotion = exact_id_map(read_csv(root, PROMOTION), field="proposed_special_id", expected=promoted_ids, label="promotion")
    ja = exact_id_map(read_csv(root, JA_METADATA), field="proposed_special_id", expected=promoted_ids, label="ja metadata")
    taxonomy = exact_id_map(read_csv(root, TAXONOMY), field="proposed_special_id", expected=promoted_ids, label="taxonomy")
    duplicate = exact_id_map(
        read_csv(root, DUPLICATE_VALIDATED), field="proposed_special_id", expected=promoted_ids, label="duplicate validation"
    )

    surfaces_seen: set[str] = set()
    for item_id in promoted_ids:
        row = promotion[item_id]
        label = f"promotion {item_id}"
        require_nonblank(row, ("canonical_tag", "display_ja", "search_ja", "kind_id", "duplicate_guard", "proposal_status"), label)
        canonical = row["canonical_tag"]
        aliases = [value.strip() for value in row.get("canonical_aliases", "").split("|") if value.strip()]
        for surface in [canonical, *aliases]:
            if surface in surfaces_seen:
                raise RuntimeError(f"{label}: duplicate promoted canonical/alias surface {surface}")
            surfaces_seen.add(surface)
        if row["duplicate_guard"] != "CURRENT_SPECIAL_GAP_PASS":
            raise RuntimeError(f"{label}: promotion duplicate_guard={row['duplicate_guard']!r}")
        if row["proposal_status"] != "PREP_READY_FOR_DEV_REVIEW":
            raise RuntimeError(f"{label}: unexpected proposal_status={row['proposal_status']!r}")

        ja_row = ja[item_id]
        require_nonblank(ja_row, ("canonical_tag", "display_ja", "search_ja", "ja_status"), f"ja {item_id}")
        if any(ja_row[field] != row[field] for field in ("canonical_tag", "display_ja", "search_ja")):
            raise RuntimeError(f"ja {item_id}: metadata differs from promotion authority")

        taxonomy_row = taxonomy[item_id]
        require_nonblank(taxonomy_row, ("canonical_tag", "kind_id", "browse_status", "validation_status"), f"taxonomy {item_id}")
        if taxonomy_row["canonical_tag"] != canonical or taxonomy_row["validation_status"] != "TAXONOMY_RESOLVED":
            raise RuntimeError(f"taxonomy {item_id}: authority mismatch or unresolved taxonomy")

        duplicate_row = duplicate[item_id]
        require_nonblank(duplicate_row, ("canonical_tag", "duplicate_guard", "validation_status"), f"duplicate {item_id}")
        if duplicate_row["canonical_tag"] != canonical:
            raise RuntimeError(f"duplicate {item_id}: canonical differs from promotion authority")
        if duplicate_row["duplicate_guard"] != "PASS_GENERAL_ONLY_GAP_CURRENT_SPECIAL_2788":
            raise RuntimeError(f"duplicate {item_id}: duplicate guard did not pass")
        if duplicate_row["validation_status"] != "IDENTITY_LAYER_TAXONOMY_DUPLICATE_READY":
            raise RuntimeError(f"duplicate {item_id}: validation not ready")

    return promotion, {
        "promotion": len(promotion),
        "ja_metadata_promoted": len(ja),
        "taxonomy_promoted": len(taxonomy),
        "duplicate_validated_promoted": len(duplicate),
    }


def check_expanded_sidecars(root: Path, promotion: dict[int, dict[str, str]]) -> dict[str, int]:
    all_ids = range(1, EXPANDED_SPECIAL_COUNT + 1)
    profile = exact_id_map(read_csv(root, GENERATION_PROFILE), field="SpecialID", expected=all_ids, label="generation profile")
    fit = exact_id_map(read_csv(root, PRODUCT_FIT), field="special_id", expected=all_ids, label="product fit")
    for item_id, row in fit.items():
        require_nonblank(row, ("product_fit_verdict",), f"product fit {item_id}")
    for item_id, promoted in promotion.items():
        profile_row = profile[item_id]
        if profile_row.get("Tag") != promoted["canonical_tag"]:
            raise RuntimeError(f"generation profile {item_id}: tag differs from promotion authority")
        if profile_row.get("EvidenceClass") != "ISSUE96_ACCEPTED_SPECIAL_EXPANSION":
            raise RuntimeError(f"generation profile {item_id}: missing Issue96 evidence class")
    return {"generation_profile": len(profile), "product_fit": len(fit)}


def parse_special_id(value: str) -> int:
    if not value.startswith("S:"):
        raise RuntimeError(f"invalid Special catalog id: {value}")
    try:
        return int(value[2:])
    except ValueError as error:
        raise RuntimeError(f"invalid Special catalog id: {value}") from error


def check_catalog(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"catalog not found: {path}")
    uri = f"file:{path.resolve()}?mode=ro&immutable=1"
    with sqlite3.connect(uri, uri=True) as connection:
        rows = connection.execute("SELECT id, payload FROM entries ORDER BY ordinal").fetchall()
    specials: dict[int, dict[str, object]] = {}
    for catalog_id, payload_text in rows:
        payload = json.loads(payload_text)
        if payload.get("IsSpecial") is not True:
            continue
        item_id = parse_special_id(catalog_id)
        if item_id in specials:
            raise RuntimeError(f"catalog duplicate Special id: {item_id}")
        specials[item_id] = payload
    expected_ids = set(range(1, EXPANDED_SPECIAL_COUNT + 1))
    if set(specials) != expected_ids:
        raise RuntimeError("catalog Special IDs are not exact 1..2983")

    for item_id, payload in specials.items():
        if not str(payload.get("Japanese") or "").strip():
            raise RuntimeError(f"catalog Japanese display missing at {item_id}")
        if not payload.get("JapaneseSearch"):
            raise RuntimeError(f"catalog Japanese search missing at {item_id}")
        if not str(payload.get("ProductFit") or "").strip():
            raise RuntimeError(f"catalog product fit missing at {item_id}")
        browse = payload.get("SpecialBrowseV2")
        if not isinstance(browse, dict):
            raise RuntimeError(f"catalog Browse v2 missing at {item_id}")
        status = browse.get("Status")
        has_route = bool(browse.get("KindId") or browse.get("BodySiteIds") or browse.get("ThemeIds"))
        if status in (0, 1) and not has_route:
            raise RuntimeError(f"catalog browsable Special has no v2 route at {item_id}")
        if status in (2, 3, 4) and has_route:
            raise RuntimeError(f"catalog non-browse Special still has v2 route at {item_id}")
        if status not in STATUS_NAMES:
            raise RuntimeError(f"catalog unknown Browse v2 status at {item_id}: {status!r}")

    statuses = Counter(STATUS_NAMES[specials[item_id]["SpecialBrowseV2"]["Status"]] for item_id in specials)
    if dict(statuses) != EXPECTED_STATUS:
        raise RuntimeError(f"catalog Browse v2 status distribution drift: {dict(statuses)}")

    promoted_ids = range(PROMOTION_START_ID, EXPANDED_SPECIAL_COUNT + 1)
    if any(specials[item_id]["SpecialBrowseV2"]["Status"] != 1 for item_id in promoted_ids):
        raise RuntimeError("promoted Special rows are not all HumanResolved in Browse v2")

    base_surfaces: set[str] = set()
    for item_id in range(1, BASE_SPECIAL_COUNT + 1):
        payload = specials[item_id]
        for surface in [payload.get("English"), payload.get("Canonical"), *(payload.get("Aliases") or [])]:
            if surface:
                base_surfaces.add(str(surface))
    promoted_surfaces: set[str] = set()
    for item_id in promoted_ids:
        payload = specials[item_id]
        for surface in [payload.get("English"), payload.get("Canonical"), *(payload.get("Aliases") or [])]:
            if not surface:
                continue
            value = str(surface)
            if value in base_surfaces:
                raise RuntimeError(f"promoted canonical/alias overlaps base Special at {item_id}: {value}")
            if value in promoted_surfaces:
                raise RuntimeError(f"promoted canonical/alias collision at {item_id}: {value}")
            promoted_surfaces.add(value)

    return {
        "special": len(specials),
        "japanese_display": len(specials),
        "japanese_search": len(specials),
        "browse_v2": len(specials),
        "product_fit_catalog": len(specials),
        "status": dict(statuses),
        "promoted_human_resolved": PROMOTION_COUNT,
        "promoted_base_surface_overlap": 0,
    }


def stale_2788_candidates(root: Path) -> list[dict[str, object]]:
    number = re.compile(r"(?<![A-Za-z0-9_])(?:2788|2,788)(?![A-Za-z0-9_])")
    allowed = re.compile(r"\bBaseSpecialCount\s*=\s*(?:2788|2,788)\b")
    candidates: list[dict[str, object]] = []
    for relative in ACTIVE_2788_SCAN:
        path = root / relative
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if number.search(line) and not allowed.search(line):
                candidates.append({"path": relative.as_posix(), "line": line_no, "text": line.strip()})
    return candidates


def audit(root: Path, catalog: Path | None) -> dict[str, object]:
    promotion, promoted_counts = check_promoted_authority(root)
    expanded_counts = check_expanded_sidecars(root, promotion)
    stale = stale_2788_candidates(root)
    result: dict[str, object] = {
        "issue": 97,
        "read_only": True,
        "user_db_opened": False,
        "base_special_count": BASE_SPECIAL_COUNT,
        "expanded_special_count": EXPANDED_SPECIAL_COUNT,
        "promotion_range": [PROMOTION_START_ID, EXPANDED_SPECIAL_COUNT],
        "promotion_count": PROMOTION_COUNT,
        "counts": {**promoted_counts, **expanded_counts},
        "catalog": check_catalog(catalog) if catalog is not None else None,
        "stale_2788_candidates": stale,
        "human_audit_candidates": stale,
    }
    result["ok"] = not stale
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue #97 read-only Special quality audit")
    parser.add_argument("--catalog", type=Path, help="optional built catalog.db for full 2,983-row verification")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    try:
        result = audit(root, args.catalog)
    except Exception as error:  # noqa: BLE001 - concise audit CLI failure is intentional
        print(json.dumps({"ok": False, "issue": 97, "error": str(error)}, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
