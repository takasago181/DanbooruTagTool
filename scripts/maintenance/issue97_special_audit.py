"""Issue #97 read-only Special expansion quality audit.

This audit verifies the committed post-#96 authority surfaces without mutating
production data or UserData. It intentionally does not rewrite legacy
`special2788` path names: those paths are compatibility/authority names, while
live cardinality must be 2,983.
"""

from __future__ import annotations

import csv
import json
import re
import sys
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
    rows: Iterable[dict[str, str]],
    *,
    field: str,
    expected: range,
    label: str,
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
    promotion = exact_id_map(
        read_csv(root, PROMOTION), field="proposed_special_id", expected=promoted_ids, label="promotion"
    )
    ja = exact_id_map(
        read_csv(root, JA_METADATA), field="proposed_special_id", expected=promoted_ids, label="ja metadata"
    )
    taxonomy = exact_id_map(
        read_csv(root, TAXONOMY), field="proposed_special_id", expected=promoted_ids, label="taxonomy"
    )
    duplicate = exact_id_map(
        read_csv(root, DUPLICATE_VALIDATED),
        field="proposed_special_id",
        expected=promoted_ids,
        label="duplicate validation",
    )

    canonical_seen: set[str] = set()
    alias_seen: set[str] = set()
    for item_id in promoted_ids:
        row = promotion[item_id]
        label = f"promotion {item_id}"
        require_nonblank(
            row,
            ("canonical_tag", "display_ja", "search_ja", "kind_id", "duplicate_guard", "proposal_status"),
            label,
        )
        canonical = row["canonical_tag"]
        if canonical in canonical_seen:
            raise RuntimeError(f"{label}: duplicate promoted canonical {canonical}")
        canonical_seen.add(canonical)
        aliases = [value.strip() for value in row.get("canonical_aliases", "").split("|") if value.strip()]
        for surface in [canonical, *aliases]:
            if surface in alias_seen:
                raise RuntimeError(f"{label}: duplicate promoted canonical/alias surface {surface}")
            alias_seen.add(surface)

        if row["duplicate_guard"] != "CURRENT_SPECIAL_GAP_PASS":
            raise RuntimeError(f"{label}: promotion duplicate_guard={row['duplicate_guard']!r}")
        if row["proposal_status"] != "PREP_READY_FOR_DEV_REVIEW":
            raise RuntimeError(f"{label}: unexpected proposal_status={row['proposal_status']!r}")

        ja_row = ja[item_id]
        require_nonblank(ja_row, ("canonical_tag", "display_ja", "search_ja", "ja_status"), f"ja {item_id}")
        if any(
            ja_row[field] != row[field]
            for field in ("canonical_tag", "display_ja", "search_ja")
        ):
            raise RuntimeError(f"ja {item_id}: metadata differs from promotion authority")

        taxonomy_row = taxonomy[item_id]
        require_nonblank(
            taxonomy_row,
            ("canonical_tag", "kind_id", "browse_status", "validation_status"),
            f"taxonomy {item_id}",
        )
        if taxonomy_row["canonical_tag"] != canonical:
            raise RuntimeError(f"taxonomy {item_id}: canonical differs from promotion authority")
        if taxonomy_row["validation_status"] != "TAXONOMY_RESOLVED":
            raise RuntimeError(f"taxonomy {item_id}: unresolved taxonomy")

        duplicate_row = duplicate[item_id]
        require_nonblank(
            duplicate_row,
            ("canonical_tag", "duplicate_guard", "validation_status"),
            f"duplicate {item_id}",
        )
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
    profile = exact_id_map(
        read_csv(root, GENERATION_PROFILE), field="SpecialID", expected=all_ids, label="generation profile"
    )
    fit = exact_id_map(
        read_csv(root, PRODUCT_FIT), field="special_id", expected=all_ids, label="product fit"
    )

    for item_id, promoted in promotion.items():
        profile_row = profile[item_id]
        if profile_row.get("Tag") != promoted["canonical_tag"]:
            raise RuntimeError(f"generation profile {item_id}: tag differs from promotion authority")
        if profile_row.get("EvidenceClass") != "ISSUE96_ACCEPTED_SPECIAL_EXPANSION":
            raise RuntimeError(f"generation profile {item_id}: missing Issue96 evidence class")
        require_nonblank(fit[item_id], ("product_fit_verdict",), f"product fit {item_id}")

    return {
        "generation_profile": len(profile),
        "product_fit": len(fit),
    }


def stale_2788_candidates(root: Path) -> list[dict[str, object]]:
    """Return active-code 2788 literals that are not the intentional base boundary.

    Legacy file/directory names such as `special2788` are not matched because the
    digits are embedded in an identifier. `BaseSpecialCount = 2788` is explicitly
    retained as the pre-promotion boundary used to validate IDs 2789..2983.
    """

    number = re.compile(r"(?<![A-Za-z0-9_])(?:2788|2,788)(?![A-Za-z0-9_])")
    allowed = re.compile(r"\bBaseSpecialCount\s*=\s*(?:2788|2,788)\b")
    candidates: list[dict[str, object]] = []
    for relative in ACTIVE_2788_SCAN:
        path = root / relative
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not number.search(line) or allowed.search(line):
                continue
            candidates.append({"path": relative.as_posix(), "line": line_no, "text": line.strip()})
    return candidates


def audit(root: Path) -> dict[str, object]:
    promotion, promoted_counts = check_promoted_authority(root)
    expanded_counts = check_expanded_sidecars(root, promotion)
    stale = stale_2788_candidates(root)
    result: dict[str, object] = {
        "issue": 97,
        "read_only": True,
        "base_special_count": BASE_SPECIAL_COUNT,
        "expanded_special_count": EXPANDED_SPECIAL_COUNT,
        "promotion_range": [PROMOTION_START_ID, EXPANDED_SPECIAL_COUNT],
        "promotion_count": PROMOTION_COUNT,
        "counts": {**promoted_counts, **expanded_counts},
        "stale_2788_candidates": stale,
        "human_audit_candidates": stale,
    }
    result["ok"] = not stale
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    try:
        result = audit(root)
    except Exception as error:  # noqa: BLE001 - concise audit CLI failure is intentional
        print(json.dumps({"ok": False, "issue": 97, "error": str(error)}, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
