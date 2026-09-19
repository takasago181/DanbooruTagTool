#!/usr/bin/env python3
"""Generate Issue #70 Character audit batches 011-012.

011: preserve Latin fallback when the source note explicitly says the available
Japanese-looking evidence is non-Japanese or machine/identity-mismatched.
012: repair a strong duplicate-variant pattern where the display contains only
a shared costume/form label and drops the character identity. Uses the frozen
family-base display and explicit overrides where a second qualifier is needed.

Proposal-only. Production translation data is never modified.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "docs/issue70/audit"
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-batches011-012"
OUT11 = AUDIT_DIR / "character_unreliable_candidate_fallback_batch011.csv"
OUT12 = AUDIT_DIR / "character_duplicate_variant_identity_batch012.csv"
GENERATED = {OUT11.name, OUT12.name}

BAD_FALLBACK_NOTES = {
    "non-Japanese/simplified-Chinese evidence",
    "machine-like or identity-mismatched wording",
}

# Canonical-specific labels are used only when the current shared display would
# remain ambiguous after prefixing the family identity.
OVERRIDE_DISPLAY = {
    "baobhan_sith_(first_ascension)_(fate)": "バーヴァン・シー（第1再臨・Fate）",
    "carmilla_(swimsuit_rider)_(first_ascension)_(fate)": "カーミラ（水着・第1再臨）",
    "carmilla_(swimsuit_rider)_(third_ascension)_(fate)": "カーミラ（水着・第3再臨）",
    "marie_antoinette_(swimsuit_caster)_(first_ascension)_(fate)": "マリー・アントワネット（水着・第1再臨）",
    "marie_antoinette_(swimsuit_caster)_(second_ascension)_(fate)": "マリー・アントワネット（水着・第2再臨）",
    "illyasviel_von_einzbern_(swimsuit_archer)_(third_ascension)": "イリヤスフィール（水着・第3再臨）",
    "kriemhild_(swimsuit_rider)_(first_ascension)_(fate)": "クリームヒルト（水着・第1再臨）",
    "gareth_(swimsuit_saber)_(first_ascension)_(fate)": "ガレス（水着・第1再臨）",
    "magical_mirai_miku_(2020_summer)": "初音ミク（マジカルミライ2020・夏）",
    "magical_mirai_miku_(2020_winter)": "初音ミク（マジカルミライ2020・冬）",
    "cloud_strife_(blue_dress)": "クラウド・ストライフ（青ドレス）",
    "cloud_strife_(black_dress)": "クラウド・ストライフ（黒ドレス）",
    "raising_heart_(device_mode)_(1st)": "レイジングハート（デバイスモード・1st）",
    "raising_heart_(accel_mode)_(2nd)": "レイジングハート（アクセルモード・2nd）",
    "rimuru_tempest_(slime)": "リムル＝テンペスト（スライム）",
}


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
        if path.name in GENERATED:
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
    if TMP.exists(): shutil.rmtree(TMP)
    subprocess.run([
        sys.executable, str(ROOT / "scripts/issue70/audit_semantic_risk_v3.py"),
        "--out", str(TMP), "--sample-per-category", "300",
    ], cwd=ROOT, check=True)
    return TMP / "audit_ledger_template.csv"


def main() -> int:
    audited = prior_ids()
    ledger = read_csv(run_census())

    b11 = []
    b11_ids = set()
    for row in ledger:
        if row.get("row_id") in audited or row.get("category_name") != "Character": continue
        if row.get("translation_status") != "REVIEW_REQUIRED": continue
        if row.get("translation_note") not in BAD_FALLBACK_NOTES: continue
        display = row.get("display_ja") or ""
        if not display.isascii(): continue
        b11_ids.add(row["row_id"])
        b11.append({
            "row_id": row["row_id"], "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"], "display_ja": display,
            "translation_note": row.get("translation_note") or "",
            "related_copyright_top1": row.get("related_copyright_top1") or "",
            "audit_verdict": "KEEP", "proposed_display_ja": "", "proposed_search_ja": "",
            "reason_code": "KEEP_LATIN_FALLBACK_REJECT_UNRELIABLE_JA_CANDIDATE",
            "confidence": "HIGH", "evidence_refs": "translation_note + frozen source evidence",
            "audit_note": "中国語・機械訳・identity mismatch と判定済みの候補を表示へ昇格せず、現在のLatin/canonical fallbackを維持。",
            "approval_status": "PROPOSED",
        })

    b12 = []
    for row in ledger:
        if row.get("row_id") in audited or row.get("row_id") in b11_ids: continue
        if row.get("category_name") != "Character": continue
        flags = row.get("risk_flags") or ""
        if "DUPLICATE_DISPLAY_WITHIN_CATEGORY" not in flags or "VARIANT_DISPLAY_MISSING_BASE_IDENTITY" not in flags: continue
        base_display = (row.get("family_base_display_ja") or "").strip()
        current = (row.get("display_ja") or "").strip()
        if not base_display or not current: continue
        proposed = OVERRIDE_DISPLAY.get(row["canonical_tag"])
        if not proposed:
            proposed = f"{base_display}（{current}）"
        b12.append({
            "row_id": row["row_id"], "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"], "display_ja": current,
            "family_base_canonical": row.get("family_base_canonical") or "",
            "family_base_display_ja": base_display,
            "audit_verdict": "FIX_DISPLAY", "proposed_display_ja": proposed,
            "proposed_search_ja": "", "reason_code": "RESTORE_CHARACTER_IDENTITY_IN_VARIANT_DISPLAY",
            "confidence": "HIGH", "evidence_refs": "canonical family + current variant label + duplicate-display collision",
            "audit_note": "衣装/フォーム名だけになり他Characterと衝突していた表示へ、family baseのキャラ本人名を復元。",
            "approval_status": "PROPOSED",
        })

    b11.sort(key=lambda r: (-int(r['post_count'] or 0), r['row_id']))
    b12.sort(key=lambda r: (-int(r['post_count'] or 0), r['row_id']))
    write_csv(OUT11, b11, ["row_id","canonical_tag","post_count","display_ja","translation_note","related_copyright_top1","audit_verdict","proposed_display_ja","proposed_search_ja","reason_code","confidence","evidence_refs","audit_note","approval_status"])
    write_csv(OUT12, b12, ["row_id","canonical_tag","post_count","display_ja","family_base_canonical","family_base_display_ja","audit_verdict","proposed_display_ja","proposed_search_ja","reason_code","confidence","evidence_refs","audit_note","approval_status"])
    print({"batch011":len(b11),"batch012":len(b12),"production_modified":False})
    return 0

if __name__ == "__main__": raise SystemExit(main())
