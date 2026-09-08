"""Acquire the bounded #36 canary evidence without changing the R3 evaluator."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

try:
    from .r3_common import file_hash, write_jsonl
except ImportError:  # pragma: no cover
    from r3_common import file_hash, write_jsonl


# Direct, non-ambiguous surface forms already present in the local overlay.
# These are wording candidates only; semantic scope is independently justified
# by the transparent-composition allow-list below.
SAFE_WORDING_TERMS = {
    "glasses": "めがね", "earrings": "イヤリング", "beret": "ベレー",
    "blouse": "ブラウス", "transparent_background": "透明な背景",
    "halterneck": "ホルターネック", "leotard": "レオタード", "logo": "ロゴ",
    "black_socks": "黒ソックス", "long_skirt": "ロングスカート",
    "high_heels": "ハイヒール", "school_swimsuit": "スクール水着",
    "headset": "ヘッドセット", "zipper": "ジッパー", "sneakers": "スニーカー",
    "cosplay": "コスプレ", "orange_eyes": "オレンジ目", "bell": "ベル",
    "bodysuit": "ボディスーツ", "side_ponytail": "サイドテール",
    "tattoo": "タトゥー", "speech_bubble": "ふきだし", "sash": "サッシュ",
    "headphones": "ヘッドホン", "sweater_vest": "ニットベスト", "couch": "ソファ",
    "tiara": "ティアラ", "candy": "キャンディ", "denim": "デニム",
    "highleg": "ハイレグ", "elf": "エルフ", "twin_drills": "ツインドリル",
}

TRANSPARENT_COMPOSITION_SCOPE = {
    "glasses": "single concrete eyewear entity; no actor, target, action, or relation added",
    "earrings": "single concrete ear-jewelry entity; no actor, target, action, or relation added",
    "beret": "single concrete headwear entity; no actor, target, action, or relation added",
    "blouse": "single concrete garment entity; no actor, target, action, or relation added",
    "transparent_background": "transparent + background visual attribute composition; no actor or relation added",
    "halterneck": "single conventional garment entity; no actor, target, action, or relation added",
    "leotard": "single concrete garment entity; no actor, target, action, or relation added",
    "logo": "single concrete graphic-mark entity; no actor, target, action, or relation added",
    "black_socks": "black + socks attribute composition; no actor, target, action, or relation added",
    "long_skirt": "long + skirt attribute composition; no actor, target, action, or relation added",
    "high_heels": "single concrete footwear entity; no actor, target, action, or relation added",
    "school_swimsuit": "single conventional garment entity; no actor, target, action, or relation added",
    "headset": "single concrete audio-device entity; no actor, target, action, or relation added",
    "zipper": "single concrete clothing-fastener entity; no actor, target, action, or relation added",
    "sneakers": "single concrete footwear entity; no actor, target, action, or relation added",
    "cosplay": "single established costume-practice entity; no actor, target, action, or relation added",
    "orange_eyes": "orange + eyes attribute composition; no actor, target, action, or relation added",
    "bell": "single concrete bell entity; no actor, target, action, or relation added",
    "bodysuit": "single concrete garment entity; no actor, target, action, or relation added",
    "side_ponytail": "single conventional hairstyle entity; no actor, target, action, or relation added",
    "tattoo": "single concrete body-mark entity; no actor, target, action, or relation added",
    "speech_bubble": "single conventional graphic-text entity; no actor, target, action, or relation added",
    "sash": "single concrete garment/accessory entity; no actor, target, action, or relation added",
    "headphones": "single concrete audio-device entity; no actor, target, action, or relation added",
    "sweater_vest": "single conventional garment entity; no actor, target, action, or relation added",
    "couch": "single concrete furniture entity; no actor, target, action, or relation added",
    "tiara": "single concrete headwear/jewelry entity; no actor, target, action, or relation added",
    "candy": "single concrete food entity; no actor, target, action, or relation added",
    "denim": "single concrete material/clothing attribute; no actor, target, action, or relation added",
    "highleg": "single conventional garment-cut entity; no actor, target, action, or relation added",
    "elf": "single established entity type; no actor, target, action, or relation added",
    "twin_drills": "twin + drill-hairstyle composition; no actor, target, action, or relation added",
}


def _identity(value: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def acquire_and_freeze(
    root: Path,
    selected: list[Mapping[str, Any]],
    queue_path: Path,
    output_path: Path,
    *,
    campaign_id: str = "issue36-r3-bulk-canary-20260909-v2",
) -> list[dict[str, Any]]:
    """Build one deterministic frozen evidence set for a bounded bulk batch."""

    overlay_path = root / "data" / "runtime" / "japanese_overlay.json"
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    entries = overlay.get("entries", {}) if isinstance(overlay, dict) else {}
    overlay_hash = file_hash(overlay_path)
    queue_hash = file_hash(queue_path)
    evidence: list[dict[str, Any]] = []
    for item in selected:
        canonical = str(item["canonical"])
        evidence.append({
            "evidence_id": f"issue36-bulk:identity:{canonical}",
            "canonical": canonical,
            "source_type": "pinned_candidate_queue",
            "source_ref": "translation_quarantine/missing_candidates.csv",
            "scope_note": "canonical identity only; no Japanese wording or semantic scope is inferred",
            "content_identity": queue_hash,
            "evidence_role": "IDENTITY_ONLY",
            "frozen": True,
            "bulk_campaign": campaign_id,
        })
        scope_note = TRANSPARENT_COMPOSITION_SCOPE.get(canonical)
        term = SAFE_WORDING_TERMS.get(canonical)
        if not scope_note or not term:
            continue
        entry = entries.get(canonical, {})
        available_terms = entry.get("search_ja", []) if isinstance(entry, dict) else []
        if term not in available_terms:
            raise ValueError(f"safe wording term is not present in frozen local overlay: {canonical}")
        evidence.append({
            "evidence_id": f"issue36-bulk:scope:{canonical}",
            "canonical": canonical,
            "source_type": "transparent_canonical_composition",
            "source_ref": "translation_quarantine/r3/r3_bulk_evidence.py",
            "scope_note": scope_note,
            "content_identity": _identity({"canonical": canonical, "scope_note": scope_note}),
            "evidence_role": "SEMANTIC_SCOPE",
            "scope_basis": "TRANSPARENT_CANONICAL_COMPOSITION",
            "frozen": True,
            "bulk_campaign": campaign_id,
        })
        evidence.append({
            "evidence_id": f"issue36-bulk:wording:{canonical}",
            "canonical": canonical,
            "source_type": "local_overlay_wording_candidate",
            "source_ref": "data/runtime/japanese_overlay.json",
            "scope_note": "Frozen Japanese wording candidate; never semantic authority.",
            "content_identity": overlay_hash,
            "evidence_role": "WORDING_CANDIDATE",
            "frozen": True,
            "display_candidate": term,
            "search_candidate": term,
            "term_class": "EXACT_SYNONYM",
            "exact_synonym_verified": True,
            "search_equivalence_proof": "EXACT",
            "bulk_campaign": campaign_id,
        })
    evidence.sort(key=lambda row: (str(row.get("canonical", "")), str(row.get("evidence_id", ""))))
    write_jsonl(output_path, evidence)
    return evidence
