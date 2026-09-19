#!/usr/bin/env python3
"""Generate deterministic high-confidence Issue #70 semantic-audit batches.

This script is proposal-only. It re-runs the v3 read-only census, excludes rows
already audited in earlier committed batches, then emits only decisions that do
not require guessing names or translations:

- restore preserved Japanese search terms when Japanese discoverability was lost;
- de-duplicate search terms by the runtime normalizer;
- complete the initial Artist audit conservatively (keep established/romanized
  surfaces; isolate unsupported Japanese readings for external verification).

No production translation file is modified.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "docs/issue70/audit"
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-autobatch"
OUTPUTS = {
    "restore": AUDIT_DIR / "search_restore_batch006.csv",
    "dedup": AUDIT_DIR / "search_dedup_batch007.csv",
    "artist": AUDIT_DIR / "artist_initial_audit_batch008.csv",
    "summary": AUDIT_DIR / "high_confidence_batches_006_008_summary.json",
}
GENERATED_NAMES = {path.name for path in OUTPUTS.values()}

JA_RANGES = (
    ("\u3040", "\u30ff"),
    ("\u3400", "\u9fff"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def contains_ja(value: str) -> bool:
    return any(lo <= ch <= hi for ch in (value or "") for lo, hi in JA_RANGES)


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def norm(value: str) -> str:
    import unicodedata
    value = unicodedata.normalize("NFKC", value or "").strip().lower()
    value = value.replace("・", " ").replace("_", " ")
    value = value.replace("（", "(").replace("）", ")")
    return " ".join(value.split())


def dedup_norm(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = norm(value)
        if key and key not in seen:
            seen.add(key)
            out.append(value.strip())
    return out


def prior_audited_ids() -> set[str]:
    ids: set[str] = set()
    if not AUDIT_DIR.is_dir():
        return ids
    for path in sorted(AUDIT_DIR.glob("*.csv")):
        if path.name in GENERATED_NAMES:
            continue
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            row_id = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if row_id and verdict:
                ids.add(row_id)
    return ids


def run_census() -> Path:
    if TMP.exists():
        shutil.rmtree(TMP)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/issue70/audit_semantic_risk_v3.py"),
            "--out", str(TMP),
            "--sample-per-category", "300",
        ],
        cwd=ROOT,
        check=True,
    )
    return TMP / "audit_ledger_template.csv"


def main() -> int:
    ledger = read_csv(run_census())
    audited = prior_audited_ids()
    remaining = [row for row in ledger if row["row_id"] not in audited]

    restore_rows: list[dict[str, str]] = []
    restore_ids: set[str] = set()
    for row in remaining:
        flags = row.get("risk_flags") or ""
        if "SOURCE_JA_SEARCH_NOT_INDEXED" not in flags:
            continue
        current = split_pipe(row.get("search_ja") or "")
        source = [term for term in split_pipe(row.get("existing_search_ja") or "") if contains_ja(term)]
        proposed = dedup_norm(current + source)
        if not proposed:
            continue
        restore_ids.add(row["row_id"])
        restore_rows.append({
            "row_id": row["row_id"],
            "canonical_tag": row["canonical_tag"],
            "category_name": row["category_name"],
            "post_count": row["post_count"],
            "display_ja": row["display_ja"],
            "search_ja": row.get("search_ja") or "",
            "existing_search_ja": row.get("existing_search_ja") or "",
            "audit_verdict": "FIX_SEARCH",
            "proposed_search_ja": " | ".join(proposed),
            "reason_code": "RESTORE_TRUSTED_JA_SEARCH",
            "confidence": "HIGH",
            "evidence_refs": "existing_search_ja + RuntimeCatalogIndex search contract",
            "audit_note": "表示名は変更せず、保存済みexisting_search_jaの日本語検索語のみ復元。英字公式名は保持。",
            "approval_status": "PROPOSED",
        })

    dedup_rows: list[dict[str, str]] = []
    dedup_ids: set[str] = set()
    for row in remaining:
        if row["row_id"] in restore_ids:
            continue
        flags = row.get("risk_flags") or ""
        if "DUPLICATE_SEARCH_TERM" not in flags:
            continue
        current = split_pipe(row.get("search_ja") or "")
        proposed = dedup_norm(current)
        if not proposed or len(proposed) >= len(current):
            continue
        dedup_ids.add(row["row_id"])
        dedup_rows.append({
            "row_id": row["row_id"],
            "canonical_tag": row["canonical_tag"],
            "category_name": row["category_name"],
            "post_count": row["post_count"],
            "display_ja": row["display_ja"],
            "search_ja": row.get("search_ja") or "",
            "audit_verdict": "FIX_SEARCH",
            "proposed_search_ja": " | ".join(proposed),
            "reason_code": "DEDUP_SEARCH_TERMS",
            "confidence": "HIGH",
            "evidence_refs": "current search_ja + runtime normalizer",
            "audit_note": "NFKC/括弧/underscore正規化後に同一となる検索語だけを重複除去。語彙の意味は変更しない。",
            "approval_status": "PROPOSED",
        })

    artist_rows: list[dict[str, str]] = []
    for row in remaining:
        if row["row_id"] in restore_ids or row["row_id"] in dedup_ids:
            continue
        if row.get("category_name") != "Artist":
            continue
        flags = row.get("risk_flags") or ""
        unsupported = "ARTIST_JA_DISPLAY_UNSUPPORTED_BY_SOURCE" in flags
        artist_rows.append({
            "row_id": row["row_id"],
            "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"],
            "display_ja": row["display_ja"],
            "search_ja": row.get("search_ja") or "",
            "audit_bucket": row.get("audit_bucket") or "",
            "risk_flags": flags,
            "audit_verdict": "NEEDS_EXTERNAL_CHECK" if unsupported else "KEEP",
            "proposed_display_ja": "",
            "proposed_search_ja": "",
            "reason_code": "ARTIST_JA_READING_UNSUPPORTED" if unsupported else "ARTIST_CONSERVATIVE_KEEP",
            "confidence": "MEDIUM" if unsupported else "HIGH",
            "evidence_refs": "canonical_tag + current display + preserved source evidence",
            "audit_note": (
                "Artist名の日本語表記は誤読リスクが高いため自動修正しない。一次寄り根拠で確認する。"
                if unsupported else
                "Artistは読みを推測しない方針。現行の英字/既知表記を維持し、機械候補のカナ化・意味訳は採用しない。"
            ),
            "approval_status": "PROPOSED",
        })

    write_csv(OUTPUTS["restore"], restore_rows, [
        "row_id", "canonical_tag", "category_name", "post_count", "display_ja", "search_ja",
        "existing_search_ja", "audit_verdict", "proposed_search_ja", "reason_code", "confidence",
        "evidence_refs", "audit_note", "approval_status",
    ])
    write_csv(OUTPUTS["dedup"], dedup_rows, [
        "row_id", "canonical_tag", "category_name", "post_count", "display_ja", "search_ja",
        "audit_verdict", "proposed_search_ja", "reason_code", "confidence", "evidence_refs",
        "audit_note", "approval_status",
    ])
    write_csv(OUTPUTS["artist"], artist_rows, [
        "row_id", "canonical_tag", "post_count", "display_ja", "search_ja", "audit_bucket", "risk_flags",
        "audit_verdict", "proposed_display_ja", "proposed_search_ja", "reason_code", "confidence",
        "evidence_refs", "audit_note", "approval_status",
    ])

    summary = {
        "issue": 70,
        "mode": "proposal_only_high_confidence_batches",
        "production_modified": False,
        "prior_audited_ids": len(audited),
        "search_restore_batch006": len(restore_rows),
        "search_dedup_batch007": len(dedup_rows),
        "artist_initial_audit_batch008": len(artist_rows),
        "artist_keep": sum(r["audit_verdict"] == "KEEP" for r in artist_rows),
        "artist_external_check": sum(r["audit_verdict"] == "NEEDS_EXTERNAL_CHECK" for r in artist_rows),
        "unique_new_rows": len(restore_ids | dedup_ids | {r["row_id"] for r in artist_rows}),
    }
    OUTPUTS["summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
