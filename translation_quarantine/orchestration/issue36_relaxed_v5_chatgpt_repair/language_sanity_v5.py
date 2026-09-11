#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TABLE = SCRIPT_DIR / "materialized/final_translation_table_v5.csv"
OVERRIDE_DIR = SCRIPT_DIR / "overrides"
OUT_DIR = SCRIPT_DIR / "materialized"
CANDIDATES = OUT_DIR / "language_sanity_candidates.csv"
RAW_WRAPPERS = OUT_DIR / "language_sanity_raw_english_wrappers.csv"
REPORT = OUT_DIR / "language_sanity_report.json"

HANGUL_RE = re.compile(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{2,}")
RAW_WRAPPER_RE = re.compile(r"(?:タグ|tag)\s*[「\"'].*?[A-Za-z].*?[」\"']", re.IGNORECASE)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# High-signal Simplified-Chinese forms that are not normal modern Japanese
# orthography. Do not include characters that are also ordinary Japanese
# (for example 猫, 体, 画, 学, 着, 会, 里, 与, 条). The previous detector
# included those shared characters and produced >1,000 false-positive rows.
# This remains a review-candidate detector only; it never auto-fixes text.
SIMPLIFIED_CHINESE_HINT_RE = re.compile(
    r"[这们为发见说让还过从对开关头脸门车书样气边进远两东乐龙鱼鸟马岁现给么饭药员厂广网线级场术块张颗]"
)


def read_override_canonicals() -> set[str]:
    result: set[str] = set()
    for path in sorted(OVERRIDE_DIR.glob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames and "canonical" in reader.fieldnames:
                for row in reader:
                    result.add(row["canonical"])
    return result


def write_candidates(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["row_number", "canonical", "display_ja", "checks", "already_overridden"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with TABLE.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    overridden = read_override_canonicals()
    candidates: list[dict[str, str]] = []
    raw_wrappers: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    raw_override_counts: Counter[str] = Counter()

    for idx, row in enumerate(rows, start=1):
        text = row["display_ja"]
        checks: list[str] = []
        if HANGUL_RE.search(text):
            checks.append("HANGUL")
        if RAW_WRAPPER_RE.search(text):
            checks.append("RAW_ENGLISH_WRAPPER")
        if CONTROL_RE.search(text):
            checks.append("CONTROL_CHAR")
        if ASCII_WORD_RE.search(text):
            checks.append("ASCII_WORD")
        if SIMPLIFIED_CHINESE_HINT_RE.search(text):
            checks.append("SIMPLIFIED_CHINESE_HINT")
        if not checks:
            continue

        for check in checks:
            counts[check] += 1
        item = {
            "row_number": str(idx),
            "canonical": row["canonical"],
            "display_ja": text,
            "checks": ";".join(checks),
            "already_overridden": "true" if row["canonical"] in overridden else "false",
        }
        candidates.append(item)
        if "RAW_ENGLISH_WRAPPER" in checks:
            raw_wrappers.append(item)
            raw_override_counts[item["already_overridden"]] += 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_candidates(CANDIDATES, candidates)
    write_candidates(RAW_WRAPPERS, raw_wrappers)

    hard_fail_counts = {
        "HANGUL": counts["HANGUL"],
        "RAW_ENGLISH_WRAPPER": counts["RAW_ENGLISH_WRAPPER"],
        "CONTROL_CHAR": counts["CONTROL_CHAR"],
    }
    report = {
        "status": "PASS" if not any(hard_fail_counts.values()) else "REVIEW_REQUIRED",
        "rows_scanned": len(rows),
        "candidate_rows": len(candidates),
        "check_counts": dict(sorted(counts.items())),
        "hard_fail_counts": hard_fail_counts,
        "raw_english_wrapper_rows": len(raw_wrappers),
        "raw_english_wrapper_already_overridden": raw_override_counts["true"],
        "raw_english_wrapper_not_overridden": raw_override_counts["false"],
        "notes": {
            "ASCII_WORD": "review candidate only; proper names, acronyms, codes and product names may be valid",
            "SIMPLIFIED_CHINESE_HINT": "high-signal Simplified-Chinese-form heuristic only; shared Japanese characters are intentionally excluded; never auto-fix from this signal",
            "RAW_ENGLISH_WRAPPER": "semantic review required; this script never auto-fixes it",
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
