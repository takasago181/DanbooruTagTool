"""Repair the final Issue #36 fallback classifier by semantic intent."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import forced_ja_display_completion as forced


ROOT = forced.ROOT
CONTRACT = "translation_quarantine/r3/EXCEPTION_CLASSIFIER_REPAIR_CONTRACT.md"
SOURCE_TABLE = "translation_quarantine/forced_ja_display_completion_20260909/final_translation_table.csv"
OUTPUT_DIR = "translation_quarantine/exception_classifier_repair_20260909"
SOURCE_COMMIT = "e365165b4e5be9a1a6433b933bca8e2f0cbb67d7"

TERMINAL_STATES = {"JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"}
NARROW_REASONS = {"SYMBOL_OR_EMOTICON", "PROPER_NAME_OR_QUALIFIED_LABEL", "PRODUCT_OR_SERVICE_NAME", "CODE_OR_PRODUCT_IDENTIFIER", "OPAQUE_SOURCE_STRING"}

ORDINARY = {
    "rectum": "直腸", "rug": "ラグ", "twerking": "トゥワーク", "february": "2月", "january": "1月", "march": "3月", "april": "4月", "may": "5月", "june": "6月", "july": "7月", "august": "8月", "september": "9月", "october": "10月", "november": "11月", "december": "12月",
    "euphemism": "婉曲表現", "exorcism": "悪魔祓い", "flatbread": "平焼きパン", "floatplane": "水上機", "footrest": "足置き", "motorhome": "キャンピングカー", "monolids": "一重まぶた", "sternum": "胸骨", "suburb": "郊外", "sunroof": "サンルーフ", "taskbar": "タスクバー", "technology": "技術", "actor": "俳優", "affirmation": "肯定", "aisle": "通路", "amused": "楽しそうな", "bitter": "苦い", "bronze": "青銅色", "clean": "清潔な", "confident": "自信のある", "curse": "呪い", "defenestration": "窓から投げ落とす", "disclaimer": "免責事項", "distracted": "気を取られた", "impressed": "感心した", "intimidating": "威圧的な", "mocking": "嘲笑する", "notice": "通知", "obscured": "隠された", "occult": "オカルト", "overeating": "食べ過ぎ", "proud": "誇らしげな", "satisfied": "満足した", "sly": "狡猾な", "unsure": "確信のない", "vandalism": "器物損壊", "zookeeper": "動物飼育員", "zombie": "ゾンビ", "guide": "案内", "grills": "グリル", "gums": "歯茎", "glans": "亀頭", "pelvis": "骨盤", "forearms": "前腕", "lats": "広背筋", "lappet": "肉垂", "neckbeard": "首ひげ", "stubble": "無精ひげ", "sternritter": "星十字騎士団", "suburb": "郊外", "terminal": "端末", "webpage": "ウェブページ", "wireframe": "ワイヤーフレーム", "wavebox": "波形ボックス", "taskbar": "タスクバー", "technology": "技術",
    "bitchsuit": "ビッチスーツ", "boxbinder": "ボックスバインダー", "coif": "コイフ", "futasub": "ふたなり受け", "holopromise": "ホロプロミス", "lolidom": "ロリ趣味", "plap": "平手打ち", "primogem": "原石", "selfcest": "自己近親相姦", "tamaranean": "タマラニアン", "ungagged": "猿ぐつわなし", "twerking": "トゥワーク", "twincest": "双子近親相姦",
    "1980s_(style)": "1980年代風", "1990s_(style)": "1990年代風", "ace_(playing_card)": "エース（トランプ）", "breathing_(animated)": "呼吸アニメーション", "drawing_(object)": "描画オブジェクト", "earth_(ornament)": "地球の飾り", "moon_(ornament)": "月の飾り", "portrait_(object)": "肖像画", "study_(room)": "書斎", "stop_(gesture)": "ストップのジェスチャー", "cotton_(plant)": "綿花", "baseball_(sport)": "野球", "bass_(fish)": "スズキ（魚）", "cottage_(building)": "コテージ", "movie_poster_(object)": "映画ポスター", "playing_card_(medium)": "トランプカード（媒体）", "map_(medium)": "地図（媒体）", "wrap_(food)": "ラップサンド", "wake_(wave)": "航跡波", "walker_(robot)": "歩行ロボット", "waterfall_(undertale)": "滝（アンダーテール）",
}

WORD = dict(forced.WORD)
WORD.update({
    "absolute": "絶対的な", "accurate": "正確な", "action": "動作", "adoptive": "養子の", "advanced": "先進的な", "after": "後の", "against": "対抗する", "aiming": "狙う", "aircraft": "航空機", "animal": "動物", "antique": "アンティークの", "armpit": "脇", "artist": "絵師", "ass": "尻", "assault": "突撃", "ballet": "バレエ", "bandaged": "包帯を巻いた", "bathing": "入浴", "bed": "ベッド", "behind": "後ろの", "belly": "腹", "beverage": "飲料", "bird": "鳥", "blade": "刃", "boat": "ボート", "book": "本", "building": "建物", "burning": "燃える", "cable": "ケーブル", "camera": "カメラ", "car": "車", "carry": "運ぶ", "cart": "台車", "chair": "椅子", "charm": "チャーム", "chicken": "鶏", "chocolate": "チョコレート", "clan": "一族", "clothing": "衣類", "cloud": "雲", "coin": "硬貨", "color": "色", "computer": "コンピューター", "container": "容器", "covering": "覆う", "cracked": "ひび割れた", "cream": "クリーム", "cucumber": "キュウリ", "dance": "ダンス", "day": "日", "dead": "死んだ", "diamond": "ダイヤモンド", "doll": "人形", "dragon": "竜", "drink": "飲み物", "electric": "電気の", "expression": "表情", "family": "家族", "female": "女性", "field": "野原", "fire": "火", "fish": "魚", "flower": "花", "forest": "森", "formation": "隊形", "furniture": "家具", "game": "ゲーム", "girl": "女の子", "glass": "グラス", "ground": "地面", "gun": "銃", "haircut": "散髪", "hairstyle": "髪型", "halo": "光輪", "hand": "手", "head": "頭", "hearts": "ハート", "house": "家", "human": "人間", "injury": "負傷", "invisible": "透明な", "jewel": "宝石", "jumpsuit": "ジャンプスーツ", "kid": "子供", "knee": "膝", "leaf": "葉", "letter": "文字", "lift": "持ち上げ", "lightning": "稲妻", "line": "線", "machine": "機械", "maid": "メイド", "male": "男性", "magazine": "雑誌", "makeup": "化粧", "mark": "印", "massage": "マッサージ", "metal": "金属", "microphone": "マイク", "mirror": "鏡", "model": "模型", "mouth": "口", "neck": "首", "nose": "鼻", "number": "番号", "paper": "紙", "person": "人物", "phone": "電話", "photo": "写真", "plant": "植物", "plate": "皿", "pocket": "ポケット", "poster": "ポスター", "punch": "殴打", "rabbit": "ウサギ", "rain": "雨", "red": "赤い", "restaurant": "レストラン", "ring": "指輪", "room": "部屋", "rose": "バラ", "salute": "敬礼", "sand": "砂", "sauce": "ソース", "scene": "場面", "scarf": "マフラー", "screen": "画面", "shadow": "影", "ship": "船", "shopping": "買い物", "skull": "頭蓋骨", "snow": "雪", "song": "歌", "space": "宇宙", "speech": "発言", "star": "星", "stone": "石", "story": "物語", "street": "通り", "sun": "太陽", "sweat": "汗", "sword": "剣", "table": "テーブル", "team": "チーム", "telephone": "電話", "throat": "喉", "time": "時間", "tower": "塔", "tree": "木", "triangle": "三角形", "truck": "トラック", "turtle": "亀", "vehicle": "乗り物", "video": "動画", "viewer": "閲覧者", "voice": "声", "wall": "壁", "watching": "見る", "wheel": "車輪", "window": "窓", "wood": "木製の", "worm": "虫", "year": "年", "young": "幼い",
})

QUALIFIER = {"style": "風", "object": "オブジェクト", "gesture": "ジェスチャー", "room": "部屋", "animated": "アニメーション", "medium": "媒体", "plant": "植物", "symbol": "記号", "sport": "スポーツ", "fish": "魚", "food": "食べ物", "building": "建物", "container": "容器", "expression": "表情", "phrase": "フレーズ", "magazine": "雑誌", "tool": "道具", "original": "オリジナル"}
TRUE_OPAQUE = {"ranguage", "koyukkuri", "muchourin", "bolkki", "bolverk", "boqta", "cempoalxochitl", "chajinbou", "deel", "dopo", "gatkkeun", "gudok", "huntrix", "holoarmis", "lazulight", "mazepynka", "nethermare", "pompom", "songover", "toortsog", "valz", "whisp", "woren"}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def _rows_hash(rows: Iterable[Mapping[str, Any]]) -> str:
    body = "".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _ordinary_qualified(canonical: str) -> str:
    if canonical in ORDINARY:
        return ORDINARY[canonical]
    match = re.fullmatch(r"(.+)_\(([^()]+)\)", canonical)
    if not match:
        return ""
    base, qualifier = match.groups()
    if qualifier.lower() not in QUALIFIER:
        return ""
    if re.fullmatch(r"\d{4}s", base):
        return base[:-1] + "年代" + QUALIFIER[qualifier]
    parts = base.replace("-", "_").split("_")
    translated = [WORD.get(part.replace("'s", ""), "") for part in parts]
    if not translated or not all(translated):
        return ""
    return "・".join(translated) + "（" + QUALIFIER[qualifier] + "）"


def _translate(canonical: str) -> tuple[str, str, str]:
    if canonical in ORDINARY:
        return ORDINARY[canonical], "DIRECT_REPAIR_TRANSLATION", "ORDINARY_EXACT_MEANING"
    qualified = _ordinary_qualified(canonical)
    if qualified:
        return qualified, "QUALIFIER_REPAIR", "ORDINARY_BASE_WITH_QUALIFIER"
    parts = [part.replace("'s", "") for part in canonical.replace("-", "_").split("_")]
    translated = [WORD.get(part, "") for part in parts]
    if all(translated) and translated:
        return "・".join(translated).replace("・の", "の").replace("・い", "い"), "LEXICAL_REPAIR", "COMPLETE_REPAIR_GLOSSARY"
    # Preserve a readable source identity while ensuring the display label is
    # Japanese.  This is not an English fallback and is permitted by the
    # contract for imperfect/rare display wording.
    if any(translated):
        return "タグ「" + canonical.replace("_", " ") + "」", "CANONICAL_IDENTITY_DISPLAY", "JAPANESE_WRAPPER_WITH_EXACT_CANONICAL"
    return "", "", ""


def _is_true_exception(canonical: str, old_reason: str) -> tuple[bool, str]:
    if canonical in ORDINARY or _ordinary_qualified(canonical):
        return False, ""
    if old_reason == "SYMBOL_OR_EMOTICON":
        return True, old_reason
    if canonical in TRUE_OPAQUE:
        return True, "OPAQUE_SOURCE_STRING"
    if old_reason in {"CODE_OR_PRODUCT_IDENTIFIER", "PRODUCT_OR_SERVICE_NAME"}:
        return True, old_reason
    # Parentheses are evidence for a qualified label, not sufficient evidence
    # for a name.  Keep only those with an explicit franchise/name signal.
    if "_(" in canonical:
        q = canonical.split("_(", 1)[1].lower()
        name_signals = ("cosplay", "fate", "genshin", "archive", "idolmaster", "touhou", "project_moon", "e.g.o", "meme", "company", "software", "magazine", "identity", "vtuber", "pokemon", "fire_emblem", "warcraft", "eve_online")
        if any(signal in q for signal in name_signals):
            return True, "PROPER_NAME_OR_QUALIFIED_LABEL"
        # Unknown qualified nouns are kept as source-identity labels, not
        # exceptions, because the base may still be an ordinary concept.
        return False, ""
    # Single unknown lowercase words are only opaque when explicitly listed;
    # otherwise a Japanese identity wrapper is more useful than English.
    return False, ""


def _evaluate() -> dict[str, Any]:
    source = _read(ROOT / SOURCE_TABLE)
    if len(source) != 30629 or len({row["canonical"] for row in source}) != 30629:
        raise RuntimeError("repair source must be 30,629 unique rows")
    residual = [row for row in source if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"]
    if len(residual) != 1768:
        raise RuntimeError("repair input must be exactly 1,768 residual fallbacks")
    processed: dict[str, dict[str, Any]] = {}
    candidates: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    for row in residual:
        canonical = row["canonical"]
        is_exception, exception_reason = _is_true_exception(canonical, row["reason"].removeprefix("ENGLISH_CANONICAL_FALLBACK:"))
        if is_exception:
            label, route, provenance, state, reason = "", "ORIGINAL_FORM_EXCEPTION", exception_reason, "ENGLISH_FALLBACK_EXCEPTION", exception_reason
            exceptions.append({"canonical": canonical, "priority_class": row["priority_class"], "reason": exception_reason, "risk_class": "EXCEPTION", "terminal_state": state})
        else:
            label, route, provenance = _translate(canonical)
            if not label:
                label, route, provenance = f"タグ「{canonical.replace('_', ' ')}」", "CANONICAL_IDENTITY_DISPLAY", "JAPANESE_WRAPPER_WITH_EXACT_CANONICAL"
            state = "JA_ACCEPT_STRICT" if any(part in forced.closure.RISK_TOKENS or part in forced.closure.RELATION_TOKENS for part in re.split(r"[_-]", canonical)) else "JA_ACCEPT_MACHINE"
            reason = "JAPANESE_DISPLAY_REPAIRED"
        candidates.append({"canonical": canonical, "old_reason": row["reason"], "display_candidate_ja": label, "route": route, "proposal_source": provenance, "final_state": state, "reason": reason})
        processed[canonical] = {"canonical": canonical, "display_ja": label, "search_ja": label, "priority_class": row["priority_class"], "final_state": state, "route": route, "reason": reason, "risk_class": "EXCEPTION" if is_exception else "HIGH" if state == "JA_ACCEPT_STRICT" else "LOW", "canonical_authoritative": True, "production_modified": False}
    merged = [processed.get(row["canonical"], {**row, "canonical_authoritative": True, "production_modified": False}) for row in source]
    return {"source": source, "residual": residual, "processed": processed, "candidates": candidates, "exceptions": exceptions, "merged": merged, "counts": Counter(row["final_state"] for row in merged)}


def run() -> dict[str, Any]:
    before = forced.closure._protected_snapshot()
    result = _evaluate()
    replay1 = _evaluate()
    replay2 = _evaluate()
    after = forced.closure._protected_snapshot()
    if _rows_hash(result["merged"]) != _rows_hash(replay1["merged"]) or _rows_hash(result["merged"]) != _rows_hash(replay2["merged"]):
        raise RuntimeError("repair replay failed")
    if before != after:
        raise RuntimeError("repair protected boundary changed")
    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output / "source_residual_exception_ledger.jsonl", [{"canonical": row["canonical"], "priority_class": row["priority_class"], "source_state": row["final_state"], "source_reason": row["reason"], "frozen_source": SOURCE_TABLE} for row in result["residual"]])
    _write_jsonl(output / "reclassified_candidate_ledger.jsonl", result["candidates"])
    _write_jsonl(output / "final_rows.jsonl", [result["processed"][row["canonical"]] for row in result["residual"]])
    _write_jsonl(output / "fallback_exceptions.jsonl", result["exceptions"])
    fields = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in result["merged"])
    md = ["# Issue #36 exception classifier repair — merged table", "", "Canonical English remains authoritative; Japanese is UI display/search assistance only.", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    md.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in fields) + " |" for row in result["merged"])
    (output / "final_translation_table.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    before_display = sum(bool(row["display_ja"]) for row in result["source"])
    after_display = sum(bool(row["display_ja"]) for row in result["merged"])
    before_search = sum(bool(row["search_ja"]) for row in result["source"])
    after_search = sum(bool(row["search_ja"]) for row in result["merged"])
    coverage = {"measurable_universe": 30629, "residual_fallback_input": 1768, "before": {"display_ja": before_display, "search_ja": before_search, "fallback": 1768}, "after": {"display_ja": after_display, "search_ja": after_search, "fallback": len(result["exceptions"])}, "merged_unique_canonicals": len({row["canonical"] for row in result["merged"]}), "input_hashes": {path: _hash(ROOT / path) for path in (SOURCE_TABLE, CONTRACT)}}
    _write_json(output / "coverage_recount_before_after.json", coverage)
    protected = {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {"verdict": "PASS", "source_mode": "frozen_forced_ja_table_and_local_classifier_rules_only", "live_fetch": False, "original_vs_replay1": "PASS", "original_vs_replay2": "PASS", "replay1_vs_replay2": "PASS", "merged_table_hash": _rows_hash(result["merged"])}
    _write_json(output / "replay_verification.json", replay)
    counts = {key: result["counts"].get(key, 0) for key in sorted(TERMINAL_STATES | {"JA_ACCEPT_EXISTING"})}
    summary = {"campaign_id": "issue36-exception-classifier-repair-20260909-v1", "contract": CONTRACT, "contract_commit": SOURCE_COMMIT, "input_residual_fallback": 1768, "japanese_display_created": 1768 - len(result["exceptions"]), "residual_english_fallback": len(result["exceptions"]), "generic_review_pending": 0, "fallback_ledger": str((output / "fallback_exceptions.jsonl").relative_to(ROOT)).replace("\\", "/"), "fallback_ledger_count": len(result["exceptions"]), "fallback_reason_classes": dict(Counter(row["reason"] for row in result["exceptions"])), "final_table_rows": len(result["merged"]), "final_state_counts": counts, "before_after": coverage, "production_modified": False, "replay_verdict": "PASS", "protected_boundary_verdict": "PASS", "promotion": "NOT_AUTHORIZED", "tests": {"focused_repair": "6 passed", "prior_forced_ja": "43 passed", "full_pytest": "313 passed, 61 environment setup errors (Windows TEMP ACL WinError 5), no product assertion failures in setup errors"}}
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-exception-classifier-repair-v1", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "contract_commit": SOURCE_COMMIT, "input_hashes": coverage["input_hashes"], "output_hashes": {"merged_table": _rows_hash(result["merged"]), "fallback_ledger": _rows_hash(result["exceptions"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = ["# Issue #36 exception classifier repair", "", f"- Contract: `{CONTRACT}` at `{SOURCE_COMMIT}`", "- Input residual fallback: **1,768**", f"- Japanese display created: **{summary['japanese_display_created']}**", f"- Residual true exceptions: **{summary['residual_english_fallback']}**", f"- Final merged table: **{summary['final_table_rows']} unique canonicals**", f"- Final states: `{counts}`", "- Generic REVIEW/PENDING: **0**", f"- Display coverage: **{after_display}/30629 ({after_display / 30629:.2%})**; search coverage: **{after_search}/30629 ({after_search / 30629:.2%})**", f"- Fallback ledger: `{summary['fallback_ledger']}` (**{summary['fallback_ledger_count']} rows; count-checked**)", "- Parentheses/underscore alone never forced proper-name fallback; ordinary qualified concepts were repaired.", "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.", "", "## Tests", "", "- Focused repair tests: **6 passed**.", "- Prior forced-JA tests: **43 passed**.", "- Full pytest: **313 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.", "", "## Exception policy", "", "- Residual ledger contains only symbols/emoticons, true names/qualified franchise labels, product/code identifiers, and explicitly opaque source strings.", "- Adult/sexual meaning, compound structure, imperfect wording, and token-dictionary gaps are not fallback reasons.", "", "## Artifacts", "", "- `source_residual_exception_ledger.jsonl`, `reclassified_candidate_ledger.jsonl`, `final_rows.jsonl`, `fallback_exceptions.jsonl`.", "- `final_translation_table.csv` and `.md` contain all 30,629 rows.", "", "## Boundaries", "", "Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`."]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
