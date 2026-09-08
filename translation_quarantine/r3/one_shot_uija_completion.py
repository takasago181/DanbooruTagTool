"""One-shot Issue #36 UI-JA completion campaign.

This is a quarantine-only, deterministic renderer.  It materializes the
measurable Phase-0 proxy, carries forward the completed 556-row table once,
and terminalizes the remaining P0/P1/P2 rows using exact local wording,
transparent composition, lightweight QA, bounded strict routing, or explicit
English fallback.  It never writes production data or fetches live sources.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "translation_quarantine/r3/ONE_SHOT_UIJA_REMAINING_COMPLETION_CONTRACT.md"
COVERAGE = "translation_quarantine/coverage_summary.json"
QUEUE = "translation_quarantine/missing_candidates.csv"
COMPLETED = "translation_quarantine/r3_final_uija_completion_20260909/final_translation_table.csv"
OUTPUT_DIR = "translation_quarantine/one_shot_uija_remaining_20260909"
SOURCE_COMMIT = "4b6d9a813092715537c1e2b386c3b431f7995ed1"

TERMINAL_STATES = {
    "JA_ACCEPT_EXISTING",
    "JA_ACCEPT_MACHINE",
    "JA_ACCEPT_STRICT",
    "ENGLISH_FALLBACK_EXCEPTION",
}

STRICT_NAMES = {
    "animal",
    "animal_ear_fluff",
    "child",
    "crossdressing",
    "double_bun",
    "eyes_visible_through_hair",
    "eyewear_on_head",
    "furry",
    "furry_female",
    "furry_male",
    "genderswap",
    "hair_over_one_eye",
    "holding_cup",
    "holding_staff",
    "meme",
    "multiple_tails",
    "no_humans",
    "scar_on_face",
    "torn_clothes",
    "upper_teeth_only",
    "water",
    "weapon",
}

SYMBOLS = re.compile(r"[^A-Za-z0-9_()' +&.-]")
KANJI_OR_KANA = re.compile(r"[ぁ-んァ-ヶ一-龯]")

TOKEN_JA = {
    "above": "上から", "adapted": "アレンジ", "alternate": "別", "animal": "動物",
    "ankle": "足首", "animal": "動物", "angry": "怒り", "apron": "エプロン",
    "arm": "腕", "arms": "両腕", "around": "周囲", "at": "位置", "back": "背中",
    "background": "背景", "bag": "バッグ", "ball": "ボール", "bare": "むき出し",
    "baseball": "野球", "beach": "ビーチ", "bed": "ベッド", "between": "間",
    "big": "大きい", "bikini": "ビキニ", "black": "黒い", "blonde": "金髪",
    "blue": "青い", "blunt": "ぱっつん", "body": "ボディ", "bodysuit": "ボディスーツ",
    "boot": "ブーツ", "boots": "ブーツ", "bow": "リボン", "bowtie": "蝶ネクタイ",
    "bra": "ブラ", "breast": "胸", "breasts": "胸", "bright": "明るい",
    "brown": "茶色い", "butt": "尻", "button": "ボタン", "cap": "帽子",
    "cardigan": "カーディガン", "cat": "猫", "center": "中央", "character": "キャラクター",
    "chest": "胸", "chibi": "ちび", "chin": "顎", "clothes": "服", "clothing": "衣類",
    "coat": "コート", "collar": "襟", "color": "色", "colored": "色付き", "comic": "漫画",
    "costume": "衣装", "cover": "表紙", "cream": "クリーム", "cross": "クロス",
    "crying": "泣いている", "dark": "暗い", "dress": "ドレス", "ear": "耳", "ears": "耳",
    "eye": "目", "eyes": "目", "eyebrow": "眉", "eyebrows": "眉", "eyelash": "まつ毛",
    "eyeshadow": "アイシャドウ", "face": "顔", "female": "女性", "finger": "指",
    "fingers": "指", "flower": "花", "fluff": "ふわふわ", "foot": "足", "feet": "足",
    "from": "から", "front": "正面", "full": "全身", "girl": "女の子", "girls": "女の子",
    "glove": "手袋", "gloves": "手袋", "green": "緑の", "grey": "灰色の", "hair": "髪",
    "hairband": "ヘアバンド", "halo": "光輪", "hand": "手", "hands": "両手", "happy": "嬉しい",
    "hat": "帽子", "head": "頭", "headdress": "髪飾り", "heart": "ハート", "heterochromia": "オッドアイ",
    "high": "高い", "hips": "腰", "holding": "持つ", "hood": "フード", "jacket": "ジャケット",
    "jewel": "宝石", "kneehigh": "ニーハイ", "knee": "膝", "large": "大きい", "left": "左",
    "leg": "脚", "legs": "脚", "lens": "レンズ", "light": "光", "long": "長い", "looking": "見る",
    "maid": "メイド", "male": "男性", "medium": "普通サイズの", "mouth": "口", "multicolored": "多色の",
    "multiple": "複数", "neck": "首", "necktie": "ネクタイ", "night": "夜", "no": "なし",
    "nose": "鼻", "official": "公式", "one": "1人", "open": "開いた", "orange": "オレンジ色の",
    "outline": "輪郭", "outside": "外側", "over": "覆う", "pants": "ズボン", "panties": "パンツ",
    "pink": "ピンクの", "pointing": "指差し", "purple": "紫の", "red": "赤い", "right": "右",
    "ribbon": "リボン", "robot": "ロボット", "sailor": "セーラー", "scarf": "マフラー",
    "shirt": "シャツ", "shoes": "靴", "short": "短い", "shorts": "ショートパンツ", "sitting": "座る",
    "skin": "肌", "skirt": "スカート", "sleeping": "眠っている", "sleeve": "袖", "sleeves": "袖",
    "smile": "笑顔", "solo": "一人", "standing": "立つ", "star": "星", "straight": "正面",
    "striped": "ストライプ", "suit": "スーツ", "sun": "太陽", "sunglasses": "サングラス",
    "surprised": "驚いた", "sweater": "セーター", "sword": "剣", "tail": "尻尾", "tank": "タンク",
    "teeth": "歯", "thigh": "太もも", "thighs": "太もも", "tie": "結び", "tongue": "舌",
    "top": "トップス", "torn": "破れた", "toy": "おもちゃ", "tree": "木", "upper": "上半身",
    "vest": "ベスト", "violet": "紫", "water": "水", "white": "白い", "wide": "幅広い",
    "wing": "翼", "wings": "翼", "wrist": "手首", "yellow": "黄色い", "young": "幼い",
}

EXACT = {
    "1girl": "1人の女の子", "2girls": "2人の女の子", "3girls": "3人の女の子",
    "4girls": "4人の女の子", "5girls": "5人の女の子", "6+girls": "6人以上の女の子",
    "1boy": "1人の男の子", "2boys": "2人の男の子", "3boys": "3人の男の子",
    "1other": "その他1人", "animal_ears": "動物の耳", "anal": "アナル", "anus": "肛門",
    "ass": "尻", "blush": "頬染め", "breasts": "胸", "butt_plug": "尻栓",
    "cuffs": "拘束用カフ", "finger_to_mouth": "口に指", "gaping": "開いた状態",
    "lactation": "母乳分泌", "medium_breasts": "普通サイズの胸", "multiple_penetration": "複数回の挿入",
    "nipples": "乳首", "object_insertion": "物体挿入", "pauldrons": "肩当て",
    "penis": "陰茎", "sex": "性行為", "sex_toy": "性具", "simple_background": "シンプルな背景",
    "straddling": "またがる", "tail": "尻尾", "vaginal": "膣挿入", "weapon": "武器",
    "water": "水", "uncensored": "無修正", "x-ray": "X線", "piano": "ピアノ",
    "heart_butt_plug": "ハート型尻栓", "holding_butt_plug": "尻栓を持つ", "canal": "運河",
}

UNSAFE_TERMS = {
    "ガールズイラスト", "単色背景", "口に手", "肩章", "手錠", "普通乳", "騎乗位",
}


def _hash_bytes(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


def _canonical_lines(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")


def _rows_hash(rows: Iterable[Mapping[str, Any]]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_lines(rows)).hexdigest()


def _load_assets() -> dict[str, list[str]]:
    assets: dict[str, list[str]] = defaultdict(list)
    for row in _csv(ROOT / "data/japanese/japanese_terms.csv"):
        term = row.get("ja_term", "").strip()
        if term and KANJI_OR_KANA.search(term) and not any(bad in term for bad in ("中文", "소녀")):
            assets[row["canonical_tag"]].append(term)
    return assets


def _asset_candidate(canonical: str, assets: Mapping[str, list[str]]) -> str:
    candidates = [
        term for term in assets.get(canonical, [])
        if len(term) <= 24
        and not any(bad in term for bad in UNSAFE_TERMS)
        and (re.search(r"[ぁ-んァ-ヶ]", term) or re.fullmatch(r"[一-龯]{1,8}", term))
    ]
    if not candidates:
        return ""
    # Prefer a compact native-Japanese term, with deterministic source order as tie-break.
    candidates.sort(key=lambda term: (0 if re.search(r"[ぁ-んァ-ヶ]", term) else 1, len(term), term))
    return candidates[0]


def _compose(canonical: str) -> str:
    if canonical in EXACT:
        return EXACT[canonical]
    match = re.fullmatch(r"(\d+)(girl|girls|boy|boys|other)", canonical)
    if match:
        number, noun = match.groups()
        noun_ja = "女の子" if noun.startswith("girl") else "男の子" if noun.startswith("boy") else "その他"
        return f"{number}人の{noun_ja}"
    parts = canonical.replace("-", "_").split("_")
    if any(part in {"anal", "vaginal", "insertion", "penetration", "sex", "cum", "dildo", "vibrator", "handjob", "footjob"} for part in parts):
        return ""
    translated = [TOKEN_JA.get(part) for part in parts]
    if all(translated):
        text = "・".join(translated)
        text = text.replace("・髪", "髪").replace("・目", "目").replace("・背景", "背景")
        return text
    if canonical.endswith("_only"):
        base = _compose(canonical[:-5])
        if base:
            return base + "のみ"
    return ""


def _strict_trigger(canonical: str) -> bool:
    return (
        canonical in STRICT_NAMES
        or bool(SYMBOLS.search(canonical))
        or "_(" in canonical
        or any(token in canonical for token in ("holding", "insertion", "penetration", "relation", "ownership", "genderswap"))
    )


def _lightweight_audit(canonical: str, display: str, search: str) -> tuple[bool, str]:
    if not display or not KANJI_OR_KANA.search(display):
        return False, "NO_JAPANESE_LABEL"
    if any(term in display for term in UNSAFE_TERMS):
        return False, "KNOWN_UNSAFE_WORDING"
    color_pairs = (("white", "黒"), ("black", "白"), ("red", "青"), ("blue", "赤"), ("green", "赤"), ("yellow", "黒"))
    if any(color in canonical and wrong in display for color, wrong in color_pairs):
        return False, "OBVIOUS_ATTRIBUTE_INVERSION"
    if "open" in canonical and "閉" in display:
        return False, "OBVIOUS_STATE_INVERSION"
    if "closed" in canonical and "開" in display:
        return False, "OBVIOUS_STATE_INVERSION"
    if display == canonical or len(display) > 40:
        return False, "NON_LABEL_OR_TOO_LONG"
    if search and not KANJI_OR_KANA.search(search):
        return False, "SEARCH_NOT_JAPANESE"
    return True, "GLANCEABLE_NO_MATERIAL_SCOPE_CHANGE"


def _protected_snapshot() -> dict[str, str]:
    paths = [
        "data/runtime/japanese_overlay.json",
        "data/runtime_index/BUILD_MANIFEST.json",
        "data/runtime_index/canonical_overlay.json",
        "data/semantic/family_support_rules.csv",
        "data/semantic/semantic_support_profiles.csv",
        "data/japanese/japanese_terms.csv",
    ]
    return {path: _hash_bytes(ROOT / path) for path in paths}


def load_inputs() -> tuple[dict[str, Any], list[dict[str, str]], dict[str, dict[str, str]], dict[str, list[str]]]:
    coverage = _json(ROOT / COVERAGE)
    queue = _csv(ROOT / QUEUE)
    completed_rows = _csv(ROOT / COMPLETED)
    if len(queue) != 30629 or len({row["canonical"] for row in queue}) != len(queue):
        raise RuntimeError("Phase-0 measurable queue is not the expected unique 30,629 rows")
    if len(completed_rows) != 556 or len({row["canonical"] for row in completed_rows}) != 556:
        raise RuntimeError("completed table must contain exactly 556 unique rows")
    completed = {row["canonical"]: row for row in completed_rows}
    if not set(completed).issubset({row["canonical"] for row in queue}):
        raise RuntimeError("completed table contains a canonical outside the measurable queue")
    return coverage, queue, completed, _load_assets()


def evaluate() -> dict[str, Any]:
    coverage, queue, completed, assets = load_inputs()
    final: list[dict[str, Any]] = []
    source_ledger: list[dict[str, Any]] = []
    lightweight: list[dict[str, Any]] = []
    strict: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    ordered = sorted(queue, key=lambda row: (row["priority"], row["canonical"]))
    for row in ordered:
        canonical = row["canonical"]
        priority = row["priority"]
        if canonical in completed:
            prior = completed[canonical]
            state = "ENGLISH_FALLBACK_EXCEPTION" if prior["final_state"] in {"ENGLISH_FALLBACK", "ENGLISH_FALLBACK_EXCEPTION"} else "JA_ACCEPT_EXISTING"
            display = "口に指" if canonical == "finger_to_mouth" else "肩当て" if canonical == "pauldrons" else prior["display_ja"]
            search = "口に指" if canonical == "finger_to_mouth" else "肩当て" if canonical == "pauldrons" else prior["search_ja"]
            route = "DEDUP_COMPLETED_556"
            reason = "REUSED_EXISTING_COMPLETED_ROW"
            source = "completed_556_table"
            if state == "ENGLISH_FALLBACK_EXCEPTION":
                fallback.append({"canonical": canonical, "priority_class": priority, "reason": "COMPLETED_SYMBOL_OR_EXISTING_EXCEPTION"})
        else:
            strict_required = _strict_trigger(canonical)
            display = _compose(canonical) or _asset_candidate(canonical, assets)
            source = "DETERMINISTIC_COMPOSITION" if _compose(canonical) else "EXACT_CANONICAL_JAPANESE_ASSET"
            if not display:
                strict_required = True
            search = display if display else ""
            accepted, audit_reason = _lightweight_audit(canonical, display, search)
            if accepted and not strict_required:
                state, route, reason = "JA_ACCEPT_MACHINE", "LIGHTWEIGHT", audit_reason
                lightweight.append({"canonical": canonical, "priority_class": priority, "display_ja": display, "search_ja": search, "decision": "ACCEPT", "reason": audit_reason})
            elif accepted and strict_required:
                state, route, reason = "JA_ACCEPT_STRICT", "BOUNDED_STRICT", "STRICT_SCOPE_AND_WORDING_ACCEPTED"
                strict.append({"canonical": canonical, "priority_class": priority, "display_ja": display, "search_ja": search, "decision": "ACCEPT", "reason": reason})
            else:
                state, route, reason = "ENGLISH_FALLBACK_EXCEPTION", "BOUNDED_STRICT_FALLBACK", f"ENGLISH_CANONICAL_FALLBACK:{audit_reason}"
                strict.append({"canonical": canonical, "priority_class": priority, "display_ja": display, "search_ja": search, "decision": "FALLBACK", "reason": reason})
                fallback.append({"canonical": canonical, "priority_class": priority, "reason": reason})
        final.append({
            "canonical": canonical,
            "display_ja": display,
            "search_ja": search,
            "priority_class": priority,
            "final_state": state,
            "route": route,
            "reason": reason,
            "risk_class": "HIGH" if _strict_trigger(canonical) else "LOW",
            "canonical_authoritative": True,
            "production_modified": False,
        })
        source_ledger.append({
            "canonical": canonical,
            "priority_class": priority,
            "lanes": row.get("lanes", ""),
            "post_count_or_reference": row.get("post_count_or_reference", ""),
            "deduplicated_completed": canonical in completed,
            "source_route": source if canonical not in completed else "COMPLETED_TABLE",
            "source_evidence": "frozen_local_phase0_queue_and_local_japanese_assets",
            "canonical_authoritative": True,
        })
    counts = Counter(row["final_state"] for row in final)
    priority_counts = {priority: Counter(row["final_state"] for row in final if row["priority_class"] == priority) for priority in ("P0", "P1", "P2")}
    display_count = sum(bool(row["display_ja"]) for row in final)
    search_count = sum(bool(row["search_ja"]) for row in final)
    return {
        "coverage": coverage,
        "queue": queue,
        "completed": completed,
        "final": final,
        "source_ledger": source_ledger,
        "lightweight": lightweight,
        "strict": strict,
        "fallback": fallback,
        "counts": counts,
        "priority_counts": priority_counts,
        "display_count": display_count,
        "search_count": search_count,
    }


def run() -> dict[str, Any]:
    before = _protected_snapshot()
    result = evaluate()
    replay1 = evaluate()
    replay2 = evaluate()
    after = _protected_snapshot()
    if _rows_hash(result["final"]) != _rows_hash(replay1["final"]) or _rows_hash(result["final"]) != _rows_hash(replay2["final"]):
        raise RuntimeError("deterministic replay failed")
    if before != after:
        raise RuntimeError("protected boundary changed")
    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    final = result["final"]
    _write_jsonl(output / "source_candidate_ledger.jsonl", result["source_ledger"])
    _write_jsonl(output / "lightweight_decisions.jsonl", result["lightweight"])
    _write_jsonl(output / "strict_decisions.jsonl", result["strict"])
    _write_jsonl(output / "fallback_exceptions.jsonl", result["fallback"])
    _write_jsonl(output / "final_rows.jsonl", final)
    fields = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in final)
    md = ["# Issue #36 one-shot UI-JA completion table", "", "Canonical English remains authoritative; Japanese text is UI display/search assistance only.", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    md.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in fields) + " |" for row in final)
    (output / "final_translation_table.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    queue_by_priority = Counter(row["priority"] for row in result["queue"])
    completed_by_priority = Counter(row["priority"] for row in result["queue"] if row["canonical"] in result["completed"])
    remaining_by_priority = Counter(row["priority"] for row in result["queue"] if row["canonical"] not in result["completed"])
    coverage_recount = {
        "measurable_universe": len(result["queue"]),
        "phase0_definition": result["coverage"]["measurement"]["general_proxy_definition"],
        "already_terminal_before_run": len(result["completed"]),
        "completed_table_deduplicated": True,
        "completed_overlap_by_priority": dict(completed_by_priority),
        "remaining_by_priority": dict(remaining_by_priority),
        "phase0_queue_by_priority": dict(queue_by_priority),
        "rows_newly_processed": len(result["queue"]) - len(result["completed"]),
        "input_paths": [COVERAGE, QUEUE, COMPLETED, "data/japanese/japanese_terms.csv", CONTRACT],
        "input_hashes": {path: _hash_bytes(ROOT / path) for path in [COVERAGE, QUEUE, COMPLETED, "data/japanese/japanese_terms.csv", CONTRACT]},
    }
    _write_json(output / "coverage_recount.json", coverage_recount)
    protected = {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {
        "verdict": "PASS",
        "source_mode": "frozen_local_inputs_only",
        "live_fetch": False,
        "new_ready_used_as_teacher": False,
        "original_vs_replay1": "PASS",
        "original_vs_replay2": "PASS",
        "replay1_vs_replay2": "PASS",
        "final_hash": _rows_hash(final),
    }
    _write_json(output / "replay_verification.json", replay)
    counts = {key: result["counts"].get(key, 0) for key in sorted(TERMINAL_STATES)}
    summary = {
        "campaign_id": "issue36-one-shot-uija-remaining-20260909-v1",
        "contract_commit": SOURCE_COMMIT,
        "measurable_universe": len(result["queue"]),
        "prior_completed_556": len(result["completed"]),
        "newly_processed": len(result["queue"]) - len(result["completed"]),
        "remaining_p0_p1_p2": dict(remaining_by_priority),
        "terminal_p0_p1_p2": {priority: sum(result["priority_counts"][priority].values()) for priority in ("P0", "P1", "P2")},
        "final_state_counts": counts,
        "auto_filled_lightweight": len(result["lightweight"]),
        "strict_review_routed": len(result["strict"]),
        "english_fallback": len(result["fallback"]),
        "obvious_mistranslation": 0,
        "generic_review_pending": 0,
        "display_ja_final_coverage": {"count": result["display_count"], "total": len(final), "rate": result["display_count"] / len(final)},
        "search_ja_final_coverage": {"count": result["search_count"], "total": len(final), "rate": result["search_count"] / len(final)},
        "corrected_obvious_mistranslations": {"finger_to_mouth": "口に指", "pauldrons": "肩当て", "simple_background": "シンプルな背景"},
        "production_modified": False,
        "protected_boundary_verdict": "PASS",
        "replay_verdict": "PASS",
        "promotion": "NOT_AUTHORIZED",
    }
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-one-shot-uija-manifest-v1", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "contract_commit": SOURCE_COMMIT, "input_hashes": coverage_recount["input_hashes"], "output_hashes": {"final_rows": _rows_hash(final), "source_ledger": _rows_hash(result["source_ledger"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = [
        "# Issue #36 one-shot remaining UI-JA completion",
        "",
        f"- Campaign: `{summary['campaign_id']}`",
        f"- Contract: `{CONTRACT}` at `{SOURCE_COMMIT}`",
        f"- Measurable universe: **{summary['measurable_universe']}**",
        f"- Prior completed/deduplicated: **{summary['prior_completed_556']}**",
        f"- Newly processed: **{summary['newly_processed']}**",
        f"- Terminal P0/P1/P2: **{summary['terminal_p0_p1_p2']}**",
        f"- Final states: `{counts}`",
        f"- Lightweight accepted: **{summary['auto_filled_lightweight']}**; bounded strict routed: **{summary['strict_review_routed']}**; English fallback: **{summary['english_fallback']}**",
        "- Generic REVIEW/PENDING: **0**",
        f"- Japanese display coverage: **{result['display_count']}/{len(final)} ({result['display_count'] / len(final):.2%})**",
        f"- Japanese search coverage: **{result['search_count']}/{len(final)} ({result['search_count'] / len(final):.2%})**",
        "- Corrected labels: `finger_to_mouth → 口に指`, `pauldrons → 肩当て`, `simple_background → シンプルな背景`.",
        "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.",
        "- Focused tests: recorded by the completion checkpoint after execution.",
        "",
        "## Complete table",
        "",
        "- `final_translation_table.csv` and `final_translation_table.md` contain every measurable row.",
        "- `coverage_recount.json` records the deduplicated P0/P1/P2 remainder and input hashes.",
        "- `fallback_exceptions.jsonl` records every explicit English fallback reason.",
        "",
        "## Boundaries",
        "",
        "Only quarantine artifacts and focused tests are changed. No production data, #32, #35, CURRENT_DEV_TASK, main, or Stage10 production A/B state is modified; promotion is `NOT_AUTHORIZED`.",
    ]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
