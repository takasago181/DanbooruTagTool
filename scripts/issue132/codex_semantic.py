#!/usr/bin/env python3
from __future__ import annotations

import hashlib

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


def identity_sha256(identity_key: str) -> str:
    return hashlib.sha256(identity_key.encode("utf-8")).hexdigest()


def validate_binding(entry: dict, expected: dict, local_index: int) -> list[str]:
    errors: list[str] = []
    try:
        got_index = int(entry.get("lane_local_index"))
    except Exception:
        got_index = -1
    try:
        got_seq = int(entry.get("review_seq"))
    except Exception:
        got_seq = -1
    if got_index != local_index:
        errors.append(f"lane_local_index {got_index} != {local_index}")
    if got_seq != int(expected["review_seq"]):
        errors.append(f"review_seq {got_seq} != {expected['review_seq']}")
    if entry.get("identity_sha256") != identity_sha256(expected["identity_key"]):
        errors.append("identity_sha256 mismatch")
    return errors


def _string_list(value, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise ValueError(f"{label} must be a string list")
    return value


def validate_compact_row(
    row: dict,
    expected: dict,
    local_index: int,
    contract: dict,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(row, dict) or set(row) != COMPACT_ROW_FIELDS:
        return ["compact row field-set mismatch"]
    errors.extend(validate_binding(row, expected, local_index))

    modes = set(contract["allowed_discovery_modes"])
    strengths = set(contract["allowed_route_strengths"])
    depths = set(contract["allowed_review_depths"])
    route_ids = set(contract["route_ids"])
    body_ids = set(contract["body_site_ids"])
    theme_ids = set(contract["theme_ids"])
    local_parent = contract["local_refinement_parent"]
    rules = contract["validation_rules"]

    mode = row["discovery_mode"]
    depth = row["review_depth"]
    gap = row["route_vocabulary_gap"]
    if mode not in modes:
        errors.append("invalid discovery_mode")
    if depth not in depths:
        errors.append("invalid review_depth")
    if gap not in {"YES", "NO"}:
        errors.append("route_vocabulary_gap must be YES/NO")

    routes = row["routes"]
    selected: list[str] = []
    if not isinstance(routes, list) or len(routes) > int(rules["max_routes"]):
        errors.append("invalid routes")
        routes = []
    else:
        for item in routes:
            if not isinstance(item, dict) or set(item) != {"id", "strength"}:
                errors.append("route field-set mismatch")
                continue
            rid = item["id"]
            strength = item["strength"]
            if rid not in route_ids:
                errors.append(f"invalid route id {rid}")
            if strength not in strengths:
                errors.append(f"invalid route strength for {rid}")
            selected.append(rid)
    if rules["require_unique_routes"] and len(selected) != len(set(selected)):
        errors.append("duplicate route ids")

    try:
        locals_ = _string_list(row["local_refinement_ids"], "local_refinement_ids")
        bodies = _string_list(row["body_site_ids"], "body_site_ids")
        themes = _string_list(row["theme_ids"], "theme_ids")
        evidence = _string_list(row["evidence_urls"], "evidence_urls")
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    if any(x not in local_parent for x in locals_):
        errors.append("invalid local_refinement_ids")
    for local in locals_:
        parent = local_parent.get(local)
        if parent not in set(selected):
            errors.append(f"local refinement {local} requires route {parent}")
    if any(x not in body_ids for x in bodies):
        errors.append("invalid body_site_ids")
    if any(x not in theme_ids for x in themes):
        errors.append("invalid theme_ids")

    if rules["researched_requires_evidence"] and depth == "RESEARCHED" and not evidence:
        errors.append("RESEARCHED requires evidence")

    if mode in {"SEARCH_ORIENTED", "SEMANTIC_UNRESOLVED"}:
        if rules["search_or_unresolved_carries_no_browse_facets"] and (
            routes or locals_ or bodies or themes
        ):
            errors.append(f"{mode} must not carry browse facets")
        if rules["search_or_unresolved_route_vocabulary_gap_must_be_no"] and gap != "NO":
            errors.append(f"{mode} requires route_vocabulary_gap=NO")

    if mode == "SEMANTIC_UNRESOLVED":
        if rules["semantic_unresolved_requires_researched"] and depth != "RESEARCHED":
            errors.append("SEMANTIC_UNRESOLVED must be RESEARCHED")
        if rules["semantic_unresolved_requires_evidence"] and not evidence:
            errors.append("SEMANTIC_UNRESOLVED requires evidence")

    if mode in {"BROWSE_WORTHY", "MIXED"}:
        if rules["browse_capable_requires_route_or_facet_or_vocabulary_gap"] and not (
            routes or bodies or themes or gap == "YES"
        ):
            errors.append("browse-capable mode requires route/facet/gap")
        if (
            rules["browse_routes_require_at_least_one_core"]
            and routes
            and not any(item.get("strength") == "CORE" for item in routes if isinstance(item, dict))
        ):
            errors.append("browse routes require at least one CORE route")

    return errors


def validate_compact_hold(
    hold: dict,
    expected: dict,
    local_index: int,
) -> list[str]:
    if not isinstance(hold, dict) or set(hold) != COMPACT_HOLD_FIELDS:
        return ["compact hold field-set mismatch"]
    errors = validate_binding(hold, expected, local_index)
    if hold.get("reason_code") not in HOLD_REASON_CODES:
        errors.append("invalid hold reason_code")
    attempts = hold.get("research_attempt_codes")
    if (
        not isinstance(attempts, list)
        or not attempts
        or any(x not in RESEARCH_ATTEMPT_CODES for x in attempts)
    ):
        errors.append("invalid research_attempt_codes")
    return errors
