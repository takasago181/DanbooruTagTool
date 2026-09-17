#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path("docs/issue64/production_candidate/effective_sidecar.csv")
SPECIAL = Path("data/generation/special2788_generation_profile.csv")
ISSUE104 = Path("docs/issue104/product_fit_review_v1.csv")
PILOT = Path("docs/issue118/intent_pilot_sample_v1.csv")
OUT_DIR = Path("docs/issue118/holdout")
SEED = "issue118-rule-holdout-v1"

SAFE_GENERAL_ROOTS = [
    "COLOR_APPEARANCE",
    "COMPOSITION_CAMERA",
    "GAZE_ORIENTATION",
    "HAIR_FACE",
    "LIGHT_TIME_WEATHER",
    "LIVING_NATURE",
    "PLACE_BACKGROUND",
    "TEXT_SYMBOL",
]
EXPLICIT_SPECIAL_PATTERNS_V2 = [
    re.compile(r"(^|_)(handjob|blowjob|fellatio|paizuri|irrumatio|cum|cumshot|ejaculation|orgasm|masturbation|vibrator|dildo|buttjob|threesome|zoophilia|prostitution|penetration)($|_)"),
    re.compile(r"(^|_)sex($|_)"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return "_".join(v.strip().lower().replace("_", " ").split())


def rank(k: str) -> str:
    return hashlib.sha256(f"{SEED}|{k}".encode()).hexdigest()


def root(row: dict[str, str]) -> str:
    p = row.get("primary_path", "").strip()
    return p.split("/", 1)[0] if p else ""


def main() -> int:
    general = read_csv(GENERAL)
    special = read_csv(SPECIAL)
    issue104 = read_csv(ISSUE104)
    pilot = read_csv(PILOT)
    if len(general) != 30629 or len(special) != 3059 or len(pilot) != 700:
        raise SystemExit("source count drift")

    g = {norm(r["canonical"]): r for r in general}
    s = {norm(r["Tag"]): r for r in special}
    i104 = {norm(r["canonical_tag"]) for r in issue104}
    pilot_keys = {r["identity_key"] for r in pilot}

    rows: list[dict[str, str]] = []
    counts = Counter()
    chosen: set[str] = set()

    # Independent negative holdout: 20 unseen candidates from each safe General root.
    for rname in SAFE_GENERAL_ROOTS:
        pool = [
            k for k, grow in g.items()
            if k not in s and k not in i104 and k not in pilot_keys and root(grow) == rname
        ]
        pool.sort(key=lambda k: (rank(k), k))
        selected = pool[:20]
        if len(selected) != 20:
            raise SystemExit(f"insufficient holdout rows for root {rname}: {len(selected)}")
        for k in selected:
            grow = g[k]
            rows.append({
                "identity_key": k,
                "candidate_rule": "AUTO_NONSEX_SAFE_GENERAL_ROOTS_ANYCONF_V1",
                "candidate_class": "NON_SEXUAL",
                "general_primary_path": grow.get("primary_path", ""),
                "general_confidence": grow.get("confidence", ""),
                "special_id": "",
                "generation_family": "",
                "holdout_group": f"NONSEX_{rname}",
                "sample_rank": rank(k),
            })
            chosen.add(k)
            counts[f"NONSEX_{rname}"] += 1

    # Independent positive holdout: 80 unseen V2 candidates.
    sexual_pool = [
        k for k in s
        if k not in pilot_keys and k not in chosen and any(p.search(k) for p in EXPLICIT_SPECIAL_PATTERNS_V2)
    ]
    sexual_pool.sort(key=lambda k: (rank(k), k))
    selected_sex = sexual_pool[:80]
    if len(selected_sex) != 80:
        raise SystemExit(f"insufficient sexual holdout candidates: {len(selected_sex)}")
    for k in selected_sex:
        srow = s[k]
        rows.append({
            "identity_key": k,
            "candidate_rule": "AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2",
            "candidate_class": "SEXUAL",
            "general_primary_path": g.get(k, {}).get("primary_path", ""),
            "general_confidence": g.get(k, {}).get("confidence", ""),
            "special_id": srow.get("SpecialID", ""),
            "generation_family": srow.get("GenerationFamily", ""),
            "holdout_group": "SEXUAL_V2",
            "sample_rank": rank(k),
        })
        counts["SEXUAL_V2"] += 1

    if len(rows) != 240 or len({r['identity_key'] for r in rows}) != 240:
        raise SystemExit("holdout size/identity uniqueness failure")
    rows.sort(key=lambda r: (r["candidate_rule"], r["holdout_group"], r["sample_rank"], r["identity_key"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sample_path = OUT_DIR / "rule_holdout_sample_v1.csv"
    fields = list(rows[0].keys())
    with sample_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    chunk_dir = OUT_DIR / "review_chunks"
    chunk_dir.mkdir(exist_ok=True)
    for old in chunk_dir.glob("chunk_*.csv"):
        old.unlink()
    for i in range(0, 240, 80):
        path = chunk_dir / f"chunk_{i//80+1:03d}.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader(); w.writerows(rows[i:i+80])

    summary = {
        "issue": 118,
        "mode": "INDEPENDENT_RULE_HOLDOUT_V1",
        "pilot_identity_excluded": len(pilot_keys),
        "holdout_rows": len(rows),
        "group_counts": dict(sorted(counts.items())),
        "nonsexual_rows": 160,
        "sexual_rows": 80,
        "review_chunk_count": 3,
        "review_chunk_size": 80,
        "boundaries": {
            "production_classification_written": "NO",
            "main_mutated": "NO",
            "issue117_code_mutated": "NO",
            "catalog_mutated": "NO",
            "user_db_mutated": "NO",
        },
    }
    (OUT_DIR / "rule_holdout_summary_v1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("ISSUE118_RULE_HOLDOUT_MATERIALIZED=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
