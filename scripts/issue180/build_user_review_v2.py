#!/usr/bin/env python3
"""Build complete Japanese human review for Issue #180 master v2."""
from __future__ import annotations
import csv
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
MASTER = D / "CHARACTER_HOME_MASTER_V2.csv"
LEDGER = D / "APPLIED_AUTHORITY_LEDGER_V2.csv"
OUT = A / "ISSUE180_ALL_35890_USER_REVIEW_V2.txt"
SUM = A / "issue180_all_35890_user_review_v2_summary.json"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    catalog = read(CAT)
    chars = {r["canonical_tag"]: r for r in catalog if r.get("category_name") == "Character"}
    copyrights = {r["canonical_tag"]: r for r in catalog if r.get("category_name") == "Copyright"}
    master = read(MASTER)
    ledger = {r["canonical_tag"]: r for r in read(LEDGER)}

    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("Issue #180 Character→本家Copyright 全35,890件 フリーズ前確認 v2\n")
        fh.write("research-only / production未変更 / HOMEは最大1件 / 未確定は推測で埋めない\n\n")
        for i, row in enumerate(master, 1):
            tag = row["canonical_tag"]
            cr = chars[tag]
            home = row.get("home_copyright", "")
            authority = ledger.get(tag, {})
            ja = (cr.get("display_ja") or tag).strip()
            home_ja = (copyrights.get(home, {}).get("display_ja") or home or "【未確定】").strip()
            state = row["final_state"]
            if state == "HOME_CONFIRMED":
                reason = f"{row['decision_reason']} / {authority.get('authority_type', '')}"
                evidence = authority.get("evidence_url") or authority.get("source_provenance") or "repository authority"
            elif state == "NOT_OFFICIAL_CHARACTER":
                reason = "【対象外】非公式Characterとしてsecond review済み"
                evidence = "review ledger"
            else:
                reason = f"【未確定】{row['decision_reason']}"
                evidence = "-"
            fh.write(
                f"{i:05d}. {ja}\n"
                f"  Danbooru: {tag}\n"
                f"  本家作品: {home_ja}\n"
                f"  Copyright tag: {home or '【未確定】'}\n"
                f"  判定: {state}\n"
                f"  authority: {authority.get('authority_scope', '-')} / {authority.get('authority_type', '-')}\n"
                f"  理由: {reason}\n"
                f"  証拠: {evidence}\n\n"
            )

    master_summary = json.load((D / "character_home_master_v2_summary.json").open(encoding="utf-8"))
    summary = {
        "character_rows": len(master),
        "states": master_summary["states"],
        "user_review_required_before_freeze": True,
        "accepted_source_modified": False,
        "production_modified": False,
    }
    SUM.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
