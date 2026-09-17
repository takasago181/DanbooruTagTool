#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

SAMPLE = Path("docs/issue118/intent_pilot_sample_v1.csv")
REVIEW_DIR = Path("docs/issue118/reviews")
OUT = REVIEW_DIR / "pilot_rule_evaluation_v1.json"

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

EXPLICIT_SPECIAL_PATTERNS_V1 = [
    re.compile(r"(^|_)(handjob|blowjob|fellatio|paizuri|irrumatio|cum|cumshot|ejaculation|orgasm|masturbation|vibrator|dildo|buttjob|threesome|zoophilia|prostitution|penetration|condom)($|_)"),
    re.compile(r"(^|_)sex($|_)"),
]

# V2 deliberately removes generic condom-token promotion because the pilot found
# condom_thigh_strap to be CONTEXTUAL rather than SEXUAL.
EXPLICIT_SPECIAL_PATTERNS_V2 = [
    re.compile(r"(^|_)(handjob|blowjob|fellatio|paizuri|irrumatio|cum|cumshot|ejaculation|orgasm|masturbation|vibrator|dildo|buttjob|threesome|zoophilia|prostitution|penetration)($|_)"),
    re.compile(r"(^|_)sex($|_)"),
]


def primary_root(row: dict[str, str]) -> str:
    path = row.get("general_primary_path", "").strip()
    return path.split("/", 1)[0] if path else ""


def load() -> list[dict[str, str]]:
    with SAMPLE.open(encoding="utf-8-sig", newline="") as f:
        sample = list(csv.DictReader(f))
    sample_by_key = {r["identity_key"]: r for r in sample}
    reviews = []
    for path in sorted(REVIEW_DIR.glob("chunk_???_review_v1.csv")):
        with path.open(encoding="utf-8-sig", newline="") as f:
            reviews.extend(csv.DictReader(f))
    if len(sample) != 700 or len(reviews) != 700:
        raise SystemExit("pilot/review coverage mismatch")
    joined = []
    for review in reviews:
        s = sample_by_key[review["identity_key"]]
        joined.append({**s, **review, "effective_class": review["reviewed_class"].strip() or "UNCLASSIFIED"})
    return joined


def evaluate(rows: list[dict[str, str]], name: str, target: str, predicate) -> dict:
    matched = [r for r in rows if predicate(r)]
    counts = Counter(r["effective_class"] for r in matched)
    errors = [r["identity_key"] for r in matched if r["effective_class"] != target]
    opposite = "SEXUAL" if target == "NON_SEXUAL" else "NON_SEXUAL"
    severe = [r["identity_key"] for r in matched if r["effective_class"] == opposite]
    return {
        "rule": name,
        "target": target,
        "matched": len(matched),
        "class_counts": dict(sorted(counts.items())),
        "target_precision": round(counts[target] / len(matched), 6) if matched else None,
        "non_target_count": len(errors),
        "severe_opposite_count": len(severe),
        "non_target_examples": errors[:20],
        "severe_opposite_examples": severe[:20],
    }


def main() -> int:
    rows = load()
    rules = []
    rules.append(evaluate(
        rows,
        "AUTO_NONSEX_SAFE_GENERAL_ROOTS_HIGH_V1",
        "NON_SEXUAL",
        lambda r: (
            r["is_general"] == "YES" and r["is_special"] == "NO"
            and r["issue104_reviewed"] != "YES"
            and r.get("general_confidence", "") == "HIGH"
            and primary_root(r) in SAFE_GENERAL_ROOTS
        ),
    ))
    rules.append(evaluate(
        rows,
        "AUTO_NONSEX_SAFE_GENERAL_ROOTS_ANYCONF_V1",
        "NON_SEXUAL",
        lambda r: (
            r["is_general"] == "YES" and r["is_special"] == "NO"
            and r["issue104_reviewed"] != "YES"
            and primary_root(r) in SAFE_GENERAL_ROOTS
        ),
    ))
    rules.append(evaluate(
        rows,
        "AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V1",
        "SEXUAL",
        lambda r: (
            r["is_special"] == "YES"
            and any(p.search(r["identity_key"]) for p in EXPLICIT_SPECIAL_PATTERNS_V1)
        ),
    ))
    rules.append(evaluate(
        rows,
        "AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2",
        "SEXUAL",
        lambda r: (
            r["is_special"] == "YES"
            and any(p.search(r["identity_key"]) for p in EXPLICIT_SPECIAL_PATTERNS_V2)
        ),
    ))

    out = {
        "issue": 118,
        "mode": "PILOT_RULE_EVALUATION_V1",
        "pilot_rows": len(rows),
        "rules": rules,
        "interpretation_guard": "Pilot rule performance is calibration evidence only; it is not production authority and is not a population prevalence estimate.",
        "boundaries": {
            "production_classification_written": "NO",
            "main_mutated": "NO",
            "issue117_code_mutated": "NO",
            "catalog_mutated": "NO",
            "user_db_mutated": "NO",
        },
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for rule in rules:
        print(rule["rule"], rule["matched"], rule["target_precision"], rule["severe_opposite_count"])
    print("ISSUE118_PILOT_RULE_EVALUATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
