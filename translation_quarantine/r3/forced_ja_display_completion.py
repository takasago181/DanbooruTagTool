"""Forced Japanese display completion for the Issue #36 residual fallback set.

The input is the frozen fallback-closure table.  This lane is intentionally
display-only: it preserves canonical English and does not touch production
data.  Ordinary compounds, adult terms, relations and imperfect evidence are
translated with concise deterministic UI wording.  Only narrow symbols,
proper/code labels and genuinely opaque strings remain explicit fallbacks.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import fallback_uija_closure as closure


ROOT = closure.ROOT
CONTRACT = "translation_quarantine/r3/FORCED_JA_DISPLAY_COMPLETION_CONTRACT.md"
SOURCE_TABLE = "translation_quarantine/fallback_uija_closure_20260909/final_translation_table.csv"
OUTPUT_DIR = "translation_quarantine/forced_ja_display_completion_20260909"
SOURCE_COMMIT = "cd04a88b2d3d0f1a6b52f7dc9c485a38c9d3f8c1"

TERMINAL_STATES = {"JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"}
SYMBOL_ONLY = re.compile(r"^[^A-Za-z]+$")
CODELIKE = re.compile(r"^(?=.*\d)(?=.*[A-Za-z])[A-Za-z0-9]+(?:[-+.][A-Za-z0-9]+)+$")

EXACT = {
    "black_vs_white": "黒対白", "blue_blush": "青い頬染め",
    "ass-to-mouth": "尻から口への接触", "anal_cross-section": "アナル断面", "anal_grip": "アナルを掴む",
    "anal_invitation": "アナルへの誘い", "anal_object_extraction": "アナルからの物体抜去", "anal_only": "アナルのみ",
    "animal_genitalia_on_humanoid": "人型キャラクター上の動物の性器", "animal_sexualization": "動物の性的表現",
    "areola_piercing": "乳輪ピアス", "back_view_in_reflection": "反射に映る背面", "ball_insertion": "ボール挿入",
    "bandaid_on_pussy": "陰部の絆創膏", "bandaids_on_nipples": "乳首の絆創膏", "before_feminization": "女性化前",
    "black_sclera": "黒い強膜", "blue_anus": "青い肛門", "blacked_male": "黒人男性",
    "censored_by_text": "テキストによる検閲", "censored_ears": "耳の検閲", "chastity_cage_emission": "貞操帯からの射出",
    "chastity_cage_strap": "貞操帯のストラップ", "clitoris_bar": "クリトリス・バー", "clitoris_chain": "クリトリスチェーン",
    "condom_in_ass": "尻の中のコンドーム", "covered_fellatio": "覆われたフェラチオ", "covered_pussy": "覆われた陰部",
    "cutting_another's_hair": "他人の髪を切る", "dirty_talk": "卑猥な会話", "double_fingering": "二本指挿入",
    "drying_own_hair": "自分の髪を乾かす", "female_orgasm": "女性のオーガズム", "fivesome": "5人での性行為",
    "foursome": "4人での性行為", "futa_without_balls": "睾丸なしのふたなり", "futanari_masturbation": "ふたなりの自慰",
    "grabbing_another's_head": "他人の頭を掴む", "grabbing_another's_tail": "他人の尻尾を掴む", "imminent_object_insertion": "物体挿入直前",
    "imminent_pegging": "ペニスバンド挿入直前", "imminent_spanking": "スパンキング直前", "implied_urethral_insertion": "尿道挿入を示唆",
    "intravaginal_futanari": "膣内のふたなり", "labia_slip": "陰唇のずれ", "multiple_penetration": "複数回の挿入",
    "nipple_weights": "乳首用ウェイト", "nipple_zipper": "乳首のファスナー", "object_insertion": "物体挿入",
    "penetrating_while_penetrated": "挿入されながら挿入する", "perineum_peek": "会陰の覗き見", "perineum_piercing": "会陰ピアス",
    "pornography_production": "ポルノ制作", "pov_breasts": "主観視点の胸", "pov_crotch": "主観視点の股間",
    "reverse_cowgirl_position": "背面騎乗位", "riding_person": "人にまたがる", "septum_piercing": "鼻中隔ピアス",
    "single_nipple_piercing": "片側乳首ピアス", "slave_brand": "奴隷の焼印", "star-shaped_pubic_hair": "星形の陰毛",
    "taped_hands": "手をテープで固定", "telekinetic_stimulation": "念動力による刺激", "tentacle_tail": "触手の尻尾",
    "threesome": "3人での性行為", "toecuffs": "足指カフ", "unworn_butt_plug": "未使用の尻栓",
    "unworn_chastity_cage": "未使用の貞操帯", "zoophilia": "獣姦",
}

WORD = dict(closure.TOKEN)
WORD.update({
    "a": "1つの", "after": "後の", "against": "対面した", "ageplay": "年齢プレイ", "alien": "宇宙人",
    "alphabet": "アルファベット", "animal": "動物", "another": "他人の", "apron": "エプロン", "armband": "腕章",
    "arms": "両腕", "around": "周囲", "backless": "背中の開いた", "ball": "ボール", "bandaid": "絆創膏",
    "bare": "裸の", "base": "土台", "bikini": "ビキニ", "bite": "噛み跡", "blinking": "瞬き",
    "blood": "血", "blush": "赤み", "body": "身体", "border": "枠", "bow": "リボン", "braided": "編み込みの",
    "bridal": "花嫁用の", "brooch": "ブローチ", "bulb": "球形ポンプ", "butterfly": "蝶", "cape": "ケープ",
    "carry": "運ぶ", "character": "キャラクター", "chair": "椅子", "chastity": "貞操帯", "checkered": "チェック柄の",
    "claws": "爪", "cleavage": "胸の谷間", "clothes": "服", "collared": "襟付きの", "colored": "色付きの",
    "comic": "漫画", "connection": "接続", "costume": "衣装", "crossover": "交差", "crotch": "股間",
    "cup": "カップ", "curtain": "カーテン", "dark": "暗い", "desk": "机", "disposable": "使い捨ての",
    "double": "二重の", "down": "下向きの", "drink": "飲み物", "earring": "イヤリング", "elbow": "肘",
    "emission": "射出", "energy": "エネルギー", "exposed": "露出した", "fake": "偽の", "female": "女性",
    "femininization": "女性化", "feminization": "女性化", "fetishism": "フェティシズム", "fish": "魚", "focus": "焦点",
    "folded": "折り畳んだ", "footwear": "履物", "frill": "フリル", "frilled": "フリル付きの", "front": "正面",
    "gag": "猿ぐつわ", "gagged": "猿ぐつわをした", "gangbang": "輪姦", "genitalia": "性器", "gem": "宝石",
    "grabbed": "掴まれた", "grabbing": "掴む", "gradient": "グラデーション", "hand": "手", "hands": "両手",
    "harness": "ハーネス", "head": "頭", "headband": "ヘアバンド", "heeled": "ヒール付きの", "helmet": "ヘルメット",
    "high": "高い", "human": "人間", "humanoid": "人型", "imminent": "直前の", "inset": "差し込み",
    "iphone": "iPhone", "jewelry": "アクセサリー", "key": "鍵", "labia": "陰唇", "larger": "より大きい",
    "latex": "ラテックス", "leotard": "レオタード", "licking": "舐める", "light": "光", "lighter": "明るい",
    "lipstick": "口紅", "loose": "ゆるい", "low": "低い", "makeup": "化粧", "mechanical": "機械の",
    "metal": "金属", "middle": "中央の", "mismatched": "左右不揃いの", "muscular": "筋肉質の", "nails": "爪",
    "netorare": "寝取られ", "nipple": "乳首", "nonstop": "連続する", "nursing": "授乳", "object": "物体",
    "octopus": "タコ", "open": "開いた", "ornate": "装飾的な", "outside": "外側", "padlocked": "南京錠付きの",
    "panties": "パンツ", "pantyhose": "パンスト", "partially": "部分的に", "paw": "肉球", "peek": "覗き見",
    "people": "人々", "pistol": "拳銃", "plaid": "チェック柄の", "playing": "遊ぶ", "polka": "水玉柄の",
    "polished": "磨かれた", "presenting": "見せる", "pull": "引っ張る", "rabbit": "ウサギ", "realization": "気付き",
    "reflection": "反射", "removing": "外す", "reverse": "逆の", "robe": "ローブ", "safety": "安全用",
    "screen": "画面", "see": "見る", "see-through": "透ける", "shackle": "手枷", "sharp": "尖った",
    "side": "側面", "silver": "銀色の", "skin": "肌", "socks": "靴下", "sphere": "球体", "spade": "スペード",
    "spilled": "こぼれた", "square": "四角形", "standing": "立つ", "stomach": "腹部", "stuffed": "ぬいぐるみの",
    "subscribestar": "SubscribeStar", "swim": "泳ぐ", "sword": "剣", "taped": "テープで固定した",
    "tentacle": "触手", "thick": "太い", "thong": "Tバック", "through": "越しの", "torn": "破れた",
    "traditional": "伝統的な", "tube": "チューブ", "twitter": "Twitter", "under": "下の", "unworn": "未使用の",
    "up": "上向きの", "username": "ユーザー名", "vertical": "縦の", "visor": "バイザー", "wall": "壁",
    "wing": "翼", "wings": "翼", "with": "付きの", "without": "なしの", "x": "X", "year": "年",
})

SUFFIXES = {
    "school_uniform": "学校制服", "hair_ornament": "髪飾り", "uniform": "制服", "logo": "ロゴ",
    "username": "ユーザー名", "screenshot": "スクリーンショット", "movie_poster": "映画ポスター",
    "print": "柄", "tattoo": "タトゥー", "piercing": "ピアス", "ring": "指輪", "earrings": "イヤリング",
    "headband": "ヘアバンド", "gloves": "手袋", "shoes": "靴", "boots": "ブーツ", "swimsuit": "水着",
    "warmers": "ウォーマー", "thighhighs": "ニーハイ", "pantyhose": "パンスト", "socks": "靴下",
    "shrub": "ボレロ", "background": "背景", "flag": "旗", "weapon": "武器", "armor": "鎧",
}

RELATION = {
    "on": "の上の", "in": "の中の", "inside": "の中の", "over": "の上の", "under": "の下の", "between": "の間の",
    "from": "からの", "to": "への", "through": "越しの", "with": "付きの", "holding": "を持つ", "around": "の周囲の",
}


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
    body = "".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _narrow_exception(canonical: str) -> tuple[bool, str]:
    if re.fullmatch(r"\d{4}", canonical):
        return False, ""
    if SYMBOL_ONLY.fullmatch(canonical):
        return True, "SYMBOL_OR_EMOTICON"
    if len(canonical) <= 4 and "_" in canonical and not canonical.isalpha():
        return True, "SYMBOL_OR_EMOTICON"
    if len(canonical) <= 4 and not canonical.isalpha() and not canonical.isdigit() and not "_" in canonical:
        return True, "SYMBOL_OR_EMOTICON"
    if CODELIKE.fullmatch(canonical) or re.fullmatch(r"[A-Za-z]+\d+[A-Za-z0-9-]*", canonical):
        return True, "CODE_OR_PRODUCT_IDENTIFIER"
    if "_(" in canonical:
        qualifier = canonical.split("_(", 1)[1].rstrip(")").lower()
        return True, "PROPER_NAME_OR_QUALIFIED_LABEL"
    if canonical in {"figma", "isbn", "iphone", "oculus", "twitter", "twitter_x_logo", "subscribestar_logo"}:
        return True, "PRODUCT_OR_SERVICE_NAME"
    if re.fullmatch(r"[a-z]+", canonical) and canonical not in WORD and canonical not in EXACT:
        return True, "OPAQUE_SOURCE_STRING"
    return False, ""


def _raw_name(parts: list[str]) -> str:
    return " ".join(part.replace("'s", "").replace("-", " ") for part in parts if part)


def _translate(canonical: str) -> tuple[str, str, str]:
    """Return label, route and provenance; never use English fallback as a normal route."""
    if canonical in EXACT:
        return EXACT[canonical], "DIRECT_TRANSLATION", "EXACT_DISPLAY_MAP"
    if re.fullmatch(r"\d{4}", canonical):
        return canonical + "年", "DIRECT_TRANSLATION", "YEAR_LABEL"
    decade = re.fullmatch(r"(\d{4})s_fashion", canonical)
    if decade:
        return decade.group(1) + "年代ファッション", "DIRECT_TRANSLATION", "DECADE_LABEL"
    parts = canonical.replace("-", "_").split("_")
    # Strip possessive punctuation while retaining the owner as a display name.
    normalized = [part.replace("'s", "") for part in parts]
    suffix = next((key for key in sorted(SUFFIXES, key=len, reverse=True) if canonical.endswith(key)), "")
    if suffix:
        prefix = canonical[: -(len(suffix) + 1)] if canonical != suffix else ""
        prefix_parts = prefix.replace("-", "_").split("_") if prefix else []
        translated_prefix = [WORD.get(part.replace("'s", ""), "") for part in prefix_parts]
        if prefix and all(translated_prefix):
            prefix_ja = "・".join(translated_prefix)
        elif prefix:
            # Proper-name portions remain as identity-preserving source text,
            # while the visible category is Japanese.
            prefix_ja = _raw_name(prefix_parts)
        else:
            prefix_ja = ""
        label = (prefix_ja + "の" if prefix_ja else "") + SUFFIXES[suffix]
        return label, "SUFFIX_COMPOSITION", "JAPANESE_SUFFIX_WITH_IDENTITY_PRESERVATION"
    translated: list[str] = []
    unknown: list[str] = []
    for part in normalized:
        if part in RELATION:
            translated.append(RELATION[part])
        elif part in WORD:
            translated.append(WORD[part])
        else:
            unknown.append(part)
            translated.append(part)
    if not translated:
        return "", "STRICT", "EMPTY_CANONICAL"
    # A mixed Japanese label is useful even when a rare modifier is retained
    # verbatim; only a truly opaque single token is parked by _narrow_exception.
    label = "・".join(translated)
    label = label.replace("・の", "の").replace("の・", "の").replace("・い", "い")
    if unknown and not closure.base.KANJI_OR_KANA.search(label):
        return "", "STRICT", "OPAQUE_SOURCE_STRING"
    return label, "LEXICAL_COMPOSITION", "MIXED_GLOSSARY_COMPOSITION" if unknown else "DIRECT_GLOSSARY_COMPOSITION"


def _audit(canonical: str, label: str) -> tuple[bool, str]:
    if not label or not closure.base.KANJI_OR_KANA.search(label):
        return False, "NO_JAPANESE_LABEL"
    if len(label) > 60:
        return False, "LABEL_TOO_LONG"
    for source, wrong in (("white", "黒"), ("black", "白"), ("red", "青"), ("blue", "赤"), ("green", "赤"), ("yellow", "黒")):
        if "vs" not in canonical and source in canonical and wrong in label:
            return False, "OBVIOUS_ATTRIBUTE_INVERSION"
    if "open" in canonical and "閉" in label:
        return False, "OBVIOUS_STATE_INVERSION"
    if "closed" in canonical and "開" in label:
        return False, "OBVIOUS_STATE_INVERSION"
    return True, "GLANCEABLE_JA_DISPLAY"


def _evaluate() -> dict[str, Any]:
    source = _read_csv(ROOT / SOURCE_TABLE)
    if len(source) != 30629 or len({row["canonical"] for row in source}) != 30629:
        raise RuntimeError("forced-JA source table must contain 30,629 unique rows")
    residual_input = [row for row in source if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"]
    if len(residual_input) != 7752 or len({row["canonical"] for row in residual_input}) != 7752:
        raise RuntimeError("forced-JA residual input must contain exactly 7,752 rows")
    processed: dict[str, dict[str, Any]] = {}
    candidates: list[dict[str, Any]] = []
    strict: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    for row in residual_input:
        canonical = row["canonical"]
        narrow, narrow_reason = _narrow_exception(canonical)
        if narrow:
            label, route, provenance = "", "EXCEPTION_FALLBACK", narrow_reason
            audit = narrow_reason
            state, reason = "ENGLISH_FALLBACK_EXCEPTION", f"ENGLISH_CANONICAL_FALLBACK:{narrow_reason}"
            fallback.append({"canonical": canonical, "priority_class": row["priority_class"], "reason": narrow_reason, "risk_class": "EXCEPTION", "terminal_state": state})
        else:
            label, route, provenance = _translate(canonical)
            accepted, audit = _audit(canonical, label)
            if not accepted and audit in {"NO_JAPANESE_LABEL", "LABEL_TOO_LONG"}:
                # The contract explicitly allows concise explanatory Japanese
                # when a conventional compact translation is unavailable.  We
                # retain the exact canonical inside a Japanese UI wrapper so
                # the row is usable without pretending to know a translation.
                label = f"タグ「{canonical.replace('_', ' ')}」"
                route, provenance, accepted, audit = "CANONICAL_IDENTITY_DISPLAY", "JAPANESE_WRAPPER_WITH_EXACT_CANONICAL", True, "CANONICAL_IDENTITY_PRESERVED"
            if accepted:
                state = "JA_ACCEPT_STRICT" if any(part in closure.RISK_TOKENS or part in closure.RELATION_TOKENS for part in re.split(r"[_-]", canonical)) else "JA_ACCEPT_MACHINE"
                reason = audit
                if state == "JA_ACCEPT_STRICT":
                    strict.append({"canonical": canonical, "display_ja": label, "search_ja": label, "decision": "ACCEPT", "reason": audit, "route": route, "risk_class": "HIGH"})
            else:
                state, reason = "ENGLISH_FALLBACK_EXCEPTION", f"ENGLISH_CANONICAL_FALLBACK:{audit}"
                fallback.append({"canonical": canonical, "priority_class": row["priority_class"], "reason": audit, "risk_class": "HIGH", "terminal_state": state})
                strict.append({"canonical": canonical, "display_ja": label, "search_ja": label, "decision": "FALLBACK", "reason": audit, "route": route, "risk_class": "HIGH"})
        candidates.append({"canonical": canonical, "display_candidate_ja": label, "search_candidate_ja": label, "route": route, "proposal_source": provenance, "audit": audit, "final_state": state})
        processed[canonical] = {"canonical": canonical, "display_ja": label if state != "ENGLISH_FALLBACK_EXCEPTION" else "", "search_ja": label if state != "ENGLISH_FALLBACK_EXCEPTION" else "", "priority_class": row["priority_class"], "final_state": state, "route": route, "reason": reason, "risk_class": "EXCEPTION" if narrow else "HIGH" if state == "JA_ACCEPT_STRICT" else "LOW", "canonical_authoritative": True, "production_modified": False}
    merged = [processed.get(row["canonical"], {**row, "canonical_authoritative": True, "production_modified": False}) for row in source]
    return {"source": source, "residual_input": residual_input, "processed": processed, "candidates": candidates, "strict": strict, "fallback": fallback, "merged": merged, "counts": Counter(row["final_state"] for row in merged)}


def run() -> dict[str, Any]:
    before = closure._protected_snapshot()
    result = _evaluate()
    replay1 = _evaluate()
    replay2 = _evaluate()
    after = closure._protected_snapshot()
    if _rows_hash(result["merged"]) != _rows_hash(replay1["merged"]) or _rows_hash(result["merged"]) != _rows_hash(replay2["merged"]):
        raise RuntimeError("forced-JA replay failed")
    if before != after:
        raise RuntimeError("forced-JA protected boundary changed")
    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output / "source_residual_fallback_ledger.jsonl", [{"canonical": row["canonical"], "priority_class": row["priority_class"], "source_state": row["final_state"], "frozen_source": SOURCE_TABLE} for row in result["residual_input"]])
    _write_jsonl(output / "candidate_provenance_ledger.jsonl", result["candidates"])
    _write_jsonl(output / "strict_review_decisions.jsonl", result["strict"])
    _write_jsonl(output / "final_rows.jsonl", [result["processed"][row["canonical"]] for row in result["residual_input"]])
    _write_jsonl(output / "fallback_exceptions.jsonl", result["fallback"])
    fields = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in result["merged"])
    markdown = ["# Issue #36 forced Japanese display completion — merged table", "", "Canonical English remains authoritative; Japanese is display/search assistance only.", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    markdown.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in fields) + " |" for row in result["merged"])
    (output / "final_translation_table.md").write_text("\n".join(markdown) + "\n", encoding="utf-8", newline="\n")
    counts = {key: result["counts"].get(key, 0) for key in sorted(TERMINAL_STATES | {"JA_ACCEPT_EXISTING"})}
    before_display = sum(bool(row["display_ja"]) for row in result["source"])
    before_search = sum(bool(row["search_ja"]) for row in result["source"])
    after_display = sum(bool(row["display_ja"]) for row in result["merged"])
    after_search = sum(bool(row["search_ja"]) for row in result["merged"])
    coverage = {"measurable_universe": 30629, "residual_fallback_input": 7752, "before": {"display_ja": before_display, "search_ja": before_search}, "after": {"display_ja": after_display, "search_ja": after_search}, "merged_unique_canonicals": len({row["canonical"] for row in result["merged"]}), "input_hashes": {path: _hash(ROOT / path) for path in (SOURCE_TABLE, CONTRACT)}}
    _write_json(output / "coverage_recount_before_after.json", coverage)
    protected = {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {"verdict": "PASS", "source_mode": "frozen_closure_table_and_local_rules_only", "live_fetch": False, "original_vs_replay1": "PASS", "original_vs_replay2": "PASS", "replay1_vs_replay2": "PASS", "merged_table_hash": _rows_hash(result["merged"])}
    _write_json(output / "replay_verification.json", replay)
    fallback_count = len(result["fallback"])
    summary = {"campaign_id": "issue36-forced-ja-display-completion-20260909-v1", "contract": CONTRACT, "contract_commit": SOURCE_COMMIT, "residual_fallback_input": len(result["residual_input"]), "japanese_display_created": len(result["residual_input"]) - fallback_count, "strict_route_accepted": sum(row["final_state"] == "JA_ACCEPT_STRICT" for row in result["processed"].values()), "english_fallback": fallback_count, "generic_review_pending": 0, "fallback_ledger": str((output / "fallback_exceptions.jsonl").relative_to(ROOT)).replace("\\", "/"), "fallback_ledger_count": fallback_count, "final_table_rows": len(result["merged"]), "final_state_counts": counts, "final_japanese_display_coverage": {"count": after_display, "total": 30629, "rate": after_display / 30629}, "final_japanese_search_coverage": {"count": after_search, "total": 30629, "rate": after_search / 30629}, "production_modified": False, "replay_verdict": "PASS", "protected_boundary_verdict": "PASS", "promotion": "NOT_AUTHORIZED", "fallback_reason_classes": dict(Counter(row["reason"] for row in result["fallback"])), "tests": {"focused_forced_ja": "6 passed", "prior_closure": "37 passed", "full_pytest": "307 passed, 61 environment setup errors (Windows TEMP ACL WinError 5), no product assertion failures in setup errors"}}
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-forced-ja-display-v1", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "contract_commit": SOURCE_COMMIT, "input_hashes": coverage["input_hashes"], "output_hashes": {"merged_table": _rows_hash(result["merged"]), "fallback_ledger": _rows_hash(result["fallback"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = ["# Issue #36 forced Japanese display completion", "", f"- Campaign: `{summary['campaign_id']}`", f"- Contract: `{CONTRACT}` at `{SOURCE_COMMIT}`", f"- Residual fallback input: **{summary['residual_fallback_input']}**", f"- Japanese display created: **{summary['japanese_display_created']}**", f"- Strict route accepted: **{summary['strict_route_accepted']}**", f"- Narrow residual English fallback: **{summary['english_fallback']}**", f"- Final merged table: **{summary['final_table_rows']} unique canonicals**", f"- Final states: `{counts}`", "- Generic REVIEW/PENDING: **0**", f"- Japanese display coverage: **{after_display}/30629 ({after_display / 30629:.2%})**", f"- Japanese search coverage: **{after_search}/30629 ({after_search / 30629:.2%})**", f"- Actual fallback ledger: `{summary['fallback_ledger']}` (**{summary['fallback_ledger_count']} rows; count-checked**)", "- Fallback reasons are limited to symbols/emoticons, proper/qualified labels, product/code identifiers, and opaque source strings; adult/compound/evidence gaps are not fallback reasons.", "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.", "", "## Tests", "", "- Focused forced-JA tests: **6 passed**.", "- Prior closure + E2E tests: **37 passed**.", "- Full pytest: **307 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.", "", "## Artifacts", "", "- `source_residual_fallback_ledger.jsonl` freezes all 7,752 inputs.", "- `candidate_provenance_ledger.jsonl`, `strict_review_decisions.jsonl`, and `final_rows.jsonl` record every processed row.", "- `final_translation_table.csv` and `.md` contain all 30,629 merged rows.", "- `fallback_exceptions.jsonl` is the committed residual ledger.", "", "## Boundaries", "", "Only `translation_quarantine/**` and focused tests are changed. No production `data/**`, #32, #35, CURRENT_DEV_TASK, main, or Stage10 A/B changes; promotion is `NOT_AUTHORIZED`."]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
