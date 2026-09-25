#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json

SCHEMA_V2 = "issue132-pass-a-staging-window-v2"

COMPACT_ROW_FIELDS = {
    "lane_local_index",
    "review_seq",
    "identity_sha256",
    "discovery_mode",
    "routes",
    "local_refinement_ids",
    "body_site_ids",
    "theme_ids",
    "route_vocabulary_gap",
    "review_depth",
    "evidence_urls",
}

COMPACT_HOLD_FIELDS = {
    "lane_local_index",
    "review_seq",
    "identity_sha256",
    "reason_code",
    "research_attempt_codes",
}

HOLD_REASON_CODES = {
    "DIRECT_EVIDENCE_NOT_FOUND",
    "IDENTITY_AMBIGUOUS",
    "SEMANTIC_SCOPE_AMBIGUOUS",
    "ROUTE_AMBIGUOUS",
    "OTHER_UNRESOLVED",
}

RESEARCH_ATTEMPT_CODES = {
    "DANBOORU_EXACT",
    "SAFEBOORU_EXACT",
    "OFFICIAL_SOURCE",
    "DIRECT_WEB_SOURCE",
    "OTHER_DIRECT_SOURCE",
}

ROUTE_REASON_JA = {
    "PEOPLE_COUNT": "人数・人数構成として探すのが自然",
    "RELATION_ROLE": "人物同士の関係・役割として探すのが自然",
    "BODY_SITE": "身体部位・身体特徴として探すのが自然",
    "HAIR_FACE": "髪・顔・目などの外観として探すのが自然",
    "CLOTHING_EXPOSURE": "衣服・装身具・露出状態として探すのが自然",
    "TOOL_OBJECT": "物体・道具・小物として探すのが自然",
    "LIVING": "生物・植物として探すのが自然",
    "NONHUMAN_TRANSFORM": "非人間的特徴・変身要素として探すのが自然",
    "ACTION_CONTACT": "動作・接触として探すのが自然",
    "POSE_POSITION": "姿勢・位置関係として探すのが自然",
    "EXPRESSION_GAZE": "表情・視線として探すのが自然",
    "FLUID_EXCRETION": "液体・分泌・排泄表現として探すのが自然",
    "COMPOSITION_CAMERA": "構図・カメラ表現として探すのが自然",
    "SCENE_BACKGROUND": "場所・背景として探すのが自然",
    "LIGHT_TIME_WEATHER": "光・時間帯・天候として探すのが自然",
    "COLOR_PATTERN_SHAPE": "色・模様・形状として独立に探すのが自然",
    "STYLE_PROCESSING": "画風・処理・表現様式として探すのが自然",
    "TEXT_SYMBOL": "文字・記号・レイアウトとして探すのが自然",
    "CONTENT_RATING": "内容区分として探すのが自然",
}

ROUTE_SUMMARY_JA = {
    "PEOPLE_COUNT": "人数・人数構成に関するタグ",
    "RELATION_ROLE": "人物関係・役割に関するタグ",
    "BODY_SITE": "身体部位・身体特徴に関するタグ",
    "HAIR_FACE": "髪・顔・目などの外観に関するタグ",
    "CLOTHING_EXPOSURE": "衣服・装身具・露出状態に関するタグ",
    "TOOL_OBJECT": "物体・道具・小物に関するタグ",
    "LIVING": "生物・植物に関するタグ",
    "NONHUMAN_TRANSFORM": "非人間的特徴・変身要素に関するタグ",
    "ACTION_CONTACT": "動作・接触に関するタグ",
    "POSE_POSITION": "姿勢・位置関係に関するタグ",
    "EXPRESSION_GAZE": "表情・視線に関するタグ",
    "FLUID_EXCRETION": "液体・分泌・排泄表現に関するタグ",
    "COMPOSITION_CAMERA": "構図・カメラ表現に関するタグ",
    "SCENE_BACKGROUND": "場所・背景に関するタグ",
    "LIGHT_TIME_WEATHER": "光・時間帯・天候に関するタグ",
    "COLOR_PATTERN_SHAPE": "色・模様・形状に関するタグ",
    "STYLE_PROCESSING": "画風・処理・表現様式に関するタグ",
    "TEXT_SYMBOL": "文字・記号・レイアウトに関するタグ",
    "CONTENT_RATING": "内容区分に関するタグ",
}


def identity_sha256(identity_key: str) -> str:
    return hashlib.sha256(identity_key.encode("utf-8")).hexdigest()


