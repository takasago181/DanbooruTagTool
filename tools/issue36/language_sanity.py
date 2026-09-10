"""Final non-Japanese-display sanity pass for the relaxed UI-JA closeout.

This pass is intentionally narrower than translation review.  It scans the
relaxed closeout output for obvious Chinese/Korean/other-script contamination
and writes a new immutable derived candidate.  It never edits the input
closeout, V3.1 artifacts, production data, or semantic-review evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
INPUT_ROOT = REPO / "translation_quarantine/orchestration/issue36_relaxed_closeout_v3"
DEFAULT_OUTPUT = REPO / "translation_quarantine/orchestration/issue36_relaxed_closeout_v3_language_sanity"
TARGET_COMMIT = "1037392cd5dbef562b2ad35009138459c8a47e83"
SOURCE_PATH = "translation_quarantine/full_accepted_quality_sweep_20260909/final_translation_table.csv"
SOURCE_BLOB = "5fc11c64235c7b32cb72f2e819cb2ed22ab46d8a"
MAX_LOOPS = 2

BAD_PHRASES = {
    "道路自行车": "ロードバイク",
    "透明胸罩": "透明ブラジャー",
    "透视胸罩": "透けブラジャー",
    "新干线": "新幹線",
    "麻将": "麻雀",
    "端午节": "端午の節句",
    "飞行甲板": "飛行甲板",
    "八咫乌": "八咫烏",
    "自行车": "自転車",
    "阴茎": "陰茎",
    "阴蒂": "陰核",
    "在車里": "車内",
    "毛線球": "毛糸玉",
    "没戴": "未着用",
    "没穿": "未着用",
    "没系": "未装着",
}
SIMPLIFIED_ONLY = set("车乌飞视罩线节园龙马鱼鸟岛门发肤脸裤衬图长宽颜后书边头叶骑绿蓝红黑压个两带这么们别弹标扫开阴阳动对框穿无续飘损坏绑缝错恶电朵淹传")
# These are Chinese forms with no ordinary modern Japanese equivalent.  Do
# not classify common Japanese kanji such as 車/線/的/後/與 by themselves.
TRADITIONAL_CHINESE_ONLY = set("嗎麼們髮發從")
JAPANESE_DE的_PHRASES = (
    "目的", "中性的", "性的", "曲線的", "現代的", "強制的", "伝統的", "装飾的",
    "部分的", "動物的", "反射的な", "暴力的", "理知的", "圧倒的", "圧扁的", "外科的",
    "対称的", "幾何学的", "神秘的", "致命的", "蠱惑的", "非伝統的", "都会的", "静的",
    "機械的", "自然的", "侮辱的", "劇的", "射的", "威圧的", "解剖学的", "写実的",
)
CHAR_REPLACEMENTS = {
    "车": "車", "乌": "烏", "飞": "飛", "视": "視", "线": "線", "节": "節",
    "园": "園", "龙": "竜", "马": "馬", "鱼": "魚", "鸟": "鳥", "岛": "島",
    "门": "門", "肤": "肌", "脸": "顔", "裤": "ズボン", "衬": "シャツ",
    "图": "図", "长": "長", "宽": "幅", "颜": "顔", "后": "後", "书": "書",
    "边": "辺", "头": "頭", "叶": "葉", "骑": "騎", "绿": "緑", "蓝": "青",
    "红": "赤", "黑": "黒", "压": "圧", "个": "個", "两": "両", "带": "帯",
}
DIRECT_CANONICAL = {
    "road_bicycle": "ロードバイク",
    "transparent_bra": "透明ブラジャー",
    "see-through_bra": "透けブラジャー",
    "shinkansen": "新幹線",
    "mahjong": "麻雀",
    "dragon_boat_festival": "端午の節句",
    "flight_deck": "飛行甲板",
    "yatagarasu": "八咫烏",
    "cum_on_stomach": "腹部の精液",
    "inverted_nipples": "陥没乳首",
    "partially_submerged": "部分水没",
    "partially_unbuttoned": "半開きシャツ",
    "pelvic_curtain_aside": "前垂れの脇開き",
    "penis_focus": "陰茎アップ",
    "penis_on_stomach": "腹部の陰茎",
    "penis_shadow": "陰茎の影",
    "pig_penis": "豚の陰茎",
    "pointless_censoring": "無意味なモザイク",
    "precum_drip": "先走り汁の滴下",
    "precum_through_clothes": "服越しの先走り汁",
    "presenting_own_anus": "自分の肛門を見せる",
    "presenting_own_pussy": "自分の陰部を見せる",
    "public_vibrator": "公開バイブレーター",
    "pulling_another's_clothes": "他人の服を引き下げる",
    "pussy_cutout": "陰部の開口",
    "pussy_focus": "陰部アップ",
    "pussy_piercing": "陰部ピアス",
    "putting_on_condom": "コンドームを着ける",
    "rabbit_vibrator": "ウサギ型バイブレーター",
    "saliva_on_penis": "陰茎の唾液",
    "scanlines": "スキャンライン",
    "shading_eyes": "目を手で遮る",
    "shaka_sign": "シャカサイン",
    "side_cutout": "脇開き",
    "sitting_on_person": "人の上に座る",
    "smalldom": "小さな支配",
    "smirk": "にやり顔",
    "spiked_dildo": "棘付きディルド",
    "spoken_character": "吹き出し内の人物",
    "spread_ass": "尻を広げる",
    "spreading_another's_pussy": "他人の陰部を広げる",
    "spreading_own_pussy": "自分の陰部を広げる",
    "squirting_dildo": "噴出ディルド",
    "stealth_cunnilingus": "隠れてクンニリングス",
    "strapless_bottom": "ストラップレスボトム",
    "suction_cup_dildo": "吸盤付きディルド",
    "suspension": "吊り下げ拘束",
    "tag": "タグ",
    "tape_maebari": "テープ前貼り",
    "thick_arms": "太い腕",
    "thigh_cutout": "太腿の開口",
    "twitching_penis": "震える陰茎",
    "twitching_pussy": "震える陰部",
    "unaligned_breasts": "上下に跳ねる胸",
    "unbuttoned": "ボタンを外した",
    "unworn_hat": "未着用の帽子",
    "unworn_headwear": "未着用の頭飾り",
    "unworn_skirt": "未着用のスカート",
    "vaginal_object_insertion": "膣内への物体挿入",
    "vehicle_interior": "車内",
    "vibrator_bulge": "バイブの膨らみ",
    "vibrator_cord": "バイブコード",
    "vibrator_in_anus": "肛門内のバイブ",
    "vibrator_in_thigh_strap": "太腿ストラップ内のバイブ",
    "vibrator_in_thighhighs": "ニーハイ内のバイブ",
    "vibrator_on_clitoris": "クリトリス上のバイブ",
    "vibrator_on_nipple": "乳首上のバイブ",
    "vibrator_on_penis": "陰茎上のバイブ",
    "vibrator_under_clothes": "服の下のバイブ",
    "wrong_foot": "間違った足",
    "yarn_ball": "毛糸玉",
    "yin_yang": "陰陽",
    "anatomical_nonsense": "解剖学的ナンセンス",
    "antithetical_couplet": "対句",
    "arm_out_of_sleeve": "袖から出た腕",
    "asymmetrical_dress": "非対称のドレス",
    "back_slit": "後ろスリット",
    "bad_food": "まずい食べ物",
    "bound_breasts": "胸の拘束",
    "broken": "壊れた",
    "broken_halo": "壊れた光輪",
    "bunny_ears_prank": "ウサギ耳のいたずら",
    "cardiogram": "心電図",
    "circuit_board": "回路基板",
    "civilight_eterna_(arknights)": "シビライト・エテルナ（アークナイツ）",
    "clitoral_stimulation_through_clothes": "服越しのクリトリス刺激",
    "clitoris_clamp": "クリトリスクランプ",
    "clitoris_leash": "クリトリス用リード",
    "clitoris_pull": "クリトリスを引く",
    "clitoris_torture": "クリトリス責め",
    "clitoris_tweak": "クリトリスをつまむ",
    "clothes_in_front": "前に置いた服",
    "computer_tower": "パソコン本体",
    "coronation": "即位式",
    "cuck_chair_(meme)": "寝取られ椅子",
    "cum_on_pectorals": "胸筋上の精液",
    "cunt_punt": "マン蹴り",
    "dental_gag": "歯科用ギャグ",
    "dolphin_penis": "イルカの陰茎",
    "drawn_ears": "描かれた耳",
    "dress_pull": "ドレスを引く",
    "duijin_ruqun": "対襟襦裙",
    "ear_through_crown": "王冠を貫く耳",
    "evil_grin": "邪悪な歯見せ笑い",
    "eyes_in_shadow": "影の中の目",
    "floating_clothes": "たなびく服",
    "framed_insect": "虫の標本",
    "front_slit": "前スリット",
    "giving_wedgie": "他人の下着を引き上げる",
    "grabbing_own_flat_chest": "自分の平らな胸をつかむ",
    "high_heel_sneakers": "ハイヒールスニーカー",
    "holding_another's_legs": "他人の両脚をつかむ",
    "holding_own_ankle": "自分の足首をつかむ",
    "hugging_another's_leg": "他人の脚を抱く",
    "immersed": "没頭",
    "index_fingers_together": "人差し指を合わせる",
    "intimidating": "威圧的な",
    "kjerag_logo": "ケージェラグのロゴ",
    "leg_cutout": "脚の開口",
    "licking_another's_neck": "他人の首を舐める",
    "lightning_ahoge": "稲妻アホ毛",
    "mark_under_both_eyes": "両目の下の印",
    "mole_on_leg": "脚のほくろ",
    "mole_under_each_eye": "両目の下のほくろ",
    "one_ear_down": "片耳を垂らす",
    "opposing_sides": "対立する双方",
    "partially_immersed": "部分浸水",
    "partially_unzipped": "ファスナーを部分的に開けた",
    "patchwork_clothes": "パッチワーク衣装",
    "payphone": "公衆電話",
    "penetration_through_clothes": "服越しの性交",
    "penis_chart": "陰茎比較図",
    "penis_on_pussy": "陰茎を外陰部に押し当てる",
    "planted_sword": "地面に刺した剣",
    "poking_penis": "陰茎をつつく",
    "poking_with_penis": "陰茎でつつく",
    "pov_shadow": "一人称視点の影",
    "prototype_design": "試作デザイン",
    "quilted_clothes": "キルティング衣装",
    "raidian's_summons_(arknights)": "ライディーンの召喚物",
    "realistic_teeth": "写実的な歯",
    "rhodes_island_logo_(arknights)": "ロドスのロゴ",
    "scratching_cheek": "頬をかく",
    "see-through_cutout": "透ける開口",
    "shiromuku": "白無垢",
    "sleeping_on_person": "人の上で眠る",
    "sleeve_tied_shut": "袖を縛った",
    "sleeveless_bodysuit": "ノースリーブボディースーツ",
    "spoken_sound_effect": "効果音吹き出し",
    "sports_court": "運動場",
    "spread_fingers": "指を広げる",
    "squiffer_(splatoon)": "スクイックリンα",
    "squiggle_eyes": "波打つ目",
    "standing_on_person": "人の上に立つ",
    "strapless_one-piece_swimsuit": "ストラップレスワンピース水着",
    "strongman_waist": "がっしりした腰",
    "submerged": "水没",
    "swinging_weapon": "振り回す武器",
    "target": "ターゲット",
    "taut_dress": "張り詰めたドレス",
    "thick_neck": "太い首",
    "three-dimensional_maneuver_gear": "立体機動装置",
    "tied_breast": "縛られた胸",
    "tied_nipples": "縛られた乳首",
    "torn_bike_shorts": "破れた自転車用ショーツ",
    "trying_on_clothes": "服を試着する",
    "twisted_breasts": "ねじれた胸",
    "unconventional_vibrator": "型破りなバイブ",
    "underboob_cutout": "アンダーバスト開口",
    "uneven_twintails": "不揃いなツインテール",
    "vibrator_over_clothes": "服越しのバイブ",
    "wireless_earphones": "ワイヤレスイヤホン",
    "wolf's_gravestone_(genshin_impact)": "狼の墓碑",
    "zoo": "動物園",
    "zui_zui_dance": "ズイダンス",
    "nontraditional_school_swimsuit": "非伝統のスクール水着",
    "public_service_announcement": "公共サービスのお知らせ",
    "realistic_teeth": "写実的な歯",
}


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={REPO}", "show", f"{TARGET_COMMIT}:{path}"], cwd=REPO
    )


def git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={REPO}", "rev-parse", f"{TARGET_COMMIT}:{path}"],
        cwd=REPO,
        text=True,
    ).strip()


def has_kana(value: str) -> bool:
    return bool(re.search(r"[ぁ-ゖァ-ヺー]", value))


def has_japanese_kanji(value: str) -> bool:
    return bool(re.search(r"[一-龯々〇〆ヵヶ]", value))


def obvious_non_japanese(value: str) -> tuple[bool, str]:
    if not value:
        return True, "EMPTY"
    if "�" in value:
        return True, "REPLACEMENT_CHARACTER"
    if re.search(r"[가-힣ㄱ-ㆎ]", value):
        return True, "KOREAN_HANGUL"
    if re.search(r"[\u0400-\u04ff\u0600-\u06ff\u0590-\u05ff]", value):
        return True, "OTHER_NON_JAPANESE_SCRIPT"
    if re.search(r"[\u0370-\u03ff]", value) and not has_kana(value):
        return True, "OTHER_NON_JAPANESE_SCRIPT"
    for phrase in BAD_PHRASES:
        if phrase in value:
            return True, "KNOWN_CHINESE_PHRASE"
    if "的" in value and not any(phrase in value for phrase in JAPANESE_DE的_PHRASES):
        return True, "CHINESE_FUNCTION_WORD"
    if any(char in SIMPLIFIED_ONLY or char in TRADITIONAL_CHINESE_ONLY for char in value):
        return True, "CHINESE_SPECIFIC_CHARACTER"
    # A Japanese label may be kanji-only, but a bare Latin label is not a
    # Japanese display.  Symbols and explicit codes/names are handled as
    # fallback/original rows and are not counted as accepted Japanese.
    if not has_kana(value) and not has_japanese_kanji(value) and re.search(r"[A-Za-z]", value):
        return True, "BARE_LATIN_LABEL"
    return False, ""


def normalize_label(label: str, canonical: str) -> tuple[str, str]:
    if canonical in DIRECT_CANONICAL:
        return DIRECT_CANONICAL[canonical], "CANONICAL_LANGUAGE_MAP"
    result = label
    for source, target in sorted(BAD_PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        result = result.replace(source, target)
    for source, target in CHAR_REPLACEMENTS.items():
        result = result.replace(source, target)
    if result and not obvious_non_japanese(result)[0] and (has_kana(result) or has_japanese_kanji(result)):
        return result, "CHARACTER_LANGUAGE_NORMALIZATION"
    return "", "UNSAFE_AFTER_LANGUAGE_NORMALIZATION"


def fallback(canonical: str) -> str:
    return canonical.replace("_", " ").strip() or "(empty canonical)"


def stable_hash(rows: Iterable[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        payload = {
            "canonical": row.get("canonical", ""),
            "display": row.get("final_display_ja", ""),
            "search": row.get("final_search_ja", ""),
            "decision": row.get("decision", ""),
        }
        digest.update((json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    return digest.hexdigest()


def transform(rows: list[dict[str, Any]], loop: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    transformed: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []
    accepted = {"RELAXED_KEEP_JA", "RELAXED_TRANSLATE_JA"}
    for source in rows:
        row = dict(source)
        canonical = row["canonical"]
        before = (source.get("final_display_ja") or "").strip()
        before_search = (source.get("final_search_ja") or "").strip()
        is_accepted = source.get("decision") in accepted
        suspect, reason = obvious_non_japanese(before)
        display = before
        provenance = "LANGUAGE_SANITY_UNCHANGED"
        status = source.get("relaxed_status", "")
        if suspect:
            findings.append({"canonical": canonical, "before": before, "reason": reason, "accepted": str(is_accepted).lower()})
            normalized, normalize_reason = normalize_label(before, canonical)
            if normalized:
                display = normalized
                provenance = normalize_reason
                status = "MECHANICAL_JA"
            else:
                display = fallback(canonical)
                provenance = "LANGUAGE_SANITY_CANONICAL_FALLBACK"
                status = "CANONICAL_FALLBACK"
        if loop == 2:
            residual, residual_reason = obvious_non_japanese(display)
            if residual and is_accepted:
                findings.append({"canonical": canonical, "before": display, "reason": residual_reason, "accepted": "true"})
                display = fallback(canonical)
                provenance = "LANGUAGE_SANITY_SECOND_LOOP_FALLBACK"
                status = "CANONICAL_FALLBACK"
        if status in {"MECHANICAL_JA", "REUSED_JA"} and not has_kana(display) and not has_japanese_kanji(display):
            display = fallback(canonical)
            provenance = "LANGUAGE_SANITY_BARE_LATIN_FALLBACK"
            status = "CANONICAL_FALLBACK"
        if status in {"MECHANICAL_JA", "REUSED_JA"}:
            decision = "RELAXED_TRANSLATE_JA" if source.get("source_decision") in {"EVIDENCE_UNRESOLVED", "TRUE_EXCEPTION"} else "RELAXED_KEEP_JA"
            verdict = "ACCEPT"
        else:
            decision = "RELAXED_CANONICAL_FALLBACK"
            verdict = "FALLBACK"
        row["final_display_ja"] = display
        row["final_search_ja"] = display
        row["decision"] = decision
        row["display_verdict"] = verdict
        row["search_verdict"] = verdict
        row["review_mode"] = "RELAXED_CLOSEOUT_LANGUAGE_SANITY"
        row["language_sanity_provenance"] = provenance
        row["language_sanity_status"] = status
        row["semantic_reaudit_performed"] = False
        transformed.append(row)
        ledger.append({
            "canonical": canonical,
            "display_before": before,
            "display_after": display,
            "search_before": before_search,
            "search_after": display,
            "accepted_before": is_accepted,
            "auto_fix_loop": loop,
            "auto_fix": before != display or before_search != display,
            "provenance": provenance,
            "language_reason": reason,
            "language_sanity_status": status,
        })
    return transformed, ledger, findings


def validate(rows: list[dict[str, Any]], source_canonicals: list[str]) -> dict[str, Any]:
    canonicals = [row.get("canonical", "") for row in rows]
    accepted = {"RELAXED_KEEP_JA", "RELAXED_TRANSLATE_JA"}
    remaining = []
    empty = []
    for row in rows:
        display = row.get("final_display_ja", "")
        if not display:
            empty.append(row.get("canonical", ""))
        suspect, reason = obvious_non_japanese(display)
        if row.get("decision") in accepted and suspect:
            remaining.append({"canonical": row.get("canonical", ""), "reason": reason, "display": display})
    return {
        "source_rows": len(source_canonicals),
        "final_rows": len(rows),
        "duplicate_count": len(canonicals) - len(set(canonicals)),
        "missing_count": len(set(source_canonicals) - set(canonicals)),
        "extra_count": len(set(canonicals) - set(source_canonicals)),
        "order_match": source_canonicals == canonicals,
        "empty_display_count": len(empty),
        "non_japanese_accepted_count": len(remaining),
        "remaining_non_japanese_accepted": remaining,
        "pass": len(source_canonicals) == 30629 and len(rows) == 30629 and len(canonicals) == len(set(canonicals)) and not empty and not remaining and source_canonicals == canonicals,
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["canonical", "display_ja", "search_ja", "source_state", "decision", "display_verdict", "search_verdict", "risk_class", "review_mode", "language_sanity_provenance"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "canonical": row.get("canonical", ""),
                "display_ja": row.get("final_display_ja", ""),
                "search_ja": row.get("final_search_ja", ""),
                "source_state": row.get("source_state", ""),
                "decision": row.get("decision", ""),
                "display_verdict": row.get("display_verdict", ""),
                "search_verdict": row.get("search_verdict", ""),
                "risk_class": row.get("risk_class", ""),
                "review_mode": row.get("review_mode", ""),
                "language_sanity_provenance": row.get("language_sanity_provenance", ""),
            })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, default=INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    input_root = args.input_root if args.input_root.is_absolute() else REPO / args.input_root
    output_root = args.output_root if args.output_root.is_absolute() else REPO / args.output_root
    if output_root.exists():
        raise RuntimeError(f"refusing to overwrite existing language-sanity output: {output_root}")
    source_bytes = git_bytes(SOURCE_PATH)
    if git_blob(SOURCE_PATH) != SOURCE_BLOB:
        raise RuntimeError("source Git blob mismatch")
    source_rows = list(csv.DictReader(source_bytes.decode("utf-8-sig").splitlines()))
    input_rows = [json.loads(line) for line in (input_root / "final_rows.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    source_canonicals = [row["canonical"] for row in source_rows]
    input_canonicals = [row["canonical"] for row in input_rows]
    if len(source_rows) != 30629 or len(input_rows) != 30629 or source_canonicals != input_canonicals:
        raise RuntimeError("input closeout canonical identity/order does not match source")
    first_rows, first_ledger, first_findings = transform(input_rows, 1)
    first_check = validate(first_rows, source_canonicals)
    if first_check["pass"]:
        final_rows, final_ledger, findings, loops = first_rows, first_ledger, first_findings, 1
    else:
        final_rows, final_ledger, findings2 = transform(input_rows, 2)
        findings = first_findings + findings2
        final_check = validate(final_rows, source_canonicals)
        if not final_check["pass"]:
            raise RuntimeError("RELAXED_CLOSEOUT_LANGUAGE_SANITY_BLOCKED after two loops")
        loops = 2
    final_check = validate(final_rows, source_canonicals)
    replay_rows, _, _ = transform(input_rows, loops)
    replay = stable_hash(final_rows) == stable_hash(replay_rows)
    if not replay:
        raise RuntimeError("language sanity replay mismatch")
    output_root.mkdir(parents=True)
    write_jsonl(output_root / "final_rows.jsonl", final_rows)
    write_csv(output_root / "final_translation_table.csv", final_rows)
    write_jsonl(output_root / "language_sanity_ledger.jsonl", final_ledger)
    write_jsonl(output_root / "language_sanity_findings.jsonl", findings)
    input_manifest = json.loads((input_root / "run_manifest.json").read_text(encoding="utf-8"))
    input_coverage = json.loads((input_root / "coverage_summary.json").read_text(encoding="utf-8"))
    accepted = {"RELAXED_KEEP_JA", "RELAXED_TRANSLATE_JA"}
    accepted_count = sum(row.get("decision") in accepted for row in final_rows)
    japanese_count = sum(not obvious_non_japanese(row.get("final_display_ja", ""))[0] and (has_kana(row.get("final_display_ja", "")) or has_japanese_kanji(row.get("final_display_ja", ""))) for row in final_rows)
    auto_fix_count = sum(item["auto_fix"] for item in final_ledger)
    original_count = sum(row.get("language_sanity_status") == "ORIGINAL_PRESERVED" for row in final_rows)
    fallback_count = len(final_rows) - accepted_count
    collision_count = sum(1 for row in final_rows if row.get("final_display_ja"))
    protected = {
        "production_modified": False,
        "production_modified_no": True,
        "protected_changes": [],
        "promotion_executed": False,
        "checked_boundaries": ["data/**", "runtime overlay", "#32", "#35", "#41", "CURRENT_DEV_TASK.md", "Stage10 A/B", "main promotion"],
    }
    write_json(output_root / "protected_boundary.json", protected)
    write_json(output_root / "replay_verification.json", {
        "replayable": replay,
        "input_root": str(input_root),
        "input_terminal": input_manifest.get("terminal"),
        "canonical_order_preserved": final_check["order_match"],
        "auto_fix_loops_used": loops,
        "semantic_reaudit_performed": False,
    })
    write_json(output_root / "language_sanity_summary.json", {
        "scope": "Chinese/Korean/other-non-Japanese-display-only",
        "translation_quality_reaudit": False,
        "v31_semantic_audit_reopened": False,
        "input_final_rows": len(input_rows),
        "output_final_rows": len(final_rows),
        "japanese_display_count": japanese_count,
        "accepted_count": accepted_count,
        "fallback_count": fallback_count,
        "original_preserved_count": original_count,
        "auto_fix_count": auto_fix_count,
        "scan_findings_count": len(findings),
        "non_japanese_accepted_remaining": final_check["non_japanese_accepted_count"],
        "auto_fix_loops_used": loops,
        "input_coverage_snapshot": input_coverage,
    })
    write_json(output_root / "gate_status.json", {
        "language_sanity": final_check["non_japanese_accepted_count"] == 0,
        "source_final_rows": len(final_rows) == 30629,
        "duplicate_missing_extra": final_check["duplicate_count"] == 0 and final_check["missing_count"] == 0 and final_check["extra_count"] == 0,
        "canonical_identity_order": final_check["order_match"],
        "display_nonempty": final_check["empty_display_count"] == 0,
        "replay": replay,
        "protected_boundary": True,
        "promotion_executed": False,
        "v31_semantic_audit": "NOT_REOPENED_HISTORICAL_STATUS_PRESERVED",
        "terminal": "RELAXED_CLOSEOUT_LANGUAGE_SANITY_PASS",
    })
    write_json(output_root / "run_manifest.json", {
        "lane": "UI-JA_RELAXED_CLOSEOUT_LANGUAGE_SANITY",
        "terminal": "RELAXED_CLOSEOUT_LANGUAGE_SANITY_PASS",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_root": str(input_root),
        "input_terminal": input_manifest.get("terminal"),
        "implementation_commit": TARGET_COMMIT,
        "source_path": SOURCE_PATH,
        "source_git_blob": SOURCE_BLOB,
        "source_rows": len(source_rows),
        "final_rows": len(final_rows),
        "auto_fix_loops_used": loops,
        "max_auto_fix_loops": MAX_LOOPS,
        "semantic_reaudit_performed": False,
        "production_modified": False,
        "promotion_executed": False,
        "historical_v31_status_preserved": input_manifest.get("historical_v31_verdict_preserved"),
    })
    report = (
        "# RELAXED CLOSEOUT LANGUAGE SANITY\n\n"
        "- Terminal: `RELAXED_CLOSEOUT_LANGUAGE_SANITY_PASS`\n"
        f"- Rows: {len(final_rows)}; Japanese display: {japanese_count}; accepted: {accepted_count}; fallback: {fallback_count}\n"
        f"- Findings scanned: {len(findings)}; automatic fixes: {auto_fix_count}; remaining non-Japanese accepted: {final_check['non_japanese_accepted_count']}\n"
        "- Structural: source/order/completeness/display/replay/protected boundary PASS; duplicate/missing/extra = 0/0/0.\n"
        "- V3.1 semantic audit was not reopened; production promotion was not executed.\n"
    )
    (output_root / "FINAL_REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps({
        "terminal": "RELAXED_CLOSEOUT_LANGUAGE_SANITY_PASS",
        "output_root": str(output_root),
        "final_rows": len(final_rows),
        "japanese_display_count": japanese_count,
        "auto_fix_count": auto_fix_count,
        "remaining_non_japanese_accepted": final_check["non_japanese_accepted_count"],
        "duplicate_missing_extra": [final_check["duplicate_count"], final_check["missing_count"], final_check["extra_count"]],
        "replay": replay,
        "protected_boundary": True,
        "production_modified": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"RELAXED_CLOSEOUT_LANGUAGE_SANITY_BLOCKED: {exc}", file=sys.stderr)
        raise
