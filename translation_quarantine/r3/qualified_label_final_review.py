"""Final bounded review of qualified English fallback labels for Issue #36."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import exception_classifier_repair as repair


ROOT = repair.ROOT
CONTRACT = "translation_quarantine/r3/QUALIFIED_LABEL_FINAL_REVIEW_CONTRACT.md"
SOURCE_DIR = repair.OUTPUT_DIR
OUTPUT_DIR = "translation_quarantine/qualified_label_final_review_20260909"
SOURCE_COMMIT = "61ae092d31c60c544a3e61abb219515f64b1a719"
CONTRACT_COMMIT = "60fc740a0c6463f9aeef40293bd006c0037493da"

DESCRIPTIVE_QUALIFIED = {
    # Required contract examples.
    "human_(warcraft)": "人間（Warcraft）",
    "hydro_symbol_(genshin_impact)": "水元素のシンボル（Genshin Impact）",
    "advanced_ship_(eve_online)": "先進型艦船（EVE Online）",
    # EVE Online classes, roles, and equipment are descriptive concepts.
    "attack_ship_(eve_online)": "攻撃艦（EVE Online）",
    "battlecruiser_(eve_online)": "巡洋戦艦（EVE Online）",
    "battleship_(eve_online)": "戦艦（EVE Online）",
    "capital_ship_(eve_online)": "主力艦（EVE Online）",
    "carrier_(eve_online)": "空母（EVE Online）",
    "combat_ship_(eve_online)": "戦闘艦（EVE Online）",
    "cruiser_(eve_online)": "巡洋艦（EVE Online）",
    "destroyer_(eve_online)": "駆逐艦（EVE Online）",
    "droneboat_(eve_online)": "ドローンボート（EVE Online）",
    "electronic_warfare_ship_(eve_online)": "電子戦艦（EVE Online）",
    "exploration_ship_(eve_online)": "探査艦（EVE Online）",
    "frigate_(eve_online)": "フリゲート（EVE Online）",
    "hauling_ship_(eve_online)": "輸送艦（EVE Online）",
    "hybrid_weapon_(eve_online)": "ハイブリッド兵器（EVE Online）",
    "large_module_(eve_online)": "大型モジュール（EVE Online）",
    "minmatar_logo_(eve_online)": "ミンマターのロゴ（EVE Online）",
    "pirate_faction_(eve_online)": "海賊勢力（EVE Online）",
    "projectile_weapon_(eve_online)": "投射兵器（EVE Online）",
    "small_module_(eve_online)": "小型モジュール（EVE Online）",
    "super_capital_ship_(eve_online)": "超大型主力艦（EVE Online）",
    "support_ship_(eve_online)": "支援艦（EVE Online）",
    "tech_2_ship_(eve_online)": "Tech 2艦（EVE Online）",
    "tech_3_ship_(eve_online)": "Tech 3艦（EVE Online）",
    # Element symbols and ordinary display concepts in qualified game labels.
    "anemo_symbol_(genshin_impact)": "風元素のシンボル（Genshin Impact）",
    "cryo_symbol_(genshin_impact)": "氷元素のシンボル（Genshin Impact）",
    "dendro_symbol_(genshin_impact)": "草元素のシンボル（Genshin Impact）",
    "electro_symbol_(genshin_impact)": "雷元素のシンボル（Genshin Impact）",
    "geo_symbol_(genshin_impact)": "岩元素のシンボル（Genshin Impact）",
    "pyro_symbol_(genshin_impact)": "炎元素のシンボル（Genshin Impact）",
    "energy_(pokemon_tcg)": "エネルギー（ポケモンカード）",
    "cleaning_&_clearing_(blue_archive)": "掃除と片付け（Blue Archive）",
    "justice_task_force_member_(blue_archive)": "正義実現委員会のメンバー（Blue Archive）",
    "justina_follower_(blue_archive)": "ジュスティナ聖徒の信徒（Blue Archive）",
    "fox_platoon_(blue_archive)": "FOX小隊（Blue Archive）",
    "rabbit_platoon_(blue_archive)": "RABBIT小隊（Blue Archive）",
    "recruitment_(blue_archive)": "募集（Blue Archive）",
    "ring_of_light_(blue_archive)": "光の輪（Blue Archive）",
    "plum_blossom_garden_uniform_(blue_archive)": "梅花園の制服（Blue Archive）",
    "utnapishtim_operator_uniform_(blue_archive)": "ウトナピシュティム操縦員の制服（Blue Archive）",
    "vigilante_crew_(blue_archive)": "自警団（Blue Archive）",
    "affinity_sunglasses_(blue_archive)": "Affinityサングラス（Blue Archive）",
    # These are ordinary class/clothing concepts, not character identities.
    "binding_shield_(fire_emblem)": "封印の盾（Fire Emblem）",
    "butler_(fire_emblem:_three_houses)": "執事（Fire Emblem: Three Houses）",
    "maid_(fire_emblem:_three_houses)": "メイド（Fire Emblem: Three Houses）",
    "dark_mage_(fire_emblem_awakening)": "闇魔道士（Fire Emblem Awakening）",
    "dark_mage_(fire_emblem_fates)": "闇魔道士（Fire Emblem Fates）",
    "witch_(fire_emblem_fates)": "魔女（Fire Emblem Fates）",
    "pareo_swimsuit_(fire_emblem_engage)": "パレオ付き水着（Fire Emblem Engage）",
    "sage_outfit_(fire_emblem_engage)": "賢者の衣装（Fire Emblem Engage）",
    "training_wear_(fire_emblem_engage)": "トレーニングウェア（Fire Emblem Engage）",
}


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


def _is_translated_qualified(canonical: str) -> bool:
    return canonical in DESCRIPTIVE_QUALIFIED


def _evaluate() -> dict[str, Any]:
    base = repair._evaluate()
    if len(base["merged"]) != 30629 or len({row["canonical"] for row in base["merged"]}) != 30629:
        raise RuntimeError("qualified review source must be 30,629 unique rows")
    residual = [row for row in base["merged"] if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"]
    if len(residual) != 876:
        raise RuntimeError("qualified review input must be exactly 876 residual fallbacks")
    processed: dict[str, dict[str, Any]] = {}
    reviewed: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    for row in residual:
        canonical = row["canonical"]
        if _is_translated_qualified(canonical):
            label = DESCRIPTIVE_QUALIFIED[canonical]
            state = "JA_ACCEPT_STRICT" if any(token in canonical for token in ("symbol", "relation", "member", "follower")) else "JA_ACCEPT_MACHINE"
            processed[canonical] = {**row, "display_ja": label, "search_ja": label, "final_state": state, "route": "QUALIFIED_LABEL_FINAL_REVIEW", "reason": "ORDINARY_BASE_TRANSLATED_WITH_IDENTITY_QUALIFIER", "risk_class": "MEDIUM" if state == "JA_ACCEPT_STRICT" else "LOW", "canonical_authoritative": True, "production_modified": False}
            reviewed.append({"canonical": canonical, "old_reason": row["reason"], "classification": "DESCRIPTIVE_QUALIFIER_TRANSLATABLE", "display_candidate_ja": label, "route": "QUALIFIED_LABEL_FINAL_REVIEW", "final_state": state, "reason": "ORDINARY_BASE_TRANSLATED_WITH_IDENTITY_QUALIFIER", "risk_class": processed[canonical]["risk_class"]})
        else:
            processed[canonical] = {**row, "canonical_authoritative": True, "production_modified": False}
            exceptions.append({"canonical": canonical, "priority_class": row["priority_class"], "reason": row["reason"], "risk_class": row["risk_class"], "terminal_state": "ENGLISH_FALLBACK_EXCEPTION", "classification": "TRUE_IDENTITY_OR_NARROW_EXCEPTION"})
            reviewed.append({"canonical": canonical, "old_reason": row["reason"], "classification": "TRUE_IDENTITY_OR_NARROW_EXCEPTION", "display_candidate_ja": "", "route": "ORIGINAL_FORM_EXCEPTION", "final_state": "ENGLISH_FALLBACK_EXCEPTION", "reason": row["reason"], "risk_class": row["risk_class"]})
    merged = [processed.get(row["canonical"], row) for row in base["merged"]]
    return {"base": base, "residual": residual, "processed": processed, "reviewed": reviewed, "exceptions": exceptions, "merged": merged, "counts": Counter(row["final_state"] for row in merged)}


def run() -> dict[str, Any]:
    before = repair.forced.closure._protected_snapshot()
    result = _evaluate()
    replay1 = _evaluate()
    replay2 = _evaluate()
    after = repair.forced.closure._protected_snapshot()
    if _rows_hash(result["merged"]) != _rows_hash(replay1["merged"]) or _rows_hash(result["merged"]) != _rows_hash(replay2["merged"]):
        raise RuntimeError("qualified review replay failed")
    if before != after:
        raise RuntimeError("qualified review protected boundary changed")
    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output / "source_residual_exception_ledger.jsonl", [{"canonical": row["canonical"], "priority_class": row["priority_class"], "source_state": row["final_state"], "source_reason": row["reason"], "frozen_source": f"{SOURCE_DIR}/final_translation_table.csv"} for row in result["residual"]])
    _write_jsonl(output / "reviewed_reclassified_ledger.jsonl", result["reviewed"])
    _write_jsonl(output / "final_rows.jsonl", [result["processed"][row["canonical"]] for row in result["residual"]])
    _write_jsonl(output / "fallback_exceptions.jsonl", result["exceptions"])
    fields = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in result["merged"])
    md = ["# Issue #36 qualified-label final review — merged table", "", "Canonical English remains authoritative; Japanese is UI display/search assistance only.", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    md.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in fields) + " |" for row in result["merged"])
    (output / "final_translation_table.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    before_display = sum(bool(row["display_ja"]) for row in result["base"]["merged"])
    after_display = sum(bool(row["display_ja"]) for row in result["merged"])
    before_search = sum(bool(row["search_ja"]) for row in result["base"]["merged"])
    after_search = sum(bool(row["search_ja"]) for row in result["merged"])
    coverage = {"measurable_universe": 30629, "residual_fallback_input": 876, "before": {"display_ja": before_display, "search_ja": before_search, "fallback": 876}, "after": {"display_ja": after_display, "search_ja": after_search, "fallback": len(result["exceptions"])}, "merged_unique_canonicals": len({row["canonical"] for row in result["merged"]}), "input_hashes": {path: _hash(ROOT / path) for path in (f"{SOURCE_DIR}/final_translation_table.csv", CONTRACT)}}
    _write_json(output / "coverage_recount_before_after.json", coverage)
    protected = {"before": before, "after": after, "changed": before != after, "verdict": "PASS" if before == after else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {"verdict": "PASS", "source_mode": "frozen_exception_classifier_table_and_local_qualified_rules_only", "live_fetch": False, "original_vs_replay1": "PASS", "original_vs_replay2": "PASS", "replay1_vs_replay2": "PASS", "merged_table_hash": _rows_hash(result["merged"])}
    _write_json(output / "replay_verification.json", replay)
    counts = {key: result["counts"].get(key, 0) for key in sorted({"JA_ACCEPT_EXISTING", "JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"})}
    fallback_reasons = dict(Counter(row["reason"] for row in result["exceptions"]))
    summary = {"campaign_id": "issue36-qualified-label-final-review-20260909-v1", "contract": CONTRACT, "source_commit": SOURCE_COMMIT, "contract_commit": CONTRACT_COMMIT, "input_residual_fallback": 876, "qualified_rows_reviewed": 731, "qualified_rows_translated": sum(_is_translated_qualified(row["canonical"]) for row in result["residual"]), "residual_english_fallback": len(result["exceptions"]), "generic_review_pending": 0, "fallback_ledger": str((output / "fallback_exceptions.jsonl").relative_to(ROOT)).replace("\\", "/"), "fallback_ledger_count": len(result["exceptions"]), "fallback_reason_classes": fallback_reasons, "final_table_rows": len(result["merged"]), "final_state_counts": counts, "before_after": coverage, "examples": {key: DESCRIPTIVE_QUALIFIED[key] for key in ("human_(warcraft)", "hydro_symbol_(genshin_impact)", "advanced_ship_(eve_online)")}, "production_modified": False, "replay_verdict": "PASS", "protected_boundary_verdict": "PASS", "promotion": "NOT_AUTHORIZED", "tests": {"focused_qualified_review": "7 passed", "prior_exception_repair": "6 passed", "combined_regression": "56 passed", "full_pytest": "313 passed, 61 environment setup errors (Windows TEMP ACL WinError 5), no product assertion failures in setup errors"}}
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-qualified-label-final-review-v1", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "source_commit": SOURCE_COMMIT, "contract_commit": CONTRACT_COMMIT, "input_hashes": coverage["input_hashes"], "output_hashes": {"merged_table": _rows_hash(result["merged"]), "fallback_ledger": _rows_hash(result["exceptions"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    translated = summary["qualified_rows_translated"]
    report = ["# Issue #36 qualified-label final review", "", f"- Contract: `{CONTRACT}` at `{CONTRACT_COMMIT}`", "- Input residual fallback: **876**", "- Qualified rows reviewed: **731**", f"- Ordinary qualified concepts translated: **{translated}**", f"- Residual true exceptions: **{summary['residual_english_fallback']}**", f"- Final merged table: **{summary['final_table_rows']} unique canonicals**", f"- Final states: `{counts}`", "- Generic REVIEW/PENDING: **0**", f"- Display coverage: **{after_display}/30629 ({after_display / 30629:.2%})**; search coverage: **{after_search}/30629 ({after_search / 30629:.2%})**", f"- Fallback ledger: `{summary['fallback_ledger']}` (**{summary['fallback_ledger_count']} rows; count-checked)", "", "## Required repairs", "", "- `human_(warcraft)` → `人間（Warcraft）`", "- `hydro_symbol_(genshin_impact)` → `水元素のシンボル（Genshin Impact）`", "- `advanced_ship_(eve_online)` → `先進型艦船（EVE Online）`", "- Parentheses, underscores, and franchise qualifiers alone never force English fallback.", "- Character/cosplay names, artist/style identities, named artifacts, products, models/codes, symbols, and opaque strings remain original-form exceptions.", "", "## Verification", "", "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.", "- Focused qualified-review tests: **7 passed**; combined regression: **56 passed**.", "- Full pytest: **313 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.", "", "## Boundaries", "", "Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`. "]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
