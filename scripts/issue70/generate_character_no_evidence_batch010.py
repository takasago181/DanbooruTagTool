#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 010.

Resolve Character REVIEW_REQUIRED rows whose current display is a Latin fallback
and for which the frozen source contains no trustworthy Japanese-facing evidence.
For low-impact rows the safest semantic decision is KEEP: do not invent a reading.
High-impact rows are isolated for external verification.

Proposal-only. Production translation data is never modified.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "docs/issue70/audit"
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-batch010"
OUT = AUDIT_DIR / "character_no_trusted_ja_batch010.csv"

KANA_RE = re.compile(r"[\u3040-\u30ff]")
JA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff々〆ヶ]")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def prior_ids() -> set[str]:
    ids: set[str] = set()
    for path in AUDIT_DIR.glob("*.csv"):
        if path.name == OUT.name:
            continue
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            if row.get("audit_verdict") and row.get("row_id"):
                ids.add(row["row_id"].strip())
    return ids


def run_census() -> Path:
    if TMP.exists():
        shutil.rmtree(TMP)
    subprocess.run([
        sys.executable, str(ROOT / "scripts/issue70/audit_semantic_risk_v3.py"),
        "--out", str(TMP), "--sample-per-category", "300",
    ], cwd=ROOT, check=True)
    return TMP / "audit_ledger_template.csv"


def has_trusted_ja(row: dict[str, str]) -> bool:
    # Same trust boundary as the v3 refinement: existing display/search are
    # Japanese-facing evidence; raw candidates count only when kana-bearing.
    if JA_RE.search(row.get("existing_display_ja") or ""):
        return True
    if JA_RE.search(row.get("existing_search_ja") or ""):
        return True
    if KANA_RE.search(row.get("existing_candidate_ja") or ""):
        return True
    return False


def main() -> int:
    audited = prior_ids()
    ledger = read_csv(run_census())
    targets = []
    for row in ledger:
        if row.get("row_id") in audited:
            continue
        if row.get("category_name") != "Character":
            continue
        if row.get("translation_status") != "REVIEW_REQUIRED":
            continue
        flags = row.get("risk_flags") or ""
        if "ASCII_ONLY_DISPLAY_NON_ARTIST" not in flags:
            continue
        if has_trusted_ja(row):
            continue
        targets.append(row)
    targets.sort(key=lambda r: (-int(r.get("post_count") or 0), r["row_id"]))

    rows: list[dict[str, str]] = []
    for row in targets:
        posts = int(row.get("post_count") or 0)
        high_impact = posts >= 500
        rows.append({
            "row_id": row["row_id"],
            "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"],
            "display_ja": row["display_ja"],
            "search_ja": row.get("search_ja") or "",
            "translation_note": row.get("translation_note") or "",
            "related_copyright_top1": row.get("related_copyright_top1") or "",
            "audit_verdict": "NEEDS_EXTERNAL_CHECK" if high_impact else "KEEP",
            "proposed_display_ja": "",
            "proposed_search_ja": "",
            "reason_code": "HIGH_IMPACT_NO_TRUSTED_JA_EVIDENCE" if high_impact else "CONSERVATIVE_LATIN_FALLBACK_NO_TRUSTED_JA_EVIDENCE",
            "confidence": "MEDIUM" if high_impact else "HIGH",
            "evidence_refs": "canonical_tag + frozen Issue70 source evidence",
            "audit_note": (
                "日本語表示の根拠が無い高使用数Character。推測せず外部一次寄り確認へ隔離。"
                if high_impact else
                "日本語表示の信頼できる根拠が無いため、誤った読みを作らず現在のLatin/canonical fallbackを維持。"
            ),
            "approval_status": "PROPOSED",
        })

    write_csv(OUT, rows, [
        "row_id", "canonical_tag", "post_count", "display_ja", "search_ja",
        "translation_note", "related_copyright_top1", "audit_verdict",
        "proposed_display_ja", "proposed_search_ja", "reason_code", "confidence",
        "evidence_refs", "audit_note", "approval_status",
    ])
    print({
        "rows": len(rows),
        "keep": sum(r["audit_verdict"] == "KEEP" for r in rows),
        "external": sum(r["audit_verdict"] == "NEEDS_EXTERNAL_CHECK" for r in rows),
        "production_modified": False,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
