#!/usr/bin/env python3
"""Deterministically classify the current OPEN Issue #180 units/campaigns.

The lane labels are execution scheduling only. This audit never creates HOME
evidence or changes the v3 resolver's semantic decisions.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/issue180-v3"
UNITS = OUT / "research_units_v3.csv"
CLOSURES = ROOT / "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
CAMPAIGNS = OUT / "parallel_authority_campaigns_v2.csv"
QA_LEDGER = ROOT / "docs/issue180/parallel/QA_REVIEW_LEDGER_V2.csv"
SOURCE_LEDGER = ROOT / "docs/issue180/parallel/SOURCE_REVIEW_LEDGER_V2.csv"
MIGRATION = OUT / "migration_comparison_v3.csv"
DISPATCH_DIR = ROOT / "docs/issue180/parallel/dispatch"
AUDIT = ROOT / "docs/issue180/v3/PHASE_B_LANE_AUDIT_V2.csv"
MEMBER_AUDIT = ROOT / "docs/issue180/v3/PHASE_B_MEMBER_LANE_AUDIT_V2.csv"

FIELDS = [
    "unit_id", "member_ids_sha256", "campaign_id", "campaign_fingerprint",
    "campaign_state", "campaign_key", "member_count", "lane", "route_basis",
    "accepted_source_review_ids", "dispatch_source_review_ids",
    "dispatch_source_hint_urls", "prior_checked_routes", "migration_residual_tags", "v3_classification",
    "work_bucket", "candidate_roots", "rejection_reason",
]
LANES = {"AUTO_SAFE", "HIGH_YIELD_RESEARCH", "FINAL_UNRESOLVED"}
MEMBER_FIELDS = [
    "unit_id", "member_ids_sha256", "campaign_id", "campaign_fingerprint",
    "campaign_key", "canonical_tag", "lane", "home_roots",
    "source_review_ids", "source_urls", "prior_checked_routes",
    "migration_residual", "unit_classification", "work_bucket", "reason",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def member_hash(tags: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(tags)).encode("utf-8")).hexdigest()


def classify_lane(
    closure_classification: str,
    conflict: bool,
    migration_residual: bool,
) -> tuple[str, str]:
    """Classify unit-level conflict/migration; exact source scope is classified per member."""
    if closure_classification == "AUTO_RESOLVE_STRUCTURE":
        return "AUTO_SAFE", "current v3 closure has one validated structural HOME path"
    if conflict:
        return "HIGH_YIELD_RESEARCH", "validated competing HOME path requires final conflict review"
    if migration_residual:
        return "HIGH_YIELD_RESEARCH", "current v3 migration residual requires exact final-gate review"
    return (
        "FINAL_UNRESOLVED",
        "no validated HOME path, accepted reusable source, migration residual, or validated conflict; candidate roots remain non-authoritative",
    )


def accepted_sources(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_campaign: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[str] = set()
    for row in rows:
        if row.get("review_status") != "ACCEPTED":
            continue
        rid = row.get("source_review_id", "").strip()
        if not rid or rid in seen:
            raise ValueError(f"blank/duplicate ACCEPTED source_review_id: {rid!r}")
        seen.add(rid)
        keys = json.loads(row.get("campaign_keys", "[]") or "[]")
        for key in keys:
            by_campaign[key].append(row)
    return by_campaign


def checked_routes(
    qa_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    """Return every route already reviewed, including approved source URLs."""
    prior_routes: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in qa_rows:
        key = row.get("campaign_key", "")
        routes = json.loads(row.get("research_routes_json", "[]") or "[]")
        if not isinstance(routes, list):
            raise ValueError(f"research_routes_json is not a list for {key}")
        for route in routes:
            if isinstance(route, dict):
                prior_routes[key].append({**route, "checked_campaign_fingerprint": row.get("campaign_fingerprint", "")})
            elif isinstance(route, str) and route.strip():
                prior_routes[key].append({
                    "route_type": "RECORDED_ROUTE",
                    "url_or_query": route,
                    "result": "Recorded prior route; do not repeat.",
                    "checked_campaign_fingerprint": row.get("campaign_fingerprint", ""),
                })
    for row in source_rows:
        if row.get("review_status") != "ACCEPTED":
            continue
        url = row.get("source_url", "").strip()
        if not url:
            continue
        for key in json.loads(row.get("campaign_keys", "[]") or "[]"):
            prior_routes[key].append({
                "route_type": row.get("authority_type", "ACCEPTED_SOURCE_REVIEW"),
                "url_or_query": url,
                "result": f"Already reviewed under accepted source {row.get('source_review_id', '')}; reuse its recorded exact scope without repeating the route.",
                "source_review_id": row.get("source_review_id", ""),
                "checked_campaign_fingerprint": "accepted-source-ledger",
            })
    for key, routes in prior_routes.items():
        unique = {(route.get("url_or_query", ""), route.get("source_review_id", "")): route for route in routes}
        prior_routes[key] = [unique[item] for item in sorted(unique)]
    return prior_routes


def exact_positive_scope_match(scope: str, tag: str) -> bool:
    """Match a complete canonical tag in an accepted positive scope statement."""
    for match in re.finditer(r"(?<![A-Za-z0-9_])" + re.escape(tag) + r"(?![A-Za-z0-9_])", scope, re.I):
        context = scope[max(0, match.start() - 72):min(len(scope), match.end() + 88)]
        if re.search(r"not\s+(?:named|covered|included|mapped|imported)|withheld|excluded|unresolved|does\s+not\s+(?:name|cover|include)", context, re.I):
            continue
        return True
    return False


def build_member_audit(unit_rows: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    """Classify every exact OPEN Character member while retaining its RU fingerprint."""
    unit_rows = unit_rows if unit_rows is not None else build_unit_audit()
    open_units = {row["unit_id"]: row for row in read_csv(UNITS) if row["status"] == "OPEN"}
    sources = read_csv(SOURCE_LEDGER)
    source_rows_by_campaign: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in sources:
        if source.get("review_status") != "ACCEPTED":
            continue
        for key in json.loads(source.get("campaign_keys", "[]") or "[]"):
            source_rows_by_campaign[key].append(source)
    result: list[dict[str, str]] = []
    for unit in unit_rows:
        campaign_key = unit["campaign_key"]
        campaign_sources = source_rows_by_campaign.get(campaign_key, [])
        prior = json.loads(unit["prior_checked_routes"])
        checked_urls = {route.get("url_or_query", "") for route in prior}
        hints = json.loads(unit["dispatch_source_hint_urls"])
        fresh_hints = sorted(url for url in hints if url and url not in checked_urls)
        migration_tags = set(json.loads(unit["migration_residual_tags"]))
        unit_conflict = unit["v3_classification"] == "CONFLICT_REVIEW"
        unit_tags = sorted(json.loads(open_units[unit["unit_id"]]["member_ids/tags"]))
        for tag in unit_tags:
            exact_sources = [source for source in campaign_sources if exact_positive_scope_match(source.get("proved_scope", ""), tag)]
            roots = sorted({source.get("home_root", "").strip() for source in exact_sources if source.get("home_root", "").strip()})
            source_ids = sorted({source.get("source_review_id", "") for source in exact_sources if source.get("source_review_id", "")})
            source_urls = sorted({source.get("source_url", "") for source in exact_sources if source.get("source_url", "")})
            is_migration = tag in migration_tags
            if unit_conflict:
                lane, reason = "HIGH_YIELD_RESEARCH", "validated competing HOME conflict requires exact conflict review"
            elif is_migration:
                lane, reason = "HIGH_YIELD_RESEARCH", "current v3 migration residual requires exact final-gate review"
            elif len(roots) > 1:
                lane, reason = "HIGH_YIELD_RESEARCH", "accepted exact-scope evidence has competing HOME roots"
            elif roots:
                lane, reason = "AUTO_SAFE", "ACCEPTED source ledger names this exact member and one canonical HOME"
            elif fresh_hints:
                lane, reason = "HIGH_YIELD_RESEARCH", "tracked dispatch provides a concrete not-yet-reviewed official source hint"
            else:
                lane, reason = "FINAL_UNRESOLVED", "no exact accepted source coverage, unreviewed official hint, migration residual, or validated conflict"
            result.append({
                "unit_id": unit["unit_id"],
                "member_ids_sha256": unit["member_ids_sha256"],
                "campaign_id": unit["campaign_id"],
                "campaign_fingerprint": unit["campaign_fingerprint"],
                "campaign_key": campaign_key,
                "canonical_tag": tag,
                "lane": lane,
                "home_roots": json.dumps(roots, ensure_ascii=False, separators=(",", ":")),
                "source_review_ids": json.dumps(source_ids, ensure_ascii=False, separators=(",", ":")),
                "source_urls": json.dumps(source_urls, ensure_ascii=False, separators=(",", ":")),
                "prior_checked_routes": json.dumps(prior, ensure_ascii=False, separators=(",", ":")),
                "migration_residual": "true" if is_migration else "false",
                "unit_classification": unit["v3_classification"],
                "work_bucket": unit["work_bucket"],
                "reason": reason,
            })
    return result


def build_unit_audit() -> list[dict[str, str]]:
    units = read_csv(UNITS)
    closures = read_csv(CLOSURES)
    campaigns = read_csv(CAMPAIGNS)
    source_rows = read_csv(SOURCE_LEDGER)
    migration_rows = read_csv(MIGRATION)
    qa_rows = read_csv(QA_LEDGER)

    unit_by_id = {row["unit_id"]: row for row in units}
    if len(unit_by_id) != len(units):
        raise ValueError("duplicate Research Unit id")
    closure_by_id = {row["unit_id"]: row for row in closures}
    if len(closure_by_id) != len(closures):
        raise ValueError("duplicate closure classification id")
    current_open = {uid: row for uid, row in unit_by_id.items() if row["status"] == "OPEN"}
    if set(current_open) != set(closure_by_id):
        raise ValueError("closure classifications do not cover exactly the current OPEN Research Units")

    sources_by_campaign = accepted_sources(source_rows)
    migration_tags = {
        row["canonical_tag"] for row in migration_rows
        if row.get("migration_state") == "V3_UNRESOLVED"
    }
    conflict_keys = {
        row.get("campaign_key", "") for row in qa_rows
        if row.get("decision") == "ACCEPT_CONFLICT"
    }
    prior_routes = checked_routes(qa_rows, source_rows)
    dispatch_by_campaign: dict[tuple[str, str], dict[str, str]] = {}
    for slot in range(4):
        for row in read_csv(DISPATCH_DIR / f"fwd-{slot}.csv"):
            key = (row.get("campaign_key", ""), row.get("campaign_fingerprint", ""))
            if key in dispatch_by_campaign:
                raise ValueError(f"duplicate tracked dispatch campaign: {key}")
            dispatch_by_campaign[key] = row

    campaign_by_unit: dict[str, tuple[dict[str, str], str]] = {}
    for campaign in campaigns:
        tags = json.loads(campaign["member_ids/tags"])
        campaign_fingerprint = campaign["campaign_fingerprint"]
        for source_unit in json.loads(campaign["source_units"]):
            uid = source_unit["unit_id"]
            if uid not in current_open:
                continue
            unit_tags = json.loads(current_open[uid]["member_ids/tags"])
            expected_hash = member_hash(unit_tags)
            if source_unit.get("member_ids_sha256") != expected_hash:
                raise ValueError(f"campaign {campaign['campaign_key']} has stale unit fingerprint: {uid}")
            if set(tags) != set(unit_tags):
                raise ValueError(f"campaign {campaign['campaign_key']} does not exactly cover Research Unit {uid}")
            if uid in campaign_by_unit:
                raise ValueError(f"OPEN Research Unit is mapped to multiple campaigns: {uid}")
            campaign_by_unit[uid] = (campaign, expected_hash)
    if set(campaign_by_unit) != set(current_open):
        missing = sorted(set(current_open) - set(campaign_by_unit))
        raise ValueError(f"OPEN Research Units lack an exact campaign: {missing[:10]}")

    result: list[dict[str, str]] = []
    for uid, unit in sorted(current_open.items()):
        campaign, fingerprint = campaign_by_unit[uid]
        closure = closure_by_id[uid]
        tags = json.loads(unit["member_ids/tags"])
        reusable = sorted(sources_by_campaign.get(campaign["campaign_key"], []), key=lambda r: r["source_review_id"])
        reusable_ids = [row["source_review_id"] for row in reusable]
        exact_migration_tags = sorted(set(tags) & migration_tags)
        is_conflict = closure["classification"] == "CONFLICT_REVIEW" or campaign["campaign_key"] in conflict_keys
        lane, basis = classify_lane(closure["classification"], is_conflict, bool(exact_migration_tags))
        dispatch = dispatch_by_campaign.get((campaign["campaign_key"], campaign_fingerprint), {})
        dispatch_ids = json.loads(dispatch.get("source_hint_review_ids", "[]") or "[]")
        dispatch_urls = json.loads(dispatch.get("source_hint_urls", "[]") or "[]")
        urls = sorted({row["source_url"] for row in reusable} | set(dispatch_urls))
        result.append({
            "unit_id": uid,
            "member_ids_sha256": fingerprint,
            "campaign_id": campaign["campaign_id"],
            "campaign_fingerprint": campaign["campaign_fingerprint"],
            "campaign_state": campaign["research_state"],
            "campaign_key": campaign["campaign_key"],
            "member_count": str(len(tags)),
            "lane": lane,
            "route_basis": basis,
            "accepted_source_review_ids": json.dumps(reusable_ids, ensure_ascii=False, separators=(",", ":")),
            "dispatch_source_review_ids": json.dumps(sorted(dispatch_ids), ensure_ascii=False, separators=(",", ":")),
            "dispatch_source_hint_urls": json.dumps(urls, ensure_ascii=False, separators=(",", ":")),
            "prior_checked_routes": json.dumps(
                prior_routes.get(campaign["campaign_key"], []),
                ensure_ascii=False, separators=(",", ":"),
            ),
            "migration_residual_tags": json.dumps(exact_migration_tags, ensure_ascii=False, separators=(",", ":")),
            "v3_classification": closure["classification"],
            "work_bucket": closure["work_bucket"],
            "candidate_roots": closure["candidate_roots"],
            "rejection_reason": closure["rejection_reason"],
        })
    if len(result) != len(current_open) or any(row["lane"] not in LANES for row in result):
        raise ValueError("lane audit is incomplete or contains an invalid scheduling label")
    return result


def build_audit() -> list[dict[str, str]]:
    """Return one row per OPEN unit, with its queue lane derived from member lanes."""
    units = build_unit_audit()
    members = build_member_audit(units)
    by_unit: dict[str, list[str]] = defaultdict(list)
    for member in members:
        by_unit[member["unit_id"]].append(member["lane"])
    for unit in units:
        lanes = set(by_unit[unit["unit_id"]])
        if lanes == {"AUTO_SAFE"}:
            unit["lane"] = "AUTO_SAFE"
        elif "HIGH_YIELD_RESEARCH" in lanes:
            unit["lane"] = "HIGH_YIELD_RESEARCH"
        else:
            unit["lane"] = "FINAL_UNRESOLVED"
        unit["route_basis"] = "member lanes: " + ", ".join(
            f"{lane}={by_unit[unit['unit_id']].count(lane)}"
            for lane in ("AUTO_SAFE", "HIGH_YIELD_RESEARCH", "FINAL_UNRESOLVED")
            if lane in lanes
        )
    return units


def main() -> None:
    rows = build_audit()
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    member_rows = build_member_audit(rows)
    with MEMBER_AUDIT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MEMBER_FIELDS, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(member_rows)
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["lane"]] += 1
    print(json.dumps({
        "rows": len(rows),
        "lane_counts": {lane: counts.get(lane, 0) for lane in sorted(LANES)},
        "audit": AUDIT.relative_to(ROOT).as_posix(),
        "member_rows": len(member_rows),
        "member_lane_counts": {lane: sum(row["lane"] == lane for row in member_rows) for lane in sorted(LANES)},
        "member_audit": MEMBER_AUDIT.relative_to(ROOT).as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
