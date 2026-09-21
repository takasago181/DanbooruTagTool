#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
OUT = ROOT / "artifacts/issue180-diverse-pilot"

# 10 structurally different ecosystems x 25 rows = 250 Character rows.
# Membership here is only for PILOT SELECTION.  Legacy relation matches are
# deliberately allowed so false-positive/hard-negative examples enter the pilot.
ECOSYSTEMS = {
    "pokemon": {"home": "pokemon", "tokens": ["pokemon"]},
    "vocaloid": {"home": "vocaloid", "tokens": ["vocaloid"]},
    "fate": {"home": "fate_(series)", "tokens": ["fate"]},
    "umamusume": {"home": "umamusume", "tokens": ["umamusume"]},
    "blue_archive": {"home": "blue_archive", "tokens": ["blue_archive"]},
    "honkai_star_rail": {"home": "honkai:_star_rail", "tokens": ["honkai:_star_rail", "honkai_star_rail"]},
    "arknights": {"home": "arknights", "tokens": ["arknights"]},
    "kantai_collection": {"home": "kantai_collection", "tokens": ["kancolle", "kantai_collection"]},
    "touhou": {"home": "touhou", "tokens": ["touhou"]},
    "hololive": {"home": "hololive", "tokens": ["hololive"]},
}

TARGET_PER_ECOSYSTEM = 25

def read_rows() -> list[dict[str, str]]:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def pc(row: dict[str, str]) -> int:
    try:
        return int(row.get("post_count", "") or 0)
    except ValueError:
        return 0

def has_explicit_qualifier(tag: str, tokens: list[str]) -> bool:
    low = tag.lower()
    return any(f"_({token.lower()})" in low for token in tokens)

def legacy_mentions(row: dict[str, str], home: str, tokens: list[str]) -> bool:
    text = " ".join([
        row.get("related_copyright", ""),
        row.get("search_ja", ""),
        row.get("aliases", ""),
    ]).lower()
    needles = [home.lower(), *[t.lower() for t in tokens]]
    return any(n and n in text for n in needles)

def candidate_kind(row: dict[str, str], spec: dict[str, object]) -> str | None:
    tag = row["canonical_tag"]
    tokens = list(spec["tokens"])
    explicit = has_explicit_qualifier(tag, tokens)
    multi = tag.count("_(") >= 2
    legacy = legacy_mentions(row, str(spec["home"]), tokens)

    if explicit and multi:
        return "VARIANT_OR_MULTI_QUALIFIER"
    if explicit:
        return "EXPLICIT_QUALIFIER"
    if legacy:
        return "LEGACY_RELATION_HARD_CASE"
    return None

def take_unique(dest, rows, limit, role, used):
    count = 0
    for row in rows:
        rid = row["row_id"]
        if rid in used:
            continue
        item = dict(row)
        item["pilot_role"] = role
        dest.append(item)
        used.add(rid)
        count += 1
        if count >= limit:
            break

def main() -> int:
    rows = read_rows()
    chars = [r for r in rows if r.get("category_name") == "Character"]

    pilot: list[dict[str, str]] = []
    ecosystem_counts = {}
    shortfalls = {}

    for ecosystem, spec in ECOSYSTEMS.items():
        candidates = []
        for row in chars:
            kind = candidate_kind(row, spec)
            if kind:
                candidates.append({
                    "ecosystem": ecosystem,
                    "expected_root_candidate": str(spec["home"]),
                    "row_id": row.get("row_id", ""),
                    "canonical_tag": row.get("canonical_tag", ""),
                    "display_ja": row.get("display_ja", ""),
                    "search_ja": row.get("search_ja", ""),
                    "aliases": row.get("aliases", ""),
                    "post_count": str(pc(row)),
                    "old_related_copyright": row.get("related_copyright", ""),
                    "candidate_kind": kind,
                })

        used: set[str] = set()
        selected: list[dict[str, str]] = []

        variants = sorted(
            [r for r in candidates if r["candidate_kind"] == "VARIANT_OR_MULTI_QUALIFIER"],
            key=lambda r: (-int(r["post_count"]), r["canonical_tag"]),
        )
        explicit = sorted(
            [r for r in candidates if r["candidate_kind"] == "EXPLICIT_QUALIFIER"],
            key=lambda r: (-int(r["post_count"]), r["canonical_tag"]),
        )
        legacy = sorted(
            [r for r in candidates if r["candidate_kind"] == "LEGACY_RELATION_HARD_CASE"],
            key=lambda r: (-int(r["post_count"]), r["canonical_tag"]),
        )

        # Intentionally mix easy positives, variants, and legacy hard cases.
        take_unique(selected, variants, 6, "VARIANT_INHERITANCE", used)
        take_unique(selected, explicit, 9, "QUALIFIER_AUTHORITY", used)
        take_unique(selected, legacy, 6, "LEGACY_HARD_NEGATIVE_OR_UNQUALIFIED", used)

        # Fill remaining slots with post-count extremes from the whole candidate pool.
        remaining = TARGET_PER_ECOSYSTEM - len(selected)
        if remaining > 0:
            hi = sorted(candidates, key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))
            lo = sorted(candidates, key=lambda r: (int(r["post_count"]), r["canonical_tag"]))
            take_unique(selected, hi, (remaining + 1) // 2, "HIGH_POST_FILL", used)
            remaining = TARGET_PER_ECOSYSTEM - len(selected)
            if remaining > 0:
                take_unique(selected, lo, remaining, "LONG_TAIL_FILL", used)

        ecosystem_counts[ecosystem] = len(selected)
        if len(selected) < TARGET_PER_ECOSYSTEM:
            shortfalls[ecosystem] = {
                "selected": len(selected),
                "target": TARGET_PER_ECOSYSTEM,
                "candidate_pool": len(candidates),
            }
        pilot.extend(selected)

    if shortfalls:
        raise SystemExit("pilot ecosystem shortfall: " + json.dumps(shortfalls, ensure_ascii=False))

    if len(pilot) != 250:
        raise SystemExit(f"expected 250 pilot rows, got {len(pilot)}")

    # Ensure the same Character is not silently selected into multiple ecosystems.
    ids = [r["row_id"] for r in pilot]
    if len(ids) != len(set(ids)):
        duplicates = sorted({x for x in ids if ids.count(x) > 1})
        raise SystemExit("cross-ecosystem duplicate row_ids: " + ", ".join(duplicates[:20]))

    OUT.mkdir(parents=True, exist_ok=True)
    fields = [
        "ecosystem", "expected_root_candidate", "row_id", "canonical_tag",
        "display_ja", "search_ja", "aliases", "post_count",
        "old_related_copyright", "candidate_kind", "pilot_role",
    ]
    with (OUT / "PILOT_250.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(pilot)

    role_counts = {}
    for row in pilot:
        role_counts[row["pilot_role"]] = role_counts.get(row["pilot_role"], 0) + 1

    summary = {
        "pilot_rows": len(pilot),
        "ecosystem_counts": ecosystem_counts,
        "role_counts": role_counts,
        "selection_only": True,
        "expected_root_candidate_is_not_a_verdict": True,
        "legacy_relation_used_for_sampling_only": True,
        "production_modified": False,
        "accepted_source_modified": False,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
