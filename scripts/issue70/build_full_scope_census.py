#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "docs/issue70/data/source_chunks"
SCOPE_DIR = ROOT / "docs/issue70/scope"
SEED_PATH = SCOPE_DIR / "confirmed_real3d_seed.csv"

LEDGER_PATH = SCOPE_DIR / "full_scope_ledger.csv"
SUMMARY_PATH = SCOPE_DIR / "scope_summary.json"
REVIEW_PATH = SCOPE_DIR / "scope_review_queue.csv"
EXCLUDE_PATH = SCOPE_DIR / "runtime_exclude_real3d_candidates.csv"

EXPECTED = {"Character": 35890, "Copyright": 8536}
EXPECTED_TOTAL = sum(EXPECTED.values())
VALID_SCOPE = {"IN_2D", "REAL_3D", "UNCERTAIN"}
CLASSIFIER_VERSION = "issue70_scope_v1"

LEDGER_FIELDS = [
    "row_id",
    "canonical_tag",
    "category",
    "post_count",
    "media_scope",
    "confidence",
    "decision_source",
    "scope_reason",
    "primary_copyright",
    "primary_copyright_coverage",
    "evidence_refs",
]

REVIEW_FIELDS = [
    "row_id",
    "canonical_tag",
    "category",
    "post_count",
    "review_band",
    "primary_copyright",
    "primary_copyright_coverage",
    "current_reason",
]

EXCLUDE_FIELDS = [
    "row_id",
    "canonical_tag",
    "category",
    "post_count",
    "media_scope",
    "confidence",
    "decision_source",
    "scope_reason",
    "evidence_refs",
]

EXPLICIT_2D_PATTERNS = [
    ("VISUAL_NOVEL_MARKER", re.compile(r"(?:^|[_ (])visual_novel(?:[_) ]|$)", re.I)),
    ("MANGA_MARKER", re.compile(r"(?:^|[_ (])manga(?:[_) ]|$)", re.I)),
    ("ANIME_MARKER", re.compile(r"(?:^|[_ (])anime(?:[_) ]|$)", re.I)),
    ("VIDEO_GAME_MARKER", re.compile(r"(?:^|[_ (])video_game(?:[_) ]|$)", re.I)),
    ("GAME_DISAMBIG_MARKER", re.compile(r"\(game\)", re.I)),
    ("WEBCOMIC_MARKER", re.compile(r"(?:^|[_ (])webcomic(?:[_) ]|$)", re.I)),
    ("WEBTOON_MARKER", re.compile(r"(?:^|[_ (])webtoon(?:[_) ]|$)", re.I)),
    ("COMIC_DISAMBIG_MARKER", re.compile(r"\(comic\)", re.I)),
    ("CARTOON_MARKER", re.compile(r"(?:^|[_ (])cartoon(?:[_) ]|$)", re.I)),
    ("ANIMATION_MARKER", re.compile(r"(?:^|[_ (])animation(?:[_) ]|$)", re.I)),
    ("ANIMATED_SERIES_MARKER", re.compile(r"animated_series", re.I)),
    ("LIGHT_NOVEL_MARKER", re.compile(r"(?:^|[_ (])light_novel(?:[_) ]|$)", re.I)),
]


def source_sort_key(path: Path) -> tuple[int, str]:
    m = re.search(r"source_(\d+)_", path.name)
    return (int(m.group(1)) if m else 10**9, path.name)


def load_scope_source() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    counts: Counter[str] = Counter()

    for path in sorted(SOURCE_DIR.glob("source_*.csv"), key=source_sort_key):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                category = (row.get("category_name") or "").strip()
                if category not in EXPECTED:
                    continue
                rid = (row.get("row_id") or "").strip()
                assert rid, f"missing row_id in {path}"
                assert rid not in seen, f"duplicate row_id: {rid}"
                seen.add(rid)
                counts[category] += 1
                rows.append(row)

    assert len(rows) == EXPECTED_TOTAL, (len(rows), EXPECTED_TOTAL)
    assert dict(counts) == EXPECTED, (dict(counts), EXPECTED)
    return rows


