"""Issue #36 machine-translation convergence campaign.

This is a quarantine-only, deterministic display/search candidate pass.  The
English canonical remains authoritative: Japanese text is generated from a
small, reviewable lexical table and transparent canonical composition.  No
candidate is used as semantic evidence for another row and no production
overlay is written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from .r3_common import classify_risk, file_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from r3_common import classify_risk, file_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl


CAMPAIGN_ID = "issue36-machine-translation-convergence-20260909-v1"
PRIOR_TERMINAL = "translation_quarantine/r3_autonomous_safe_or_park_20260909/terminal_states.jsonl"
PRIOR_SUMMARY = "translation_quarantine/r3_autonomous_safe_or_park_20260909/run_summary.json"
PRIOR_WORDING = "translation_quarantine/r3_autonomous_safe_or_park_20260909/wording_decisions.jsonl"
PRIOR_SEARCH = "translation_quarantine/r3_autonomous_safe_or_park_20260909/search_decisions.jsonl"
OVERLAY_PATH = "data/runtime/japanese_overlay.json"
LEXICAL_PATH = "data/japanese/japanese_terms.csv"
FROZEN_WIKI = "translation_quarantine/r3_restricted_routes_20260909/wiki_evidence.jsonl"
POLICY_PATH = "translation_quarantine/r3/MACHINE_TRANSLATION_CONVERGENCE_POLICY.md"
OUTPUT_DIR = "translation_quarantine/r3_machine_convergence_20260909"

_JP = re.compile(r"[ぁ-んァ-ヶ一-龯々ー]")
_BAD = re.compile(r"(?:�|を示す語|を表す語|を意味する語|説明|などを含む)")

# These are intentionally plain lexical renderings.  They are not semantic
# authority and are only used when the canonical is structurally transparent.
TOKENS: dict[str, str] = {
    "animal": "動物", "animal_print": "アニマル柄", "animal_ear_fluff": "動物耳の毛", "anime_coloring": "アニメ塗り",
    "apron": "エプロン", "armband": "腕章", "armlet": "腕輪", "armpits": "脇", "ascot": "アスコットタイ",
    "backpack": "リュック", "bag": "バッグ", "ball": "ボール", "bandages": "包帯", "barefoot": "裸足",
    "baseball_cap": "野球帽", "beach": "ビーチ", "bed": "ベッド", "bed_sheet": "シーツ", "bike_shorts": "自転車用ショーツ",
    "bikini": "ビキニ", "bird": "鳥", "black": "黒", "blue": "青", "blonde": "金髪", "blunt_bangs": "ぱっつん前髪",
    "blunt_ends": "切りそろえた毛先", "blurry": "ぼやけた", "blurry_background": "ぼやけた背景", "blush_stickers": "頬染めシール",
    "bob_cut": "ボブカット", "book": "本", "boots": "ブーツ", "border": "縁取り", "bottle": "ボトル", "bowtie": "蝶ネクタイ",
    "box": "箱", "bracelet": "ブレスレット", "braid": "三つ編み", "breath": "息", "brooch": "ブローチ", "brown": "茶色",
    "bug": "虫", "building": "建物", "buttons": "ボタン", "cake": "ケーキ", "cape": "マント", "cardigan": "カーディガン",
    "casual": "カジュアル", "cat_ears": "猫耳", "cat_girl": "猫娘", "cellphone": "携帯電話", "censored": "修正あり",
    "chain": "鎖", "chair": "椅子", "cherry_blossoms": "桜", "chibi": "ちびキャラ", "child": "子ども", "choker": "チョーカー",
    "cloak": "クローク", "cloud": "雲", "cloudy_sky": "曇り空", "comic": "漫画", "crown": "王冠", "cup": "カップ",
    "curtains": "カーテン", "dark": "暗い", "desk": "机", "dog_ears": "犬耳", "double_bun": "お団子ツインテール",
    "dress": "ドレス", "dress_shirt": "ドレスシャツ", "ear_piercing": "耳ピアス", "embarrassed": "照れ", "eyepatch": "眼帯",
    "facial_hair": "顔の毛", "fang": "牙", "fangs": "牙", "feathers": "羽毛", "fingerless_gloves": "指ぬき手袋",
    "fingernails": "爪", "flat_chest": "平らな胸", "flower": "花", "forehead": "額", "formal_clothes": "正装",
    "freckles": "そばかす", "frills": "フリル", "fruit": "果物", "full_moon": "満月", "fur_trim": "ファートリム",
    "furry": "獣人", "gem": "宝石", "glowing": "発光", "grass": "草", "green": "緑", "grey": "灰色",
    "groin": "股間", "gun": "銃", "hair": "髪", "hair_bobbles": "髪ゴム", "hair_bow": "髪リボン", "hair_flaps": "なびく髪",
    "hair_flower": "髪飾りの花", "hair_over_one_eye": "片目隠れ", "hair_over_shoulder": "肩かけ髪", "hair_ribbon": "髪リボン",
    "hairband": "ヘアバンド", "hairclip": "ヘアピン", "hakama": "袴", "halo": "光輪", "handgun": "拳銃", "headband": "ヘッドバンド",
    "heart": "ハート", "helmet": "ヘルメット", "hood": "フード", "hoodie": "パーカー", "horns": "角", "hug": "抱擁",
    "indoors": "屋内", "jacket": "ジャケット", "japanese_clothes": "和服", "kimono": "着物", "knife": "ナイフ", "lace_trim": "レース飾り",
    "leaf": "葉", "lens_flare": "レンズフレア", "lips": "唇", "lipstick": "口紅", "loafers": "ローファー", "makeup": "化粧",
    "mask": "マスク", "meme": "ミーム", "messy_hair": "乱れ髪", "military": "軍装", "miniskirt": "ミニスカート", "mole": "ほくろ",
    "monochrome": "モノクロ", "moon": "月", "motion_lines": "動線", "motor_vehicle": "自動車", "neck_ribbon": "首リボン",
    "neckerchief": "スカーフ", "no_bra": "ノーブラ", "no_humans": "人間なし", "no_pants": "ズボンなし", "no_shoes": "靴なし",
    "ocean": "海", "outline": "輪郭線", "pants": "ズボン", "pantyhose": "パンスト", "parody": "パロディ", "phone": "電話",
    "pillow": "枕", "pink": "ピンク", "plate": "皿", "pocket": "ポケット", "ponytail": "ポニーテール", "portrait": "肖像",
    "pouch": "ポーチ", "pov": "主観視点", "purple": "紫", "rabbit_ears": "ウサギ耳", "red": "赤", "reflection": "反射",
    "ribbon": "リボン", "rifle": "ライフル", "robe": "ローブ", "rope": "ロープ", "rose": "バラ", "sandals": "サンダル",
    "scar": "傷跡", "scenery": "風景", "school_uniform": "制服", "scrunchie": "シュシュ", "shadow": "影", "sheath": "鞘",
    "shirt": "シャツ", "shorts": "ショートパンツ", "sky": "空", "sleeveless": "ノースリーブ", "smartphone": "スマートフォン",
    "smoke": "煙", "snow": "雪", "suit": "スーツ", "sweater": "セーター", "swimsuit": "水着", "sword": "剣",
    "t-shirt": "Tシャツ", "towel": "タオル", "tree": "木", "turtleneck": "タートルネック", "veil": "ベール", "veins": "血管",
    "vest": "ベスト", "water": "水", "watermark": "透かし", "weapon": "武器", "white": "白", "yellow": "黄色",
}

WHOLE: dict[str, str] = {
    "!": "！", "?": "？", "ahoge": "アホ毛", "alternate_costume": "別衣装", "alternate_hairstyle": "別髪型",
    "androgynous": "中性的", "angel_wings": "天使の翼", "anger_vein": "怒りマーク", "angry": "怒り", "antenna_hair": "アンテナ髪",
    "animal_ear_fluff": "動物耳の毛", "animal_print": "アニマル柄", "anime_coloring": "アニメ塗り", "apron": "エプロン",
    "aqua_eyes": "水色の目", "ascot": "アスコットタイ", "black_background": "黒い背景", "blue_background": "青い背景",
    "blush_stickers": "頬染めシール", "cat_ears": "猫耳", "cat_girl": "猫娘", "cherry_blossoms": "桜", "close-up": "クローズアップ",
    "closed_eyes": "閉じた目", "clothes_pull": "服を引っ張る", "clothing_cutout": "衣服の切り抜き", "cloudy_sky": "曇り空",
    "colored_sclera": "色付き白目", "colored_skin": "色付き肌", "covered_navel": "へそが隠れている", "cowboy_shot": "カウボーイショット",
    "crop_top": "クロップトップ", "cropped_jacket": "クロップドジャケット", "cropped_legs": "脚の途中まで", "cropped_torso": "胴体の途中まで",
    "crossdressing": "女装・男装", "crossed_arms": "腕組み", "crossed_bangs": "交差した前髪", "crossed_legs": "脚組み",
    "demon_girl": "悪魔娘", "demon_horns": "悪魔の角", "demon_wings": "悪魔の翼", "depth_of_field": "被写界深度",
    "dog_ears": "犬耳", "double_bun": "お団子ツインテール", "dragon_girl": "竜娘", "dutch_angle": "ダッチアングル", "eating": "食事",
    "eye_contact": "目が合う", "eyepatch": "眼帯", "eyes_visible_through_hair": "髪越しに見える目", "eyewear_on_head": "頭に乗せた眼鏡",
    "faceless": "顔なし", "feathered_wings": "羽毛の翼", "fox_ears": "狐耳", "fox_girl": "狐娘", "frilled_apron": "フリルエプロン",
    "frilled_bikini": "フリルビキニ", "frilled_dress": "フリルドレス", "frilled_shirt_collar": "フリル襟", "frilled_skirt": "フリルスカート",
    "front-tie_top": "前結びトップス", "full_moon": "満月", "furrowed_brow": "眉間にしわ", "furry_female": "女性獣人", "furry_male": "男性獣人",
    "genderswap": "性別入れ替え", "glowing_eyes": "光る目", "gradient_hair": "グラデーション髪", "green_background": "緑の背景",
    "hair_intakes": "吸い込み髪", "hair_over_one_eye": "片目隠れ", "hair_over_shoulder": "肩かけ髪", "hair_rings": "髪輪",
    "hand_in_pocket": "ポケットに手", "hand_up": "手を上げる", "hands_up": "両手を上げる", "heart-shaped_pupils": "ハート形の瞳孔",
    "high-waist_skirt": "ハイウエストスカート", "high_collar": "ハイカラー", "high_heel_boots": "ハイヒールブーツ", "holding_cup": "カップを持つ",
    "holding_staff": "杖を持つ", "hood_up": "フードをかぶる", "horse_ears": "馬耳", "horse_girl": "馬娘", "index_finger_raised": "人差し指を立てる",
    "interlocked_fingers": "指を組む", "jingle_bell": "鈴", "knee_up": "片膝を上げる", "knees_up": "両膝を上げる", "lace_trim": "レース飾り",
    "light_blush": "薄い赤面", "light_particles": "光の粒", "light_smile": "かすかな笑顔", "long_dress": "ロングドレス", "long_fingernails": "長い爪",
    "low_ponytail": "低いポニーテール", "low_twintails": "低いツインテール", "magical_girl": "魔法少女", "maid_apron": "メイドエプロン",
    "micro_bikini": "マイクロビキニ", "military_uniform": "軍服", "mosaic_censoring": "モザイク修正", "multicolored_eyes": "多色の目",
    "multiple_tails": "複数の尾", "muscular": "筋肉質", "muscular_male": "筋肉質の男性", "musical_note": "音符", "neck_ribbon": "首リボン",
    "nose_blush": "鼻赤面", "one-piece_swimsuit": "ワンピース水着", "one_eye_closed": "片目閉じ", "one_side_up": "片側アップ",
    "open_coat": "開いたコート", "open_shirt": "開いたシャツ", "outstretched_arm": "伸ばした腕", "outstretched_arms": "伸ばした両腕",
    "own_hands_together": "自分の手を合わせる", "pale_skin": "色白の肌", "parted_bangs": "分けた前髪", "parted_lips": "開いた唇",
    "pelvic_curtain": "骨盤カーテン", "pink_eyes": "ピンクの目", "pink_flower": "ピンクの花", "pink_hair": "ピンク髪", "pink_nails": "ピンクの爪",
    "pink_panties": "ピンクのパンツ", "pink_ribbon": "ピンクのリボン", "pink_skirt": "ピンクのスカート", "plaid_clothes": "チェック柄の服",
    "plaid_skirt": "チェック柄のスカート", "pointy_ears": "尖った耳", "polka_dot": "水玉模様", "ponytail": "ポニーテール", "puffy_sleeves": "パフスリーブ",
    "purple_bow": "紫のリボン", "purple_dress": "紫のドレス", "purple_flower": "紫の花", "purple_hair": "紫髪", "purple_shirt": "紫のシャツ", "purple_skirt": "紫のスカート",
    "rabbit_ears": "ウサギ耳", "red_bow": "赤いリボン", "red_bowtie": "赤い蝶ネクタイ", "red_dress": "赤いドレス", "red_flower": "赤い花",
    "red_gloves": "赤い手袋", "red_hair": "赤髪", "red_nails": "赤い爪", "red_neckerchief": "赤いスカーフ", "red_necktie": "赤いネクタイ",
    "red_ribbon": "赤いリボン", "red_shirt": "赤いシャツ", "red_shoes": "赤い靴", "ribbon_trim": "リボン飾り", "scar_on_face": "顔の傷跡",
    "school_uniform": "制服", "shaded_face": "影のある顔", "sharp_teeth": "尖った歯", "shirt_tucked_in": "シャツを入れている", "short_dress": "ショートドレス",
    "short_shorts": "ショートパンツ", "short_sleeves": "半袖", "short_twintails": "短いツインテール", "side_braid": "サイド三つ編み", "sidelocks": "触角", "single_braid": "一本三つ編み",
    "single_earring": "片耳ピアス", "single_glove": "片手手袋", "single_hair_bun": "一本お団子", "sleeves_past_wrists": "手首を越える袖", "sleeveless_dress": "ノースリーブドレス",
    "sleeveless_shirt": "ノースリーブシャツ", "spiked_hair": "ツンツン髪", "spikes": "トゲ", "spoken_heart": "吹き出しハート", "spot_color": "差し色",
    "star_hair_ornament": "星の髪飾り", "starry_sky": "星空", "strapless_dress": "肩紐なしドレス", "strapless_leotard": "肩紐なしレオタード",
    "string_bikini": "紐ビキニ", "striped_clothes": "縞模様の服", "striped_shirt": "ボーダーシャツ", "stuffed_animal": "ぬいぐるみ",
    "stuffed_toy": "ぬいぐるみ", "sunlight": "日光", "swept_bangs": "流し前髪", "symbol-shaped_pupils": "記号形の瞳孔", "tareme": "垂れ目",
    "tearing_up": "涙ぐむ", "tears": "涙", "thick_eyebrows": "太い眉", "thick_thighs": "太い太もも", "thigh_boots": "サイハイブーツ",
    "thigh_strap": "太ももストラップ", "thought_bubble": "思考吹き出し", "torn_clothes": "破れた服", "track_jacket": "トラックジャケット",
    "turtleneck_sweater": "タートルネックセーター", "upper_teeth_only": "上の歯だけ", "v-shaped_eyebrows": "V字眉", "waist_apron": "腰エプロン",
    "wavy_hair": "ウェーブヘア", "wavy_mouth": "波打つ口", "wet_clothes": "濡れた服", "white_pantyhose": "白いパンスト", "white_socks": "白い靴下",
    "white_wings": "白い翼", "wide-eyed": "見開いた目", "wide_hips": "広い腰", "wide_sleeves": "幅広の袖", "wing_collar": "翼襟",
    "witch_hat": "魔女帽子", "wolf_ears": "オオカミ耳", "yellow_bow": "黄色いリボン", "yellow_flower": "黄色い花",
}

COLORS = {"black": "黒い", "blue": "青い", "brown": "茶色の", "green": "緑の", "grey": "灰色の", "pink": "ピンクの", "purple": "紫の", "red": "赤い", "white": "白い", "yellow": "黄色い", "aqua": "水色の"}

# These forms can look lexically simple while changing actors, relations,
# body sites, counts, or action/state.  They require the strict route.
STRICT_CANONICALS = {
    "1other", "3boys", "3girls", "5girls", "6+girls", "child", "couple", "crossdressing", "dated", "dark-skinned_female",
    "dual_persona", "furry", "furry_female", "furry_male", "genderswap", "no_humans", "siblings", "sisters", "twitter_username",
    "v", "wet", "water", "weapon", "animal", "animal_ear_fluff", "artist_name", "character_name", "copyright_name", "copyright_notice",
    "cover", "cover_page", "crossover", "meme", "official_alternate_costume", "official_alternate_hairstyle", "pokemon_(creature)",
    "signature", "tachi-e", "tang", "torn_clothes", "uncensored", "upper_teeth_only",
}


def _canonical_lines(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n" for row in rows)


def _hash_rows(rows: Iterable[Mapping[str, Any]]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_lines(rows)).hexdigest()


def _clean_candidate(value: str) -> bool:
    return bool(value and _JP.search(value) and not _BAD.search(value))


def machine_candidate(canonical: str) -> tuple[str, str, str]:
    """Return (candidate, route, reason) without consulting another row."""

    key = canonical.strip().lower()
    if key in WHOLE:
        return WHOLE[key], "MACHINE_WHOLE_LEXICON", "deterministic whole-canonical lexical rendering"
    if key in TOKENS:
        return TOKENS[key], "MACHINE_LEXICON", "deterministic whole-canonical lexical rendering"
    match = re.fullmatch(r"(\d+)(\+?)(girls?|boys?)", key)
    if match:
        count, plus, group = match.groups()
        noun = "女の子" if group.startswith("girl") else "男の子"
        suffix = "以上" if plus else ""
        return f"{count}人{suffix}の{noun}", "MACHINE_COUNT_COMPOSITION", "transparent count + group composition"
    tokens = [part for part in re.split(r"[_-]+", key) if part]
    if len(tokens) == 2 and tokens[0] in COLORS and tokens[1] in TOKENS:
        return COLORS[tokens[0]] + TOKENS[tokens[1]], "MACHINE_ATTRIBUTE_COMPOSITION", "transparent color + noun composition"
    if len(tokens) == 2 and tokens[0] in {"long", "short", "high", "low", "light", "dark", "large", "small", "thick"} and tokens[1] in TOKENS:
        modifiers = {"long": "長い", "short": "短い", "high": "高い", "low": "低い", "light": "薄い", "dark": "暗い", "large": "大きい", "small": "小さい", "thick": "太い"}
        return modifiers[tokens[0]] + TOKENS[tokens[1]], "MACHINE_ATTRIBUTE_COMPOSITION", "transparent modifier + noun composition"
    if len(tokens) == 1 and tokens[0] in TOKENS:
        return TOKENS[tokens[0]], "MACHINE_LEXICON", "deterministic single-token lexical rendering"
    if tokens and all(token in TOKENS for token in tokens) and len(tokens) <= 2:
        return "・".join(TOKENS[token] for token in tokens), "MACHINE_COMPONENT_COMPOSITION", "deterministic component composition"
    return "", "MACHINE_UNRESOLVED", "no transparent deterministic rendering"


def lightweight_audit(canonical: str, risk: str, candidate: str) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not candidate:
        reasons.append("NO_MACHINE_CANDIDATE")
    elif not _clean_candidate(candidate):
        reasons.append("NONSENSE_OR_UNSAFE_SHAPE")
    if canonical in STRICT_CANONICALS or risk in {"HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"}:
        reasons.append("STRICT_ROUTE_REQUIRED")
    if canonical.startswith(("official_", "copyright_")) or any(piece in canonical for piece in ("_between_", "_with_", "_on_", "_under_")):
        reasons.append("RELATION_OR_PROVENANCE_AMBIGUITY")
    if canonical in {"!", "?", ":d", ":o", ":p", ";d", "@_@", "^^^", "^_^"}:
        reasons.append("SYMBOL_WORDING_REVIEW")
    if reasons:
        return "REJECT", sorted(set(reasons))
    return "ACCEPT", []


def _load_input(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    prior = read_jsonl(root / PRIOR_TERMINAL)
    if len(prior) != 556 or len({str(row.get("canonical")) for row in prior}) != 556:
        raise RuntimeError("expected 556 unique rows from the prior Issue #36 campaign")
    ready = [dict(row) for row in prior if row.get("final_state") == "READY"]
    unresolved = [dict(row) for row in prior if row.get("final_state") == "REVIEW"]
    if len(ready) != 14 or len(unresolved) != 542:
        raise RuntimeError("expected prior result split of 14 READY and 542 REVIEW")
    return sorted(unresolved, key=lambda row: str(row["canonical"])), sorted(ready, key=lambda row: str(row["canonical"]))


def _source_ledger(canonical: str, candidate: str, route: str, audit: str, reasons: list[str]) -> list[dict[str, Any]]:
    return [
        {"campaign_id": CAMPAIGN_ID, "canonical": canonical, "route": "machine_candidate", "status": "GENERATED" if candidate else "EXHAUSTED", "reason": route},
        {"campaign_id": CAMPAIGN_ID, "canonical": canonical, "route": "lightweight_safety_audit", "status": audit, "reason_codes": reasons},
        {"campaign_id": CAMPAIGN_ID, "canonical": canonical, "route": "strict_review", "status": "REQUIRED" if "STRICT_ROUTE_REQUIRED" in reasons else "NOT_REQUIRED", "reason_codes": reasons},
        {"campaign_id": CAMPAIGN_ID, "canonical": canonical, "route": "final_fallback_freeze", "status": "PENDING"},
    ]


def evaluate(root: Path) -> dict[str, Any]:
    unresolved, carried = _load_input(root)
    prior_wording = {str(row.get("canonical")): dict(row) for row in read_jsonl(root / PRIOR_WORDING)}
    prior_search = {str(row.get("canonical")): dict(row) for row in read_jsonl(root / PRIOR_SEARCH)}
    rows: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    strict: list[dict[str, Any]] = []
    wording: list[dict[str, Any]] = []
    search: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for row in unresolved:
        canonical = str(row["canonical"])
        risk = str(row.get("risk_class", classify_risk(canonical)))
        candidate, route, candidate_reason = machine_candidate(canonical)
        audit, reasons = lightweight_audit(canonical, risk, candidate)
        strict_required = "STRICT_ROUTE_REQUIRED" in reasons or "NO_MACHINE_CANDIDATE" in reasons or "NONSENSE_OR_UNSAFE_SHAPE" in reasons
        if audit == "ACCEPT" and not strict_required:
            final_state = "AUTO_ACCEPT"
            display = candidate
            search_value = candidate
            final_reason = "LIGHTWEIGHT_ACCEPT_TRANSPARENT_MACHINE_RENDERING"
        elif strict_required and candidate and "NO_MACHINE_CANDIDATE" not in reasons and "NONSENSE_OR_UNSAFE_SHAPE" not in reasons:
            final_state = "REVIEW"
            display = ""
            search_value = ""
            final_reason = "STRICT_REVIEW_REQUIRED"
        else:
            final_state = "FALLBACK_ENGLISH"
            display = ""
            search_value = ""
            final_reason = "ENGLISH_CANONICAL_FALLBACK_AFTER_ROUTE_EXHAUSTION"
        candidate_record = {"canonical": canonical, "risk_class": risk, "candidate_display_ja": candidate, "candidate_search_ja": candidate, "route": route, "reason": candidate_reason}
        audit_record = {"canonical": canonical, "risk_class": risk, "candidate_display_ja": candidate, "decision": audit, "reason_codes": reasons}
        strict_record = {"canonical": canonical, "risk_class": risk, "required": strict_required, "status": "REVIEW" if strict_required else "NOT_REQUIRED", "reason_codes": reasons}
        candidates.append(candidate_record); audits.append(audit_record); strict.append(strict_record)
        wording.append({"canonical": canonical, "risk_class": risk, "candidate": candidate, "status": "READY" if final_state == "AUTO_ACCEPT" else "REVIEW", "reason": final_reason, "machine_marked": bool(candidate)})
        search.append({"canonical": canonical, "risk_class": risk, "search_candidate": search_value, "status": "READY" if search_value else "PARKED", "reason": "DISPLAY_ACCEPTED" if search_value else final_reason})
        provenance.append({"canonical": canonical, "candidate_source": "fixed lexical table + canonical components", "canonical_authoritative": True, "overlay_used_as_authority": False, "new_ready_used_as_teacher": False})
        route_ledger = _source_ledger(canonical, candidate, route, audit, reasons)
        route_ledger[-1]["status"] = {"AUTO_ACCEPT": "ACCEPTED", "REVIEW": "STRICT_REVIEW", "FALLBACK_ENGLISH": "FALLBACK_ENGLISH"}[final_state]
        route_ledger[-1]["reason"] = final_reason
        ledger.extend(route_ledger)
        rows.append({"canonical": canonical, "display_ja": display, "search_ja": search_value, "candidate_display_ja": candidate, "candidate_search_ja": candidate, "final_state": final_state, "route": "LIGHTWEIGHT" if final_state == "AUTO_ACCEPT" else ("STRICT" if final_state == "REVIEW" else "FALLBACK"), "reason": final_reason, "reason_codes": sorted(set(reasons + ([final_reason] if final_reason else []))), "risk_class": risk, "canonical_authoritative": True, "production_modified": False})
    # Carry-forward is deliberately isolated from candidate generation.
    for row in carried:
        canonical = str(row["canonical"])
        display = str(prior_wording.get(canonical, {}).get("display_candidate", ""))
        search_value = str(prior_search.get(canonical, {}).get("search_candidate", ""))
        rows.append({"canonical": canonical, "display_ja": display, "search_ja": search_value, "candidate_display_ja": display, "candidate_search_ja": search_value, "final_state": "STRICT_ACCEPT", "route": "CARRY_FORWARD", "reason": "PRIOR_CAMPAIGN_READY_CARRY_FORWARD", "reason_codes": ["PRIOR_CAMPAIGN_READY_CARRY_FORWARD"], "risk_class": str(row.get("risk_class", "LOW")), "canonical_authoritative": True, "production_modified": False})
        wording.append({"canonical": canonical, "risk_class": str(row.get("risk_class", "LOW")), "candidate": display, "status": "CARRY_FORWARD", "reason": "PRIOR_CAMPAIGN_READY_CARRY_FORWARD", "machine_marked": False})
        search.append({"canonical": canonical, "risk_class": str(row.get("risk_class", "LOW")), "search_candidate": search_value, "status": "CARRY_FORWARD", "reason": "PRIOR_CAMPAIGN_READY_CARRY_FORWARD"})
        provenance.append({"canonical": canonical, "candidate_source": "prior quarantine result", "canonical_authoritative": True, "overlay_used_as_authority": False, "new_ready_used_as_teacher": False})
        ledger.append({"campaign_id": CAMPAIGN_ID, "canonical": canonical, "route": "carry_forward", "status": "REUSED", "reason": "prior campaign READY; not re-evaluated"})
    rows.sort(key=lambda row: row["canonical"])
    return {"rows": rows, "candidates": sorted(candidates, key=lambda row: row["canonical"]), "audits": sorted(audits, key=lambda row: row["canonical"]), "strict": sorted(strict, key=lambda row: row["canonical"]), "wording": sorted(wording, key=lambda row: row["canonical"]), "search": sorted(search, key=lambda row: row["canonical"]), "provenance": sorted(provenance, key=lambda row: row["canonical"]), "ledger": sorted(ledger, key=lambda row: (row["canonical"], row["route"]))}


def _protected(root: Path) -> dict[str, str]:
    return protected_snapshot(root)


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    output = (root / OUTPUT_DIR).resolve()
    quarantine = (root / "translation_quarantine").resolve()
    output.relative_to(quarantine)
    output.mkdir(parents=True, exist_ok=True)
    before = _protected(root)
    result = evaluate(root)
    first_hashes = {name: "sha256:" + hashlib.sha256(_canonical_lines(result[name])).hexdigest() for name in ("candidates", "audits", "strict", "wording", "search", "provenance", "ledger", "rows")}
    replay1 = evaluate(root); replay2 = evaluate(root)
    replay_hashes = [{name: "sha256:" + hashlib.sha256(_canonical_lines(item[name])).hexdigest() for name in first_hashes} for item in (replay1, replay2)]
    after = _protected(root)
    replay = {"verdict": "PASS" if first_hashes == replay_hashes[0] == replay_hashes[1] else "FAIL", "original_vs_replay1": "PASS" if first_hashes == replay_hashes[0] else "FAIL", "original_vs_replay2": "PASS" if first_hashes == replay_hashes[1] else "FAIL", "replay1_vs_replay2": "PASS" if replay_hashes[0] == replay_hashes[1] else "FAIL", "source_mode": "local_frozen_inputs_only", "live_fetch": False, "new_ready_used_as_teacher": False, "artifact_hashes": first_hashes}
    counts = Counter(row["final_state"] for row in result["rows"])
    auto = [row["canonical"] for row in result["rows"] if row["final_state"] == "AUTO_ACCEPT"]
    review = [row["canonical"] for row in result["rows"] if row["final_state"] == "REVIEW"]
    fallback = [row["canonical"] for row in result["rows"] if row["final_state"] == "FALLBACK_ENGLISH"]
    rejected = [row for row in result["audits"] if row["decision"] == "REJECT"]
    summary = {"schema_version": "issue36-machine-translation-convergence-summary-v1", "campaign_id": CAMPAIGN_ID, "prior_rows": 556, "current_unresolved_input": 542, "processed_rows": 542, "complete_table_rows": len(result["rows"]), "counts": dict(sorted(counts.items())), "auto_filled_lightweight": len(auto), "lightweight_rejected": len(rejected), "strict_review": len(review), "english_fallback": len(fallback), "obvious_mistranslation": sum("NONSENSE_OR_UNSAFE_SHAPE" in row["reason_codes"] and "SYMBOL_WORDING_REVIEW" not in row["reason_codes"] and bool(row.get("candidate_display_ja")) for row in rejected), "ready_carry_forward": counts.get("STRICT_ACCEPT", 0), "production_modified": False, "promotion": "NOT_AUTHORIZED", "new_ready_used_as_teacher": False, "replay": replay, "protected_boundary_changed": before != after, "protected_boundary_verdict": "PASS" if before == after else "FAIL", "review_canonicals": review, "fallback_canonicals": fallback, "input_hashes": {path: file_hash(root / path) for path in (PRIOR_TERMINAL, PRIOR_SUMMARY, PRIOR_WORDING, PRIOR_SEARCH, OVERLAY_PATH, LEXICAL_PATH, FROZEN_WIKI, POLICY_PATH, "translation_quarantine/r3/machine_translation_convergence.py")}}
    write_jsonl(output / "machine_candidates.jsonl", result["candidates"])
    write_jsonl(output / "lightweight_audit.jsonl", result["audits"])
    write_jsonl(output / "strict_review.jsonl", result["strict"])
    write_jsonl(output / "source_exhaustion_ledger.jsonl", result["ledger"])
    write_jsonl(output / "evidence_provenance.jsonl", result["provenance"])
    write_jsonl(output / "wording_decisions.jsonl", result["wording"])
    write_jsonl(output / "search_decisions.jsonl", result["search"])
    write_jsonl(output / "terminal_states.jsonl", result["rows"])
    with (output / "translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["canonical", "display_ja", "search_ja", "candidate_display_ja", "candidate_search_ja", "final_state", "route", "reason", "reason_codes", "risk_class"]
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for row in result["rows"]:
            writer.writerow({field: ("|".join(row["reason_codes"]) if field == "reason_codes" else row.get(field, "")) for field in fields})
    review_fields = ["canonical", "candidate_display_ja", "final_state", "route", "reason", "reason_codes", "risk_class"]
    with (output / "human_review.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=review_fields); writer.writeheader()
        for row in result["rows"]:
            if row["final_state"] in {"REVIEW", "FALLBACK_ENGLISH"}:
                writer.writerow({field: ("|".join(row["reason_codes"]) if field == "reason_codes" else row.get(field, "")) for field in review_fields})
    md = ["# Issue #36 machine-translation convergence table", "", "Canonical English remains authoritative. `candidate_display_ja` is a quarantine suggestion; only AUTO_ACCEPT is eligible for this campaign's lightweight result.", "", "| canonical | display_ja | candidate_display_ja | search_ja | final_state | route | risk | reason |", "|---|---|---|---|---|---|---|---|"]
    md.extend(f"| {r['canonical']} | {r['display_ja']} | {r['candidate_display_ja']} | {r['search_ja']} | {r['final_state']} | {r['route']} | {r['risk_class']} | {r['reason']} |" for r in result["rows"])
    (output / "translation_table.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    write_json(output / "replay_verification.json", replay)
    write_json(output / "protected_boundary.json", {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False})
    write_json(output / "run_summary.json", summary)
    write_json(output / "campaign_manifest.json", {"schema_version": "issue36-machine-translation-convergence-manifest-v1", "campaign_id": CAMPAIGN_ID, "start_point": "8054ea159bd99b3531678048b5453aedd902e4ed", "prior_terminal": PRIOR_TERMINAL, "processed_input": "prior final_state=REVIEW", "processed_rows": 542, "complete_table_rows": len(result["rows"]), "input_hashes": summary["input_hashes"], "output_hashes": first_hashes, "replay": replay, "protected_before": before, "protected_after": after, "production_modified": False, "promotion": "NOT_AUTHORIZED", "new_ready_used_as_teacher": False})
    report = ["# Issue #36 machine-translation convergence", "", f"- Campaign: `{CAMPAIGN_ID}`", f"- Start point: `8054ea159bd99b3531678048b5453aedd902e4ed`", "- Current unresolved input: **542** (prior 14 READY carried forward separately)", f"- Auto-filled by lightweight route: **{summary['auto_filled_lightweight']}**", f"- Lightweight rejected: **{summary['lightweight_rejected']}**", f"- Strict review: **{summary['strict_review']}**", f"- English fallback: **{summary['english_fallback']}**", f"- Obvious mistranslation: **{summary['obvious_mistranslation']}**", f"- Carry-forward strict accepted: **{summary['ready_carry_forward']}**", f"- Replay: **{replay['verdict']}**; protected boundary: **{summary['protected_boundary_verdict']}**", "- `production_modified: NO`", "", "## Decision model", "", "Machine candidate → lightweight safety audit → strict review for flagged/high-risk rows → English canonical fallback for unresolved rows. The canonical English remains visible and authoritative; no candidate is promoted to production.", "", "## Review output", "", "- `translation_table.csv` / `translation_table.md`: all 556 rows including carry-forward.", "- `human_review.csv`: every strict-review and English-fallback row.", "- `machine_candidates.jsonl`, `lightweight_audit.jsonl`, `strict_review.jsonl`: complete machine/audit trace.", "", "## Boundaries", "", "No production data, `data/**`, #32 bridge, #35 UI, `CURRENT_DEV_TASK.md`, `main`, or Stage10 A/B state was modified. Promotion is `NOT_AUTHORIZED`."]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2]); args = parser.parse_args()
    print(json.dumps(run(args.root), ensure_ascii=False, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
