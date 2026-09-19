#!/usr/bin/env python3
"""Generate Issue #70 Copyright audit batch 018.

For remaining REVIEW_REQUIRED Copyright rows whose current display is a Latin
fallback and whose frozen source contains no Japanese evidence at all, preserve
the canonical/Latin surface instead of inventing a translation. High-impact
rows are isolated for selective external verification.

Proposal-only; production translation data is never modified.
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
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-batch018"
OUT = AUDIT_DIR / "copyright_no_trusted_ja_batch018.csv"
JA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff々〆ヶ]")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


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
            if row.get("row_id") and row.get("audit_verdict"):
                ids.add(row["row_id"].strip())
    return ids


def run_census() -> list[dict[str, str]]:
    if TMP.exists(): shutil.rmtree(TMP)
    subprocess.run([
        sys.executable, str(ROOT / "scripts/issue70/audit_semantic_risk_v3.py"),
        "--out", str(TMP), "--sample-per-category", "300",
    ], cwd=ROOT, check=True)
    return read_csv(TMP / "audit_ledger_template.csv")


def has_any_ja_evidence(row: dict[str, str]) -> bool:
    for field in (
        "source_aliases", "verified_aliases", "existing_display_ja",
        "existing_search_ja", "existing_candidate_ja",
    ):
        if JA_RE.search(row.get(field) or ""):
            return True
    return False


def main() -> int:
    audited = prior_ids(); rows = []
    for row in run_census():
        if row.get("row_id") in audited: continue
        if row.get("category_name") != "Copyright": continue
        if row.get("translation_status") != "REVIEW_REQUIRED": continue
        display = (row.get("display_ja") or "").strip()
        if not display or not display.isascii(): continue
        if has_any_ja_evidence(row): continue
        posts = int(row.get("post_count") or 0)
        external = posts >= 1000
        rows.append({
            "row_id": row["row_id"], "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"], "display_ja": display,
            "search_ja": row.get("search_ja") or "",
            "translation_note": row.get("translation_note") or "",
            "audit_verdict": "NEEDS_EXTERNAL_CHECK" if external else "KEEP",
            "proposed_display_ja": "", "proposed_search_ja": "",
            "reason_code": "HIGH_IMPACT_COPYRIGHT_NO_JA_EVIDENCE" if external else "CONSERVATIVE_COPYRIGHT_LATIN_FALLBACK_NO_JA_EVIDENCE",
            "confidence": "MEDIUM" if external else "HIGH",
            "evidence_refs": "canonical_tag + frozen source aliases/candidates/search evidence",
            "audit_note": (
                "日本語名の根拠が無い高使用数Copyright。推測翻訳せず外部一次寄り確認へ隔離。"
                if external else
                "日本語名の根拠が無いため、直訳・機械翻訳を作らず現在の公式/Canonical Latin表記を維持。"
            ),
            "approval_status": "PROPOSED",
        })
    rows.sort(key=lambda r: (-int(r["post_count"] or 0), r["row_id"]))
    write_csv(OUT, rows, [
        "row_id","canonical_tag","post_count","display_ja","search_ja","translation_note",
        "audit_verdict","proposed_display_ja","proposed_search_ja","reason_code","confidence",
        "evidence_refs","audit_note","approval_status",
    ])
    print({"rows":len(rows),"keep":sum(r["audit_verdict"]=="KEEP" for r in rows),"external":sum(r["audit_verdict"]=="NEEDS_EXTERNAL_CHECK" for r in rows),"production_modified":False})
    return 0

if __name__ == "__main__": raise SystemExit(main())