def validate_identity_binding(entry: dict, expected: dict, local_index: int) -> list[str]:
    errors: list[str] = []
    try:
        got_local = int(entry.get("lane_local_index"))
    except Exception:
        got_local = -1
    try:
        got_seq = int(entry.get("review_seq"))
    except Exception:
        got_seq = -1
    if got_local != local_index:
        errors.append(f"lane_local_index {got_local} != expected {local_index}")
    expected_seq = int(expected["review_seq"])
    if got_seq != expected_seq:
        errors.append(f"review_seq {got_seq} != expected {expected_seq}")
    expected_hash = identity_sha256(expected["identity_key"])
    if entry.get("identity_sha256") != expected_hash:
        errors.append("identity_sha256 mismatch")
    return errors


def _json_list(values) -> str:
    return json.dumps(list(values), ensure_ascii=False, separators=(",", ":"))


def compact_row_to_full(entry: dict, expected: dict, fields: list[str]) -> dict[str, str]:
    if set(entry) != COMPACT_ROW_FIELDS:
        missing = sorted(COMPACT_ROW_FIELDS - set(entry))
        extra = sorted(set(entry) - COMPACT_ROW_FIELDS)
        raise ValueError(f"compact row field-set mismatch missing={missing} extra={extra}")

    routes = entry["routes"]
    if not isinstance(routes, list) or len(routes) > 3:
        raise ValueError("routes must be a list with at most 3 entries")
    for route in routes:
        if not isinstance(route, dict) or set(route) != {"id", "strength"}:
            raise ValueError("each compact route must contain exactly id,strength")

    local = entry["local_refinement_ids"]
    body = entry["body_site_ids"]
    themes = entry["theme_ids"]
    evidence = entry["evidence_urls"]
    for name, value in (
        ("local_refinement_ids", local),
        ("body_site_ids", body),
        ("theme_ids", themes),
        ("evidence_urls", evidence),
    ):
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            raise ValueError(f"{name} must be a string list")

    mode = str(entry["discovery_mode"])
    gap = str(entry["route_vocabulary_gap"])
    depth = str(entry["review_depth"])

    if mode == "SEARCH_ORIENTED":
        summary = "検索向けタグとして確認"
    elif mode == "SEMANTIC_UNRESOLVED":
        summary = "直接根拠を調査したが意味範囲を確定できないタグ"
    elif routes:
        summary = ROUTE_SUMMARY_JA.get(str(routes[0]["id"]), "閲覧分類コードで確認したタグ")
    elif body:
        summary = "身体部位・身体特徴に関するタグ"
    elif themes:
        summary = "テーマ特性に関するタグ"
    elif gap == "YES":
        summary = "既存ルート語彙では十分に表現できない閲覧対象"
    else:
        summary = "閲覧分類コードで確認したタグ"

    row = {field: "" for field in fields}
    row["review_seq"] = str(int(entry["review_seq"]))
    row["identity_key"] = expected["identity_key"]
    row["manual_seen"] = "YES"
    row["semantic_summary_ja"] = summary
    row["discovery_mode"] = mode
    for i, route in enumerate(routes, start=1):
        rid = str(route["id"])
        row[f"route_{i}_id"] = rid
        row[f"route_{i}_strength"] = str(route["strength"])
        row[f"route_{i}_reason_ja"] = ROUTE_REASON_JA.get(rid, "独立した閲覧軸として探すのが自然")
    row["local_refinement_ids"] = _json_list(local)
    row["body_site_ids"] = _json_list(body)
    row["theme_ids"] = _json_list(themes)
    row["route_vocabulary_gap"] = gap
    row["route_vocabulary_gap_note"] = (
        "既存の閲覧ルート語彙では対象を十分に表現できない"
        if gap == "YES" else ""
    )
    row["review_depth"] = depth
    row["evidence_urls"] = _json_list(evidence)
    row["uncertainty_note"] = (
        "直接根拠を調査したがタグ固有の意味範囲を安全に確定できない"
        if mode == "SEMANTIC_UNRESOLVED" else ""
    )
    return row


def validate_compact_hold(hold: dict, expected: dict, local_index: int) -> list[str]:
    errors: list[str] = []
    if set(hold) != COMPACT_HOLD_FIELDS:
        missing = sorted(COMPACT_HOLD_FIELDS - set(hold))
        extra = sorted(set(hold) - COMPACT_HOLD_FIELDS)
        errors.append(f"compact hold field-set mismatch missing={missing} extra={extra}")
        return errors
    errors.extend(validate_identity_binding(hold, expected, local_index))
    if hold.get("reason_code") not in HOLD_REASON_CODES:
        errors.append("invalid hold reason_code")
    attempts = hold.get("research_attempt_codes")
    if not isinstance(attempts, list) or not attempts:
        errors.append("hold research_attempt_codes must be a non-empty list")
    elif any(x not in RESEARCH_ATTEMPT_CODES for x in attempts):
        errors.append("invalid hold research_attempt_codes")
    return errors
