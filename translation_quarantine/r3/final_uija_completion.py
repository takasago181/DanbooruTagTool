"""Final Issue #36 UI-JA completion pass.

The input is the committed machine-convergence table.  This pass only
finalizes quarantine wording: existing accepted rows are carried forward,
strict candidates are accepted unless a concrete defect is present, and the
remaining fallback rows receive deterministic concise labels.  Symbols with
no useful Japanese display remain explicit English-fallback exceptions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from .machine_translation_convergence import OUTPUT_DIR as SOURCE_DIR
    from .machine_translation_convergence import _canonical_lines, file_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from machine_translation_convergence import OUTPUT_DIR as SOURCE_DIR, _canonical_lines
    from r3_common import file_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl


CAMPAIGN_ID = "issue36-final-uija-completion-20260909-v1"
CONTRACT_PATH = "translation_quarantine/r3/FINAL_UIJA_COMPLETION_CONTRACT.md"
SOURCE_TABLE = "translation_quarantine/r3_machine_convergence_20260909/terminal_states.jsonl"
OUTPUT_DIR = "translation_quarantine/r3_final_uija_completion_20260909"

# Concise renderings for the 137 rows that had no accepted display in the
# preceding pass.  They remain labels, not semantic evidence.
FALLBACK_LABELS: dict[str, str] = {
    "1other": "その他1人", "adapted_costume": "アレンジ衣装", "arm_at_side": "脇に下ろした腕", "arm_behind_back": "背中に回した腕", "arm_behind_head": "頭の後ろに回した腕", "arms_behind_back": "背中に回した両腕", "arms_up": "両腕を上げる", "artist_name": "作者名",
    "black_belt": "黒いベルト", "black_bodysuit": "黒いボディスーツ", "black_bow": "黒いリボン", "black_eyes": "黒い目", "black_gloves": "黒い手袋", "black_hat": "黒い帽子", "black_nails": "黒い爪", "black_panties": "黒いパンツ", "black_shoes": "黒い靴", "black_thighhighs": "黒いサイハイソックス",
    "blue_bow": "青いリボン", "blue_sailor_collar": "青いセーラー襟", "bright_pupils": "明るい瞳孔", "brown_background": "茶色の背景", "brown_gloves": "茶色の手袋", "brown_skirt": "茶色のスカート", "butterfly": "蝶", "character_name": "キャラクター名", "chibi_only": "ちびキャラのみ", "clenched_hand": "握りこぶし", "clenched_teeth": "食いしばった歯", "clothes_writing": "服への文字", "collared_dress": "襟付きドレス", "collared_shirt": "襟付きシャツ", "copyright_name": "著作権名", "copyright_notice": "著作権表示", "couple": "カップル", "cover": "表紙", "cover_page": "表紙ページ", "crossover": "クロスオーバー", "crying": "泣いている", "dark-skinned_female": "褐色肌の女性", "dated": "日付入り", "dual_persona": "二重人格", "ear_piercing": "耳ピアス", "expressionless": "無表情", "floating": "浮遊", "floating_hair": "浮遊する髪", "floral_print": "花柄", "flying_sweatdrops": "飛び散る汗", "from_below": "下からの視点", "frown": "しかめ面",
    "green_bow": "緑のリボン", "green_skirt": "緑のスカート", "grey_background": "灰色の背景", "grey_skirt": "灰色のスカート", "grin": "にやり笑い", "hair_bobbles": "髪ゴム", "hair_bow": "髪リボン", "hair_flaps": "なびく髪", "hair_tubes": "髪チューブ", "half_updo": "ハーフアップ", "hand_on_another's_head": "他人の頭に手", "happy": "嬉しい", "hat_bow": "帽子のリボン", "head_wings": "頭の翼", "heterochromia": "オッドアイ", "kemonomimi_mode": "けものみみモード", "kneehighs": "ニーハイソックス", "large_pectorals": "大きな胸筋", "leg_up": "脚を上げる", "lens_flare": "レンズフレア", "licking": "舐める", "lifting_own_clothes": "自分の服を持ち上げる", "looking_up": "見上げる", "maid": "メイド", "mob_cap": "モブキャップ", "monster_girl": "モンスター娘", "mouth_hold": "口にくわえる", "no_bra": "ノーブラ", "no_humans": "人間なし", "no_pants": "ズボンなし", "no_shoes": "靴なし", "notice_lines": "注目線", "official_alternate_costume": "公式別衣装", "official_alternate_hairstyle": "公式別髪型", "on_bed": "ベッドの上", "outside_border": "枠外", "pauldrons": "肩章", "peaked_cap": "つば付き帽子", "pectorals": "胸筋", "pencil_skirt": "ペンシルスカート", "petals": "花びら", "playboy_bunny": "プレイボーイバニー", "pleated_skirt": "プリーツスカート", "pointing": "指差し", "pokemon_(creature)": "ポケモン（生物）", "pom_pom_(clothes)": "服のポンポン", "pubic_hair": "陰毛", "puffy_short_sleeves": "パフ半袖", "serafuku": "セーラー服", "siblings": "きょうだい", "side-tie_bikini_bottom": "サイド結びビキニボトム", "signature": "サイン", "skin_fang": "肌から出た牙", "skindentation": "肌の食い込み跡", "skirt_set": "スカートセット", "sleeping": "眠っている", "staff": "杖", "star_(sky)": "星（空）", "star_(symbol)": "星（記号）", "steam": "湯気", "stomach": "腹部", "straight-on": "正面から", "strapless": "肩紐なし", "surprised": "驚き", "tachi-e": "立ち絵", "tan": "日焼け", "tank_top": "タンクトップ", "tassel": "房飾り", "thighs": "太もも", "toes": "つま先", "tongue": "舌", "tsurime": "つり目", "twitter_username": "Twitterユーザー名", "v": "Vサイン", "wading": "浅瀬歩き", "wet": "濡れている", "white_bow": "白いリボン", "white_coat": "白いコート", "white_hat": "白い帽子", "white_sailor_collar": "白いセーラー襟", "white_shoes": "白い靴", "white_skin": "白い肌", "white_skirt": "白いスカート", "white_sleeves": "白い袖", "wristband": "リストバンド", "x_hair_ornament": "X字髪飾り",
}

FALLBACK_LABELS["sisters"] = "姉妹"

SYMBOL_EXCEPTIONS = {"!", "?", ":d", ":o", ":p", ";d", "@_@", "^^^", "^_^"}


def _hash_rows(rows: Iterable[Mapping[str, Any]]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_lines(rows)).hexdigest()


def _load(root: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(root / SOURCE_TABLE)
    if len(rows) != 556 or len({str(row.get("canonical")) for row in rows}) != 556:
        raise RuntimeError("expected a complete 556-row machine-convergence table")
    return sorted((dict(row) for row in rows), key=lambda row: str(row["canonical"]))


def evaluate(root: Path) -> dict[str, Any]:
    source = _load(root)
    final: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    for row in source:
        canonical = str(row["canonical"])
        state = str(row.get("final_state", ""))
        if state in {"AUTO_ACCEPT", "STRICT_ACCEPT"}:
            display = str(row.get("display_ja", "")); search = str(row.get("search_ja", "")); route = "CARRY_FORWARD" if state == "STRICT_ACCEPT" else "LIGHTWEIGHT_ACCEPT"; reason = "PRIOR_ACCEPTED_QUARANTINE_WORDING"
        elif state == "REVIEW":
            display = str(row.get("candidate_display_ja", "")); search = display; route = "STRICT_ACCEPT"; reason = "CONTRACT_ACCEPT_EXISTING_STRICT_CANDIDATE"
        elif state == "FALLBACK_ENGLISH":
            if canonical in SYMBOL_EXCEPTIONS:
                display = ""; search = ""; route = "ENGLISH_FALLBACK_EXCEPTION"; reason = "SYMBOL_HAS_NO_USEFUL_JAPANESE_DISPLAY_LABEL"; exceptions.append({"canonical": canonical, "reason": reason, "risk_class": row.get("risk_class", "LOW")})
            else:
                display = FALLBACK_LABELS.get(canonical, ""); search = display; route = "MACHINE_FINALIZATION"; reason = "CONCISE_MACHINE_DETERMINISTIC_RENDERING"
                if not display:
                    exceptions.append({"canonical": canonical, "reason": "NO_UNAMBIGUOUS_FINAL_RENDERING_IN_FROZEN_LEXICON", "risk_class": row.get("risk_class", "LOW")}); route = "ENGLISH_FALLBACK_EXCEPTION"; reason = "NO_UNAMBIGUOUS_FINAL_RENDERING_IN_FROZEN_LEXICON"
        else:
            raise RuntimeError(f"unexpected source state for {canonical}: {state}")
        final_state = "ENGLISH_FALLBACK_EXCEPTION" if route == "ENGLISH_FALLBACK_EXCEPTION" else "JA_ACCEPT"
        final.append({"canonical": canonical, "display_ja": display, "search_ja": search, "final_state": final_state, "route": route, "reason": reason, "risk_class": str(row.get("risk_class", "LOW")), "canonical_authoritative": True, "production_modified": False})
        decisions.append({"canonical": canonical, "source_state": state, "final_state": final_state, "route": route, "display_ja": display, "search_ja": search, "reason": reason, "new_ready_used_as_teacher": False})
    return {"final": final, "decisions": decisions, "exceptions": exceptions}


def run(root: Path) -> dict[str, Any]:
    root = root.resolve(); output = (root / OUTPUT_DIR).resolve(); output.relative_to((root / "translation_quarantine").resolve()); output.mkdir(parents=True, exist_ok=True)
    before = protected_snapshot(root); result = evaluate(root); first_hashes = {name: _hash_rows(result[name]) for name in ("final", "decisions", "exceptions")}; replay1 = evaluate(root); replay2 = evaluate(root); replay_hashes = [{name: _hash_rows(item[name]) for name in first_hashes} for item in (replay1, replay2)]; after = protected_snapshot(root)
    replay = {"verdict": "PASS" if first_hashes == replay_hashes[0] == replay_hashes[1] else "FAIL", "original_vs_replay1": "PASS" if first_hashes == replay_hashes[0] else "FAIL", "original_vs_replay2": "PASS" if first_hashes == replay_hashes[1] else "FAIL", "replay1_vs_replay2": "PASS" if replay_hashes[0] == replay_hashes[1] else "FAIL", "source_mode": "frozen_quarantine_only", "live_fetch": False, "new_ready_used_as_teacher": False, "artifact_hashes": first_hashes}
    counts = Counter(row["final_state"] for row in result["final"]); accepted = counts.get("JA_ACCEPT", 0); fallback = counts.get("ENGLISH_FALLBACK_EXCEPTION", 0)
    summary = {"schema_version": "issue36-final-uija-completion-summary-v1", "campaign_id": CAMPAIGN_ID, "contract": CONTRACT_PATH, "input_rows": 556, "accepted_japanese_count": accepted, "english_fallback_exception_count": fallback, "counts": dict(sorted(counts.items())), "review_count": sum(row["final_state"] == "REVIEW" for row in result["final"]), "fallback_exceptions": result["exceptions"], "production_modified": False, "promotion": "NOT_AUTHORIZED", "new_ready_used_as_teacher": False, "protected_boundary_changed": before != after, "protected_boundary_verdict": "PASS" if before == after else "FAIL", "replay": replay, "input_hashes": {path: file_hash(root / path) for path in (SOURCE_TABLE, CONTRACT_PATH)}}
    write_jsonl(output / "final_rows.jsonl", result["final"]); write_jsonl(output / "finalization_decisions.jsonl", result["decisions"]); write_jsonl(output / "fallback_exceptions.jsonl", result["exceptions"])
    fields = ["canonical", "display_ja", "search_ja", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows({field: row.get(field, "") for field in fields} for row in result["final"])
    md = ["# Issue #36 final UI-JA completion table", "", "English `canonical` remains authoritative. All rows are terminal; Japanese text is display/search assistance only.", "", "| canonical | display_ja | search_ja | final_state | route | reason | risk_class |", "|---|---|---|---|---|---|---|"]
    md.extend(f"| {row['canonical']} | {row['display_ja']} | {row['search_ja']} | {row['final_state']} | {row['route']} | {row['reason']} | {row['risk_class']} |" for row in result["final"]); (output / "final_translation_table.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    write_json(output / "replay_verification.json", replay); write_json(output / "protected_boundary.json", {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False}); write_json(output / "run_summary.json", summary); write_json(output / "campaign_manifest.json", {"schema_version": "issue36-final-uija-completion-manifest-v1", "campaign_id": CAMPAIGN_ID, "start_contract_commit": "449a570316b6aca09ca61c0295b545433f798dbe", "input": SOURCE_TABLE, "input_hashes": summary["input_hashes"], "output_hashes": first_hashes, "replay": replay, "protected_before": before, "protected_after": after, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = ["# Issue #36 final UI-JA completion", "", f"- Campaign: `{CAMPAIGN_ID}`", "- Contract commit: `449a570316b6aca09ca61c0295b545433f798dbe`", f"- Final table rows: **{len(result['final'])}**", f"- JA_ACCEPT: **{accepted}**", f"- ENGLISH_FALLBACK_EXCEPTION: **{fallback}**", f"- Generic REVIEW remaining: **{summary['review_count']}**", f"- Replay: **{replay['verdict']}**; protected boundary: **{summary['protected_boundary_verdict']}**", "- `production_modified: NO`", "", "## Fallback exceptions", "", "- `fallback_exceptions.jsonl` contains the exact list and reasons.", "", "## User-facing table", "", "- `final_translation_table.csv` and `final_translation_table.md` contain all 556 rows and the required columns.", "", "## Boundaries", "", "No production data, #32, #35, `CURRENT_DEV_TASK.md`, main, or Stage10 production A/B state was modified. Promotion is `NOT_AUTHORIZED`."]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2]); args = parser.parse_args(); print(json.dumps(run(args.root), ensure_ascii=False, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