def load_real3d_seeds(source_by_id: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    seeds: dict[str, dict[str, str]] = {}
    with SEED_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rid = (row.get("row_id") or "").strip()
            assert rid and rid not in seeds, f"bad/duplicate seed row: {rid}"
            assert row.get("media_scope") == "REAL_3D", (rid, row.get("media_scope"))
            src = source_by_id.get(rid)
            assert src is not None, f"seed row not found in source: {rid}"
            assert row.get("canonical_tag") == src.get("canonical_tag"), rid
            assert row.get("category") == src.get("category_name"), rid
            assert int(row.get("post_count") or 0) == int(src.get("post_count") or 0), rid
            seeds[rid] = row
    return seeds


def parse_relations(raw: str) -> list[dict[str, object]]:
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if not isinstance(item, dict):
            continue
        tag = str(item.get("copyright") or "").strip()
        if not tag:
            continue
        try:
            coverage = float(item.get("character_coverage") or 0.0)
        except (TypeError, ValueError):
            coverage = 0.0
        try:
            co_posts = int(item.get("co_posts") or 0)
        except (TypeError, ValueError):
            co_posts = 0
        out.append({"copyright": tag, "coverage": coverage, "co_posts": co_posts})
    out.sort(key=lambda x: (-int(x["co_posts"]), -float(x["coverage"]), str(x["copyright"])))
    return out


def explicit_2d_reason(row: dict[str, str]) -> str | None:
    canonical = (row.get("canonical_tag") or "").strip()
    if canonical == "original":
        return "ORIGINAL_ILLUSTRATION_IDENTITY"

    # Canonical + verified aliases are identity evidence. Existing Japanese candidates
    # are intentionally not used for media-scope classification.
    haystack = " | ".join(
        [
            canonical,
            row.get("verified_aliases") or "",
            row.get("source_aliases") or "",
        ]
    )
    for reason, pattern in EXPLICIT_2D_PATTERNS:
        if pattern.search(haystack):
            return reason
    return None


def fingerprint(rows: list[dict[str, str]]) -> str:
    h = hashlib.sha256()
    for row in rows:
        fields = [
            row.get("row_id") or "",
            row.get("canonical_tag") or "",
            row.get("category_name") or "",
            row.get("post_count") or "",
            row.get("related_copyright_candidates") or "",
        ]
        h.update(("\t".join(fields) + "\n").encode("utf-8"))
    return h.hexdigest()


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    source = load_scope_source()
    source_by_id = {row["row_id"]: row for row in source}
    seeds = load_real3d_seeds(source_by_id)

    copyright_rows = [r for r in source if r["category_name"] == "Copyright"]
    character_rows = [r for r in source if r["category_name"] == "Character"]

    decisions: dict[str, dict[str, str]] = {}
    copyright_by_tag: dict[str, str] = {}

    # Copyright-first: only explicit high-precision markers and confirmed REAL_3D seeds.
    for row in copyright_rows:
        rid = row["row_id"]
        tag = row["canonical_tag"]
        copyright_by_tag[tag] = rid

        if rid in seeds:
            seed = seeds[rid]
            decisions[rid] = {
                "media_scope": "REAL_3D",
                "confidence": "HIGH",
                "decision_source": "CONFIRMED_REAL3D_SEED",
                "scope_reason": seed.get("scope_reason") or "confirmed previous audit exclusion",
                "evidence_refs": seed.get("evidence_refs") or "",
                "primary_copyright": "",
                "primary_copyright_coverage": "",
            }
            continue

        marker = explicit_2d_reason(row)
        if marker:
            decisions[rid] = {
                "media_scope": "IN_2D",
                "confidence": "HIGH",
                "decision_source": "EXPLICIT_2D_MEDIA_MARKER",
                "scope_reason": marker,
                "evidence_refs": "",
                "primary_copyright": "",
                "primary_copyright_coverage": "",
            }
        else:
            decisions[rid] = {
                "media_scope": "UNCERTAIN",
                "confidence": "",
                "decision_source": "UNRESOLVED",
                "scope_reason": "Copyright identity requires scope review",
                "evidence_refs": "",
                "primary_copyright": "",
                "primary_copyright_coverage": "",
            }

    # Character propagation only when co-occurrence is dominant enough to be safe.
    for row in character_rows:
        rid = row["row_id"]
        if rid in seeds:
            seed = seeds[rid]
            decisions[rid] = {
                "media_scope": "REAL_3D",
                "confidence": "HIGH",
                "decision_source": "CONFIRMED_REAL3D_SEED",
                "scope_reason": seed.get("scope_reason") or "confirmed previous audit exclusion",
                "evidence_refs": seed.get("evidence_refs") or "",
                "primary_copyright": "",
                "primary_copyright_coverage": "",
            }
            continue

        relations = parse_relations(row.get("related_copyright_candidates") or "")
        top = relations[0] if relations else None
        primary_tag = str(top["copyright"]) if top else ""
        primary_cov = float(top["coverage"]) if top else 0.0
        primary_decision = None
        if primary_tag:
            copyright_rid = copyright_by_tag.get(primary_tag)
            if copyright_rid:
                primary_decision = decisions[copyright_rid]

        if primary_decision and primary_decision["media_scope"] == "IN_2D" and primary_cov >= 0.80:
            decisions[rid] = {
                "media_scope": "IN_2D",
                "confidence": "HIGH",
                "decision_source": "DOMINANT_COPYRIGHT_2D",
                "scope_reason": f"dominant related Copyright is IN_2D at coverage {primary_cov:.6f}",
                "evidence_refs": "",
                "primary_copyright": primary_tag,
                "primary_copyright_coverage": f"{primary_cov:.6f}",
            }
            continue

        # REAL_3D propagation is deliberately stricter than IN_2D propagation.
        # It requires an almost-exclusive confirmed REAL_3D property and no other
        # meaningful IN_2D relation among the preserved top candidates.
        if primary_decision and primary_decision["media_scope"] == "REAL_3D" and primary_cov >= 0.98:
            competing_in2d = False
            for rel in relations[1:]:
                if float(rel["coverage"]) < 0.10:
                    continue
                crid = copyright_by_tag.get(str(rel["copyright"]))
                if crid and decisions[crid]["media_scope"] == "IN_2D":
                    competing_in2d = True
                    break
            if not competing_in2d:
                decisions[rid] = {
                    "media_scope": "REAL_3D",
                    "confidence": "HIGH",
                    "decision_source": "DOMINANT_COPYRIGHT_REAL3D",
                    "scope_reason": f"almost-exclusive confirmed REAL_3D Copyright at coverage {primary_cov:.6f}",
                    "evidence_refs": primary_decision.get("evidence_refs", ""),
                    "primary_copyright": primary_tag,
                    "primary_copyright_coverage": f"{primary_cov:.6f}",
                }
                continue

        decisions[rid] = {
            "media_scope": "UNCERTAIN",
            "confidence": "",
            "decision_source": "UNRESOLVED",
            "scope_reason": "Character scope not safely derivable from current Copyright decisions",
            "evidence_refs": "",
            "primary_copyright": primary_tag,
            "primary_copyright_coverage": f"{primary_cov:.6f}" if top else "",
        }

    ledger: list[dict[str, str]] = []
    for row in source:
        d = decisions[row["row_id"]]
        ledger.append(
            {
                "row_id": row["row_id"],
                "canonical_tag": row["canonical_tag"],
                "category": row["category_name"],
                "post_count": row["post_count"],
                **d,
            }
        )

    validate_ledger(ledger, seeds)

    scope_counts = Counter(r["media_scope"] for r in ledger)
    by_category = {
        category: dict(Counter(r["media_scope"] for r in ledger if r["category"] == category))
        for category in EXPECTED
    }
    by_source = dict(Counter(r["decision_source"] for r in ledger))

    summary: dict[str, object] = {
        "format_version": 1,
        "issue": 70,
        "classifier_version": CLASSIFIER_VERSION,
        "production_modified": False,
        "population": {
            "total": len(ledger),
            "Character": EXPECTED["Character"],
            "Copyright": EXPECTED["Copyright"],
            "Artist_scope_filtered": 0,
        },
        "scope_counts": dict(sorted(scope_counts.items())),
        "scope_counts_by_category": by_category,
        "decision_source_counts": dict(sorted(by_source.items())),
        "confirmed_real3d_seed_rows": len(seeds),
        "source_fingerprint_sha256": fingerprint(source),
        "policy": {
            "runtime_candidate": "IN_2D + UNCERTAIN until full review closes",
            "runtime_exclusion_candidate": "REAL_3D only",
            "copyright_first": True,
            "character_2d_propagation_threshold": 0.80,
            "character_real3d_propagation_threshold": 0.98,
        },
        "next_step": "review UNCERTAIN Copyright rows first, regenerate, then review residual Character rows",
    }
    return ledger, summary


def validate_ledger(ledger: list[dict[str, str]], seeds: dict[str, dict[str, str]]) -> None:
    assert len(ledger) == EXPECTED_TOTAL, (len(ledger), EXPECTED_TOTAL)
    ids = [r["row_id"] for r in ledger]
    assert len(ids) == len(set(ids)), "duplicate ledger row_id"
    counts = Counter(r["category"] for r in ledger)
    assert dict(counts) == EXPECTED, (dict(counts), EXPECTED)
    assert all(r["media_scope"] in VALID_SCOPE for r in ledger)
    assert all(r["category"] in EXPECTED for r in ledger)
    for rid in seeds:
        row = next((r for r in ledger if r["row_id"] == rid), None)
        assert row is not None and row["media_scope"] == "REAL_3D", rid


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_outputs(ledger: list[dict[str, str]], summary: dict[str, object]) -> None:
    write_csv(LEDGER_PATH, LEDGER_FIELDS, ledger)

    uncertain = [r for r in ledger if r["media_scope"] == "UNCERTAIN"]
    uncertain.sort(
        key=lambda r: (
            0 if r["category"] == "Copyright" else 1,
            -int(r["post_count"] or 0),
            r["row_id"],
        )
    )
    review_rows = [
        {
            "row_id": r["row_id"],
            "canonical_tag": r["canonical_tag"],
            "category": r["category"],
            "post_count": r["post_count"],
            "review_band": "COPYRIGHT_SCOPE_FIRST" if r["category"] == "Copyright" else "CHARACTER_RESIDUAL",
            "primary_copyright": r.get("primary_copyright", ""),
            "primary_copyright_coverage": r.get("primary_copyright_coverage", ""),
            "current_reason": r["scope_reason"],
        }
        for r in uncertain
    ]
    write_csv(REVIEW_PATH, REVIEW_FIELDS, review_rows)

    real3d = [r for r in ledger if r["media_scope"] == "REAL_3D"]
    write_csv(EXCLUDE_PATH, EXCLUDE_FIELDS, real3d)

    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_generated() -> None:
    source = load_scope_source()
    source_by_id = {row["row_id"]: row for row in source}
    seeds = load_real3d_seeds(source_by_id)

    with LEDGER_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        ledger = list(csv.DictReader(f))
    validate_ledger(ledger, seeds)

    with REVIEW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        review = list(csv.DictReader(f))
    with EXCLUDE_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        exclude = list(csv.DictReader(f))
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    uncertain_count = sum(r["media_scope"] == "UNCERTAIN" for r in ledger)
    real3d_count = sum(r["media_scope"] == "REAL_3D" for r in ledger)
    assert len(review) == uncertain_count, (len(review), uncertain_count)
    assert len(exclude) == real3d_count, (len(exclude), real3d_count)
    assert int(summary["population"]["total"]) == EXPECTED_TOTAL
    assert summary["production_modified"] is False
    assert int(summary["scope_counts"].get("UNCERTAIN", 0)) == uncertain_count
    assert int(summary["scope_counts"].get("REAL_3D", 0)) == real3d_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        validate_generated()
        print("Issue70 full-scope validation PASS")
        return

    ledger, summary = build()
    write_outputs(ledger, summary)
    validate_generated()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
