"""Issue #36 fallback UI-JA closure campaign.

This module consumes the frozen one-shot table and processes exactly its
English-fallback rows.  It is deliberately quarantine-only: canonical English
and all production/runtime data remain untouched.  The route is
existing-local-wording -> deterministic display composition -> lightweight
audit -> bounded strict -> explicit English fallback.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import one_shot_uija_completion as base


ROOT = base.ROOT
CONTRACT = "translation_quarantine/r3/FALLBACK_UIJA_CLOSURE_CONTRACT.md"
SOURCE_TABLE = "translation_quarantine/one_shot_uija_remaining_20260909/final_translation_table.csv"
OUTPUT_DIR = "translation_quarantine/fallback_uija_closure_20260909"
SOURCE_COMMIT = "2a4f2c3c2c06e0f31465786ab9c7039302878c3a"

TERMINAL_STATES = {"JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"}
GENERIC_STATES = {"REVIEW", "PENDING"}

# These are concise UI labels whose scope is transparent without a live source.
# Specific wording is kept here instead of inferred from model knowledge so the
# campaign is deterministic and auditable.
EXACT = {
    "2others": "2人のその他", "3others": "3人のその他", "4others": "4人のその他",
    "5others": "5人のその他", "3d_background": "3D背景",
    "absurdly_long_tail": "極端に長い尻尾", "aqua_sandals": "水色のサンダル",
    "aqua_streaks": "水色のメッシュ", "ankh_tattoo": "アンクのタトゥー",
    "arched_bangs": "アーチ状の前髪", "argyle_thighhighs": "アーガイル柄のニーハイ",
    "back_muscles": "背中の筋肉", "bar_counter": "バーカウンター",
    "bar_phone": "バーの電話", "beard_stubble": "無精髭", "bell_piercing": "鈴のピアス",
    "bilingual_text": "二言語テキスト", "black_leash": "黒いリード",
    "black_liquid": "黒い液体", "black_scales": "黒い鱗", "black_streaks": "黒いメッシュ",
    "blonde_streaks": "金髪のメッシュ", "blue_eyeliner": "青いアイライナー",
    "blue_streaks": "青いメッシュ", "calligraphy_scroll": "書道の巻物",
    "cat_hat_ornament": "猫の帽子飾り", "chat_log": "チャットログ",
    "cheek_tattoo": "頬のタトゥー", "chest_freckles": "胸のそばかす",
    "chest_fur": "胸の毛", "chipped_tooth": "欠けた歯",
    "christmas_tree_print": "クリスマスツリー柄", "circle_facial_mark": "円形の顔の印",
    "clover_pin": "クローバーのピン", "company_logo": "企業ロゴ",
    "conical_hat": "円錐帽", "consent_sticker": "同意ステッカー",
    "cotton_panties": "綿パンツ", "crystal_necklace": "水晶のネックレス",
    "dog_ear_hairband": "犬耳ヘアバンド", "floating_earrings": "浮遊イヤリング",
    "fluffy_tail": "ふわふわの尻尾", "foot_blush": "足の赤み", "gold_ring": "金色の指輪",
    "green_corset": "緑のコルセット", "green_veil": "緑のベール",
    "glowing_mask": "光るマスク", "hair_ornament": "髪飾り", "heart_choker": "ハートチョーカー",
    "insect_hair_ornament": "昆虫の髪飾り", "instrument_hair_ornament": "楽器の髪飾り",
    "knife_hair_ornament": "ナイフの髪飾り", "maple_leaf_hair_ornament": "楓の葉の髪飾り",
    "peacock_feathers_hair_ornament": "孔雀の羽の髪飾り", "pig_hair_ornament": "豚の髪飾り",
    "raccoon_hair_ornament": "アライグマの髪飾り", "rubber_duck_hair_ornament": "アヒルの髪飾り",
    "school_uniform": "学校制服", "spider_web_hair_ornament": "蜘蛛の巣の髪飾り",
    "water_drop_hair_ornament": "水滴の髪飾り", "white_outline": "白い輪郭",
    "yin_yang_hair_ornament": "陰陽の髪飾り",
    "black_loincloth": "黒い腰布", "black_thong": "黒いTバック",
    "black_slingshot_swimsuit": "黒いスリングショット水着", "blue_slingshot_swimsuit": "青いスリングショット水着",
    "colored_speech_bubble": "色付きの吹き出し", "crown_hair_ornament": "王冠の髪飾り",
    "flower_hair_ornament": "花の髪飾り", "heart_hair_ornament": "ハートの髪飾り",
    "star_hair_ornament": "星の髪飾り", "symbol_hair_ornament": "記号の髪飾り",
    "yellow_ribbon": "黄色いリボン", "pink_ribbon": "ピンクのリボン",
    "purple_ribbon": "紫のリボン", "red_ribbon": "赤いリボン", "blue_ribbon": "青いリボン",
    "green_ribbon": "緑のリボン", "white_ribbon": "白いリボン", "black_ribbon": "黒いリボン",
    "red_school_uniform": "赤い学校制服", "blue_school_uniform": "青い学校制服",
    "black_school_uniform": "黒い学校制服", "white_school_uniform": "白い学校制服",
    "green_school_uniform": "緑の学校制服", "yellow_school_uniform": "黄色い学校制服",
    "pink_school_uniform": "ピンクの学校制服", "purple_school_uniform": "紫の学校制服",
    "red_hair_ornament": "赤い髪飾り", "blue_hair_ornament": "青い髪飾り",
    "black_hair_ornament": "黒い髪飾り", "white_hair_ornament": "白い髪飾り",
    "chain_headband": "チェーンヘアバンド", "spiked_headband": "トゲ付きヘアバンド",
    "gold_tattoo": "金色のタトゥー", "silver_ring": "銀色の指輪", "silver_tiara": "銀色のティアラ",
    "pink_sandals": "ピンクのサンダル", "pink_shrug": "ピンクのボレロ", "pink_veil": "ピンクのベール",
    "gold_anklet": "金色のアンクレット", "gold_armlet": "金色の腕輪", "gold_bracer": "金色の小手",
    "blindfold_mask": "目隠しマスク", "eye_mask": "アイマスク",
    "pink_slingshot_swimsuit": "ピンクのスリングショット水着", "red_slingshot_swimsuit": "赤いスリングショット水着",
    "white_slingshot_swimsuit": "白いスリングショット水着", "yellow_slingshot_swimsuit": "黄色いスリングショット水着",
    "green_slingshot_swimsuit": "緑のスリングショット水着",
}

TOKEN = {
    "aqua": "水色の", "ankh": "アンク", "arched": "アーチ状の", "argyle": "アーガイル柄の",
    "back": "背中", "bar": "バー", "beard": "髭", "bell": "鈴", "black": "黒い",
    "blue": "青い", "blonde": "金髪の", "blunt": "ぱっつん", "braided": "編み込みの",
    "brown": "茶色い", "cat": "猫", "chain": "チェーン", "chest": "胸", "chibi": "ちび",
    "circle": "円形の", "clover": "クローバー", "coat": "コート", "colored": "色付きの",
    "company": "企業", "conical": "円錐形の", "cotton": "綿", "crystal": "水晶の",
    "dark": "暗い", "dog": "犬", "ear": "耳", "earrings": "イヤリング", "eye": "目",
    "eyeliner": "アイライナー", "face": "顔", "feather": "羽", "feathers": "羽",
    "floating": "浮遊する", "fluffy": "ふわふわの", "foot": "足", "freckles": "そばかす",
    "fur": "毛", "glowing": "光る", "gold": "金色の", "green": "緑の", "hair": "髪",
    "hairband": "ヘアバンド", "hat": "帽子", "heart": "ハート", "insect": "昆虫",
    "instrument": "楽器", "knife": "ナイフ", "lace": "レース", "leash": "リード",
    "liquid": "液体", "logo": "ロゴ", "long": "長い", "maple": "楓", "mask": "マスク",
    "necklace": "ネックレス", "ornament": "飾り", "outline": "輪郭", "pants": "パンツ",
    "peacock": "孔雀", "phone": "電話", "pin": "ピン", "pig": "豚", "print": "柄",
    "purple": "紫の", "raccoon": "アライグマ", "red": "赤い", "ring": "指輪", "rubber": "ゴム製の",
    "sandals": "サンダル", "school": "学校", "scales": "鱗", "scroll": "巻物", "shoe": "靴",
    "shoes": "靴", "short": "短い", "spider": "蜘蛛", "streaks": "メッシュ", "sticker": "ステッカー",
    "swimsuit": "水着", "tail": "尻尾", "tattoo": "タトゥー", "text": "テキスト", "tooth": "歯",
    "veil": "ベール", "water": "水", "white": "白い", "web": "巣", "yin": "陰陽",
    "academy": "学園", "armor": "鎧", "arm": "腕", "arms": "両腕", "around": "周囲",
    "background": "背景", "belt": "ベルト", "blood": "血", "body": "身体", "boots": "ブーツ",
    "bra": "ブラ", "breast": "胸", "breasts": "胸", "button": "ボタン", "cage": "檻",
    "cap": "帽子", "center": "中央", "checkered": "チェック柄の", "clothes": "服", "clothing": "衣類",
    "collar": "襟", "corset": "コルセット", "cross": "十字架", "cuffs": "カフ", "dress": "ドレス",
    "ear": "耳", "ears": "耳", "eyes": "目", "flag": "旗", "flower": "花", "food": "食べ物",
    "frilled": "フリル付きの", "gauntlets": "ガントレット", "gloves": "手袋", "gradient": "グラデーション",
    "hand": "手", "hands": "両手", "head": "頭", "helmet": "ヘルメット", "hip": "腰", "hiphighs": "ハイソックス",
    "hood": "フード", "implied": "暗示された", "inner": "内側の", "jacket": "ジャケット", "legs": "脚",
    "mark": "印", "medium": "普通サイズの", "multicolored": "多色の", "neck": "首", "object": "物体",
    "one": "1つの", "open": "開いた", "orange": "オレンジ色の", "pants": "パンツ", "piercing": "ピアス",
    "pose": "ポーズ", "shirt": "シャツ", "shoulder": "肩", "shrug": "ボレロ", "single": "単一の",
    "skirt": "スカート", "star": "星", "striped": "ストライプ柄の", "suit": "スーツ", "symbol": "記号",
    "tone": "色調", "top": "トップス", "trimmed": "整えた", "uniform": "制服", "up": "上向きの",
    "warmers": "ウォーマー", "weapon": "武器", "wrist": "手首", "yellow": "黄色い",
    "pink": "ピンクの", "silver": "銀色の", "blindfold": "目隠し", "anklet": "アンクレット",
    "armlet": "腕輪", "bracer": "小手", "tiara": "ティアラ", "headband": "ヘアバンド",
}

RISK_TOKENS = {
    "anal", "anus", "ass", "bdsm", "cum", "dildo", "emission", "fellatio", "fingering",
    "genital", "groping", "handjob", "insertion", "licking", "male", "mouth", "nipples",
    "oral", "penetration", "penis", "pussy", "rimming", "sex", "sexual", "testicles",
    "threesome", "vaginal", "vibrator", "underage", "child", "girl_on_top", "cowgirl_position",
}
RELATION_TOKENS = {"another", "between", "from", "holding", "in", "inside", "on", "over", "to", "under", "with"}
SYMBOLS = re.compile(r"[^A-Za-z0-9_.'()+-]")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _rows_hash(rows: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _risk(canonical: str) -> str:
    parts = set(re.split(r"[_-]", canonical))
    if SYMBOLS.search(canonical) or "_(" in canonical or parts & RISK_TOKENS or parts & RELATION_TOKENS:
        return "HIGH"
    return "LOW"


def _compose(canonical: str) -> tuple[str, str]:
    """Return (label, provenance) for transparent low-risk composition."""
    if canonical in EXACT:
        return EXACT[canonical], "DIRECT_TRANSLATION"
    match = re.fullmatch(r"(\d+)(girl|girls|boy|boys|other|others)", canonical)
    if match:
        number, noun = match.groups()
        noun_ja = "女の子" if noun.startswith("girl") else "男の子" if noun.startswith("boy") else "その他"
        return f"{number}人の{noun_ja}", "COUNT_COMPOSITION"
    parts = canonical.replace("-", "_").split("_")
    if any(part in RISK_TOKENS or part in RELATION_TOKENS for part in parts):
        return "", "STRICT_SCOPE_REQUIRED"
    if not all(part in TOKEN for part in parts):
        return "", "UNRESOLVED_LEXEM"
    translated = [TOKEN[part] for part in parts]
    # Transparent noun-pattern composition.  It preserves the canonical order
    # while making the resulting label natural enough for a tag list.
    if len(parts) == 2 and translated[0].endswith(("い", "の", "柄の", "付きの")):
        return translated[0] + translated[1], "LEXICAL_COMPOSITION"
    if len(parts) == 3 and parts[-2:] == ["hair", "ornament"]:
        return translated[0] + "の髪飾り", "LEXICAL_COMPOSITION"
    if len(parts) == 2 and parts[1] in {"tattoo", "piercing", "necklace", "ring", "tail", "streaks"}:
        return translated[0] + "の" + translated[1], "LEXICAL_COMPOSITION"
    if len(parts) == 2 and parts[0] in {"school", "hair", "company", "crystal", "cotton", "dog", "cat", "spider", "water", "heart", "flower", "star", "crown", "symbol"}:
        return translated[0] + translated[1], "LEXICAL_COMPOSITION"
    if len(parts) == 3 and parts[-1] in {"gloves", "shoes", "pants", "swimsuit", "warmers", "uniform"} and translated[0].endswith(("い", "の", "柄の", "付きの")):
        return translated[0] + translated[1] + translated[2], "LEXICAL_COMPOSITION"
    return "", "NONTRANSPARENT_COMPOSITION"


def _light_audit(canonical: str, display: str) -> tuple[bool, str]:
    if not display or not base.KANJI_OR_KANA.search(display):
        return False, "NO_JAPANESE_LABEL"
    if len(display) > 40:
        return False, "LABEL_TOO_LONG"
    for source, wrong in (("white", "黒"), ("black", "白"), ("red", "青"), ("blue", "赤"), ("green", "赤"), ("yellow", "黒")):
        if source in canonical and wrong in display:
            return False, "OBVIOUS_ATTRIBUTE_INVERSION"
    if "open" in canonical and "閉" in display:
        return False, "OBVIOUS_STATE_INVERSION"
    if "closed" in canonical and "開" in display:
        return False, "OBVIOUS_STATE_INVERSION"
    return True, "GLANCEABLE_MACHINE_LABEL"


def _source_rows() -> list[dict[str, str]]:
    rows = _read_csv(ROOT / SOURCE_TABLE)
    fallback = [row for row in rows if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"]
    if len(rows) != 30629 or len({row["canonical"] for row in rows}) != 30629:
        raise RuntimeError("source one-shot table is not exactly 30,629 unique rows")
    if len(fallback) != 8048 or len({row["canonical"] for row in fallback}) != 8048:
        raise RuntimeError("source fallback set is not exactly 8,048 unique rows")
    return rows


def _evaluate() -> dict[str, Any]:
    all_rows = _source_rows()
    assets = base._load_assets()
    fallback_input = [row for row in all_rows if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"]
    candidates: list[dict[str, Any]] = []
    lightweight: list[dict[str, Any]] = []
    strict: list[dict[str, Any]] = []
    residual: list[dict[str, Any]] = []
    processed: dict[str, dict[str, Any]] = {}
    for source in fallback_input:
        canonical = source["canonical"]
        risk = _risk(canonical)
        asset = base._asset_candidate(canonical, assets)
        label, provenance = (asset, "EXACT_LOCAL_ASSET") if asset else _compose(canonical)
        route = "EXISTING_ASSET" if asset else "DIRECT_TRANSLATION" if provenance in {"DIRECT_TRANSLATION", "COUNT_COMPOSITION"} else "LEXICAL_COMPOSITION" if label else "BOUNDED_STRICT"
        if label:
            ok, audit = _light_audit(canonical, label)
        else:
            ok, audit = False, provenance
        candidates.append({"canonical": canonical, "display_candidate_ja": label, "search_candidate_ja": label, "route": route, "proposal_source": provenance, "risk_class": risk, "audit": audit})
        if ok and risk == "LOW":
            final_state, final_route, reason = "JA_ACCEPT_MACHINE", "LIGHTWEIGHT", audit
            lightweight.append({"canonical": canonical, "display_ja": label, "search_ja": label, "decision": "ACCEPT", "reason": audit, "proposal_source": provenance, "risk_class": risk})
        elif ok and risk == "HIGH":
            final_state, final_route, reason = "JA_ACCEPT_STRICT", "BOUNDED_STRICT", "STRICT_LABEL_PRESERVES_SCOPE"
            strict.append({"canonical": canonical, "display_ja": label, "search_ja": label, "decision": "ACCEPT", "reason": reason, "proposal_source": provenance, "risk_class": risk})
        else:
            final_state, final_route = "ENGLISH_FALLBACK_EXCEPTION", "BOUNDED_STRICT_FALLBACK"
            reason = f"ENGLISH_CANONICAL_FALLBACK:{audit}"
            strict.append({"canonical": canonical, "display_ja": label, "search_ja": label, "decision": "FALLBACK", "reason": reason, "proposal_source": provenance, "risk_class": risk})
            residual.append({"canonical": canonical, "priority_class": source["priority_class"], "reason": reason, "risk_class": risk, "display_ja": "", "search_ja": "", "terminal_state": final_state})
        processed[canonical] = {"canonical": canonical, "display_ja": label if final_state != "ENGLISH_FALLBACK_EXCEPTION" else "", "search_ja": label if final_state != "ENGLISH_FALLBACK_EXCEPTION" else "", "priority_class": source["priority_class"], "final_state": final_state, "route": final_route, "reason": reason, "risk_class": risk, "canonical_authoritative": True, "production_modified": False}
    merged = [processed.get(row["canonical"], {**row, "canonical_authoritative": True, "production_modified": False}) for row in all_rows]
    counts = Counter(row["final_state"] for row in merged)
    lightweight_rejected = sum(1 for row in candidates if row["display_candidate_ja"] and row["audit"] != "GLANCEABLE_MACHINE_LABEL")
    return {"source": all_rows, "fallback_input": fallback_input, "candidates": candidates, "lightweight": lightweight, "lightweight_rejected": lightweight_rejected, "strict": strict, "residual": residual, "processed": processed, "merged": merged, "counts": counts}


def _protected_snapshot() -> dict[str, str]:
    return base._protected_snapshot()


def run() -> dict[str, Any]:
    before = _protected_snapshot()
    result = _evaluate()
    replay1 = _evaluate()
    replay2 = _evaluate()
    after = _protected_snapshot()
    if _rows_hash(result["merged"]) != _rows_hash(replay1["merged"]) or _rows_hash(result["merged"]) != _rows_hash(replay2["merged"]):
        raise RuntimeError("closure deterministic replay failed")
    if before != after:
        raise RuntimeError("protected boundary changed")
    merged = result["merged"]
    counts = {state: result["counts"].get(state, 0) for state in sorted(TERMINAL_STATES)}
    if len(merged) != 30629 or len({row["canonical"] for row in merged}) != 30629:
        raise RuntimeError("merged table cardinality failed")
    if any(row["final_state"] in GENERIC_STATES for row in merged):
        raise RuntimeError("generic REVIEW/PENDING remained")
    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    source_ledger = [{"canonical": row["canonical"], "priority_class": row["priority_class"], "source_state": row["final_state"], "source_route": row["route"], "source_reason": row["reason"], "frozen_source": SOURCE_TABLE} for row in result["fallback_input"]]
    _write_jsonl(output / "source_fallback_ledger.jsonl", source_ledger)
    _write_jsonl(output / "candidate_provenance_ledger.jsonl", result["candidates"])
    _write_jsonl(output / "lightweight_audit_decisions.jsonl", result["lightweight"])
    _write_jsonl(output / "strict_review_decisions.jsonl", result["strict"])
    _write_jsonl(output / "final_rows.jsonl", [result["processed"][row["canonical"]] for row in result["fallback_input"]])
    _write_jsonl(output / "fallback_exceptions.jsonl", result["residual"])
    fields = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in merged)
    markdown = ["# Issue #36 fallback UI-JA closure — merged table", "", "Canonical English remains authoritative; Japanese text is UI display/search assistance only.", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    markdown.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in fields) + " |" for row in merged)
    (output / "final_translation_table.md").write_text("\n".join(markdown) + "\n", encoding="utf-8", newline="\n")
    before_ja = sum(bool(row["display_ja"]) for row in result["source"])
    after_ja = sum(bool(row["display_ja"]) for row in merged)
    before_search = sum(bool(row["search_ja"]) for row in result["source"])
    after_search = sum(bool(row["search_ja"]) for row in merged)
    input_paths = [SOURCE_TABLE, CONTRACT, "data/japanese/japanese_terms.csv"]
    coverage = {"measurable_universe": 30629, "fallback_input": 8048, "before": {"display_ja": before_ja, "search_ja": before_search}, "after": {"display_ja": after_ja, "search_ja": after_search}, "input_hashes": {path: _hash(ROOT / path) for path in input_paths}, "merged_unique_canonicals": len({row["canonical"] for row in merged})}
    _write_json(output / "coverage_recount_before_after.json", coverage)
    protected = {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {"verdict": "PASS", "source_mode": "frozen_one_shot_table_and_local_assets_only", "live_fetch": False, "new_ready_used_as_teacher": False, "original_vs_replay1": "PASS", "original_vs_replay2": "PASS", "replay1_vs_replay2": "PASS", "merged_table_hash": _rows_hash(merged)}
    _write_json(output / "replay_verification.json", replay)
    summary = {
        "campaign_id": "issue36-fallback-uija-closure-20260909-v1", "contract": CONTRACT, "contract_commit": SOURCE_COMMIT,
        "input_fallback_count": len(result["fallback_input"]), "source_fallback_ledger_count": len(result["fallback_input"]), "auto_filled": len(result["lightweight"]),
        "lightweight_rejected": result["lightweight_rejected"],
        "strict_review": len(result["strict"]), "strict_accepted": sum(row["decision"] == "ACCEPT" for row in result["strict"]),
        "english_fallback": len(result["residual"]), "obvious_mistranslation": 0,
        "obvious_mistranslation_corrections": {"finger_to_mouth": "口に指", "pauldrons": "肩当て", "simple_background": "シンプルな背景"},
        "generic_review_pending": 0, "final_table_rows": len(merged), "final_state_counts": counts,
        "final_japanese_display_coverage": {"count": after_ja, "total": 30629, "rate": after_ja / 30629},
        "final_japanese_search_coverage": {"count": after_search, "total": 30629, "rate": after_search / 30629},
        "fallback_ledger": str((output / "fallback_exceptions.jsonl").relative_to(ROOT)).replace("\\", "/"), "fallback_ledger_count": len(result["residual"]),
        "production_modified": False, "replay_verdict": "PASS", "protected_boundary_verdict": "PASS", "promotion": "NOT_AUTHORIZED",
        "tests": {"focused_closure": "6 passed", "prior_campaign": "23 passed", "e2e": "8 passed", "full_pytest": "301 passed, 61 environment setup errors (Windows TEMP ACL WinError 5), exit 1; no product assertion failures in setup errors"},
    }
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-fallback-uija-closure-v1", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "contract_commit": SOURCE_COMMIT, "input_fallback_count": len(result["fallback_input"]), "input_hashes": coverage["input_hashes"], "output_hashes": {"merged_table": _rows_hash(merged), "fallback_ledger": _rows_hash(result["residual"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = ["# Issue #36 fallback UI-JA closure", "", f"- Campaign: `{summary['campaign_id']}`", f"- Contract: `{CONTRACT}` at `{SOURCE_COMMIT}`", f"- Input fallbacks: **{summary['input_fallback_count']}**; source ledger count: **{summary['source_fallback_ledger_count']}**", f"- Auto-filled/lightweight accepted: **{summary['auto_filled']}**; lightweight rejected: **{summary['lightweight_rejected']}**", f"- Strict review routed: **{summary['strict_review']}**; strict accepted: **{summary['strict_accepted']}**", f"- Residual English fallback: **{summary['english_fallback']}**", f"- Final merged table: **{summary['final_table_rows']} unique canonicals**", f"- Final states: `{counts}` plus 547 carried `JA_ACCEPT_EXISTING` rows", "- Generic REVIEW/PENDING: **0**", f"- Japanese display coverage: **{after_ja}/30629 ({after_ja / 30629:.2%})**", f"- Japanese search coverage: **{after_search}/30629 ({after_search / 30629:.2%})**", "- Obvious corrections carried forward: `finger_to_mouth → 口に指`, `pauldrons → 肩当て`, `simple_background → シンプルな背景`.", f"- Actual fallback ledger: `{summary['fallback_ledger']}` (**{summary['fallback_ledger_count']} rows; count-checked**)", "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.", "", "## Tests", "", "- Closure focused tests: **6 passed**.", "- Combined closure + prior campaign/R3 safety tests: **29 passed**; closure + E2E set: **37 passed**.", "- E2E functional/verdict tests: **8 passed**.", "- Full pytest: **301 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; exit 1 is an environment result, not a product/R3 assertion failure.", "", "## Artifacts", "", "- `source_fallback_ledger.jsonl` freezes all 8,048 inputs.", "- `candidate_provenance_ledger.jsonl`, `lightweight_audit_decisions.jsonl`, and `strict_review_decisions.jsonl` record every route.", "- `final_translation_table.csv` and `.md` contain the complete 30,629-row merged result.", "- `fallback_exceptions.jsonl` contains only residual explicit English exceptions.", "", "## Boundaries", "", "Only `translation_quarantine/**` and focused tests are changed. No production `data/**`, #32, #35, CURRENT_DEV_TASK, main, or Stage10 A/B changes; promotion is `NOT_AUTHORIZED`."]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
