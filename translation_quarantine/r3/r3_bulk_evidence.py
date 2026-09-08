"""Acquire frozen Issue #36 evidence without changing the R3 evaluator.

This module is deliberately conservative.  The local Japanese overlay can
only provide wording candidates.  Semantic scope comes from either a small,
mechanical transparent-composition rule for LOW/MEDIUM rows or an exact
canonical reference row for HIGH/CRITICAL rows.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

try:
    from .r3_common import classify_risk, file_hash, read_csv, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from r3_common import classify_risk, file_hash, read_csv, write_json, write_jsonl


# Retain the original validated canary evidence exactly.  These entries are
# not used as a semantic allow-list for the remaining 625 rows.
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

# These are token classes, not canonical tags.  Keeping the vocabulary
# intentionally small makes generalisation explicit and fail-closed.
TRANSPARENT_ATTRIBUTE_TOKENS = {
    "aqua", "black", "blue", "brown", "closed", "colored", "dark", "double",
    "frilled", "green", "grey", "gray", "high", "large", "light", "long",
    "low", "medium", "multicolored", "narrow", "orange", "pink", "pointed",
    "polka", "purple", "red", "round", "short", "simple", "single", "small",
    "soft", "starry", "straight", "striped", "thick", "transparent", "twin",
    "vertical", "wavy", "wide", "white", "wooden", "yellow",
}
TRANSPARENT_ENTITY_TOKENS = {
    "apron", "background", "bag", "bell", "belt", "beret", "bikini", "book",
    "boots", "bow", "bowtie", "bra", "cap", "candy", "camera", "chair", "cloud",
    "coat", "couch", "collar", "computer", "cup", "dress", "earrings", "eyes",
    "flower", "food", "fork", "glasses", "gloves", "guitar", "hair", "hat", "eyewear",
    "headphones", "headset", "jacket", "key", "mask", "microphone", "necklace",
    "pants", "pen", "phone", "pillow", "plate", "pot", "ring", "ribbon", "scarf",
    "shirt", "shoes", "shorts", "skirt", "socks", "suit", "sweater", "sword",
    "table", "tail", "tie", "tiara", "top", "toy", "towel", "umbrella", "water",
    "weapon", "wheel", "window", "wings", "wood", "zipper",
}
TRANSPARENT_REJECT_TOKENS = {
    "action", "anal", "anus", "ass", "between", "bound", "clitoris", "cum",
    "dildo", "ejaculation", "erection", "feet", "footjob", "groping", "handjob",
    "holding", "insertion", "kneeling", "multiple", "object", "penetration", "penis",
    "pose", "pussy", "sex", "straddling", "testicles", "vaginal", "vulva", "with",
}

SPECIAL_REFERENCE = "data/special2788/illustrious_tag_knowledge_base_2788.csv"
# A single overlay term is still rejected when the local wording visibly
# narrows, broadens, or disambiguates the canonical.  This is a safety
# blocklist, not an approval allow-list; unknown cases remain REVIEW.
TRANSPARENT_WORDING_HAZARDS = {
    "green_jacket": ("ブレザー",),
    "sword": ("グレート",),
    "frilled_bikini": ("フレア",),
    "grey_hair": ("銀髪", "ロング"),
    "cloud": ("くも",),
    "scarf": ("マフラー",),
}


def _identity(value: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tokens(canonical: str) -> list[str]:
    return [token for token in re.split(r"[_-]+", canonical.strip().lower()) if token]


def transparent_composition_scope(canonical: str, risk_class: str) -> tuple[str, str] | None:
    """Return a scope note and basis only for mechanically transparent rows."""

    if risk_class not in {"LOW", "MEDIUM"} or canonical == "simple_background":
        return None
    tokens = _tokens(canonical)
    if not tokens or len(tokens) > 2 or any(not token.isalpha() for token in tokens):
        return None
    if set(tokens) & TRANSPARENT_REJECT_TOKENS:
        return None
    if len(tokens) == 1 and tokens[0] in TRANSPARENT_ENTITY_TOKENS:
        return (
            "single concrete entity; no actor, target, action, relation, count, or qualifier added",
            "TRANSPARENT_CANONICAL_COMPOSITION",
        )
    if len(tokens) == 2:
        attributes = [token for token in tokens if token in TRANSPARENT_ATTRIBUTE_TOKENS]
        entities = [token for token in tokens if token in TRANSPARENT_ENTITY_TOKENS]
        if len(attributes) == 1 and len(entities) == 1:
            return (
                f"{attributes[0]} + {entities[0]} transparent composition; no actor, target, action, relation, count, or extra qualifier added",
                "TRANSPARENT_CANONICAL_COMPOSITION",
            )
    return None


def _exact_reference_index(root: Path) -> tuple[dict[str, dict[str, Any]], str, dict[str, int]]:
    path = root / SPECIAL_REFERENCE
    if not path.exists():
        return {}, "", {"missing_reference": 1}
    rows = read_csv(path)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        tag = str(row.get("Tag", "")).strip().replace(" ", "_").lower()
        target = str(row.get("canonical_target", "")).strip().replace(" ", "_").lower()
        if not tag or target:
            # Alias/redirect rows are not exact-canonical authority.
            continue
        grouped.setdefault(tag, []).append(row)
    index: dict[str, dict[str, Any]] = {}
    ambiguous = 0
    for tag, candidates in grouped.items():
        fingerprints = {
            (str(row.get("Tag", "")), str(row.get("元の日本語説明", "")), str(row.get("主カテゴリ", "")))
            for row in candidates
        }
        if len(fingerprints) != 1:
            ambiguous += 1
            continue
        index[tag] = candidates[0]
    return index, file_hash(path), {"exact_rows": len(index), "ambiguous_exact_rows": ambiguous}


def _overlay_wording(entry: Any) -> list[str]:
    if not isinstance(entry, dict):
        return []
    values = entry.get("search_ja", [])
    if isinstance(values, str):
        values = [values]
    return [str(value).strip() for value in values if str(value).strip()]


def _safe_transparent_wording(canonical: str, terms: list[str]) -> str | None:
    if len(terms) != 1:
        return None
    term = terms[0]
    if any(marker in term for marker in TRANSPARENT_WORDING_HAZARDS.get(canonical, ())):
        return None
    return term


def _append_wording(evidence: list[dict[str, Any]], *, canonical: str, term: str, overlay_hash: str, campaign_id: str) -> None:
    evidence.append({
        "evidence_id": f"issue36-bulk:wording:{canonical}",
        "canonical": canonical,
        "source_type": "local_overlay_wording_candidate",
        "source_ref": "data/runtime/japanese_overlay.json",
        "scope_note": "Frozen Japanese wording candidate only; never semantic authority.",
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


def acquire_and_freeze(
    root: Path,
    selected: list[Mapping[str, Any]],
    queue_path: Path,
    output_path: Path,
    *,
    campaign_id: str = "issue36-r3-bulk-canary-20260909-v2",
    report_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Build one deterministic frozen evidence set for a bounded bulk batch."""

    overlay_path = root / "data" / "runtime" / "japanese_overlay.json"
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    entries = overlay.get("entries", {}) if isinstance(overlay, dict) else {}
    overlay_hash = file_hash(overlay_path)
    queue_hash = file_hash(queue_path)
    exact_index, exact_hash, reference_stats = _exact_reference_index(root)
    legacy_canary_mode = campaign_id.startswith("issue36-r3-bulk-canary")
    evidence: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "schema_version": "issue36-bulk-evidence-acquisition-2", "campaign_id": campaign_id,
        "selected_rows": len(selected), "source_type_counts": Counter(), "evidence_role_counts": Counter(),
        "transparent_scope_candidates": 0, "exact_authoritative_scope_candidates": 0,
        "wording_candidates": 0, "skipped": Counter(),
        "reference": {"path": SPECIAL_REFERENCE, "content_identity": exact_hash, **reference_stats},
    }
    for item in selected:
        canonical = str(item["canonical"])
        risk_class = classify_risk(canonical, str(item.get("semantic_class", "")))
        evidence.append({
            "evidence_id": f"issue36-bulk:identity:{canonical}", "canonical": canonical,
            "source_type": "pinned_candidate_queue", "source_ref": "translation_quarantine/missing_candidates.csv",
            "scope_note": "canonical identity only; no Japanese wording or semantic scope is inferred",
            "content_identity": queue_hash, "evidence_role": "IDENTITY_ONLY", "frozen": True,
            "bulk_campaign": campaign_id,
        })
        entry = entries.get(canonical, {})
        terms = _overlay_wording(entry)
        scope = None if legacy_canary_mode else transparent_composition_scope(canonical, risk_class)
        # The old 32 are retained verbatim for canary compatibility.
        if canonical in TRANSPARENT_COMPOSITION_SCOPE and canonical in SAFE_WORDING_TERMS:
            term = SAFE_WORDING_TERMS[canonical]
            if term not in terms:
                raise ValueError(f"safe wording term is not present in frozen local overlay: {canonical}")
            scope_note = TRANSPARENT_COMPOSITION_SCOPE[canonical]
            evidence.append({
                "evidence_id": f"issue36-bulk:scope:{canonical}", "canonical": canonical,
                "source_type": "transparent_canonical_composition", "source_ref": "translation_quarantine/r3/r3_bulk_evidence.py",
                "scope_note": scope_note, "content_identity": _identity({"canonical": canonical, "scope_note": scope_note}),
                "evidence_role": "SEMANTIC_SCOPE", "scope_basis": "TRANSPARENT_CANONICAL_COMPOSITION",
                "frozen": True, "bulk_campaign": campaign_id,
            })
            _append_wording(evidence, canonical=canonical, term=term, overlay_hash=overlay_hash, campaign_id=campaign_id)
            continue
        if scope is not None:
            scope_note, scope_basis = scope
            evidence.append({
                "evidence_id": f"issue36-bulk:scope:{canonical}", "canonical": canonical,
                "source_type": "transparent_canonical_composition", "source_ref": "translation_quarantine/r3/r3_bulk_evidence.py",
                "scope_note": scope_note, "content_identity": _identity({"canonical": canonical, "scope_note": scope_note}),
                "evidence_role": "SEMANTIC_SCOPE", "scope_basis": scope_basis,
                "frozen": True, "bulk_campaign": campaign_id,
            })
            report["transparent_scope_candidates"] += 1
            safe_term = _safe_transparent_wording(canonical, terms)
            if safe_term is not None:
                _append_wording(evidence, canonical=canonical, term=safe_term, overlay_hash=overlay_hash, campaign_id=campaign_id)
                report["wording_candidates"] += 1
            else:
                report["skipped"]["transparent_without_safe_overlay_wording"] += 1
            continue
        exact = exact_index.get(canonical.lower())
        if not legacy_canary_mode and risk_class in {"HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"}:
            if exact is None:
                report["skipped"]["high_or_critical_without_exact_authority"] += 1
                continue
            description = str(exact.get("元の日本語説明", "")).strip()
            category = str(exact.get("主カテゴリ", "")).strip()
            scope_note = "exact canonical authoritative reference; scope is frozen from the exact Tag row only"
            evidence.append({
                "evidence_id": f"issue36-bulk:scope:{canonical}", "canonical": canonical,
                "source_type": "local_exact_authoritative_reference", "source_ref": SPECIAL_REFERENCE,
                "scope_note": scope_note, "content_identity": exact_hash, "evidence_role": "SEMANTIC_SCOPE",
                "scope_basis": "EXACT_CANONICAL_AUTHORITATIVE_REFERENCE", "authority": "EXACT_CANONICAL_ONLY",
                "reference_tag": exact.get("Tag", ""), "reference_description": description,
                "reference_category": category, "frozen": True, "bulk_campaign": campaign_id,
            })
            report["exact_authoritative_scope_candidates"] += 1
            if len(terms) != 1:
                report["skipped"]["exact_authority_without_unambiguous_wording"] += 1
            continue
        report["skipped"]["no_safe_transparent_or_exact_scope"] += 1
    evidence.sort(key=lambda row: (str(row.get("canonical", "")), str(row.get("evidence_id", ""))))
    write_jsonl(output_path, evidence)
    report["source_type_counts"] = dict(sorted(Counter(str(row.get("source_type", "")) for row in evidence).items()))
    report["evidence_role_counts"] = dict(sorted(Counter(str(row.get("evidence_role", "")) for row in evidence).items()))
    report["skipped"] = dict(sorted(report["skipped"].items()))
    if report_path is not None:
        write_json(report_path, report)
    return evidence
