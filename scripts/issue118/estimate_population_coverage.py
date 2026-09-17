#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path("docs/issue64/production_candidate/effective_sidecar.csv")
SPECIAL = Path("data/generation/special2788_generation_profile.csv")
ISSUE104 = Path("docs/issue104/product_fit_review_v1.csv")
OUT = Path("docs/issue118/reviews/population_rule_coverage_v1.json")

SAFE_GENERAL_ROOTS = {
    "COLOR_APPEARANCE",
    "COMPOSITION_CAMERA",
    "GAZE_ORIENTATION",
    "HAIR_FACE",
    "LIGHT_TIME_WEATHER",
    "LIVING_NATURE",
    "PLACE_BACKGROUND",
    "TEXT_SYMBOL",
}

EXPLICIT_SPECIAL_PATTERNS_V2 = [
    re.compile(r"(^|_)(handjob|blowjob|fellatio|paizuri|irrumatio|cum|cumshot|ejaculation|orgasm|masturbation|vibrator|dildo|buttjob|threesome|zoophilia|prostitution|penetration)($|_)"),
    re.compile(r"(^|_)sex($|_)"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize(value: str) -> str:
    return "_".join(value.strip().lower().replace("_", " ").split())


def root(row: dict[str, str] | None) -> str:
    path = (row or {}).get("primary_path", "").strip()
    return path.split("/", 1)[0] if path else ""


def main() -> int:
    general = read_csv(GENERAL)
    special = read_csv(SPECIAL)
    issue104 = read_csv(ISSUE104)
    if len(general) != 30629 or len(special) != 3059:
        raise SystemExit(f"source drift general={len(general)} special={len(special)}")

    g = {normalize(r["canonical"]): r for r in general}
    s = {normalize(r["Tag"]): r for r in special}
    r104 = {normalize(r["canonical_tag"]) for r in issue104}
    if len(g) != 30629 or len(s) != 3059:
        raise SystemExit("normalized identity collision")

    union = sorted(set(g) | set(s))
    overlap = set(g) & set(s)

    auto_nonsex = []
    auto_sexual = []
    safe_root_counts = Counter()
    for key in union:
        grow = g.get(key)
        srow = s.get(key)
        if (
            grow is not None
            and srow is None
            and key not in r104
            and root(grow) in SAFE_GENERAL_ROOTS
        ):
            auto_nonsex.append(key)
            safe_root_counts[root(grow)] += 1
        if srow is not None and any(p.search(key) for p in EXPLICIT_SPECIAL_PATTERNS_V2):
            auto_sexual.append(key)

    conflict = sorted(set(auto_nonsex) & set(auto_sexual))
    if conflict:
        raise SystemExit(f"rule conflict: {conflict[:10]}")

    auto = set(auto_nonsex) | set(auto_sexual)
    result = {
        "issue": 118,
        "mode": "READ_ONLY_FULL_POPULATION_RULE_COVERAGE_V1",
        "population": {
            "general_rows": len(general),
            "special_rows": len(special),
            "normalized_union_rows": len(union),
            "normalized_overlap_rows": len(overlap),
        },
        "pilot_calibrated_rules": {
            "AUTO_NONSEX_SAFE_GENERAL_ROOTS_ANYCONF_V1": {
                "candidate_rows": len(auto_nonsex),
                "population_share": round(len(auto_nonsex) / len(union), 6),
                "safe_root_counts": dict(sorted(safe_root_counts.items())),
                "examples": auto_nonsex[:20],
                "pilot_precision": 1.0,
                "pilot_matched": 75,
            },
            "AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2": {
                "candidate_rows": len(auto_sexual),
                "population_share": round(len(auto_sexual) / len(union), 6),
                "examples": auto_sexual[:20],
                "pilot_precision": 1.0,
                "pilot_matched": 23,
            },
        },
        "combined_auto_candidate_rows": len(auto),
        "combined_population_share": round(len(auto) / len(union), 6),
        "remaining_not_auto_candidate_rows": len(union) - len(auto),
        "rule_conflict_rows": len(conflict),
        "interpretation_guard": "Counts are candidate coverage only. Pilot precision does not certify unreviewed production rows; no production classification is written.",
        "boundaries": {
            "production_classification_written": "NO",
            "main_mutated": "NO",
            "issue117_code_mutated": "NO",
            "catalog_mutated": "NO",
            "user_db_mutated": "NO",
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "auto_nonsex": len(auto_nonsex),
        "auto_sexual": len(auto_sexual),
        "combined": len(auto),
        "remaining": len(union) - len(auto),
    }, sort_keys=True))
    print("ISSUE118_POPULATION_RULE_COVERAGE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
