#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).strip().casefold().replace("_", " ")
    return " ".join(text.split())


def split_aliases(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_columns(rows: list[dict[str, str]], required: set[str], label: str) -> None:
    if not rows:
        raise ValueError(f"{label}: no rows")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")


def as_int(value: str) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Issue #94 read-only Danbooru General -> Special identity gap scanner"
    )
    parser.add_argument("--full-kb", type=Path, required=True)
    parser.add_argument("--special", type=Path, required=True)
    parser.add_argument("--alias-map", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--expected-general", type=int, default=30743)
    parser.add_argument("--expected-special", type=int, default=2788)
    args = parser.parse_args()

    full = read_csv(args.full_kb)
    special = read_csv(args.special)
    require_columns(
        full,
        {"Tag", "DanbooruCategory", "post_count", "Aliases", "Special2788"},
        "full-kb",
    )
    require_columns(
        special,
        {"ID", "Tag", "Danbooru種別", "canonical_target"},
        "special",
    )

    if len(special) != args.expected_special:
        raise ValueError(
            f"special row count mismatch: expected {args.expected_special}, got {len(special)}"
        )
    ids = [row["ID"] for row in special]
    if len(ids) != len(set(ids)):
        raise ValueError("special contains duplicate IDs")

    special_identity_terms: dict[str, list[str]] = {}
    semantic_terms: dict[str, list[str]] = {}
    canonical_targets: dict[str, list[str]] = {}

    for row in special:
        tag_norm = norm(row["Tag"])
        source_type = (row["Danbooru種別"] or "").strip().casefold()
        sid = row["ID"]
        evidence = f"{sid}:{row['Tag']}"
        if source_type == "semantic/general":
            semantic_terms.setdefault(tag_norm, []).append(evidence)
        else:
            special_identity_terms.setdefault(tag_norm, []).append(evidence)
        target_norm = norm(row.get("canonical_target", ""))
        if target_norm:
            canonical_targets.setdefault(target_norm, []).append(evidence)

    alias_special_by_canonical: dict[str, list[str]] = {}
    if args.alias_map:
        alias_rows = read_csv(args.alias_map)
        require_columns(
            alias_rows,
            {"Alias", "CanonicalTag", "Special2788Alias"},
            "alias-map",
        )
        for row in alias_rows:
            if (row.get("Special2788Alias") or "").strip().upper() != "YES":
                continue
            canonical_norm = norm(row["CanonicalTag"])
            alias_special_by_canonical.setdefault(canonical_norm, []).append(row["Alias"])

    general = [
        row for row in full
        if (row.get("DanbooruCategory") or "").strip().casefold() == "general"
    ]
    if len(general) != args.expected_general:
        raise ValueError(
            f"General row count mismatch: expected {args.expected_general}, got {len(general)}"
        )

    inventory: list[dict[str, object]] = []
    status_counts: Counter[str] = Counter()
    legacy_false_gap_count = 0

    for row in general:
        canonical = row["Tag"]
        canonical_norm = norm(canonical)
        aliases = split_aliases(row.get("Aliases", ""))
        aliases_norm = {norm(alias): alias for alias in aliases}

        exact = special_identity_terms.get(canonical_norm, [])
        target = canonical_targets.get(canonical_norm, [])
        alias_hits: list[str] = []
        for alias_norm, original_alias in aliases_norm.items():
            if alias_norm in special_identity_terms:
                for hit in special_identity_terms[alias_norm]:
                    alias_hits.append(f"{original_alias}->{hit}")
        map_hits = alias_special_by_canonical.get(canonical_norm, [])

        semantic_hits: list[str] = []
        if canonical_norm in semantic_terms:
            semantic_hits.extend(semantic_terms[canonical_norm])
        for alias_norm, original_alias in aliases_norm.items():
            for hit in semantic_terms.get(alias_norm, []):
                semantic_hits.append(f"{original_alias}->{hit}")

        if exact:
            identity_status = "PRESENT_EXACT"
            identity_evidence = exact
        elif target:
            identity_status = "PRESENT_CANONICAL_TARGET"
            identity_evidence = target
        elif alias_hits or map_hits:
            identity_status = "PRESENT_ALIAS_CLOSURE"
            identity_evidence = alias_hits + [f"alias-map:{x}" for x in map_hits]
        elif semantic_hits:
            identity_status = "SEMANTIC_EXACT_OVERLAP_ONLY"
            identity_evidence = []
        else:
            identity_status = "GENERAL_ONLY_GAP"
            identity_evidence = []

        status_counts[identity_status] += 1
        legacy_marker = (row.get("Special2788") or "").strip().upper()
        if legacy_marker != "YES" and identity_status.startswith("PRESENT_"):
            legacy_false_gap_count += 1

        inventory.append(
            {
                "canonical": canonical,
                "post_count": as_int(row.get("post_count", "")),
                "aliases": "|".join(aliases),
                "legacy_special2788": legacy_marker,
                "identity_status": identity_status,
                "identity_evidence": "|".join(identity_evidence),
                "semantic_exact_overlap": "|".join(semantic_hits),
            }
        )

    order = {
        "GENERAL_ONLY_GAP": 0,
        "SEMANTIC_EXACT_OVERLAP_ONLY": 1,
        "PRESENT_ALIAS_CLOSURE": 2,
        "PRESENT_CANONICAL_TARGET": 3,
        "PRESENT_EXACT": 4,
    }
    inventory.sort(
        key=lambda row: (order[str(row["identity_status"])], -int(row["post_count"]), str(row["canonical"]))
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = args.out_dir / "general_special_identity_inventory.csv"
    with inventory_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inventory[0]))
        writer.writeheader()
        writer.writerows(inventory)

    summary = {
        "mode": "ISSUE94_READ_ONLY_IDENTITY_AUDIT",
        "full_kb": str(args.full_kb),
        "special": str(args.special),
        "alias_map": str(args.alias_map) if args.alias_map else None,
        "total_general_scanned": len(general),
        "special_rows": len(special),
        "identity_status_counts": dict(sorted(status_counts.items())),
        "legacy_blank_but_identity_covered": legacy_false_gap_count,
        "content_filter_used": "NO",
        "production_files_changed": "NO",
        "issue70_mutated": "NO",
        "important_note": (
            "SEMANTIC_EXACT_OVERLAP_ONLY means exact normalized term overlap only; "
            "broader semantic similarity still requires human review. GENERAL_ONLY_GAP "
            "is an identity gap inventory, not automatic product-fit approval."
        ),
    }
    with (args.out_dir / "coverage_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
