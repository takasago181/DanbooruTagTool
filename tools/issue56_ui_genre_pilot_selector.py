#!/usr/bin/env python3
"""Build the reproducible Issue #56 Special UI taxonomy pilot.

This tool is deliberately read-only with respect to canonical Special data.
It parses the human-reference files under data/special2788/prompt_reference,
materializes them as a review table, and selects a deterministic 150-row
pilot for UI browsing taxonomy review.

It does NOT classify rows and does NOT mutate production/canonical data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SELECTOR_VERSION = "issue56-ui-pilot-v1"
RANDOM_SEED = "issue56-ui-pilot-v1|random"
BOUNDARY_SEED = "issue56-ui-pilot-v1|boundary"
RARE_NONCOUNT_SEED = "issue56-ui-pilot-v1|rare-noncount"

SOURCE_GLOB = "[0-9][0-9]_*.txt"
OTHER_PREFIX = "13_その他・文脈"

MATERIALIZED_NAME = "issue56_ui_genre_source_materialized_v1.csv"
PILOT_NAME = "issue56_ui_genre_pilot_v1.csv"
META_NAME = "issue56_ui_genre_pilot_v1.meta.json"

# Sampling rules only. These patterns never assign a final UI genre.
BOUNDARY_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "BODY_EXPOSURE",
        re.compile(
            r"covered|covering|peek|slip|cutout|see[- ]through|transparent|"
            r"under clothes|through clothes|out of clothes|visible|indents|"
            r"camel ?toe|bottomless|topless|nude|naked",
            re.IGNORECASE,
        ),
    ),
    (
        "ACTIVITY_CONTACT",
        re.compile(
            r"insertion|penetration|fingering|licking|stimulation|"
            r" on (?:face|pussy|penis|anus|nipple|breast)|"
            r" to (?:breast|nipple)|sex",
            re.IGNORECASE,
        ),
    ),
    (
        "TOOLS_BDSM",
        re.compile(
            r"vibrator|dildo|sex toy|machine|gag|chastity|clamp|cuffs|"
            r"bondage|restraint|shackles|spreader|pillory|stocks|whip",
            re.IGNORECASE,
        ),
    ),
    (
        "ROLE_META_CONTEXT",
        re.compile(
            r"uncensored|censored|questionable|sensitive|netorare|\bntr\b|"
            r"assertive|public|stealth|caught|voyeur|prostitution|"
            r"relationship|dominator|submission|slave",
            re.IGNORECASE,
        ),
    ),
    (
        "INJURY_BODY_BDSM",
        re.compile(
            r"torture|busting|severed|blood|prolapse|impal|guro|gore|"
            r"mutil|asphyx|pain|bleed|decap|amput|crusher|strangl",
            re.IGNORECASE,
        ),
    ),
)


@dataclass(frozen=True)
class PromptRow:
    source_file: str
    old_reference_row: str
    japanese_display: str
    english_tag: str
    special_id: int
    layer: str
    post_count: int | None
    canonical_target: str

    @property
    def is_alias(self) -> bool:
        return self.layer == "A"

    @property
    def old_reference_category(self) -> str:
        stem = Path(self.source_file).stem
        return stem.split("_part", 1)[0]

    @property
    def search_text(self) -> str:
        return f"{self.english_tag.replace('_', ' ')} {self.japanese_display}"


TAIL_RE = re.compile(r"^(?P<count>\d+|-)(?:\s+->(?P<target>.+))?$")


def normalize_tag(value: str) -> str:
    value = value.strip().lower().replace("_", " ")
    return "_".join(value.split())


def stable_key(seed: str, row: PromptRow, extra: str = "") -> str:
    payload = f"{seed}|{extra}|{row.special_id}|{row.english_tag}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def parse_prompt_reference_file(path: Path) -> list[PromptRow]:
    rows: list[PromptRow] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip("\ufeff")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 5)
        if len(parts) != 6:
            raise ValueError(f"{path}:{line_number}: expected 6 tab fields, got {len(parts)}")
        row_ref, ja, tag, id_field, layer, tail = parts
        if not id_field.startswith("ID:"):
            raise ValueError(f"{path}:{line_number}: invalid Special ID field {id_field!r}")
        try:
            special_id = int(id_field[3:])
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: invalid Special ID {id_field!r}") from exc
        match = TAIL_RE.fullmatch(tail.strip())
        if not match:
            raise ValueError(f"{path}:{line_number}: invalid post_count/target field {tail!r}")
        count_text = match.group("count")
        post_count = None if count_text == "-" else int(count_text)
        canonical_target = (match.group("target") or "").strip()
        rows.append(
            PromptRow(
                source_file=path.name,
                old_reference_row=row_ref,
                japanese_display=ja.strip(),
                english_tag=tag.strip(),
                special_id=special_id,
                layer=layer.strip(),
                post_count=post_count,
                canonical_target=canonical_target,
            )
        )
    return rows


def load_prompt_reference(source_dir: Path) -> tuple[list[PromptRow], dict[str, str]]:
    paths = sorted(p for p in source_dir.glob(SOURCE_GLOB) if p.name != "MANIFEST.txt")
    if not paths:
        raise FileNotFoundError(f"no prompt-reference files found under {source_dir}")

    rows: list[PromptRow] = []
    source_hashes: dict[str, str] = {}
    for path in paths:
        source_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.extend(parse_prompt_reference_file(path))

    ids = [row.special_id for row in rows]
    if len(ids) != len(set(ids)):
        duplicate_ids = sorted(sid for sid, count in Counter(ids).items() if count > 1)
        raise ValueError(f"duplicate Special IDs in prompt reference: {duplicate_ids[:20]}")
    return rows, source_hashes


def build_tag_lookup(rows: Sequence[PromptRow]) -> dict[str, list[PromptRow]]:
    lookup: dict[str, list[PromptRow]] = {}
    for row in rows:
        lookup.setdefault(normalize_tag(row.english_tag), []).append(row)
    return lookup


def resolve_alias_target(row: PromptRow, lookup: dict[str, list[PromptRow]]) -> PromptRow | None:
    if not row.is_alias or not row.canonical_target:
        return None
    candidates = lookup.get(normalize_tag(row.canonical_target), [])
    non_alias = [candidate for candidate in candidates if not candidate.is_alias]
    candidates = non_alias or candidates
    if len(candidates) != 1:
        return None
    return candidates[0]


def take_unique(
    candidates: Iterable[PromptRow],
    selected_ids: set[int],
    count: int,
) -> list[PromptRow]:
    chosen: list[PromptRow] = []
    for row in candidates:
        if row.special_id in selected_ids:
            continue
        chosen.append(row)
        selected_ids.add(row.special_id)
        if len(chosen) == count:
            break
    if len(chosen) != count:
        raise ValueError(f"needed {count} rows but found only {len(chosen)} eligible rows")
    return chosen


def select_pilot(rows: Sequence[PromptRow]) -> list[dict[str, object]]:
    selected_ids: set[int] = set()
    output: list[dict[str, object]] = []
    lookup = build_tag_lookup(rows)

    def append_row(row: PromptRow, stratum: str, pair_group: str = "", boundary_family: str = "") -> None:
        output.append(
            {
                "selection_stratum": stratum,
                "pair_group": pair_group,
                "boundary_family": boundary_family,
                "row": row,
            }
        )

    # 1) Global high-usage rows from the old catch-all, after all parts are materialized.
    high_candidates = sorted(
        (
            row
            for row in rows
            if row.source_file.startswith(OTHER_PREFIX)
            and not row.is_alias
            and row.post_count is not None
        ),
        key=lambda row: (-int(row.post_count or 0), row.special_id),
    )
    for row in take_unique(high_candidates, selected_ids, 50):
        append_row(row, "HIGH_USAGE_OTHER")

    # 2) 15 resolvable Alias/canonical pairs. Prefer pairs spanning old categories,
    # then higher-usage aliases, then stable SpecialID order.
    alias_pairs: list[tuple[PromptRow, PromptRow]] = []
    for alias in rows:
        if not alias.is_alias:
            continue
        target = resolve_alias_target(alias, lookup)
        if target is None or target.special_id == alias.special_id:
            continue
        alias_pairs.append((alias, target))
    alias_pairs.sort(
        key=lambda pair: (
            0 if pair[0].old_reference_category != pair[1].old_reference_category else 1,
            -(pair[0].post_count if pair[0].post_count is not None else -1),
            pair[0].special_id,
            pair[1].special_id,
        )
    )
    chosen_pairs = 0
    for alias, target in alias_pairs:
        if alias.special_id in selected_ids or target.special_id in selected_ids:
            continue
        group = f"ALIAS-{alias.special_id}-TO-{target.special_id}"
        selected_ids.add(alias.special_id)
        selected_ids.add(target.special_id)
        append_row(alias, "ALIAS", pair_group=group)
        append_row(target, "ALIAS_CANONICAL_CONTROL", pair_group=group)
        chosen_pairs += 1
        if chosen_pairs == 15:
            break
    if chosen_pairs != 15:
        raise ValueError(f"needed 15 Alias/canonical pairs but found only {chosen_pairs}")

    # 3) Five boundary families x six rows. Rules create sample candidates only.
    for family, pattern in BOUNDARY_RULES:
        candidates = [
            row
            for row in rows
            if not row.is_alias
            and row.special_id not in selected_ids
            and pattern.search(row.search_text)
        ]
        candidates.sort(key=lambda row: stable_key(BOUNDARY_SEED, row, family))
        chosen = take_unique(candidates, selected_ids, 6)
        for row in chosen:
            append_row(row, f"BOUNDARY_{family}", boundary_family=family)

    # 4) Rare/tail: ten lowest numeric rows plus ten deterministic non-count rows.
    rare_numeric = sorted(
        (
            row
            for row in rows
            if not row.is_alias and row.post_count is not None and row.special_id not in selected_ids
        ),
        key=lambda row: (int(row.post_count or 0), row.special_id),
    )
    for row in take_unique(rare_numeric, selected_ids, 10):
        append_row(row, "RARE_NUMERIC")

    rare_noncount = [
        row
        for row in rows
        if not row.is_alias and row.post_count is None and row.special_id not in selected_ids
    ]
    rare_noncount.sort(key=lambda row: stable_key(RARE_NONCOUNT_SEED, row))
    for row in take_unique(rare_noncount, selected_ids, 10):
        append_row(row, "RARE_NONCOUNT")

    # 5) Deterministic pseudo-random rows from the full remaining pool.
    random_candidates = [row for row in rows if row.special_id not in selected_ids]
    random_candidates.sort(key=lambda row: stable_key(RANDOM_SEED, row))
    for row in take_unique(random_candidates, selected_ids, 20):
        append_row(row, "RANDOM")

    if len(output) != 150:
        raise AssertionError(f"pilot selection must contain 150 rows, got {len(output)}")
    if len({item["row"].special_id for item in output}) != 150:
        raise AssertionError("pilot selection contains duplicate Special IDs")
    return output


MATERIALIZED_FIELDS = [
    "source_file",
    "old_reference_row",
    "old_reference_category",
    "special_id",
    "japanese_display",
    "english_tag",
    "layer",
    "post_count",
    "canonical_target",
    "is_alias",
]

PILOT_FIELDS = [
    "pilot_order",
    "selection_stratum",
    "pair_group",
    "boundary_family",
    "old_reference_file",
    "old_reference_row",
    "old_reference_category",
    "special_id",
    "japanese_display",
    "english_tag",
    "layer",
    "post_count",
    "canonical_target",
    "primary_genre_id",
    "primary_subgenre_id",
    "secondary_paths",
    "classification_status",
    "classification_reason",
    "ambiguity_note",
]


def materialized_record(row: PromptRow) -> dict[str, object]:
    return {
        "source_file": row.source_file,
        "old_reference_row": row.old_reference_row,
        "old_reference_category": row.old_reference_category,
        "special_id": row.special_id,
        "japanese_display": row.japanese_display,
        "english_tag": row.english_tag,
        "layer": row.layer,
        "post_count": "" if row.post_count is None else row.post_count,
        "canonical_target": row.canonical_target,
        "is_alias": "true" if row.is_alias else "false",
    }


def pilot_record(order: int, item: dict[str, object]) -> dict[str, object]:
    row = item["row"]
    assert isinstance(row, PromptRow)
    return {
        "pilot_order": order,
        "selection_stratum": item["selection_stratum"],
        "pair_group": item["pair_group"],
        "boundary_family": item["boundary_family"],
        "old_reference_file": row.source_file,
        "old_reference_row": row.old_reference_row,
        "old_reference_category": row.old_reference_category,
        "special_id": row.special_id,
        "japanese_display": row.japanese_display,
        "english_tag": row.english_tag,
        "layer": row.layer,
        "post_count": "" if row.post_count is None else row.post_count,
        "canonical_target": row.canonical_target,
        "primary_genre_id": "",
        "primary_subgenre_id": "",
        "secondary_paths": "",
        "classification_status": "",
        "classification_reason": "",
        "ambiguity_note": "",
    }


def write_csv(path: Path, fieldnames: Sequence[str], records: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_outputs(root: Path, out_dir: Path) -> dict[str, object]:
    source_dir = root / "data" / "special2788" / "prompt_reference"
    rows, source_hashes = load_prompt_reference(source_dir)
    if len(rows) != 2788:
        raise ValueError(f"expected 2,788 prompt-reference rows, got {len(rows)}")
    if {row.special_id for row in rows} != set(range(1, 2789)):
        missing = sorted(set(range(1, 2789)) - {row.special_id for row in rows})
        extra = sorted({row.special_id for row in rows} - set(range(1, 2789)))
        raise ValueError(f"SpecialID coverage mismatch; missing={missing[:20]} extra={extra[:20]}")

    pilot = select_pilot(rows)
    materialized_path = out_dir / MATERIALIZED_NAME
    pilot_path = out_dir / PILOT_NAME
    meta_path = out_dir / META_NAME

    write_csv(
        materialized_path,
        MATERIALIZED_FIELDS,
        (materialized_record(row) for row in sorted(rows, key=lambda row: row.special_id)),
    )
    pilot_records = [pilot_record(index, item) for index, item in enumerate(pilot, start=1)]
    write_csv(pilot_path, PILOT_FIELDS, pilot_records)

    stratum_counts = Counter(str(item["selection_stratum"]) for item in pilot)
    meta = {
        "selector_version": SELECTOR_VERSION,
        "source_dir": str(source_dir.relative_to(root)),
        "source_row_count": len(rows),
        "source_unique_special_ids": len({row.special_id for row in rows}),
        "source_files_sha256": source_hashes,
        "materialized_csv": str(materialized_path.relative_to(root)),
        "materialized_sha256": sha256_file(materialized_path),
        "pilot_csv": str(pilot_path.relative_to(root)),
        "pilot_sha256": sha256_file(pilot_path),
        "pilot_row_count": len(pilot),
        "pilot_unique_special_ids": len({item["row"].special_id for item in pilot}),
        "selection_stratum_counts": dict(sorted(stratum_counts.items())),
        "seeds": {
            "boundary": BOUNDARY_SEED,
            "rare_noncount": RARE_NONCOUNT_SEED,
            "random": RANDOM_SEED,
        },
        "notes": [
            "Sampling rules only; no final UI classification is assigned by this selector.",
            "Canonical/production Special data is read-only.",
            "Boundary regexes create pilot candidates only and have no semantic authority.",
        ],
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="default: <root>/docs/issue56/pilot",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    out_dir = (args.out_dir or (root / "docs" / "issue56" / "pilot")).resolve()
    meta = build_outputs(root, out_dir)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
