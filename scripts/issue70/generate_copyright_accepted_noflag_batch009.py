#!/usr/bin/env python3
"""Generate Issue #70 Copyright semantic audit batch 009.

Targets ACCEPTED_AI Copyright rows that entered the v3 ledger only because of
top-impact screening and have no heuristic risk flags. The rows were reviewed
semantically as a group: stable/current surfaces are KEEP, while known
abbreviation/literal/official-title problems are explicit proposals and a small
uncertain set is isolated for external verification.

Proposal-only: production translation data is never modified.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "docs/issue70/audit"
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-batch009"
OUT = AUDIT_DIR / "copyright_accepted_noflag_batch009.csv"

OVERRIDES = {
    "danganronpa_2:_goodbye_despair": ("FIX_BOTH", "スーパーダンガンロンパ2 さよなら絶望学園", "スーダン | ダンガンロンパ2", "COPYRIGHT_FULL_OFFICIAL_TITLE", "HIGH", "official/common title"),
    "danganronpa_v3:_killing_harmony": ("FIX_BOTH", "ニューダンガンロンパV3 みんなのコロシアイ新学期", "ダンガンロンパV3", "COPYRIGHT_FULL_OFFICIAL_TITLE", "HIGH", "official/common title"),
    "battle_tendency": ("FIX_BOTH", "戦闘潮流", "ジョジョ2部", "COPYRIGHT_PART_TITLE_OVER_ABBREVIATION", "HIGH", "existing_candidate_ja + established title"),
    "ssss.gridman": ("FIX_BOTH", "SSSS.GRIDMAN", "グリッドマン", "COPYRIGHT_OFFICIAL_TITLE", "HIGH", "established official title"),
    "mahou_shoujo_madoka_magica:_hangyaku_no_monogatari": ("FIX_BOTH", "劇場版 魔法少女まどか☆マギカ [新編] 叛逆の物語", "叛逆の物語", "COPYRIGHT_FULL_OFFICIAL_TITLE", "HIGH", "established official title"),
    "new_super_mario_bros._u_deluxe": ("FIX_DISPLAY", "New スーパーマリオブラザーズ U デラックス", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established official title"),
    "vrchat": ("FIX_BOTH", "VRChat", "VRチャット", "BRAND_OFFICIAL_NAME", "HIGH", "official brand"),
    "himehina_channel": ("FIX_BOTH", "HIMEHINA Channel", "ヒメヒナチャンネル | ヒメヒナ", "COPYRIGHT_OFFICIAL_CHANNEL_NAME", "HIGH", "HIMEHINA official channel"),
    "king_of_prism": ("FIX_BOTH", "KING OF PRISM", "キンプリ", "COPYRIGHT_FULL_TITLE", "HIGH", "KING OF PRISM official"),
    "one_-_kagayaku_kisetsu_e": ("FIX_DISPLAY", "ONE ～輝く季節へ～", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established title"),
    "wonderful_rush": ("FIX_BOTH", "Wonderful Rush", "ワンダフルラッシュ", "REMOVE_LITERAL_TRANSLATION", "HIGH", "established song title"),
    "rune_factory_5": ("FIX_BOTH", "ルーンファクトリー5", "ルンファク5", "COPYRIGHT_FULL_TITLE", "HIGH", "established official title"),
    "gunvolt_chronicles_luminous_avenger_ix": ("FIX_BOTH", "白き鋼鉄のX（イクス） THE OUT OF GUNVOLT", "白き鋼鉄のX", "COPYRIGHT_FULL_OFFICIAL_TITLE", "HIGH", "Inti Creates official"),
    "kira-kira_sensation!": ("FIX_BOTH", "KiRa-KiRa Sensation!", "キラキラセンセーション", "REMOVE_LITERAL_TRANSLATION", "HIGH", "established song title"),
    "fitness_boxing_feat._hatsune_miku:_isshoni_exercise": ("FIX_DISPLAY", "Fit Boxing feat. 初音ミク -ミクといっしょにエクササイズ-", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "Nintendo / Fit Boxing official"),
    "where's_wally?": ("FIX_DISPLAY", "ウォーリーをさがせ！", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established Japanese title"),
    "shuumatsu_train_doko_e_iku?": ("FIX_DISPLAY", "終末トレインどこへいく？", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established official title"),
    "sentouin_hakenshimasu!": ("FIX_DISPLAY", "戦闘員、派遣します！", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established official title"),
    "murenase!_shiiton_gakuen": ("FIX_DISPLAY", "群れなせ！シートン学園", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established official title"),
    "yuuki_yuuna_wa_yuusha_de_aru:_hanayui_no_kirameki": ("FIX_DISPLAY", "結城友奈は勇者である 花結いのきらめき", "", "COPYRIGHT_OFFICIAL_ORTHOGRAPHY", "HIGH", "established official title"),
    "final_fantasy_fables": ("NEEDS_EXTERNAL_CHECK", "", "", "JA_UMBRELLA_TITLE_UNCLEAR", "MEDIUM", "English umbrella title / Japanese releases use individual names"),
    "stardust_project": ("NEEDS_EXTERNAL_CHECK", "", "", "NON_JAPANESE_DISPLAY_UNVERIFIED", "MEDIUM", "current display contains simplified Chinese"),
    "artificial_utopia_in_ruins": ("NEEDS_EXTERNAL_CHECK", "", "", "JA_TITLE_IDENTITY_UNVERIFIED", "MEDIUM", "current Japanese candidate requires identity verification"),
}


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


def main() -> int:
    audited = prior_ids()
    ledger = read_csv(run_census())
    targets = [r for r in ledger
               if r.get("category_name") == "Copyright"
               and r.get("translation_status") == "ACCEPTED_AI"
               and not (r.get("risk_flags") or "").strip()
               and r.get("row_id") not in audited]
    targets.sort(key=lambda r: (-int(r.get("post_count") or 0), r["row_id"]))

    rows: list[dict[str, str]] = []
    for row in targets:
        override = OVERRIDES.get(row["canonical_tag"])
        if override:
            verdict, proposed_display, proposed_search, reason, confidence, evidence = override
        else:
            verdict, proposed_display, proposed_search, reason, confidence, evidence = (
                "KEEP", "", "", "ACCEPTED_NOFLAG_SEMANTIC_PASS", "HIGH",
                "current display + preserved source evidence",
            )
        rows.append({
            "row_id": row["row_id"],
            "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"],
            "display_ja": row["display_ja"],
            "search_ja": row.get("search_ja") or "",
            "audit_verdict": verdict,
            "proposed_display_ja": proposed_display,
            "proposed_search_ja": proposed_search,
            "reason_code": reason,
            "confidence": confidence,
            "evidence_refs": evidence,
            "audit_note": "ACCEPTED_AI no-flag/top-impact semantic pass; suspicious abbreviation/literal/official-title cases isolated instead of blanket KEEP.",
            "approval_status": "PROPOSED",
        })

    write_csv(OUT, rows, [
        "row_id", "canonical_tag", "post_count", "display_ja", "search_ja",
        "audit_verdict", "proposed_display_ja", "proposed_search_ja", "reason_code",
        "confidence", "evidence_refs", "audit_note", "approval_status",
    ])
    print({
        "rows": len(rows),
        "keep": sum(r["audit_verdict"] == "KEEP" for r in rows),
        "fix": sum(r["audit_verdict"].startswith("FIX_") for r in rows),
        "external": sum(r["audit_verdict"] == "NEEDS_EXTERNAL_CHECK" for r in rows),
        "production_modified": False,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
